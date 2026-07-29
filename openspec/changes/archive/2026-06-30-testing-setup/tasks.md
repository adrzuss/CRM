# Tasks: testing-setup

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~150–200 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-always |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: single-pr
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Infra de testing + tests de utils + routes | PR 1 | Cambio único, ~150–200 líneas |

## Phase 1: Infraestructura de testing

- [x] 1.1 Agregar `pytest>=8.0` y `pytest-flask>=1.3` a `requirements.txt`
- [x] 1.2 Crear `tests/__init__.py` — package marker vacío
- [x] 1.3 Crear `tests/conftest.py` — fixture `app()` con `create_app()`, `TESTING=True`, `WTF_CSRF_ENABLED=False`; fixture `client` con `app.test_client()`

## Phase 2: Tests de utilidades

- [x] 2.1 Crear `tests/test_utils.py` — test `convertir_decimal` con valores válidos ("1234.56", "1234,56") e inválidos (None, "abc" → `ValueError`)
- [x] 2.2 Test `format_currency` con valores positivo (1000 → "$1,000.00"), cero, negativo (-500 → "$-500.00")
- [x] 2.3 Test `precio` con alícuotas 21%, 10.5%, 0%, exento parcial — verificar dict `Resultado` con `Neto`, `Iva`, `PFinal`

## Phase 3: Tests de rutas de clientes

- [x] 3.1 Crear `tests/test_clientes.py` — mockear `check_session` para evitar redirects
- [x] 3.2 Mockear `Clientes.query.get` y `Localidades.query.filter_by` para GET `/clientes/<id>` y GET `/localidades/<idprovincia>`
- [x] 3.3 Test POST a `/clientes/new_cliente` sin token CSRF → 400
- [x] 3.4 Verificar que `pytest tests/` corre sin errores y al menos 5 tests pasan
