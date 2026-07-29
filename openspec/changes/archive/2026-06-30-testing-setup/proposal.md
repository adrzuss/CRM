# Proposal: testing-setup

## Intent

El proyecto CRM tiene 0 tests, 0 test runner y funciones críticas (cálculos de IVA, format_currency, CRUD de clientes) sin verificación automatizada. Necesitamos el MVP de testing para poder agregar tests en cambios futuros sin fricción.

## Scope

### In Scope
- `pytest` + `pytest-flask` en `requirements.txt`
- `tests/conftest.py` — fixture `app()` y `client()` con TESTING=True
- `tests/test_utils.py` — 4-5 tests para `convertir_decimal`, `format_currency`, `precio()`
- `tests/test_clientes.py` — tests de routes clientes (GET /clientes/<id>, GET /localidades/<idprovincia>, POST CSRF sin token → 400)
- Tests con mocking de SQLAlchemy (`unittest.mock`), sin DB real

### Out of Scope
- Tests que requieran DB real o stored procedures
- Tests de integración AFIP, templates, o cobertura completa
- Refactor del código existente para hacerlo más testeable

## Capabilities

> Cambio puramente infra/testing — no modifica comportamiento funcional de la app.

### New Capabilities
None

### Modified Capabilities
None

## Approach

1. **requirements.txt**: agregar `pytest>=8.0` y `pytest-flask>=1.3`
2. **conftest.py**: `create_app()` con `TESTING=True` y `WTF_CSRF_ENABLED=False`. Fixture `client` con `app.test_client()`.
3. **test_utils.py**:
   - `convertir_decimal`: valores válidos ("1234.56", "1234,56"), inválidos (None → ValueError, "abc" → ValueError)
   - `format_currency`: positivo (1000 → "$1,000.00"), cero, negativo (-500 → "$-500.00")
   - `precio`: alícuotas 21%, 10.5%, 0%, exento parcial — verificar dict Resultado con Neto, Iva, PFinal
4. **test_clientes.py**: mockear `check_session` para evitar redirects. Mockear `Clientes.query.get` y `Localidades.query.filter_by`. POST sin token CSRF → 400.
5. **test CSRF**: POST a `/clientes/new_cliente` sin token → 400 (confirmar que el fix del cambio anterior anda).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `requirements.txt` | Modified | +pytest, +pytest-flask |
| `tests/conftest.py` | New | App fixture con TESTING=True |
| `tests/test_utils.py` | New | Tests de funciones utils |
| `tests/test_clientes.py` | New | Tests de routes clientes + CSRF |
| `tests/__init__.py` | New | Package marker |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Mockear SQLAlchemy session falla por relaciones complejas | Medium | Tests de utils no usan DB; tests de routes mockean a nivel query |
| CSRF bloquea requests en tests | Low | `WTF_CSRF_ENABLED=False` en test config |
| `check_session` redirige en vez de responder | Low | Mockear el decorador o la función `session` |

## Rollback Plan

Revertir el commit del cambio completo. Si algún test rompe el CI futuro, borrar `tests/` y revertir `requirements.txt`.

## Dependencies

Ninguna. pytest se instala desde PyPI.

## Success Criteria

- [ ] `pytest tests/` corre sin errores de importación/config
- [ ] Al menos 5 tests pasan (utils + routes + CSRF)
- [ ] `python index.py` arranca sin errores
- [ ] `pip list | grep pytest` muestra pytest y pytest-flask instalados
