# Exploration: nueva-venta-foco-total

## Bug 1 — Focus does not return to `.codigo-articulo` after closing article search modal

### Current State

When the user types a description in `.codigo-articulo`, `fetchArticulo()` in `nueva_venta.js`
calls `mostrarModalSeleccionArticulos(data, idlista, itemDiv)` (line 865). That function lives
**locally** inside `nueva_venta.js` (lines 1003–1023):

```js
function mostrarModalSeleccionArticulos(articulos, idlista, itemDiv) {
  const callback = async (articulo) => {
    // ... fetch + asignarArticuloElegido(data.articulo, itemDiv)

    // Attempt to restore focus:
    setTimeout(function() {
      itemDiv?.target?.focus();          // ← focuses the BLUR target, not the input
    }, 200);
  };

  window.universalSearchModal.show('articulos', articulos || [], callback);
}
```

There is also a **compatibility shim** in `universal-search-modal.js` (lines 555–573):
`window.mostrarModalSeleccionArticulos`. But because `nueva_venta.js` is a **`type="module"`
script** (line 364 of `nueva_venta.html`), its local function `mostrarModalSeleccionArticulos`
shadows `window.mostrarModalSeleccionArticulos` internally — the local one is always called.

### Root Cause

`itemDiv.target` is the **`blur` event target** — the `.codigo-articulo` input itself. So
`itemDiv?.target?.focus()` should theoretically work… but it doesn't, for two reasons:

1. **Timing**: the `setTimeout(..., 200)` fires **before Bootstrap has finished hiding the
   modal**. Bootstrap's `hidden.bs.modal` fires later; meanwhile the modal's backdrop still
   holds focus. The focus call lands on a document that still has the modal in the foreground,
   and the browser silently drops it.

2. **Wrong element being focused**: `itemDiv` is the original `blur` event object captured at
   the time `handleArticuloBlur` ran. After `asignarArticuloElegido` completes, `asignarArticulo`
   may have moved focus (e.g. `precioUnitario.focus()` on lines 984 / 991). The `setTimeout`
   then attempts to focus the code input again, but if Bootstrap's hide animation is still
   running, the focus attempt is eaten by the browser's focus manager.

The correct pattern (already used in the shim at `universal-search-modal.js` line 565) is:

```js
$('#universalSearchModal').one('hidden.bs.modal', function() {
    const inputCodigo = row.querySelector('.codigo-articulo');
    if (inputCodigo) inputCodigo.focus();
});
```

This event fires **after** Bootstrap has fully detached the backdrop and is the right hook.

### Affected Files

- `static/js/nueva_venta.js` — `mostrarModalSeleccionArticulos()` lines 1003–1023
- `static/js/universal-search-modal.js` — compatibility shim lines 555–573 (already correct,
  but never called from `nueva_venta.js` because the local function takes precedence)
- `static/js/invoice-utils.js` — `asignarArticuloElegido()` line 127–130 (no focus call here,
  not responsible)

### Minimal Fix

Replace the `setTimeout` focus in `mostrarModalSeleccionArticulos` (in `nueva_venta.js`) with
a `hidden.bs.modal` one-time listener **scoped to the correct row element**:

```js
// BEFORE (lines 1016-1019):
setTimeout(function() {
  itemDiv?.target?.focus();
}, 200);

// AFTER:
$('#universalSearchModal').one('hidden.bs.modal', function() {
  const row = itemDiv?.target?.closest('tr');
  const inputCodigo = row?.querySelector('.codigo-articulo');
  if (inputCodigo) inputCodigo.focus();
});
```

The `row` reference is captured from `itemDiv.target.closest('tr')` — same row that triggered
the search, unambiguous even after `asignarArticulo` moves focus internally.

---

## Bug 2 — Grand total (`#totalFacturaDisplay`) does not update when price list changes

### Current State

`recalcularPreciosPorLista()` in `nueva_venta.js` (lines 1101–1182):

1. Updates `.precio-unitario` and `.precio-total` values via `input.value = ...` (JS property
   assignment).
2. Calls `updateTotalFactura()` at line 1174.

`updateTotalFactura()` (lines 1027–1044):
```js
function updateTotalFactura() {
  // ... sums .precio-total fields
  document.getElementById("totalFactura").value = totalFactura.toFixed(2);
  // ... calls calcSaldo() if modal is open
}
```

`sincronizarTotal()` in `nueva_venta.html` (lines 285–314) reads `#totalFactura.value` and
writes to `#totalFacturaDisplay`. It is registered via:

```js
totalInput.addEventListener('input', sincronizarTotal);
totalInput.addEventListener('change', sincronizarTotal);
const observer = new MutationObserver(sincronizarTotal);
observer.observe(totalInput, {
    attributes: true,
    attributeFilter: ['value'],   // ← watches the HTML attribute, NOT the JS property
    ...
});
```

### Root Cause — THREE independent failures

#### 1. Setting `.value` via JS does NOT fire `input` or `change` events

`element.value = '...'` is a **programmatic** assignment. The browser only fires `input` and
`change` events when the user types. Programmatic assignment is silent — no event, no callback.
This is standard browser behavior (spec §4.10.18.5).

#### 2. Setting `.value` via JS does NOT trigger a MutationObserver on `attributeFilter: ['value']`

`MutationObserver` on `attributeFilter: ['value']` watches the **DOM attribute** (`getAttribute('value')`),
not the **IDL property** (`element.value`). Setting `element.value = x` modifies the JS
property but **never** the DOM attribute. The attribute only changes via `setAttribute('value', x)`
or via HTML parsing. So the MutationObserver never fires.

#### 3. `sincronizarTotal` is defined in an inline `<script>` tag that runs **before** the module
scripts

Looking at `nueva_venta.html` load order (lines 358–365):
```html
<script nonce="...">          ← inline, runs first, sets window.sincronizarTotal
<script src="universal-search-modal.js">   ← classic script
<script src="modal-color-detalle.js">      ← classic script
<script src="transaction-color-detail-helper.js"> ← classic script
<script src="invoice-utils.js">            ← classic script
<script type="module" src="modal-transacciones-universal.js">  ← deferred
<script type="module" src="nueva_venta.js">  ← deferred (module)
```

**Module scripts are deferred by default.** They run after all classic scripts and after
`DOMContentLoaded`. The inline script runs synchronously during HTML parsing — long before
`nueva_venta.js` is executed. So `window.sincronizarTotal` IS available when
`recalcularPreciosPorLista()` runs (it's on `window` from the inline script). The ordering
is not the problem here.

The problem is exclusively **reasons 1 and 2**: `updateTotalFactura()` sets the IDL property
but the event listeners and MutationObserver only watch for user-driven events and DOM
attribute mutations, neither of which are triggered by `element.value = x`.

### Minimal Fix

After `document.getElementById("totalFactura").value = totalFactura.toFixed(2)` in
`updateTotalFactura()`, explicitly call `sincronizarTotal()` (or dispatch a synthetic event):

**Option A — Direct call (recommended, explicit, zero side effects):**

```js
// In updateTotalFactura(), after line 1037:
document.getElementById("totalFactura").value = totalFactura.toFixed(2);
if (typeof window.sincronizarTotal === 'function') {
  window.sincronizarTotal();
}
```

**Option B — Dispatch a synthetic `input` event:**

```js
document.getElementById("totalFactura").value = totalFactura.toFixed(2);
document.getElementById("totalFactura").dispatchEvent(new Event('input', { bubbles: true }));
```

Option A is preferred: it's explicit, doesn't rely on event bubbling, and is consistent with
how `nueva_nota_credito.js` already does the same thing (lines 1533–1534).

---

## Affected Files (both bugs)

- `static/js/nueva_venta.js`
  - `mostrarModalSeleccionArticulos()` ~line 1003 — Bug 1 fix
  - `updateTotalFactura()` ~line 1037 — Bug 2 fix
- `static/js/universal-search-modal.js` — no changes needed (shim is correct)
- `static/js/invoice-utils.js` — no changes needed
- `templates/ventas/nueva_venta.html` — no changes needed

---

## Approaches

### Bug 1

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| Replace `setTimeout` with `hidden.bs.modal` one-time listener | Standard Bootstrap pattern, timing-safe | None | Low |
| Keep setTimeout, increase delay to 500ms | Trivial | Fragile, animation-dependent | Low |
| Move focus logic into `asignarArticuloElegido` | Centralised | Doesn't account for modal backdrop | Medium |

**Recommendation**: `hidden.bs.modal` one-time listener in the local `mostrarModalSeleccionArticulos` callback.

### Bug 2

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| Call `window.sincronizarTotal()` directly after `.value` set | Explicit, zero coupling, consistent with nota-credito pattern | Requires `window.sincronizarTotal` to be defined | Low |
| `dispatchEvent(new Event('input'))` | Decoupled, idiomatic | Indirect, relies on listener being registered | Low |
| Change MutationObserver to watch `subtree`+`characterData` | No code change in JS | Won't work — `.value` still doesn't mutate DOM | N/A |

**Recommendation**: Direct `window.sincronizarTotal()` call in `updateTotalFactura()`.

---

## Risks

- None — both fixes are additive/corrective, no behaviour changes elsewhere.
- The `hidden.bs.modal` listener for Bug 1 should use `.one()` (jQuery) or `{ once: true }` to
  avoid accumulating listeners on repeated modal opens.

## Ready for Proposal

Yes — both bugs are fully understood with clear, minimal fixes. Ready for `sdd-propose`.
