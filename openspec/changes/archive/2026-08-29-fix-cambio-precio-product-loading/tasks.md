# Tasks: fix-cambio-precio-product-loading

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 130-200 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Route + service + JS implementation | PR 1 | Base: main; includes all tests |

---

## Phase 1: Backend Route Modification

- [x] **TASK-001**: Update `filtrar_articulos` route in `routes/articulos.py` to accept query params with backward compat for path params
  - Files: `routes/articulos.py`
  - Acceptance: SCE-001, SCE-002, SCE-003, SCE-004, SCE-005, SCE-006
  - Dependencies: None

- [x] **TASK-002**: Add `lista_precio` required validation (return 400 if missing)
  - Files: `routes/articulos.py`
  - Acceptance: SCE-005
  - Dependencies: TASK-001

- [x] **TASK-003**: Add backward compatibility route decorator for old path param format
  - Files: `routes/articulos.py`
  - Acceptance: Existing callers using `/filtrar_articulos/<marca>/<rubro>/<lista_precio>/<porcentaje>` still work
  - Dependencies: TASK-001

---

## Phase 2: Service Layer Validation

- [x] **TASK-004**: Add empty-items validation in `procesar_cambio_precio` in `services/articulos/precios.py`
  - Files: `services/articulos/precios.py`
  - Acceptance: SCE-007, SCE-008, SCE-009
  - Dependencies: None

---

## Phase 3: Frontend JS Update

- [x] **TASK-005**: Update `cargarRubroMarca` click handler to build query string with optional params
  - Files: `static/js/cambio_precio.js`
  - Acceptance: SCE-010, SCE-011, SCE-012, SCE-013, SCE-014
  - Dependencies: TASK-001 (route must accept query params)

- [x] **TASK-006**: Remove client-side validation requiring both marca AND rubro
  - Files: `static/js/cambio_precio.js`
  - Acceptance: SCE-011, SCE-012, SCE-013 (allow only marca, only rubro, or neither)
  - Dependencies: TASK-005

---

## Phase 4: Unit Tests - Route

- [x] **TASK-007**: Write unit tests for new query param route in `tests/test_articulos.py`
  - Files: `tests/test_articulos.py`
  - Acceptance: SCE-001 (all params), SCE-002 (only lista_precio), SCE-003 (only marca), SCE-004 (only rubro), SCE-005 (missing lista_precio → 400), SCE-006 (empty result → 200)
  - Dependencies: TASK-001, TASK-002, TASK-003

- [x] **TASK-008**: Write unit tests for backward compat path param route
  - Files: `tests/test_articulos.py`
  - Acceptance: Old URL format `/filtrar_articulos/1/2/3/10` still returns 200 with correct data
  - Dependencies: TASK-003

---

## Phase 5: Unit Tests - Service

- [x] **TASK-009**: Write unit test for empty-items validation in `procesar_cambio_precio`
  - Files: `tests/test_services_articulos.py`
  - Acceptance: SCE-008 (empty detalle → error, no DB changes), SCE-007 (valid items → success), SCE-009 (manual rows → success)
  - Dependencies: TASK-004

---

## Phase 6: Integration Test

- [x] **TASK-010**: Write integration test for full flow (JS → route → service)
  - Files: `tests/test_cambio_precio_integration.py` (new file)
  - Acceptance: SCE-010 through SCE-014 (JS builds correct query string, route returns filtered products, table populates)
  - Dependencies: TASK-001 through TASK-006

---

## Phase 7: Cleanup

- [x] **TASK-011**: Remove unused path param route definition (keep only query param + backward compat)
  - Files: `routes/articulos.py`
  - Acceptance: Single route definition handles both formats
  - Dependencies: TASK-003

- [x] **TASK-012**: Verify no regressions in existing `cambio_precio` page load and manual item addition
  - Files: All affected
  - Acceptance: Page loads, manual row addition works, filter flow works with all optional combos
  - Dependencies: All previous tasks