# Tasks: fix-idempotencia-facturav

## Review Workload Forecast

| Campo | Valor |
|---|---|
| Líneas cambiadas estimadas | ~100-130 |
| Riesgo presupuesto 400 líneas | Low |
| PR encadenados recomendados | No |
| Split sugerido | PR único |
| Estrategia de entrega | ask-always (C1) |
| Estrategia de cadena | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Unidades de trabajo sugeridas

| Unidad | Objetivo | PR probable | Notas |
|---|---|---|---|
| 1 | Revisión Alembic + verificación + commit | PR 1 | Base main; cambio único de BD, sin código de app |

## Fase 1: Migración Alembic

- [x] 1.1 Generar revisión: `flask db revision -m "add_idempotency_facturav"` → `migrations/versions/c2d3df6d5f32_add_idempotency_facturav.py` con `down_revision='806cfc3bfdf2'`.
- [x] 1.2 Implementar helpers `_columna()`/`_indice()` con `sqlalchemy.inspect` (patrón del design.md).
- [x] 1.3 `upgrade()` existence-checked: `ALTER TABLE facturav ADD COLUMN idempotency_key VARCHAR(36) NULL` solo si la columna falta.
- [x] 1.4 `upgrade()`: `CREATE UNIQUE INDEX idx_uq_idempotency ON facturav(idempotency_key)` solo si falta.
- [x] 1.5 `upgrade()`: pre-check duplicados (`GROUP BY punto_vta,nro_comprobante,idtipocomprobante HAVING COUNT(*)>1`); 0 dups → `CREATE UNIQUE INDEX idx_uq_comprobante`; >0 dups → print warning y diferir (no redactar revisión B: asumimos 0 dups).
- [x] 1.6 `downgrade()` existence-checked: DROP `idx_uq_comprobante`, DROP `idx_uq_idempotency`, DROP COLUMN (orden inverso).
- [x] 1.7 Docstring en español: contexto de la aplicación manual previa en prod y no-op esperado.

## Fase 2: Referencia SQL (decisión: keep)

- [x] 2.1 **Decisión: keep** — `SQL/migration_idempotencia.sql` queda como referencia DBA (gitignored, ya aplicado en prod). NO mover.
- [x] 2.2 Agregar comentario de cabecera al SQL: la fuente de verdad es la revisión Alembic `c2d3df6d5f32`; el paso manual quedó absorbido por los checks de existencia.

## Fase 3: Verificación (sin runner formal)

- [ ] 3.1 Pre-flight prod: `SELECT version_num FROM alembic_version` debe ser `806cfc3bfdf2`; si es `cc3c7d6e8978` (pyc huérfano), confirmar esquema real con DBA y reparar `UPDATE alembic_version SET version_num='806cfc3bfdf2'`. *(Verificado en BD local: `806cfc3bfdf2` → `c2d3df6d5f32`. Pendiente confirmación en prod.)*
- [x] 3.2 No-op doble aplicación: `flask db upgrade` sobre esquema ya migrado manualmente → `upgrade()` sin error, sin objetos duplicados. *(Ejecutado en BD local, que ya tenía columna + índices manuales: OK.)*
- [x] 3.3 Esquema: `SHOW COLUMNS FROM facturav LIKE 'idempotency_key'` y `SHOW INDEX FROM facturav` (deben listarse ambos índices). *(Verificado vía information_schema en BD local: columna + ambos índices únicos presentes.)*
- [ ] 3.4 Smoke venta: POST de venta con `_idempotency_key` OK (sin 1054); POST duplicado retorna factura existente. *(Pendiente: requiere app + AFIP en prod.)*
- [ ] 3.5 Smoke: recibos cta cte, remitos y listado `facturas-cli.html` OK. *(Pendiente: requiere app en prod.)*

## Fase 4: Commit (work unit único)

- [x] 4.1 Commit único conventional, en español, sin atribución AI: `feat(ventas): migración Alembic de idempotencia en facturav` (solo archivo de migración; SQL queda gitignored). *(Commit `7bbef6d`: migración + artefactos openspec del cambio; SQL gitignored, no incluido.)*
- [x] 4.2 Verificar `git status`/`git diff --stat`: solo migración nueva, sin secretos ni `.pyc`. *(Verificado: 6 archivos, sin `.pyc`, sin SQL, sin secretos.)*
