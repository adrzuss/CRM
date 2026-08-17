# Verificación: fix-idempotencia-facturav

**Change**: fix-idempotencia-facturav
**Version**: delta `specs/ventas-idempotencia/spec.md` (sin versión explícita)
**Mode**: Standard (strict_tdd=false, sin runner formal — verificación manual/estática según instrucción del orchestrator; pytest presente localmente pero NO ejecutado por orden explícita)

## Completeness

| Métrica | Valor |
|---------|-------|
| Tareas totales | 14 |
| Tareas completas | 11 |
| Tareas incompletas | 3 (3.1, 3.4, 3.5 — verificación manual prod, PENDING-MANUAL) |

Detalle: 11/14 completadas. Fase 1 (1.1–1.7) ✓, Fase 2 (2.1–2.2) ✓, Fase 3 parcial (3.2 ✓, 3.3 ✓; 3.1/3.4/3.5 pendientes prod), Fase 4 (4.1–4.2) ✓.

## Build & Tests Execution

**Build**: ➖ No aplica (fix 100% BD, sin build de app).
**Parse**: ✅ `py_compile` OK sobre `migrations/versions/c2d3df6d5f32_add_idempotency_facturav.py` (evidencia de apply).

**Tests**: ➖ No ejecutados por instrucción del orchestrator ("NO test runner... no intentar pytest; verificación manual/estática; no fabricar resultados").
```text
Nota de transparencia: pytest 9.1.1 está instalado localmente y requirements.txt declara
pytest>=8.0 (L98) y pytest-flask>=1.3 (L99). No obstante, se respetó la instrucción de no
ejecutarlo; el design.md eligió verificación manual de BD para este fix (sin runner formal).
```

**Cobertura**: ➖ No disponible (sin runner ejecutado).

**Evidencia runtime real (fase apply, BD local espejo de prod `localhost:3306/erp-vanina-modas`)**, tomada de `sdd/fix-idempotencia-facturav/apply-progress`:
```text
- Single head: ScriptDirectory → heads=['c2d3df6d5f32'] (confirmado también en verify)
- No-op doble aplicación (3.2): flask db upgrade sobre esquema ya migrado manualmente → sin error, sin objetos duplicados
- Downgrade: flask db downgrade 806cfc3bfdf2 → drops correctos, 3717 filas intactas
- Fresh-create: flask db upgrade desde estado limpio → columna + ambos índices creados, 0 duplicados
- Esquema (3.3): information_schema → idempotency_key varchar(36) NULL + idx_uq_comprobante (unique, 3 cols) + idx_uq_idempotency (unique)
```

## Spec Compliance Matrix

| Requirement | Scenario | Evidencia | Resultado |
|-------------|----------|-----------|-----------|
| REQ-1 Esquema BD | Columna e índices creados | Migración `c2d3df6d5f32` (ADD COLUMN + 2 CREATE UNIQUE INDEX) + runtime local fresh-create + information_schema (3.3) | ✅ COMPLIANT (runtime manual) |
| REQ-1 Esquema BD | Sin alteración de datos existentes | Migración solo DDL (ADD COLUMN / CREATE INDEX, sin DML); downgrade runtime preservó 3717 filas | ✅ COMPLIANT (runtime manual + inspección estática) |
| REQ-2 Aplicación idempotente | Doble aplicación (manual + Alembic) | Helpers `_columna()`/`_indice()` con `inspect()`; runtime no-op 3.2 sobre esquema ya migrado → sin error ni duplicados | ✅ COMPLIANT (runtime manual) |
| REQ-3 Pre-check correlativos | Sin duplicados → `idx_uq_comprobante` en la misma migración | Gate `GROUP BY ... HAVING COUNT(*)>1`; runtime fresh-create con 0 dups → índice creado | ✅ COMPLIANT (runtime manual) |
| REQ-3 Pre-check correlativos | Duplicados presentes → índice NO creado, diferido | Rama `if dups:` → print warning + skip (inspección estática de `upgrade()`); rama nunca ejercitada en runtime (BD local sin dups) | ⚠️ PARTIAL (solo estático) |
| REQ-4 alembic_version | Cadena de revisión normal | `down_revision='806cfc3bfdf2'`; ScriptDirectory single head `c2d3df6d5f32`; runtime local 806cfc3bfdf2 → c2d3df6d5f32 | ✅ COMPLIANT (runtime manual + estático) |
| REQ-4 alembic_version | Revisión huérfana `cc3c7d6e8978` | Pyc huérfano confirmado en `__pycache__` (sin `.py`); BD local en 806cfc3bfdf2 sin conflicto; reparación en prod = tarea 3.1 PENDING-MANUAL | ⚠️ PARTIAL (local OK; prod pendiente) |

**Compliance summary**: 5/7 compliant, 2/7 partial (1 por rama solo estática, 1 por pendiente prod).

## Correctness (Static Evidence)

| Requirement | Estado | Notas |
|------------|--------|-------|
| Identificadores de revisión | ✅ Implementado | `revision='c2d3df6d5f32'`, `down_revision='806cfc3bfdf2'`, `branch_labels=None`, `depends_on=None` |
| Cadena de revisión / head único | ✅ Implementado | ScriptDirectory: heads=`['c2d3df6d5f32']`; walk: c2d3df6d5f32 → 806cfc3bfdf2 (solo 2 revisiones `.py` trackeadas en git) |
| Helpers de existencia | ✅ Implementado | `_columna()`/`_indice()` con `sqlalchemy.inspect` sobre `facturav` (patrón design D2) |
| `upgrade()` columna | ✅ Implementado | `ALTER TABLE facturav ADD COLUMN idempotency_key VARCHAR(36) NULL` solo si falta (1.3) |
| `upgrade()` idx_uq_idempotency | ✅ Implementado | `CREATE UNIQUE INDEX` solo si falta (1.4) |
| `upgrade()` gate idx_uq_comprobante | ✅ Implementado | Pre-check duplicados; 0 → CREATE; >0 → warning + diferir (1.5, D3) |
| `downgrade()` | ✅ Implementado | Drops existence-checked en orden inverso: idx_uq_comprobante → idx_uq_idempotency → columna (1.6) |
| Docstring en español | ✅ Implementado | Contexto aplicación manual previa en prod + no-op esperado (1.7) |
| Alineación modelo | ✅ Implementado | `models/ventas.py:25` `db.Column(db.String(36), nullable=True)` == `VARCHAR(36) NULL`; sin `index` en modelo (D4: índices solo en migración) |
| Referencia SQL | ✅ Implementado | `SQL/migration_idempotencia.sql` con cabecera apuntando a la revisión como fuente de verdad (2.2); confirmado `git check-ignore` → gitignored |
| Sin cambios fuera de alcance | ✅ Implementado | Commit `9e8a33d` = solo migración + artefactos openspec (6 archivos, 452 inserciones); sin cambios en models/services/index.py |
| Uso en servicio | ✅ Alineado | `services/ventas/ventas.py:39,138` consulta `idempotency_key` (full-entity) — requiere la columna, que la migración provee; `:131` late assignment |

## Coherence (Design)

| Decisión | ¿Seguida? | Notas |
|----------|-----------|-------|
| D1 Alembic (no SQL crudo) | ✅ Sí | Revisión versionada `c2d3df6d5f32`; SQL queda solo como referencia DBA |
| D2 `op.execute` + `inspect()` | ✅ Sí | DDL crudo replica el SQL validado; helpers de existencia |
| D3 Gate skip+warning en la misma revisión | ✅ Sí | Rama de diferimiento presente; sin revisión B redactada (0 dups asumidos y confirmados en local) |
| D4 Sin cambios de modelo | ✅ Sí | `models/ventas.py` sin tocar en el commit; paridad ya existente desde `d7e89c0` |
| D5 Pre-flight huérfana `cc3c7d6e8978` | ⚠️ Parcial | Verificado local (BD en 806cfc3bfdf2, pyc huérfano presente sin conflicto); reparación prod = 3.1 pendiente |

## Issues Found

**CRITICAL**: None

**WARNING**:
1. **Tareas 3.1, 3.4, 3.5 pendientes (PENDING-MANUAL, prod)** — no ejecutables desde este entorno (requieren app + AFIP + acceso prod). No son defectos de implementación; bloquean la confirmación final de éxito en prod. Instrucciones exactas en la sección "Pendientes manuales".
2. **REQ-3 escenario "duplicados presentes" cubierto solo estáticamente** — la rama `if dups:` del gate nunca se ejercitó en runtime (BD local con 0 duplicados). El código es correcto por inspección (print + skip), pero sin evidencia runtime de ejecución de esa rama.

**SUGGESTION**:
1. **tasks.md referencia commit `7bbef6d` pero el commit real es `9e8a33d`** — `7bbef6d` existe como commit colgante (dangling, no referenciado por rama; diff con 9e8a33d = solo el checkmark de 4.1/4.2 en tasks.md). Actualizar la nota de la tarea 4.1 a `9e8a33d`.
2. **Discrepancia sobre pytest** — el contexto de lanzamiento decía "pytest not installed in requirements", pero `requirements.txt` L98-99 declara `pytest>=8.0`/`pytest-flask>=1.3` y pytest 9.1.1 está instalado localmente. No se ejecutó por instrucción explícita; si el orchestrator lo autoriza, `pytest tests/test_services_ventas.py` (SQLite, según design L89) puede servir como regresión app-level de la lógica de idempotencia (no valida la migración en sí).
3. **Ejercitar la rama de duplicados** — opcional: crear una BD scratch con un correlativo duplicado y ejecutar `flask db upgrade` para observar el warning y el diferimiento (cobertura runtime de REQ-3 dup).
4. **Rama de entrega** — el commit está en `style/table-header-colors` (no en main; base main = d7e89c0). El orchestrator debe definir la base del PR.

## Verdict

**PASS WITH WARNINGS**
Implementación correcta y verificada en runtime local (no-op doble aplicación, fresh-create, downgrade, esquema, head único); pendientes 3 tareas de verificación manual en prod (3.1 pre-flight, 3.4 smoke venta, 3.5 smoke regresión) que no son ejecutables desde este entorno, y 1 rama de spec cubierta solo estáticamente.

---

## Pendientes manuales (PENDING-MANUAL — ejecutar en prod)

### 3.1 Pre-flight `alembic_version` (antes del deploy)
```sql
SELECT version_num FROM alembic_version;
```
- Esperado: `806cfc3bfdf2`.
- Si es `cc3c7d6e8978` (pyc huérfano): confirmar con DBA que el esquema real coincide con `806cfc3bfdf2` y reparar:
```sql
UPDATE alembic_version SET version_num = '806cfc3bfdf2';
```
- Luego aplicar la migración (deploy o `flask db upgrade`). Verificar que `alembic_version` quede en `c2d3df6d5f32`.
- Pre-check de duplicados opcional antes del deploy:
```sql
SELECT punto_vta, nro_comprobante, idtipocomprobante, COUNT(*)
FROM facturav GROUP BY 1,2,3 HAVING COUNT(*) > 1;
```
  - 0 filas → se creará `idx_uq_comprobante` en la misma migración.
  - >0 filas → se creará con warning y `idx_uq_comprobante` quedará diferido (avisar al DBA).

### 3.4 Smoke venta con `_idempotency_key`
- POST de venta normal con `_idempotency_key` (UUID v4) → debe grabar sin error MySQL 1054.
- POST duplicado con la misma key → debe retornar la factura existente (nro_comprobante + id), sin duplicar.

### 3.5 Smoke regresión de rutas afectadas por el mismo 1054
- Recibo cta cte (`services/ventas/ventas.py:333,367` INSERT Factura).
- Remito (`services/ventas/remitos.py:38` INSERT Factura).
- Listado `facturas-cli.html` (`routes/clientes.py:216,229` query full-entity).
- NC (`routes/ventas.py:123`) corre con key `None` — backward compatible, pero su INSERT igual rompía sin la columna; verificar.

### Verificación post-deploy del esquema (3.3 en prod)
```sql
SHOW COLUMNS FROM facturav LIKE 'idempotency_key';
SHOW INDEX FROM facturav;  -- deben listarse idx_uq_idempotency e idx_uq_comprobante
SELECT version_num FROM alembic_version;  -- debe ser c2d3df6d5f32
```