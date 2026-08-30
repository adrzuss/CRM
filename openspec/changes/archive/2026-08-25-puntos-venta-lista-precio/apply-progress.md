# Apply Progress: puntos-venta-lista-precio

**Change**: puntos-venta-lista-precio  
**Mode**: Standard (no TDD runner)  
**Date**: 2026-08-25  
**Delivery**: single-pr-default

---

## Completed Tasks

- [x] 1.1 `models/configs.py` — Added `id_lista_precio` FK column to `PuntosVenta`
- [x] 1.2 `models/configs.py` — Added `lista_precio` relationship to `PuntosVenta`
- [x] 2.1 `services/configs.py` — Added `id_lista_precio = form.get('id_lista_precio') or None`
- [x] 2.2 `services/configs.py` — UPDATE path: `puntoVenta.id_lista_precio = id_lista_precio`
- [x] 2.3 `services/configs.py` — INSERT path: `puntoVenta.id_lista_precio = id_lista_precio`
- [x] 2.4 `routes/configs.py` — `ListasPrecios` already imported; confirmed
- [x] 2.5 `routes/configs.py` — Added `joinedload(PuntosVenta.lista_precio)` to query
- [x] 2.6 `routes/configs.py` — Added `listas_precios = ListasPrecios.query.all()` + passed to template
- [x] 3.1 `_alta-punto-venta.html` — Resized `idsucursal` col-md-5 → col-md-3; added `<select name="id_lista_precio">` col-md-4
- [x] 3.2 `_lst-puntos-ventas.html` — Added `<th>Lista de precios</th>` after Sucursal
- [x] 3.3 `_lst-puntos-ventas.html` — Added `<td>` with badge/`—` fallback for `punto.lista_precio`
- [x] 3.4 `_lst-puntos-ventas.html` — BS5: `data-dismiss` → `data-bs-dismiss`; `btn-close btn-close-white`
- [x] 3.5 `_lst-puntos-ventas.html` — BS5: `$(...).modal('show')` → `new bootstrap.Modal(...).show()` (both calls)
- [x] 3.6 `_lst-puntos-ventas.html` — BS5: alert close `data-dismiss` → `data-bs-dismiss`; `btn-close`
- [x] 3.7 `_lst-puntos-ventas.html` — BS5: `$(...).modal('hide')` → `bootstrap.Modal.getInstance(...).hide()`

---

## Files Changed

| File | Action | What Was Done |
|------|--------|---------------|
| `models/configs.py` | Modified | Added `id_lista_precio` FK column + `lista_precio` relationship to `PuntosVenta` (before existing `sucursal` relationship) |
| `services/configs.py` | Modified | Read `id_lista_precio` from form; assigned in both UPDATE and INSERT paths |
| `routes/configs.py` | Modified | Added `joinedload(PuntosVenta.lista_precio)` to query; added `listas_precios` query + pass to template |
| `templates/configuracion/partials/_alta-punto-venta.html` | Modified | Resized sucursal col-md-5→col-md-3; added `<select name="id_lista_precio">` col-md-4 with pre-selection logic |
| `templates/configuracion/partials/_lst-puntos-ventas.html` | Modified | Added Lista de precios th/td with badge; fixed all BS4 modal/alert patterns to BS5 |

---

## Deviations from Design

None — implementation matches design exactly.

Notable confirmations:
- `ListasPrecios` was already imported in `routes/configs.py` (task 2.4 confirmed, no change needed)
- `joinedload` was already imported in `routes/configs.py`
- The `or None` coercion in service correctly handles empty string → `None` (not `0`)

---

## Issues Found

None.

---

## Remaining Tasks

- [ ] 4.1 Verify DB column exists: `SHOW COLUMNS FROM puntos_venta LIKE 'id_lista_precio';`
- [ ] 4.2–4.6 Manual smoke tests (require running app + DB with migration applied)

> **Migration prerequisite**: `ALTER TABLE puntos_venta ADD COLUMN id_lista_precio INT NULL, ADD CONSTRAINT fk_pv_lista FOREIGN KEY (id_lista_precio) REFERENCES listas_precio(id);`

---

## Workload / PR Boundary

- Mode: single PR
- Estimated review budget: ~80 changed lines (well under 400-line budget)

---

## Status

15/15 implementation tasks complete. Ready for verify phase (pending DB migration + manual smoke).
