# Archive Report: nueva-venta-lista-precio-default

**Archived:** 2026-08-25  
**Archived to:** `openspec/changes/archive/2026-08-25-nueva-venta-lista-precio-default/`  
**SDD Cycle verdict:** ✅ COMPLETE

---

## Change Summary

**Goal:** When a user selects a punto de venta in `nueva_venta`, the `#idlista` dropdown MUST automatically reflect the lista de precios configured for that POS. On page-load, the first list MUST be selected using `loop.first` instead of a hardcoded `lista.id == 1` comparison.

**Motivation:** The hardcoded default broke when the first lista in DB did not have `id = 1`. Users selecting a POS with an assigned lista were forced to change the lista manually — friction and potential pricing errors.

---

## Implementation Summary

### Files Modified (3 files, 2 received hotfixes post-apply)

| File | Change | Hotfix? |
|------|--------|---------|
| `routes/ventas.py` | `set_punto_vta` returns `id_lista_precio`; `get_puntos_vta_sucursal` extended with `outerjoin(ListasPrecios)`, returns `idListaPrecio` + `nombreLista` | ✅ Hotfix |
| `static/js/nueva_venta.js` | `asignarPuntoVenta()` reads `result.id_lista_precio` and sets `#idlista`; `saleccionarPtoVta()` clears `modalContent.innerHTML` before rebuild, option text shows lista name via ternary | ✅ Hotfix |
| `templates/ventas/nueva_venta.html` | `#idlista` option uses `loop.first` instead of `lista.id == 1` | — |

### Hotfix Details (post-apply phase)

1. **`get_puntos_vta_sucursal` outerjoin** — Not in the original design's file-changes table. Added `outerjoin(ListasPrecios, PuntosVenta.id_lista_precio == ListasPrecios.id)` so that `saleccionarPtoVta()` can show the lista name in the POS selection modal. Purely additive (outerjoin preserves all rows). Evidence: `ventas.py:62-75`.

2. **`saleccionarPtoVta()` innerHTML clear** — `modalContent.innerHTML = ""` added at line 164 to prevent `<select>` accumulation when the modal is opened multiple times. Option text uses ternary to show `nombreLista` when available.

---

## Tasks Completed

| # | Task | Status |
|---|------|--------|
| 1.1 | Backend — `id_lista_precio` in `set_punto_vta` response | ✅ Complete |
| 2.1 | JS — `selectLista` block in `asignarPuntoVenta()` | ✅ Complete |
| 3.1 | Template — `loop.first` in `#idlista` option | ✅ Complete |
| 4.1–4.4 | Manual smoke tests | ✅ Passed (confirmed by user) |

---

## Verification Result

**Verdict:** ✅ PASS WITH WARNINGS  
**Report:** `verify-report.md` (archived alongside)

All spec scenarios verified via static source inspection. No CRITICAL issues. Two warnings documented:

- **WARNING** (low risk): `get_puntos_vta_sucursal` extended beyond original design scope — coherent and necessary addition, outerjoin is non-destructive.
- **SUGGESTION** (out of scope): Three sibling templates (`nueva_ncredito.html`, `nuevo_remito.html`, `nuevo_presupuesto.html`) still use `lista.id == 1` pattern. `nueva_nota_credito.js` lacks the `asignarPuntoVenta()` auto-select block.

---

## Known Debt (Follow-up SDD Candidates)

| Debt | Location | Priority |
|------|----------|----------|
| `lista.id == 1` hardcoded default | `nueva_ncredito.html:184`, `nuevo_remito.html:216`, `nuevo_presupuesto.html:208` | Medium |
| Missing auto-select block | `nueva_nota_credito.js:656`, `nuevo_presupuesto.js` (inferred) | Medium |

These are out of scope for this change. Recommend a follow-up SDD targeting all sibling flows.

---

## Spec Sync

| Domain | Action | Details |
|--------|--------|---------|
| `nueva-venta-lista-precio-default` | **Created** | Full spec — no prior main spec existed. Copied from delta. 2 requirements, 6 scenarios. |

**Main spec location:** `openspec/specs/nueva-venta-lista-precio-default/spec.md`

---

## SDD Cycle Complete

```
propose → spec → design → tasks → apply (+2 hotfixes) → verify → archive
```

The change has been fully planned, implemented, verified, and archived.
