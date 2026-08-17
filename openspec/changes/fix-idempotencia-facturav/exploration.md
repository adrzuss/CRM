# Exploration: fix-idempotencia-facturav

## Root Cause

La columna `idempotency_key` existe en el modelo SQLAlchemy (`models/ventas.py:25`) pero **NO existe en la tabla MySQL `facturav` en producción**. El código de idempotencia se desplegó completo (modelo + servicio + frontend + tests, commit `d7e89c0` 2026-08-07) **sin la migración de BD correspondiente**, y la migración raw que sí se creó (`SQL/migration_idempotencia.sql`) está en un directorio gitignored, por lo que nunca llegó al servidor de producción ni fue ejecutada.

Cadena de causa:

1. El cambio `idempotencia-en-ventas` (archivado en openspec) definió la migración como archivo SQL crudo en `SQL/` (tasks.md 1.1, design.md L115-128).
2. `.gitignore:15` (`SQL/*`) y `.gitignore:17` (`*.sql`) excluyen ese archivo de git. Verificado: `git check-ignore` → `.gitignore:17:*.sql`; `git ls-files SQL/migration_idempotencia.sql` → vacío; `git status` → limpio.
3. El commit `d7e89c0` incluyó `models/ventas.py`, `services/ventas/ventas.py`, `static/js/nueva_venta.js`, `tests/test_services_ventas.py` — pero **no** el `.sql` (confirmado con `git show --stat d7e89c0`).
4. El mecanismo de migración del proyecto es Alembic (`index.py:150-152` ejecuta `upgrade()` en cada startup). Solo existe la revisión `806cfc3bfdf2_initial_schema.py` (2026-06-30); **no hay revisión para `idempotency_key`**.
5. Resultado: en producción `upgrade()` no aplica nada nuevo, la tabla sigue sin la columna, y el ORM genera `SELECT ... facturav.idempotency_key ...` → `MySQLdb.OperationalError 1054`.

## Current State

- `models/ventas.py:25` — `idempotency_key = db.Column(db.String(36), nullable=True)` (sin `index=True`; el índice vive solo en el SQL).
- `services/ventas/ventas.py:33-42` — check de idempotencia al inicio de `procesar_nueva_venta`; **`ventas.py:39` es la línea que produce el error reportado** (query por key, siempre se ejecuta porque el frontend SIEMPRE envía la key).
- `services/ventas/ventas.py:131` — `nueva_factura.idempotency_key = idempotency_key or None`.
- `services/ventas/ventas.py:137-140` — recovery de `IntegrityError` re-query por key.
- `static/js/nueva_venta.js:10-19` — `generarUUID()` (crypto.randomUUID con fallback); `:320` y `:1295` — `formData.append('_idempotency_key', generarUUID())` en ambos paths de submit → el check de `ventas.py:39` se dispara en **cada** POST de venta.
- `routes/ventas.py:95` (venta) y `:123` (NC) — ambos pasan por `procesar_nueva_venta`.
- Flujo end-to-end confirmado: el campo fluye desde el JS hasta el INSERT. La única pieza faltante es la columna en la BD.

## Affected Areas

Rompido HOY por la columna faltante (todo lo que selecciona/inserta la entidad completa):

| Sitio | Operación | Impacto |
|---|---|---|
| `services/ventas/ventas.py:39,138` | SELECT full-entity | **Error reportado (1054)** en cada venta |
| `routes/clientes.py:216,229` | `db.session.query(Factura)` full-entity | listado `facturas-cli.html` roto |
| `services/ventas/ventas.py:74` | INSERT Factura (venta) | roto |
| `services/ventas/ventas.py:333,367` | INSERT Factura (recibos cta cte / cuota crédito) | roto (SQLAlchemy incluye todas las columnas mapeadas en el INSERT) |
| `services/ventas/remitos.py:38` | INSERT Factura (remito) | roto |
| `services/ventas/reportes.py:29-353`, `facturacion.py:225-247`, `remitos.py:133-146` | Queries con columnas explícitas | **NO** rompen (no seleccionan `idempotency_key`) |
| `templates/ventas/nueva_ncredito.html` | no carga `nueva_venta.js` → no envía key | NC corre con `idempotency_key=None` (backward compatible), pero su INSERT de Factura igual rompe hasta que exista la columna |

El fix de la columna destraba todos los sitios de una vez: los INSERTs que no setean la key simplemente guardan `NULL` (compatibilidad hacia atrás, diseñada así en el cambio original).

## Migration / SQL Needed

Migración de BD (ya existente como referencia, nunca aplicada — `SQL/migration_idempotencia.sql`):

```sql
-- Fase 1: Columna idempotency_key (nullable = backward compatibility)
ALTER TABLE facturav ADD COLUMN idempotency_key VARCHAR(36) NULL;

-- Fase 2: UNIQUE INDEX para detección de duplicados vía idempotency_key (race condition)
CREATE UNIQUE INDEX idx_uq_idempotency ON facturav(idempotency_key);

-- Fase 3: UNIQUE INDEX compuesto para evitar correlativos duplicados
CREATE UNIQUE INDEX idx_uq_comprobante ON facturav(punto_vta, nro_comprobante, idtipocomprobante);
```

Rollback (design.md L128): `DROP INDEX idx_uq_idempotency ON facturav; DROP INDEX idx_uq_comprobante ON facturav; ALTER TABLE facturav DROP COLUMN idempotency_key;`

Nota: MySQL permite múltiples `NULL` en índices UNIQUE → las filas existentes con `NULL` no rompen `idx_uq_idempotency`.

**Cambio de código: NINGUNO requerido** para el bug. Modelo, servicio y frontend están completos y con tests (`tests/test_services_ventas.py:219-340`: UUID inválido, early return, skip sin key, recovery IntegrityError).

## Approaches

| # | Approach | Pros | Cons | Effort |
|---|----------|------|------|--------|
| 1 | **Revisión Alembic** (`migrations/versions/xxxx_add_idempotency_key_facturav.py`, `down_revision='806cfc3bfdf2'`) con columna + ambos índices | Se versiona y commitea (visible en deploy); `index.py:152` (`upgrade()` en startup) la aplica automáticamente en el próximo arranque; alineado con el mecanismo del proyecto (precedente `2026-07-01-columnas-faltantes-facturac`) | Requiere verificar `alembic_version` en prod; `idx_uq_comprobante` puede fallar si hay correlativos duplicados históricos | Low |
| 2 | **Ejecutar `SQL/migration_idempotencia.sql` manualmente en prod** (one-time DBA) | Cero código, más rápido | El archivo es gitignored → invisible en deploys → el problema se repite con cualquier cambio futuro hecho así; sin versionado ni rollback automático; mismo riesgo de datos sucios con `idx_uq_comprobante` | Low |
| 3 | **Mínimo quirúrgico** (Alembic con solo columna + `idx_uq_idempotency`; `idx_uq_comprobante` en migración posterior tras limpiar duplicados) | Menor riesgo de fallo de deploy por datos históricos; destraba el bug reportado de inmediato | La protección anti-correlativos duplicados queda pendiente | Low |

## Recommendation

**Opción 1 (revisión Alembic)**, con la variante segura de la opción 3 si hay sospecha de datos sucios: dividir en dos migraciones — (a) columna + `idx_uq_idempotency` (fix del bug), (b) `idx_uq_comprobante` en un paso separado. Pasos previos recomendados:

1. Verificar en prod: `SELECT version_num FROM alembic_version;` — debe ser `806cfc3bfdf2` (el head trackeado). Atención: existe un `.pyc` huérfano `cc3c7d6e8978_add_missing_facturac_columns` en `migrations/versions/__pycache__/` cuyo `.py` nunca fue commiteado; si alguna BD quedara en esa revisión, la cadena rompería (poco probable: la app arranca hoy, lo que indica que `upgrade()` pasa sin pendientes).
2. Chequear duplicados antes de `idx_uq_comprobante`: `SELECT punto_vta, nro_comprobante, idtipocomprobante, COUNT(*) FROM facturav GROUP BY 1,2,3 HAVING COUNT(*) > 1;` (nro_comprobante es `NOT NULL` y puede haber `''` históricos).
3. Aplicar la migración vía deploy (el `upgrade()` de `index.py:152` lo hace solo) o `flask db upgrade` manual.

No tocar código de aplicación. Opcional (paridad modelo/autogenerate): agregar `index=True, unique=True` a `idempotency_key` en el modelo.

## Risks

- `CREATE UNIQUE INDEX idx_uq_comprobante` falla si existen `(punto_vta, nro_comprobante, idtipocomprobante)` duplicados o `nro_comprobante=''` históricos → mitigado por la variante de migraciones divididas.
- `alembic_version` de prod podría no estar en `806cfc3bfdf2` (revisión huérfana `cc3c7d6e8978`) → verificar antes.
- Recibos, remitos y el listado de facturas por cliente están igualmente rotos hoy (mismo 1054) aunque el reporte solo mencione la venta — el fix los destraba todos; conviene smoke-test de esas rutas post-deploy.

## Ready for Proposal

**Yes** — causa raíz confirmada con evidencia (código desplegado sin migración; migración existente pero gitignored; sin revisión Alembic). El fix es exclusivamente de BD (columna + índices), sin cambios de código. El proposal debe decidir entre migración Alembic (recomendado) vs SQL manual, y si `idx_uq_comprobante` va junto o en paso separado.