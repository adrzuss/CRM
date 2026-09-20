# Tasks: Fix Facturas Pendientes & Convert to Modal

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~50 (30 HTML additions + 13 deletions + 21 JS additions) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

## Phase 1: HTML Template Changes

- [x] 1.1 Add hidden input `#total_movs` to `nueva_op.html` so `calcularTotal()` stops throwing TypeError
- [x] 1.2 Remove inline card block (lines 46-58: `<div id="movs_select">` and its contents)
- [x] 1.3 Add badge toggle button (`#btn_facturas_pendientes` + `#badge_facturas_pendientes`) before the form
- [x] 1.4 Add Bootstrap modal `#facturasPendientesModal` with `<ul id="movs_select">` inside modal body and empty-state message

## Phase 2: JavaScript Fixes

- [x] 2.1 Guard `calcularTotal()` against missing `#total_movs` — return early if element not found
- [x] 2.2 Update `obtener_mov_ctacte()` to set badge count, toggle button disabled state, and show/hide empty-state message after fetch
- [x] 2.3 Add badge click handler with `addEventListener` to open `#facturasPendientesModal` via `bootstrap.Modal`

## Phase 3: Verification

- [ ] 3.1 Open page, load a provider — verify no TypeError in console from `calcularTotal()` or `calcSaldo()`
- [ ] 3.2 Verify badge shows correct count and is disabled when 0
- [ ] 3.3 Click badge → modal opens with invoice list; check invoices → `#total` updates
- [ ] 3.4 Audit DOM for duplicate IDs between `#facturasPendientesModal` and `#transaccionesModal`
- [ ] 3.5 Test payment modal (F9) still works independently without conflicts
