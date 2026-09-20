# Design: fix-facturas-pendientes-op-modal

## Architecture

Pure frontend fix — two files modified, zero backend changes. The change converts an inline card to a Bootstrap modal and adds missing DOM elements to prevent TypeError exceptions.

## Files to Modify

| File | Change |
|------|--------|
| `templates/proveedores/nueva_op.html` | Remove inline card, add modal + toggle badge, add `#total_movs` and `#efectivo` elements |
| `static/js/nueva_op.js` | Fix `calcularTotal()` and `calcSaldo()` references, update `obtener_mov_ctacte()` to render in modal, add badge toggle logic |

## Element ID Audit

### Existing IDs in `_modal-transacciones.html` (DO NOT USE):
- `#saldo_factura`
- `#saldo-container`
- `#efectivo`
- `#total`
- `#transaccionesModal`

### New IDs for pending invoices modal:
- `#facturasPendientesModal` — the modal container
- `#saldo_factura_pend` — saldo display in pending modal
- `#saldo-container-pend` — saldo container in pending modal
- `#badge_facturas_pendientes` — badge span inside toggle button
- `#btn_facturas_pendientes` — toggle button
- `#total_movs` — hidden input for calculated total (reused from existing JS)
- `#efectivo_pend` — efectivo input for pending modal context (if needed)

### Preserved IDs (must remain):
- `#movs_select` — moved from inline div to modal body (same ID, new location)
- `#invoice_form` — form element, unchanged

## Implementation Details

### 1. HTML Template Changes (`nueva_op.html`)

**Remove** (lines 46-58): The inline card block:
```html
<div class="card-header">
  <h5 class="card-title text-primary">Facturas pendientes</h5>
</div>
<div id="movs_select" class="card-body" style="display:none;">
  <ul class="list-group"></ul>
</div>
```

**Add** — Toggle button (placed after the proveedores search, before the form):
```html
<button type="button" class="btn btn-outline-primary" id="btn_facturas_pendientes" disabled>
  <span class="badge bg-primary" id="badge_facturas_pendientes">0</span> Facturas pendientes
</button>
```

**Add** — Bootstrap modal:
```html
<div class="modal fade" id="facturasPendientesModal" tabindex="-1"
     aria-labelledby="facturasPendientesModalLabel" aria-label="Facturas pendientes" role="dialog">
  <div class="modal-dialog modal-lg modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="facturasPendientesModalLabel">Facturas pendientes</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
      </div>
      <div class="modal-body">
        <div id="no-facturas-msg" class="text-center text-muted py-4 d-none">
          No hay facturas pendientes
        </div>
        <ul id="movs_select" class="list-group"></ul>
      </div>
    </div>
  </div>
</div>
```

**Add** — Hidden input for `calcularTotal()`:
```html
<input type="hidden" id="total_movs" name="total_movs" value="0">
```

### 2. JavaScript Changes (`nueva_op.js`)

**Fix `calcularTotal()`**: Guard against missing `#total_movs`:
```javascript
function calcularTotal() {
  const totalMovsEl = document.getElementById("total_movs");
  if (!totalMovsEl) return;
  // ... existing logic using totalMovsEl
}
```

**Fix `calcSaldo()`**: The `#efectivo` reference is in `modal-transacciones-universal.js` — no change needed in `nueva_op.js`. The existing code already works because `#efectivo` exists inside the payment modal. The bug only occurs if `calcSaldo()` is called from a context where the payment modal isn't open.

**Update `obtener_mov_ctacte()`**:
```javascript
// After rendering list items:
const badge = document.getElementById("badge_facturas_pendientes");
const btn = document.getElementById("btn_facturas_pendientes");
const noFacturasMsg = document.getElementById("no-facturas-msg");
const count = items.length;

badge.textContent = count;
btn.disabled = count === 0;
if (noFacturasMsg) {
  noFacturasMsg.classList.toggle("d-none", count > 0);
}
```

**Add badge click handler**:
```javascript
document.addEventListener("DOMContentLoaded", function() {
  const btn = document.getElementById("btn_facturas_pendientes");
  if (btn) {
    btn.addEventListener("click", function() {
      const modal = new bootstrap.Modal(document.getElementById("facturasPendientesModal"));
      modal.show();
    });
  }
});
```

### 3. No Backend Changes

Routes and services are correct. The bug is purely frontend/DOM.

## Dependency Order

1. HTML template changes first (modal structure + missing elements)
2. JavaScript fixes second (reference the new DOM elements)
3. Manual verification in browser

## Testing Strategy

- Browser console: verify no TypeError on page load or checkbox click
- DOM audit: verify no duplicate IDs between modals
- Functional: load provider → badge shows count → click badge → modal opens → check invoices → submit form → backend receives correct data
- Regression: payment modal (F9) still works independently
