# Tasks: Migraciones Alembic

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~100–150 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Dependencias y Config

- [x] 1.1 Agregar `Flask-Migrate>=4.0` a `requirements.txt` y ejecutar `pip install -r requirements.txt`
- [x] 1.2 Crear `.flaskenv` con `FLASK_APP=index.py`

## Phase 2: Modificaciones en index.py

- [x] 2.1 Importar `Migrate` y `upgrade` desde `flask_migrate` al inicio del archivo
- [x] 2.2 Instanciar `migrate = Migrate()` a nivel módulo (junto a `db`)
- [x] 2.3 Mover `db.init_app(app)` dentro de `create_app()`, antes del `return app`
- [x] 2.4 Agregar `migrate.init_app(app, db)` dentro de `create_app()`
- [x] 2.5 Reemplazar `db.create_all()` por `upgrade()` en el bloque de startup (manteniendo `with app.app_context()`)

## Phase 3: Generación de Migraciones

- [x] 3.1 Ejecutar `flask db init` para crear `migrations/` con alembic.ini y env.py
- [x] 3.2 Ejecutar `flask db migrate -m "initial_schema"` para generar script autogenerado en `migrations/versions/`
- [x] 3.3 Revisar manualmente el script generado: verificar que NO contenga DROP de tablas existentes ni ALTER innecesarios
- [x] 3.4 Ejecutar `flask db stamp head` para marcar DB como actualizada sin ejecutar cambios

## Phase 4: Verificación

- [x] 4.1 Verificar con `flask db current` que muestre una revisión (no "None")
- [x] 4.2 Ejecutar `python index.py` y confirmar que arranca sin errores
- [x] 4.3 Ejecutar `pytest tests/` y confirmar que pasan los 19 tests

## Phase 5: Commit

- [x] 5.1 Realizar commit con `migrations/`, `.flaskenv`, `index.py`, `requirements.txt`
