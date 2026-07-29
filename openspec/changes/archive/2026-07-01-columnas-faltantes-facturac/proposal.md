# Proposal: Columnas faltantes en facturac

## Intent

La tabla `facturac` tiene 3 columnas en la base de datos MySQL (`percep_iibb`, `pagpersepcuenta`, `mto_percep`) que no existen en el modelo SQLAlchemy `FacturaC`. Esto hace que Alembic intente dropearlas en `flask db upgrade`. Hay que sincronizar el modelo con la DB real.

## Scope

### In Scope
- Agregar las 3 columnas DECIMAL(20,6) al modelo `FacturaC`
- Generar migración Alembic para registrar que modelo y DB están en sync

### Out of Scope
- Migrar datos existentes
- Agregar lógica de negocio para percepciones (solo modelo)

## Approach

1. Agregar `percep_iibb`, `pagpersepcuenta`, `mto_percep` como `db.Numeric(20,6)` con default 0
2. Ejecutar `flask db migrate` → autogenerate verá que modelo y DB ya coinciden → migración vacía
3. Verificar que `flask db upgrade` no intente dropear nada

## Success Criteria

- [ ] `flask db migrate` genera migración vacía (sin operaciones)
- [ ] El modelo `FacturaC` refleja las 3 columnas existentes
- [ ] Al ejecutarse en el futuro, `flask db upgrade` no toca esas columnas
