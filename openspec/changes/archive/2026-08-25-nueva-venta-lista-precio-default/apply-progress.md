# Apply Progress: nueva-venta-lista-precio-default

## Status
3/3 implementation tasks complete. Ready for verify.

## Mode
Standard (no TDD — no test runner in project)

## Completed Tasks

- [x] 1.1 Backend — Added `'id_lista_precio': puntoVta.id_lista_precio` to `set_punto_vta` JSON response
- [x] 2.1 JS — Inserted `selectLista` auto-select block in `asignarPuntoVenta()` after `pos_printer` assignment
- [x] 3.1 Template — Replaced `lista.id == 1` with `loop.first` on `#idlista` option tag

## Files Changed

| File | Action | What Was Done |
|------|--------|---------------|
| `routes/ventas.py` | Modified | Added `id_lista_precio` field to `set_punto_vta` return dict (line 83) |
| `static/js/nueva_venta.js` | Modified | Inserted price-list auto-select block after line 571 in `asignarPuntoVenta()` |
| `templates/ventas/nueva_venta.html` | Modified | Replaced `lista.id == 1` with `loop.first` on line 118 |

## Deviations from Design
None — implementation matches design exactly.

## Issues Found
None.

## Remaining Tasks (Manual Verification — Phase 4)
- [ ] 4.1 Select a POS with `id_lista_precio = N` → confirm `#idlista` shows N
- [ ] 4.2 Select a POS with `id_lista_precio = null` → confirm `#idlista` shows first option
- [ ] 4.3 Load page fresh → confirm first list pre-selected regardless of DB `id`
- [ ] 4.4 After auto-select, change `#idlista` manually → confirm `recalcularPreciosPorLista()` fires

## Workload / PR Boundary
- Mode: single PR
- Estimated changed lines: ~12 (additions + deletions)
- Budget risk: Low
