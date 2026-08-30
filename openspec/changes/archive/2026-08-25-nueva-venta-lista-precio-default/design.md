# Design: Auto-select Default Price List on Punto de Venta Selection

## Technical Approach

Three surgical edits across three files. No new endpoints, no new files, no DB changes. The backend exposes one additional field; the JS reads it and applies it; the template fixes a fragile hardcoded ID.

## Architecture Decisions

| Decision | Choice | Rejected | Rationale |
|----------|--------|----------|-----------|
| Where to expose `id_lista_precio` | Add to existing `set_punto_vta` JSON response | New endpoint | Already the single source of truth for POS data in the session flow |
| JS fallback when null | Set `selectLista.options[0].value` | Keep current value / no-op | Guarantees a valid selection even if POS has no configured list |
| Template default | `loop.first` | `lista.id == 1` | Decoupled from DB primary key; survives deletion or renumbering of records |
| Trigger `recalcularPreciosPorLista()` | **Not triggered** | Trigger it | No items present at POS selection time; existing `change` listener handles user-driven changes |

## Data Flow

```
User selects POS
      │
      ▼
POST /ventas/set_punto_vta
      │  { punto_vta_id }
      ▼
set_punto_vta() ── db.session.get(PuntosVenta, id)
      │
      ▼
JSON { success, posPrinter, facElectronica, id_lista_precio }
      │
      ▼
asignarPuntoVenta() — updates DOM fields
      │
      ├─ id_lista_precio truthy → selectLista.value = id_lista_precio
      └─ id_lista_precio falsy  → selectLista.value = options[0].value (if options exist)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `routes/ventas.py` | Modify | Add `id_lista_precio` to `set_punto_vta` return dict (line 83) |
| `static/js/nueva_venta.js` | Modify | Insert price-list selection block after line 571 in `asignarPuntoVenta()` |
| `templates/ventas/nueva_venta.html` | Modify | Replace `lista.id == 1` with `loop.first` on line 118 |

## Interfaces / Contracts

### `POST /ventas/set_punto_vta` — updated response

```python
# routes/ventas.py — line 83 (current)
return jsonify({
    'success': True,
    'message': 'Punto de venta asignado correctamente',
    'posPrinter': puntoVta.pos_printer,
    'facElectronica': puntoVta.fac_electronica
})

# → replace with:
return jsonify({
    'success': True,
    'message': 'Punto de venta asignado correctamente',
    'posPrinter': puntoVta.pos_printer,
    'facElectronica': puntoVta.fac_electronica,
    'id_lista_precio': puntoVta.id_lista_precio  # None serializes to null automatically
})
```

### `asignarPuntoVenta()` — insert after line 571

```js
// After: document.getElementById("pos_printer").value = result.posPrinter || '';
const selectLista = document.getElementById('idlista');
if (selectLista) {
  if (result.id_lista_precio) {
    selectLista.value = result.id_lista_precio;
  } else if (selectLista.options.length > 0) {
    selectLista.value = selectLista.options[0].value;
  }
}
```

### `nueva_venta.html` — line 118

```jinja
{# Current #}
<option value="{{ lista.id }}" {{ 'selected' if lista.id == 1 else '' }}>

{# Replace with #}
<option value="{{ lista.id }}" {{ 'selected' if loop.first else '' }}>
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Manual | POS with `id_lista_precio = N` → `#idlista` shows N | Select POS in UI, inspect select value |
| Manual | POS with `id_lista_precio = null` → first option selected | Same flow with a POS that has no list configured |
| Manual | Page load → first list selected regardless of its `id` | Load page, check `#idlista` selected option |
| Manual | Manual list change after auto-select → `recalcularPreciosPorLista()` fires | Change `#idlista` manually, verify price recalc |

## Migration / Rollout

No migration required. All changes are additive or cosmetic. Rollback is three line-level reverts.

## Open Questions

None — design is complete and unambiguous.
