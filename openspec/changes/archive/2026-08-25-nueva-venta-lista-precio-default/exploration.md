# Exploration: Auto-select default price list when punto de venta is selected in nueva_venta

## Current State

### Template (`templates/ventas/nueva_venta.html`)
- Renders `#idlista` select populated from `listas_precio` (all `ListasPrecios` records).
- Default pre-selection is hardcoded: `{% if lista.id == 1 %}selected{% endif %}`.

### JavaScript (`static/js/nueva_venta.js`)
- `asignarPuntoVenta(idPuntoVenta)` (line 548): POSTs to `/ventas/set_punto_vta`, then updates DOM fields (`posPrinter`, `facElectronica`, etc.).
- `saleccionarPtoVta(datos)` (line 160): Shows a modal, calls `asignarPuntoVenta` on confirm.
- `DOMContentLoaded` (line 34): Calls `asignarPuntoVenta` directly if only 1 POS.
- `recalcularPreciosPorLista()` (line 1089): Handles list change with price recalc (no changes needed here).

### Backend endpoints

#### `GET /ventas/get_punto_vta`
Returns current session POS state:
```json
{ "success": true, "punto_vta": <id>, "fac_electronica": bool, "pos_printer": str|null }
```
Does **NOT** include `id_lista_precio`.

#### `GET /ventas/get_puntos_vta_sucursal`
Returns all POS for the current branch. Query is:
```python
db.session.query(PuntosVenta.id, PuntosVenta.punto_vta, PuntosVenta.fac_electronica)
```
Returns: `[{ "id": int, "puntoVta": int, "facElectronica": "Si"|"No" }]`  
Does **NOT** include `id_lista_precio`.

#### `POST /ventas/set_punto_vta`
Receives `{ "punto_vta_id": int }`, loads full `PuntosVenta` object via `db.session.get(PuntosVenta, punto_vta_id)`, stores in session, and returns:
```json
{ "success": true, "message": "...", "posPrinter": str|null, "facElectronica": bool }
```
Does **NOT** currently return `id_lista_precio`, but the object is already loaded — adding it is a 1-line change.

### Models

#### `PuntosVenta` (`models/configs.py`, line 154)
- Has `id_lista_precio = db.Column(db.Integer, db.ForeignKey('listas_precio.id'), nullable=True)` — already exists.
- Has `lista_precio` relationship to `ListasPrecios`.

#### `ListasPrecios` (`models/articulos.py`, line 132)
- Fields: `id`, `nombre`, `markup`.
- No default ordering defined. `ListasPrecios.query.all()` in the route returns them in DB insertion order (effectively by `id` ascending unless otherwise indexed).

### Route for `nueva_venta` (`routes/ventas.py`, line 87)
```python
listas_precio = ListasPrecios.query.all()
return render_template('nueva_venta.html', ..., listas_precio=listas_precio, ...)
```
No explicit ordering. First item rendered = first in the list = typically lowest `id`.

## Affected Areas

- `routes/ventas.py` — `set_punto_vta()` endpoint needs to return `id_lista_precio`
- `static/js/nueva_venta.js` — `asignarPuntoVenta()` needs to read `id_lista_precio` from response and update `#idlista`
- `templates/ventas/nueva_venta.html` — hardcoded `{% if lista.id == 1 %}selected{% endif %}` should change to use the first item as default (not hardcoded id=1)

## Approaches

### Option A — Add `id_lista_precio` to `/ventas/set_punto_vta` response ✅ RECOMMENDED
Change the route to also return `puntoVta.id_lista_precio`.  
In `asignarPuntoVenta()`, after the POST succeeds, set `#idlista` value:
- If `id_lista_precio` is not null → select that value.
- If null → select the first `<option>` in `#idlista`.
Then call `recalcularPreciosPorLista()` to trigger recalc.

- **Pros**: Minimal blast radius. All data is available at the point where POS is set. No new endpoint. No extra HTTP call. Consistent with existing `posPrinter`/`facElectronica` pattern. The `PuntosVenta` object is already loaded at that point.
- **Cons**: None significant.
- **Effort**: Low — 1 backend line, ~10 JS lines.

### Option B — Add `id_lista_precio` to `/ventas/get_puntos_vta_sucursal` response
Include `id_lista_precio` in the list query. JS reads it from the list at selection time.

- **Pros**: Data is available before the user confirms selection (could pre-show the list change in the modal).
- **Cons**: `saleccionarPtoVta` currently calls `asignarPuntoVenta` on confirm anyway, so the actual assignment still happens via `set_punto_vta`. Would require caching the POS data in JS. More complex plumbing. The query currently selects only 3 columns; adding `id_lista_precio` is fine but adds complexity without clear benefit over Option A.
- **Effort**: Low-Medium.

### Option C — New endpoint to query default list for a POS
A dedicated `GET /ventas/get_lista_precio_default/<pos_id>` endpoint.

- **Pros**: Clean separation of concerns.
- **Cons**: Adds an extra HTTP round trip. Adds a new endpoint that duplicates data already accessible in `set_punto_vta`. Unnecessary complexity.
- **Effort**: Medium.

## Recommendation

**Option A** — extend the existing `set_punto_vta` response with `id_lista_precio`.

This follows the exact same pattern already established for `posPrinter` and `facElectronica`: the `PuntosVenta` object is already loaded, so the only backend change is adding one field to the JSON response. The JS change is localized to `asignarPuntoVenta()`.

Additionally, the template's hardcoded `{% if lista.id == 1 %}` should be changed to `{% if loop.first %}` to properly default to the first list regardless of ID.

## Risks

- `id_lista_precio` is nullable in the model. JS must handle the null case (fall back to first `<option>`). This is covered in the approach.
- `recalcularPreciosPorLista()` must be called after setting `#idlista` — otherwise prices won't update on auto-selection. Confirm it handles being called during `DOMContentLoaded` (when POS is auto-assigned for single-POS users).
- If `#idlista` has no options yet when `asignarPuntoVenta` fires (race condition during page load), the fallback to `first option` would silently fail. Low risk — `listas_precio` is server-rendered.
- Hardcoded `id == 1` in template: if lista with `id=1` was deleted, no default is selected today. Fix with `loop.first`.

## Ready for Proposal

Yes. The scope is narrow, the approach is clear, and all affected files are identified. Ready for `sdd-propose`.
