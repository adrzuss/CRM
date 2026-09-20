# Proposal: Fix Facturas Pendientes & Convert to Modal

## Intent

Fix the broken "Facturas pendientes" section in the "Nueva Orden de Pago" page (missing DOM elements cause JS errors, empty results likely from stored procedure), and replace the inline card with a Bootstrap modal toggled by a badge button.

## Scope

### In Scope
- **Bug fix**: Add missing `#total_movs` element to `nueva_op.html` so `calcularTotal()` stops throwing TypeError
- **Bug fix**: Add missing `#efectivo` element on the main form so `calcSaldo()` works correctly
- **Bug fix**: Investigate and fix `get_movs_cc_prov` stored procedure if it returns empty results when it shouldn't
- **Modal conversion**: Replace inline `<ul class='list-group'>` card (lines 46-58 of `nueva_op.html`) with a Bootstrap modal
- **Toggle button**: Badge button showing count of pending invoices; clicking opens modal
- **Empty state**: Show "No hay facturas pendientes" message and disable button when count is 0
- **Preserve input names**: All `mov_cc[check]`, `mov_cc[saldo]`, etc. must remain intact for `procesar_nueva_op()` backend

### Out of Scope
- Modifying `procesar_nueva_op()` or any backend processing logic
- Changing the payment modal (`_modal-transacciones.html`) — that's a separate concern
- Modifying the stored procedure itself (only investigate; DB changes are a separate task)
- Other facturas-related pages

## Capabilities

### New Capabilities
- `facturas-pendientes-modal`: Bootstrap modal for displaying and selecting pending invoices in the payment order form, with toggle badge and empty state handling

### Modified Capabilities
None — no existing spec-level behavior changes. The inline card was not a formal spec; the fix restores intended behavior and improves UX.

## Approach

1. **HTML template changes** (`nueva_op.html`):
   - Remove inline card (lines 46-58) — the `<div id="movs_select">` and its contents
   - Add `#total_movs` element (hidden input or `<span>`) that `calcularTotal()` expects
   - Add `#efectivo` element on the main form (or rewire `calcSaldo()` to use `#efectivo_hidden`)
   - Add a badge button (e.g., `<button class="btn btn-outline-primary"><span class="badge">0</span> Facturas pendientes</button>`) that opens the modal
   - Add Bootstrap modal with `<ul id="movs_select" class="list-group">` inside the modal body
   - Modal body includes empty-state message "No hay facturas pendientes"

2. **JavaScript changes** (`nueva_op.js`):
   - `obtener_mov_ctacte()`: After fetch and render, update badge count and toggle button state (disabled if 0)
   - `calcularTotal()`: Ensure `#total_movs` is present — either add element or guard against missing
   - `calcSaldo()`: Fix reference to `#efectivo` — either add the element or rewire to `#efectivo_hidden`
   - Add click handler for badge button: open modal via Bootstrap JS (`new bootstrap.Modal(...)`)
   - Move modal-open logic to avoid conflict with payment modal (F9 shortcut)

3. **No backend changes** — routes and services are correct; the bug is purely frontend/DOM.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `templates/proveedores/nueva_op.html` | Modified | Remove inline card, add modal + toggle button, add missing DOM elements |
| `static/js/nueva_op.js` | Modified | Fix calcularTotal/calcSaldo references, update obtener_mov_ctacte for modal, add toggle logic |
| `proveedores/routes.py` | None | Read-only verification — no changes needed |
| `proveedores/services.py` | None | Read-only verification — no changes needed |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Duplicate element IDs between form and payment modal (`saldo_factura`, `saldo-container`) | High | Use unique IDs in the new modal (e.g., `saldo_factura_pend`, `saldo-container-pend`). Audit before implementation. |
| CSP nonce blocks inline event handlers | Medium | Follow existing pattern: Bootstrap modal uses `data-bs-toggle` attrs, not inline `onclick`. If JS handlers needed, use `addEventListener` in `nueva_op.js`. |
| F9 keyboard shortcut conflict with payment modal | Low | Only one modal should be open at a time — close provider modal before opening payment modal, and vice versa. |
| `get_movs_cc_prov` returns empty even when data exists | Medium | Investigate stored procedure call params. If procedure is broken, escalate as separate DB fix — proposal documents the finding but doesn't fix the SP. |
| Backend form submission breaks if input names change | Low | Strictly preserve all `mov_cc[check]`, `mov_cc[saldo]`, `mov_cc[id]` input names. Test with a real payment order. |

## Rollback Plan

- Revert `nueva_op.html` to remove modal and restore inline card
- Revert `nueva_op.js` to remove modal toggle logic and badge updates
- No database changes to rollback
- Git: `git revert <commit>` on the single commit that applies this change

## Dependencies

- Bootstrap 5 (already in use — no new dependency)
- `modal-transacciones-universal.js` patterns (reference only, no modification)
- Stored procedure `get_movs_cc_prov` — must return correct data for feature to be useful

## Success Criteria

- [ ] Loading a provider shows pending invoices count in badge (or "0" if none)
- [ ] Badge button opens modal with correct invoice list
- [ ] Selecting invoices and submitting form works — `procesar_nueva_op()` receives correct `mov_cc` data
- [ ] No TypeError in console when `calcularTotal()` or `calcSaldo()` runs
- [ ] Empty state shows "No hay facturas pendientes" and button is disabled
- [ ] Payment modal (F9) still works independently without conflicts
