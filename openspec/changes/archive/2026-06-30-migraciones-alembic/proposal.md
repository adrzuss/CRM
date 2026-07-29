# Proposal: Instalar Flask-Migrate (Alembic)

## Intent

`db.create_all()` en `index.py:101` no deja trazabilidad de cambios de schema ni permite rollbacks. Cualquier diferencia entre modelos y DB real queda oculta. Reemplazar por migraciones versionadas con Alembic vía Flask-Migrate.

## Scope

### In Scope
- `Flask-Migrate` en requirements.txt
- `Migrate(app, db)` + mover `db.init_app(app)` dentro de `create_app()`
- `.flaskenv` con `FLASK_APP=index.py`
- `flask db init` → `migrations/` con entorno Alembic
- `flask db migrate -m "initial_schema"` (autogenerate)
- `flask db stamp head`
- Reemplazar `db.create_all()` por `upgrade()`
- Versionar `migrations/` en git

### Out of Scope
- Corregir diferencias modelos vs schema real MySQL
- Versionar stored procedures (ya hecho)
- Tests para migraciones
- Refactorizar modelos
- Migrar datos

## Capabilities

### New Capabilities
None

### Modified Capabilities
None

## Approach

1. **requirements.txt**: + `Flask-Migrate>=4.0`
2. **index.py**: mover `db.init_app(app)` + `Migrate(app, db)` dentro de `create_app()`. Fuera: reemplazar `db.create_all()` por `upgrade()`.
3. **.flaskenv**: `FLASK_APP=index.py`
4. `flask db init` → `migrations/` con alembic.ini, env.py
5. `flask db migrate -m "initial_schema"` → comparación modelos vs DB, genera script en versions/
6. `flask db stamp head` → DB marcada como actualizada, sin ejecutar cambios
7. Verificación: `flask db current`, `python index.py`, `pytest tests/`

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `requirements.txt` | Modified | +Flask-Migrate |
| `index.py` | Modified | Init Migrate en create_app(); create_all() → upgrade() |
| `.flaskenv` | New | FLASK_APP=index.py |
| `migrations/` | New | Alembic completo (alembic.ini, env.py, versions/) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Autogenerate genera DROP de tablas existentes | Media | Revisar script antes de aplicarlo; stamp head evita ejecución |
| Tablas DB sin modelo | Media | Alembic las ignora por defecto |
| Tablas modelo sin DB | Baja | stamp head no ejecuta; upgrade() las crearía |
| flask db CLI no encuentra app | Baja | .flaskenv lo resuelve |
| Mover db.init_app() rompe algo | Baja | db es singleton en utils/db.py, init dentro de create_app() funciona |

## Rollback Plan

1. git checkout index.py (versión anterior)
2. Eliminar `.flaskenv` y `migrations/`
3. Sacar `Flask-Migrate` de requirements.txt
4. App vuelve a `db.create_all()` sin pérdida de datos

## Dependencies

- Flask CLI con FLASK_APP
- Conexión MySQL operativa
- python-dotenv (ya instalado)

## Success Criteria

- [ ] `flask db current` muestra revisión (no "None")
- [ ] `python index.py` arranca sin errores
- [ ] `pytest tests/` pasa (19 tests)
- [ ] `migrations/` versionado en git
- [ ] `db.create_all()` ya no está en el código
