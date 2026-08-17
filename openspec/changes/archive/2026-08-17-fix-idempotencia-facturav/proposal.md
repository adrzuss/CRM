# Propuesta: fix-idempotencia-facturav

## Intención

Bug prod MySQL 1054 en cada venta: `facturav.idempotency_key` existe en el modelo (commit `d7e89c0`) pero no en la BD. La migración raw (`SQL/migration_idempotencia.sql`) quedó gitignored (`SQL/*`, `*.sql`) y nunca se aplicó en prod. Fix solo de BD: columna + índices.

## Alcance

### In Scope
- Revisión Alembic (`down_revision='806cfc3bfdf2'`) con columna + `idx_uq_idempotency` + `idx_uq_comprobante`
- Pre-check de correlativos duplicados antes de `idx_uq_comprobante`
- Verificación de `alembic_version` en prod (posible revisión huérfana `cc3c7d6e8978`)

### Out of Scope
- Código de app (modelo/servicio/frontend/tests)
- Limpieza de duplicados históricos (solo pre-check + gate)
- Paridad opcional del modelo (`index=True, unique=True` en `idempotency_key`)

## Decisión de entrega (versionada)

| Opción | Tradeoff | Veredicto |
|---|---|---|
| 1. Alembic | Auto-aplica en startup (`index.py:152`); precedente `2026-07-01-columnas-faltantes-facturac`; requiere verificar head | **Elegida** |
| 2. SQL crudo en `scripts/` | Simple, pero fuera de la cadena Alembic → mismo fallo en otros ambientes | Rechazada |
| 3. Híbrido | Alembic como fuente de verdad + SQL como referencia DBA | Soporte |

**Por qué 1**: la causa raíz fue "migración no versionada ni visible en deploys"; SQL crudo re-crea ese fallo en dev/staging. Alembic ya corre `upgrade()` en cada arranque y hay precedente de sync de columnas. El SQL en `SQL/` queda como referencia del paso manual (decisión del usuario: aplicar manual primero para verificar, formalizar después).

## Enfoque

1. **Manual en prod** (decisión del usuario): aplicar `SQL/migration_idempotencia.sql` → smoke-test ventas/recibos/remitos/facturas-cli.
2. **Pre-check** antes de `idx_uq_comprobante`: `SELECT punto_vta, nro_comprobante, idtipocomprobante, COUNT(*) FROM facturav GROUP BY 1,2,3 HAVING COUNT(*) > 1;`
3. **Revisión Alembic** con DDL que verifica existencia de columna (seguro ante doble aplicación manual+Alembic). Si hay duplicados → dividir: (a) columna + `idx_uq_idempotency` ya; (b) `idx_uq_comprobante` en migración posterior.
4. **Verificar `alembic_version`** = `806cfc3bfdf2` antes del deploy; si apunta a `cc3c7d6e8978` (pyc huérfano, `.py` nunca commiteado), reparar `version_num` tras confirmar el esquema real.

## Capabilities

### New Capabilities
None

### Modified Capabilities
None — fix de BD que implementa lo ya requerido por `ventas-idempotencia` (cambio `idempotencia-en-ventas`, sin archivar); no altera requisitos a nivel spec.

## Affected Areas

| Área | Impacto | Descripción |
|---|---|---|
| `migrations/versions/<nueva>_add_idempotency_facturav.py` | New | Revisión Alembic (columna + 2 índices) |
| `SQL/migration_idempotencia.sql` | Referencia | Paso manual (gitignored) |
| `index.py:152` | Sin cambio | `upgrade()` ya corre; toma la revisión sola |
| BD prod `facturav` | Modified | Columna + índices únicos |

## Riesgos

| Riesgo | Prob. | Mitigación |
|---|---|---|
| `idx_uq_comprobante` falla por duplicados/`''` históricos | Med | Pre-check + gate; dividir migración |
| `alembic_version` ≠ head (pyc huérfano) | Low | Verificar antes; reparar `version_num` |
| Doble aplicación manual + Alembic | Med | Revisión con check de existencia |
| Dev/staging también sin columna | Med | La misma revisión los arregla en su arranque |

## Rollback

`DROP INDEX idx_uq_idempotency ON facturav; DROP INDEX idx_uq_comprobante ON facturav; ALTER TABLE facturav DROP COLUMN idempotency_key;` (también en `downgrade()` de la revisión). Sin código de app, no hay rollback de aplicación.

## Dependencias

- Acceso a BD prod (paso manual) y `alembic_version` verificado
- Pre-check con 0 duplicados (o decisión de dividir migración)

## Success Criteria

- [ ] `facturav` en prod con columna + ambos índices; `alembic_version` = nueva revisión
- [ ] POST de venta OK (sin 1054); POST duplicado retorna la factura existente
- [ ] Smoke-test: recibos cta cte, remitos y listado `facturas-cli.html` OK
- [ ] Sin cambios de código de aplicación