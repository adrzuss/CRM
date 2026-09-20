## Delta Spec: fix-facturas-pendientes-op-modal

### ADDED Requirements

#### Requirement: Pending Invoices Modal

The system MUST display pending invoices for a provider inside a Bootstrap 5 modal instead of an inline card. The modal MUST be opened via a badge toggle button.

**Scenario: Provider with pending invoices**
- GIVEN a provider with pending invoices is loaded via `obtener_mov_ctacte()`
- WHEN the fetch returns data
- THEN the badge button shows the count of pending invoices
- AND the modal body contains a `<ul class="list-group">` with one `<li>` per invoice
- AND each `<li>` contains a checkbox (`mov_cc[check]`), hidden inputs for `mov_cc_saldo` and `mov_cc_id`
- AND the modal body does NOT show the empty state message

**Scenario: Provider with no pending invoices**
- GIVEN a provider with zero pending invoices
- WHEN `obtener_mov_ctacte()` returns an empty array
- THEN the badge shows "0" and the badge button is disabled
- AND the modal body shows "No hay facturas pendientes"

**Scenario: User opens and closes modal**
- GIVEN the badge button is enabled (count > 0)
- WHEN the user clicks the badge button
- THEN the pending invoices modal opens via `bootstrap.Modal`
- AND when the user closes the modal, the form state is preserved (checkboxes retain their checked state)

**Scenario: Duplicate element IDs avoided**
- GIVEN the pending invoices modal and the payment modal (`_modal-transacciones.html`) both render on the page
- WHEN the page loads
- THEN the pending invoices modal MUST NOT use IDs that collide with the payment modal (`saldo_factura`, `saldo-container`, `efectivo`, `total`)
- AND the pending invoices modal uses unique IDs (e.g., `saldo_factura_pend`, `saldo-container-pend`)

#### Requirement: Missing DOM Element Fixes

The system MUST provide all DOM elements referenced by existing JavaScript functions to prevent TypeError exceptions.

**Scenario: `calcularTotal()` executes without error**
- GIVEN a provider is loaded and pending invoices are rendered
- WHEN the user checks/unchecks an invoice checkbox
- THEN `calcularTotal()` runs without TypeError
- AND `#total_movs` element exists in the DOM (or `calcularTotal` is guarded against missing element)
- AND the `#total` input value updates to the sum of checked invoice balances

**Scenario: `calcSaldo()` executes without error**
- GIVEN the payment modal is open and the user enters an efectivo amount
- WHEN `calcSaldo()` is called
- THEN it reads from the correct `#efectivo` element (inside the payment modal)
- AND `#saldo_factura` and `#saldo-container` update correctly
- AND no TypeError is thrown

**Scenario: `checkTotales()` executes without error**
- GIVEN the payment modal is open with efectivo and/or cheques entered
- WHEN the form is submitted
- THEN `checkTotales()` reads `#efectivo` from the payment modal without error
- AND returns `true` if total payments > 0, `false` otherwise

### MODIFIED Requirements

#### Requirement: Invoice Selection Renders in Modal

The pending invoices list MUST render inside the modal body instead of an inline card `<div id="movs_select">`.

(Previously: Invoices rendered in an inline card within the form body, with `display: none` until loaded)

**Scenario: Invoices render inside modal**
- GIVEN a provider is assigned via `asignarProveedor()`
- WHEN `obtener_mov_ctacte()` completes
- THEN the list items are appended to `#movs_select` inside the modal body
- AND the badge count updates to the number of invoices returned
- AND the inline card (lines 46-58 of `nueva_op.html`) is removed

**Scenario: `calcularTotal` works with modal-rendered checkboxes**
- GIVEN invoices are rendered inside the modal
- WHEN the user checks a checkbox
- THEN `calcularTotal()` finds checkboxes via `document.getElementById("movs_select").querySelectorAll("input[type=checkbox]:checked")`
- AND the total updates correctly regardless of modal open/closed state

### REMOVED Requirements

None — no existing spec-level requirements are removed. The inline card behavior was not formally specced; this change replaces it with a modal.

### Out of Scope

- **Backend changes**: `procesar_nueva_op()`, `get_movs_pendientes_ctacte()`, `get_movs_ctacte` route — no modifications
- **Stored procedure `get_movs_cc_prov`**: Investigation only; any DB fix is a separate task
- **Payment modal (`_modal-transacciones.html`)**: No changes to this partial
- **Other facturas-related pages**: Only `nueva_op.html` and `nueva_op.js` are affected
- **Input name changes**: All `mov_cc[check]`, `mov_cc_saldo`, `mov_cc_id` names MUST be preserved exactly

### Non-functional Requirements

- **CSP compliance**: All event handlers MUST use `addEventListener` in JS files, not inline `onclick` attributes. Bootstrap `data-bs-toggle` attributes are acceptable.
- **Accessibility**: The modal MUST have `role="dialog"`, `aria-labelledby`, and `aria-label` on the close button.
- **No duplicate IDs**: Audit all IDs across `nueva_op.html` and `_modal-transacciones.html` before implementation. The payment modal's `saldo_factura`, `saldo-container`, and `efectivo` are already used; the pending invoices modal MUST use distinct IDs.
- **Performance**: No additional network requests beyond the existing `get_movs_ctacte` fetch. Badge count is derived client-side from the fetch response.
- **Form integrity**: The `#invoice_form` submission path (`procesar_nueva_op`) MUST receive identical `mov_cc` data structure regardless of whether the list renders in modal or inline.

### Acceptance Criteria

| # | Criterion | Testable? |
|---|-----------|-----------|
| 1 | No TypeError in console when `calcularTotal()` or `calcSaldo()` runs | Yes — browser console |
| 2 | Badge button shows correct count of pending invoices after provider load | Yes — inspect badge text |
| 3 | Badge button is disabled with "0" when no pending invoices exist | Yes — inspect button state |
| 4 | Clicking badge opens modal with invoice list | Yes — visual / DOM inspection |
| 5 | Checking invoices updates `#total` and `#total_factura` | Yes — inspect input value |
| 6 | Form submission sends correct `mov_cc` data to backend | Yes — network tab / backend test |
| 7 | Payment modal (F9) still works independently | Yes — manual test |
| 8 | No duplicate element IDs between the two modals | Yes — DOM audit |
| 9 | Empty state message "No hay facturas pendientes" visible when count is 0 | Yes — DOM inspection |
| 10 | Modal close preserves checkbox state | Yes — reopen modal and verify |

### Risks (from proposal, carried forward)

| Risk | Mitigation |
|------|-----------|
| Duplicate IDs between modals | Use unique IDs; audit before implementation |
| CSP nonce blocks inline handlers | Use `addEventListener` only |
| F9 shortcut conflict | Only one modal open at a time |
| Stored procedure returns empty data | Separate DB investigation task |
| Backend breaks if input names change | Strictly preserve all `mov_cc` input names |
