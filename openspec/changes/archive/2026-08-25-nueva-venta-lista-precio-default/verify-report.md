# Verify Report: nueva-venta-lista-precio-default

**Date:** 2026-08-25  
**Mode:** Standard (no test runner — static source inspection)  
**Verdict:** ✅ PASS WITH WARNINGS

---

## Task Completeness

| Task | Status |
|------|--------|
| 1.1 Backend — `id_lista_precio` in `set_punto_vta` | ✅ Complete |
| 2.1 JS — `selectLista` block in `asignarPuntoVenta()` | ✅ Complete |
| 3.1 Template — `loop.first` in `#idlista` option | ✅ Complete |
| 4.1–4.4 Manual verification | 🔲 Pending (by design — requires running app) |

3/3 implementation tasks complete. Phase 4 is manual smoke-testing, not automatable here.

---

## Spec Compliance Matrix

| Requirement / Scenario | Evidence | Status |
|------------------------|----------|--------|
| `asignarPuntoVenta()` reads `result.id_lista_precio` | `nueva_venta.js:578` — `if (result.id_lista_precio)` | ✅ PASS |
| Sets `#idlista` to truthy `id_lista_precio` | `nueva_venta.js:579` — `selectLista.value = result.id_lista_precio` | ✅ PASS |
| Fallback to `options[0].value` when falsy | `nueva_venta.js:580-581` — `else if (selectLista.options.length > 0)` | ✅ PASS |
| Guard: no-op if no options | `nueva_venta.js:580` — `options.length > 0` check present | ✅ PASS |
| `recalcularPreciosPorLista()` NOT called in auto-select | No call in lines 576–583 block | ✅ PASS |
| `change` listener still fires `recalcularPreciosPorLista()` | `nueva_venta.js:1094-1095` — listener intact, untouched | ✅ PASS |
| Template uses `loop.first` | `nueva_venta.html:118` — `{{ 'selected' if loop.first else '' }}` | ✅ PASS |
| Template no longer uses `lista.id == 1` | Not present in `nueva_venta.html` | ✅ PASS |

---

## Verification Checklist

- [x] `set_punto_vta` response includes `id_lista_precio` — `ventas.py:94`
- [x] `get_puntos_vta_sucursal` does outerjoin with `ListasPrecios` and returns `nombreLista` — `ventas.py:62-75`
- [x] `saleccionarPtoVta()` clears modal content before rebuilding — `nueva_venta.js:164` — `modalContent.innerHTML = ""`
- [x] Option text shows lista name when available, omits when null — `nueva_venta.js:183` — conditional with ternary
- [x] `asignarPuntoVenta()` sets `#idlista` to `result.id_lista_precio` when truthy — line 578-579
- [x] `asignarPuntoVenta()` falls back to first option when falsy — lines 580-581
- [x] `#idlista` select guard: no-op if no options — `options.length > 0` on line 580
- [x] Template uses `loop.first` not `lista.id == 1` — confirmed
- [x] `recalcularPreciosPorLista()` NOT called on auto-select — confirmed absent from lines 576-583
- [x] No regressions in existing `asignarPuntoVenta()` fields — `posPrinter` (567), `facElectronica` (568), `ptovta_seleccionado` (570), `fac_electronica` (572), `pos_printer` (574) all intact

---

## Design Coherence

| Design Decision | Implemented As Designed | Notes |
|-----------------|------------------------|-------|
| Add `id_lista_precio` to `set_punto_vta` response only | ✅ Yes | `ventas.py:94` |
| JS block inserted after `pos_printer` assignment | ✅ Yes | Block at lines 575-583, after line 574 |
| No call to `recalcularPreciosPorLista()` | ✅ Yes | Absent from block |
| Fallback = `options[0].value` | ✅ Yes | Exact match to design contract |
| Template: `loop.first` | ✅ Yes | Exact match |

---

## Issues

### ⚠️ WARNING — `get_puntos_vta_sucursal` not in scope but has bonus changes

**File:** `routes/ventas.py:62-75`  
**Detail:** The route was enhanced with an `outerjoin` to `ListasPrecios` and returns `idListaPrecio` + `nombreLista`. These fields are consumed correctly by `saleccionarPtoVta()` in `nueva_venta.js:183`. The change was not in the original design's *File Changes* table but is used by the JS. This is a coherent and necessary addition — without it, `nombreLista` would be `undefined` in all option labels.  
**Risk:** Low. The change is purely additive (outerjoin doesn't drop rows), `ListasPrecios` import must be present.

### 💡 SUGGESTION — `lista.id == 1` still present in sibling templates

**Files:**  
- `templates/ventas/nueva_ncredito.html:184`  
- `templates/ventas/nuevo_remito.html:216`  
- `templates/ventas/nuevo_presupuesto.html:208`  

**Detail:** The same fragile default pattern that was fixed in `nueva_venta.html` still exists in three sibling templates. These are out of scope for this change but represent technical debt.  
**Risk:** None to this change. Flag for a follow-up SDD.

### 💡 SUGGESTION — `nueva_nota_credito.js` / `nuevo_presupuesto.js` have parallel `asignarPuntoVenta()` without the new block

**Files:** `static/js/nueva_nota_credito.js:656`, `static/js/nuevo_presupuesto.js` (inferred)  
**Detail:** The JS fix was applied only to `nueva_venta.js`. The same function in sibling flows still lacks auto-selection of `#idlista`. Out of scope, but worth noting.

---

## Evidence Summary

| Check | File | Line(s) | Finding |
|-------|------|---------|---------|
| `set_punto_vta` returns `id_lista_precio` | `routes/ventas.py` | 94 | ✅ Present in return dict |
| `get_puntos_vta_sucursal` outerjoin | `routes/ventas.py` | 68 | ✅ `outerjoin(ListasPrecios, ...)` |
| `get_puntos_vta_sucursal` returns `nombreLista` | `routes/ventas.py` | 75 | ✅ `'nombreLista': pv.nombre_lista` |
| `saleccionarPtoVta()` clears innerHTML | `nueva_venta.js` | 164 | ✅ `modalContent.innerHTML = ""` |
| Option text with `nombreLista` | `nueva_venta.js` | 183 | ✅ Ternary present |
| `selectLista` guard | `nueva_venta.js` | 577 | ✅ `if (selectLista)` |
| Set value from `id_lista_precio` | `nueva_venta.js` | 578-579 | ✅ |
| Fallback to `options[0].value` | `nueva_venta.js` | 580-581 | ✅ |
| No `recalcularPreciosPorLista()` call in block | `nueva_venta.js` | 575-583 | ✅ Absent |
| `change` listener preserved | `nueva_venta.js` | 1094-1095 | ✅ Intact |
| `loop.first` in template | `nueva_venta.html` | 118 | ✅ |

---

## Final Verdict

**✅ PASS WITH WARNINGS**

All 3 implementation tasks are correctly implemented. Every spec scenario has confirming evidence in source. The design is followed exactly. No regressions detected in `asignarPuntoVenta()` existing fields.

The two WARNINGs are:
1. `get_puntos_vta_sucursal` was extended beyond the original design table — a coherent and necessary addition, low risk.
2. Sibling templates and JS files have analogous patterns that remain unfixed — out of scope, flagged as technical debt.

Phase 4 manual verification tasks (4.1–4.4) remain pending and require a running application.
