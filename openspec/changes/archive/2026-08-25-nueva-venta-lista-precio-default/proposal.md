# Proposal: Auto-select Default Price List on Punto de Venta Selection

## Intent

When a user selects a punto de venta in `nueva_venta`, the price list (`#idlista`) is not updated — it stays on whatever was selected at page load. If the selected POS has a default `id_lista_precio` configured, that default should be applied automatically, keeping the sale screen consistent with the POS configuration. Additionally, the page-load default is hardcoded to `lista.id == 1`, which breaks if that record was deleted.

## Scope

### In Scope
- Extend `POST /ventas/set_punto_vta` response to include `id_lista_precio`
- Update `asignarPuntoVenta()` in JS to read `id_lista_precio` and set `#idlista` (with fallback to first option)
- Fix template pre-selection from `{% if lista.id == 1 %}` → `{% if loop.first %}`

### Out of Scope
- Calling `recalcularPreciosPorLista()` on auto-select (no items present at POS selection time; existing `change` listener handles manual changes)
- Modifying `GET /ventas/get_punto_vta` (reload path; template default handles it)
- Modifying `GET /ventas/get_puntos_vta_sucursal`
- Any new endpoints or new files

## Capabilities

### New Capabilities
- `nueva-venta-lista-precio-default`: Auto-selects the price list in `nueva_venta` when a POS is assigned, based on the POS's configured default list

### Modified Capabilities
- `puntos-venta-lista-precio`: `set_punto_vta` must now expose `id_lista_precio` in its response — this extends the existing capability's runtime contract

## Approach

Extend the already-loaded `PuntosVenta` object in `set_punto_vta` to return `id_lista_precio` (one field added to JSON). In `asignarPuntoVenta()`, after DOM updates, read that field: if truthy, set `$('#idlista').val(id_lista_precio)`; if falsy, set it to `$('#idlista option:first').val()`. Fix the template to use `{% if loop.first %}` for page-load default. No new HTTP calls, no new endpoints.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `routes/ventas.py` — `set_punto_vta()` | Modified | Add `id_lista_precio` to JSON response |
| `static/js/nueva_venta.js` — `asignarPuntoVenta()` | Modified | Read and apply `id_lista_precio` to `#idlista` |
| `templates/ventas/nueva_venta.html` | Modified | Replace `lista.id == 1` with `loop.first` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `id_lista_precio` is nullable | High (by design) | JS fallback to first `<option>` |
| Race condition: `#idlista` has no options at load | Low | Options are server-rendered; always present |
| POS with `id_lista_precio` pointing to deleted list | Low | `<option>` won't match; jQuery `.val()` silently no-ops; fallback acceptable |

## Rollback Plan

All changes are additive or cosmetic. To revert:
1. Remove `id_lista_precio` from `set_punto_vta` JSON dict (1 line)
2. Remove the `id_lista_precio` block from `asignarPuntoVenta()` (~5 lines)
3. Restore `{% if lista.id == 1 %}` in the template

No DB migrations. No new files to delete.

## Dependencies

- `puntos-venta-lista-precio` change must be deployed (column and model FK already exist — confirmed in exploration)

## Success Criteria

- [ ] Selecting a POS with `id_lista_precio = 2` sets `#idlista` to `2`
- [ ] Selecting a POS with `id_lista_precio = null` sets `#idlista` to the first option
- [ ] Page load with no POS pre-selected defaults `#idlista` to the first list (not hardcoded id=1)
- [ ] Changing `#idlista` manually still triggers `recalcularPreciosPorLista()` (existing behavior unchanged)
