# Tasks: Dashboard Filter Fixes

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~10 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Delivery strategy | single-pr |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: SQL Fix

- [ ] 1.1 Update `get_sucursales_lista()` in `services/reportes.py:667` — change `WHERE baja IS NULL` to `WHERE (baja IS NULL OR baja = '0000-00-00 00:00:00')` so active sucursales with zero-date `baja` are included

## Phase 2: JS Fix

- [ ] 2.1 In `static/js/dashboard-gerencial.js:637-640`, after each `setRangoFechas()` call in the keydown handler, add `form.dispatchEvent(new Event('submit'))` to trigger form reload for Alt+H, Alt+S, Alt+M, Alt+T

## Phase 3: Model Fix

- [ ] 3.1 In `models/sucursales.py:22`, change `self.baja = timedelta(0)` to `self.baja = None` so new sucursales get proper NULL default

## Phase 4: Verification

- [ ] 4.1 Verify sucursal dropdown loads active branches (NULL and zero-date `baja` rows visible)
- [ ] 4.2 Verify keyboard shortcuts Alt+H/S/M/T update dates AND trigger dashboard reload
- [ ] 4.3 Verify newly created sucursales via ORM have `baja = NULL` in database
- [ ] 4.4 Verify no regressions — button-click filter and HTMX refresh still work
