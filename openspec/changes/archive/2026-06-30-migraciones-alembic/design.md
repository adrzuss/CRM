# Design: Migraciones Alembic

## Technical Approach

Reemplazar `db.create_all()` por migraciones versionadas con Flask-Migrate/Alembic. Inicializar `Migrate()` dentro de `create_app()`, marcar la DB existente como actualizada con `stamp head` sin ejecutar cambios, y usar `upgrade()` en startup. A futuro: `flask db migrate` para cambios de schema.

## Architecture Decisions

### ¿Dónde inicializar Flask-Migrate?

**Opción A (`create_app()`) ✅** — `db.init_app(app)` y `Migrate(app, db)` dentro de la factory. Sigue el patrón existente, funciona con flask CLI, la app queda autocontenida.
**Opción B (manage.py) ❌** — agrega entry point innecesario.
**Opción C (utils/db.py) ❌** — acopla Migrate a utils, app no está disponible en tiempo de import.

### ¿Migración inicial sin romper DB existente?

**Opción A (`flask db stamp head`) ✅** — marca DB como actualizada sin ejecutar nada. Cero riesgo de DROP/ALTER sobre datos reales.
**Opción B (migración vacía + stamp) ❌** — mismo resultado con paso extra.
**Opción C (generar + revisar con `--sql`) ❌** — útil para auditoría, pero acá DB ya refleja modelos.

### ¿Entry point CLI?

**Opción A (flask CLI + `.flaskenv`) ✅** — Flask-Migrate registra comandos automáticamente. Solo necesita `FLASK_APP=index.py`.
**Opción B (manage.py) ❌** — boilerplate que replica lo que flask CLI ya da.
**Opción C (click en index.py) ❌** — mezcla comandos con la app sin beneficio.

### ¿Cómo reemplazar `db.create_all()`?

**Opción A (`upgrade()` directo) ✅** — ejecuta solo migraciones pendientes. Con DB ya en head es no-op. Reemplazo natural y limpio.
**Opción B (mantener create_all como fallback) ❌** — si hay migraciones pendientes, create_all las oculta.
**Opción C (quitar ambos) ❌** — es la misma que A.

## File Changes

| File | Acción | Descripción |
|------|--------|------------|
| `requirements.txt` | Modify | `+Flask-Migrate>=4.0` |
| `index.py` | Modify | Mover `db.init_app(app)` y `Migrate(app, db)` dentro de `create_app()`. Reemplazar `db.create_all()` por `upgrade()` |
| `.flaskenv` | Create | `FLASK_APP=index.py` |
| `migrations/` | Create | `flask db init` → alembic.ini, env.py, versions/ |
| `migrations/versions/*.py` | Create | `flask db migrate -m "initial_schema"` → script autogenerado (solo se revisa y versiona) |

### Cambios clave en index.py

```python
from flask_migrate import Migrate, upgrade
migrate = Migrate()

def create_app():
    app = Flask(__name__, ...)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    # ... blueprints, context processors ...
    return app

app = create_app()

with app.app_context():
    upgrade()       # reemplaza a db.create_all()
```

## Testing Strategy

Los 19 tests existentes importan `create_app()` desde `index.py`, **no ejecutan el bloque module-level de startup**. Usan SQLite in-memory con mocks pesados. La adición de `Migrate` dentro de `create_app()` no los afecta — instancia el objeto pero no ejecuta migraciones. Verificar con `pytest tests/`.

## Migration / Rollout Plan

1. `pip install Flask-Migrate>=4.0` + freeze requirements
2. Modificar `index.py` (factory, Migrate, upgrade)
3. Crear `.flaskenv`
4. `flask db init` → genera `migrations/`
5. `flask db migrate -m "initial_schema"` → genera script autogenerado
6. **REVISAR el script**: asegurar que no tenga DROP de tablas existentes
7. `flask db stamp head` → marca DB sin ejecutar cambios
8. Verificar: `flask db current`, `python index.py`, `pytest tests/`
9. Commit: `migrations/`, `.flaskenv`, `index.py`, `requirements.txt`

**Rollback**: `git checkout` de los 4 archivos + `Remove-Item -Recurse migrations/`

## Riesgos y mitigaciones

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Autogenerate genera DROP de tablas existentes | Media | Revisar el script manualmente antes de versionar |
| upgrade() falla si migrations/ no existe | Baja | upgrade() es no-op sin migrations/; el setup garantiza que existe |
| Tests rompen por import de flask_migrate | Baja | Tests importan create_app, no ejecutan startup; verificar con pytest |
| db.init_app() dentro de create_app() rompe dependencias tempranas | Baja | Ningún modelo/service usa db fuera del context de app |
