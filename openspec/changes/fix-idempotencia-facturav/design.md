# Design: fix-idempotencia-facturav

## Enfoque técnico

Fix 100% de BD, sin cambios de código de aplicación. Una revisión Alembic nueva encadenada a `806cfc3bfdf2` (único head commiteado) agrega `facturav.idempotency_key` (VARCHAR(36) NULL) y los índices únicos `idx_uq_idempotency` e `idx_uq_comprobante`, con DDL de existencia-verificada (idempotente ante doble aplicación manual+Alembic) y un gate de duplicados que decide en runtime si crear `idx_uq_comprobante`. `index.py:152` (`upgrade()` en startup) la aplica sola en el próximo deploy. Cumple los requisitos del delta `specs/ventas-idempotencia/spec.md`.

## Decisiones de arquitectura

| # | Decisión | Opciones | Tradeoff | Veredicto |
|---|---|---|---|---|
| D1 | Mecanismo | Alembic vs SQL crudo vs híbrido | Crudo ya falló en prod (gitignored, invisible); Alembic auto-aplica y commitea | **Alembic** |
| D2 | Forma del DDL | `op.add_column`/`create_index` vs `op.execute` crudo | Crudo replica exacto el SQL ya validado por DBA y simplifica los checks | **`op.execute` + `inspect()`** |
| D3 | Gate `idx_uq_comprobante` | Fail vs skip+warning vs split duro en 2 revisiones | Fail rompería el startup en ambientes con datos sucios; split duro complica la cadena | **Skip+warning en la misma revisión**; revisión diferida solo si hay dups |
| D4 | Paridad del modelo | `index=True, unique=True` vs índices solo en migración | Paridad añade ruido de autogenerate (`ix_` vs `idx_`); propuesta lo excluye | **Sin cambios de modelo** |
| D5 | Huérfana `cc3c7d6e8978` | Reparar `version_num` vs ignorar | Pyc sin `.py` rompe `upgrade()` solo si `alembic_version` la apunta | **Pre-flight**: verificar y reparar tras confirmar esquema |

## Flujo de datos (solo DDL)

```
index.py:152 upgrade() → <rev> → checks de existencia
  ├─ columna? no → ALTER TABLE facturav ADD idempotency_key VARCHAR(36) NULL
  ├─ idx_uq_idempotency? no → CREATE UNIQUE INDEX idx_uq_idempotency
  └─ idx_uq_comprobante? no → pre-check duplicados (GROUP BY punto_vta,nro_comprobante,idtipocomprobante HAVING COUNT(*)>1)
       ├─ 0 → CREATE UNIQUE INDEX idx_uq_comprobante
       └─ >0 → print warning con claves; índice DIFERIDO (revisión posterior)
```

## Cambios de archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `migrations/versions/<rev>_add_idempotency_facturav.py` | Create | Revisión principal: columna + 2 índices, checks y gate |
| `migrations/versions/<rev2>_add_idx_uq_comprobante.py` | Create (condicional) | Solo si hay duplicados: índice diferido, con check de existencia |
| `models/ventas.py`, `services/*`, `index.py` | Sin cambio | Fix de BD; el modelo ya coincide con el esquema objetivo |

## Interfaces / Contratos

Patrón no obvio (gate + checks) de la revisión principal:

```python
from alembic import op
from sqlalchemy import inspect, text

revision = '<rev>'              # id 12-hex generado con flask db revision
down_revision = '806cfc3bfdf2'

def _columna(conn, nombre):
    return nombre in [c['name'] for c in inspect(conn).get_columns('facturav')]

def _indice(conn, nombre):
    return nombre in [i['name'] for i in inspect(conn).get_indexes('facturav')]

def upgrade():
    conn = op.get_bind()
    if not _columna(conn, 'idempotency_key'):
        op.execute('ALTER TABLE facturav ADD COLUMN idempotency_key VARCHAR(36) NULL')
    if not _indice(conn, 'idx_uq_idempotency'):
        op.execute('CREATE UNIQUE INDEX idx_uq_idempotency ON facturav(idempotency_key)')
    if not _indice(conn, 'idx_uq_comprobante'):
        dups = conn.execute(text(
            "SELECT punto_vta, nro_comprobante, idtipocomprobante, COUNT(*) "
            "FROM facturav GROUP BY 1,2,3 HAVING COUNT(*) > 1")).fetchall()
        if dups:
            print(f"[migracion] {len(dups)} correlativos duplicados; "
                  f"idx_uq_comprobante diferido. Muestra: {dups[:5]}")
        else:
            op.execute('CREATE UNIQUE INDEX idx_uq_comprobante '
                       'ON facturav(punto_vta, nro_comprobante, idtipocomprobante)')

def downgrade():
    conn = op.get_bind()
    if _indice(conn, 'idx_uq_comprobante'):
        op.execute('DROP INDEX idx_uq_comprobante ON facturav')
    if _indice(conn, 'idx_uq_idempotency'):
        op.execute('DROP INDEX idx_uq_idempotency ON facturav')
    if _columna(conn, 'idempotency_key'):
        op.execute('ALTER TABLE facturav DROP COLUMN idempotency_key')
```

Alineación del modelo: `models/ventas.py:25` `db.Column(db.String(36), nullable=True)` — tipo, longitud y nullable coinciden con `VARCHAR(36) NULL`. Sin `index` en el modelo (índices viven solo en la migración, igual que en `SQL/migration_idempotencia.sql`). **Sin mismatch.**

## Estrategia de verificación (sin runner formal)

| Capa | Qué | Cómo |
|---|---|---|
| Manual BD | columna + índices + versión | `SHOW COLUMNS FROM facturav LIKE 'idempotency_key'`; `SHOW INDEX FROM facturav`; `SELECT version_num FROM alembic_version` |
| Sanity startup | sin 1054 | `python index.py` (upgrade no-op) + POST de venta con `_idempotency_key`; POST duplicado retorna factura existente |
| Doble aplicación | manual+Alembic | Aplicar sobre esquema ya migrado manualmente → sin error (checks de existencia) |
| Regresión app (opcional) | lógica idempotencia | `pytest tests/test_services_ventas.py` si pytest está instalado (SQLite; no valida la migración en sí) |

## Migración / Rollout — estrategia de split

Procedimiento de decisión en apply:
1. **Pre-flight**: `SELECT version_num FROM alembic_version` → debe ser `806cfc3bfdf2`. Si apunta a `cc3c7d6e8978` (pyc huérfano, `.py` nunca commiteado), confirmar con DBA que el esquema real coincide y reparar `UPDATE alembic_version SET version_num='806cfc3bfdf2'` antes del deploy.
2. **Pre-check de duplicados** (query del gate) contra prod:
   - **0 dups** → ship solo la revisión A; en el primer arranque crea columna + ambos índices.
   - **>0 dups** → ship A (crea columna + `idx_uq_idempotency`; difiere el compuesto con warning) y **redactar** la revisión B `add_idx_uq_comprobante` (`down_revision=<rev>`, mismo patrón check+CREATE). B se commitea y deployea SOLO tras la limpieza DBA — nunca junto con A mientras haya dups (rompería el startup).
3. **Rollback**: `downgrade()` con drops existence-checked; sin código de app, no hay rollback de aplicación.

## Preguntas abiertas

- [ ] Si hay dups: ¿commiteamos B recién tras la limpieza o se mantiene borrador local? (decisión del owner/DBA)
- [ ] Confirmar si el SQL manual ya se aplicó en prod (los checks lo absorben; solo informativo)
- [ ] ¿Correr `pytest tests/test_services_ventas.py` como regresión opcional? (requiere pytest instalado)
