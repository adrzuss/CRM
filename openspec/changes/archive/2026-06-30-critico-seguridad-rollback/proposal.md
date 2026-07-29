# Proposal: Crítico — Seguridad y Rollback

## Intent

Eliminar vulnerabilidades críticas y deuda técnica que ponen en riesgo la integridad de la DB, exponen credenciales y certificados, y dejan la app sin protección CSRF.

## Scope

### In Scope
- `db.session.rollback()` en todos los `except` de services/ y routes/ que hagan commit
- Inicializar `CSRFProtect(app)` en `index.py`
- Agregar `.env` y `cert_fe/` a `.gitignore`
- Crear `.env.example` con placeholders (sin datos reales)
- Limpiar dependencias fantasma de `requirements.txt`

### Out of Scope
- Migrar forms a Flask-WTF (solo protección global)
- Rotar credenciales reales de DB
- Mover certificados AFIP fuera de `cert_fe/`
- Tests automatizados
- Refactor de services/ventas.py
- Context processors

## Capabilities

> This is a pure refactor/config change — no spec-level behavior changes.

### New Capabilities
None

### Modified Capabilities
None

## Approach

1. **Rollback**: patrón mecánico — en cada `except` de services/ventas.py, services/ctactecli.py, services/ctacteprov.py, services/printer_service.py y routes/clientes.py, routes/ventas.py: agregar `db.session.rollback()` antes del `raise`/`return`. En endpoints sin try/except alrededor del commit, agregar la estructura completa.
2. **CSRF**: agregar `from flask_wtf.csrf import CSRFProtect` y `CSRFProtect(app)` en `create_app()` de `index.py`.
3. **Gitignore**: agregar `.env` y `cert_fe/` al `.gitignore`.
4. **.env.example**: copiar `.env`, sanitizar passwords/tokens/secret key con placeholders.
5. **requirements.txt**: remover fastapi, uvicorn, starlette, pymongo, pytube, yt-dlp, razorpay, fdb, firebird-*, sqlalchemy-firebird, twilio, httpx, aiohttp, aiohttp-retry, pandas, numpy, protobuf, virtualenv.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/ventas.py` | Modified | +rollback en todos los except |
| `services/ctactecli.py` | Modified | +rollback en todos los except |
| `services/ctacteprov.py` | Modified | +rollback en todos los except |
| `services/printer_service.py` | Modified | +rollback en todos los except |
| `routes/clientes.py` | Modified | +rollback en delete/add/update |
| `routes/ventas.py` | Modified | +rollback en endpoints con commit |
| `index.py` | Modified | +CSRFProtect init |
| `.gitignore` | Modified | +.env, +cert_fe/ |
| `.env.example` | New | Placeholder sanitizado |
| `requirements.txt` | Modified | -14 dependencias fantasma |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| CSRF rompe forms AJAX existentes | Media | Probar POST sin token post-aplicación |
| .env.example filtra datos reales | Baja | Revisar manualmente cada campo antes de commit |
| Rollback duplicado o en except que no lo necesita | Baja | Revisar cada caso; patrón es seguro (rollback extra es no-op) |

## Rollback Plan

Revertir commit del cambio completo. Si CSRF rompe producción y se necesita fix urgente, comentar la línea `CSRFProtect(app)` en hotfix separado.

## Dependencies

Ninguna.

## Success Criteria

- [ ] Todos los `except` en services/ y routes/ ejecutan `db.session.rollback()`
- [ ] `CSRFProtect` activo: `curl -X POST` sin token → 400
- [ ] `.env` y `cert_fe/` no aparecen en `git status`
- [ ] `.env.example` existe sin credenciales reales
- [ ] `requirements.txt` solo tiene dependencias en uso
- [ ] `python index.py` arranca sin errores
