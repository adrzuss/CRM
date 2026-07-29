# Tasks: Crítico — Seguridad y Rollback

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~80 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Delivery strategy | ask-always |
| Decision needed before apply | No |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

## Phase 1: Configuración y Fundación

- [x] 1.1 `.gitignore` — agregar `.env` y `cert_fe/` al final del archivo
- [x] 1.2 `.env.example` — crear copia de `.env` con passwords, tokens, secret key reemplazados por placeholders (`tu_password`, `tu_secret_key`, etc.)
- [x] 1.3 `index.py` — agregar `from flask_wtf.csrf import CSRFProtect` y `CSRFProtect(app)` dentro de `create_app()`
- [x] 1.4 `requirements.txt` — remover dependencias fantasma: fastapi, uvicorn, starlette, pymongo, pytube, yt-dlp, razorpay, fdb, firebird-\*, sqlalchemy-firebird, twilio, httpx, aiohttp, aiohttp-retry, pandas, numpy, protobuf, virtualenv

## Phase 2: Rollback en Services

- [x] 2.1 `services/ventas.py` — agregar `db.session.rollback()` en todos los bloques `except` con commit, antes del `raise`/`return`
- [x] 2.2 `services/ctactecli.py` — agregar `db.session.rollback()` en todos los bloques `except` con commit (ya estaba implementado)
- [x] 2.3 `services/ctacteprov.py` — agregar `db.session.rollback()` en todos los bloques `except` con commit (sin commits ni excepts — no requiere cambios)
- [x] 2.4 `services/printer_service.py` — agregar `db.session.rollback()` en todos los bloques `except` con commit (sin operaciones DB — no requiere cambios)

## Phase 3: Rollback en Routes

- [x] 3.1 `routes/clientes.py` — agregar `db.session.rollback()` en `delete_cliente`, `add_cliente`, `update_cliente` en los `except`
- [x] 3.2 `routes/ventas.py` — agregar `db.session.rollback()` en endpoints que hacen commit sin try/except (ningún endpoint tiene commit directo — no requiere cambios)

## Phase 4: Verificación

- [x] 4.1 `python index.py` — arranca sin errores de importación ni sintaxis (create_app() OK)
- [x] 4.2 `git status` — `.env` y `cert_fe/` no aparecen como untracked
- [x] 4.3 Verificar que `.env.example` no contiene credenciales reales
- [x] 4.4 Probar `curl -X POST /alguna-ruta` sin token CSRF → debe responder 400 (test_client POST → 400)
