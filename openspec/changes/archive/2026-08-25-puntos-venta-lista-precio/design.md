# Design: Add `id_lista_precio` to Puntos de Venta + UI Modernization

**Change:** `puntos-venta-lista-precio`
**Date:** 2026-08-25

---

## Technical Approach

Minimal surface-area change following the global list pattern already used in `routes/configs.py` (`listas_precios = ListasPrecios.query.all()` already exists in `configuraciones()`). Add nullable FK + relationship to model, wire service and route, add `<select>` to form partial, add column to list partial, fix BS4 remnants.

---

## Architecture Decisions

| # | Decision | Choice | Rejected | Rationale |
|---|----------|--------|----------|-----------|
| 1 | FK nullability | `nullable=True`, no default | `default=0` or `nullable=False` | Existing POS records have no list; `None` is semantically correct and backward-compatible |
| 2 | Relationship loading | `joinedload(PuntosVenta.lista_precio)` in route | Lazy load | Avoids N+1 on list view; consistent with existing `joinedload(PuntosVenta.sucursal)` pattern |
| 3 | `__init__` signature | Do NOT add `id_lista_precio` to `__init__` | Add as kwarg | Constructor is positional-heavy; post-init assignment (`puntoVenta.id_lista_precio = …`) avoids breaking all callers |
| 4 | Service coercion | `id_lista_precio = form.get('id_lista_precio') or None` | `int()` cast | Empty string from form must become `None`, not `0`; `or None` pattern matches existing `pos_printer`/`fac_electronica` style |
| 5 | BS5 modal fix | Replace `data-dismiss` → `data-bs-dismiss`, `$(...).modal(...)` → `bootstrap.Modal` | Leave as-is | Mixed BS4/BS5 causes silent failures; already a spec requirement |

---

## Data Flow

```
POST /puntos_venta/0
  form['id_lista_precio'] = "2" or ""
        │
        ▼
grabarDatosPtoVta(form)
  id_lista_precio = form.get('id_lista_precio') or None
  puntoVenta.id_lista_precio = id_lista_precio
  db.session.commit()
        │
        ▼
GET /puntos_venta/<id>
  PuntosVenta.query.options(
      joinedload(PuntosVenta.sucursal),
      joinedload(PuntosVenta.lista_precio)   ← NEW
  ).all()
  listas_precios = ListasPrecios.query.all() ← NEW
        │
        ▼
  template: select pre-selects puntoVenta.id_lista_precio
  list: badge from punto.lista_precio.nombre or "—"
```

---

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `models/configs.py` | Modify | Add `id_lista_precio` FK column + `lista_precio` relationship to `PuntosVenta` |
| `services/configs.py` | Modify | Read and persist `id_lista_precio` in `grabarDatosPtoVta` (both UPDATE and INSERT paths) |
| `routes/configs.py` | Modify | Add `joinedload(PuntosVenta.lista_precio)` to query; pass `listas_precios` to template |
| `templates/configuracion/partials/_alta-punto-venta.html` | Modify | Add `<select name="id_lista_precio">` inside `pv-section-general` row |
| `templates/configuracion/partials/_lst-puntos-ventas.html` | Modify | Add "Lista de precios" `<th>`/`<td>`; fix BS4 modal patterns |

---

## Interfaces / Contracts

### Model addition (`models/configs.py`, class `PuntosVenta`)

```python
# After existing columns, before `sucursal` relationship:
id_lista_precio = db.Column(db.Integer, db.ForeignKey('listas_precio.id'), nullable=True)
lista_precio = db.relationship('ListasPrecios', foreign_keys=[id_lista_precio], lazy='select')
```

> `lazy='select'` is fine because `joinedload` in the route overrides it for the list view. The relationship is used read-only.

### Service addition (`services/configs.py`, `grabarDatosPtoVta`)

```python
# Add near top of function, after existing form.get calls:
id_lista_precio = form.get('id_lista_precio') or None

# UPDATE path — add after clave_certificado assignment:
puntoVenta.id_lista_precio = id_lista_precio

# INSERT path — add after fac_electronica assignment:
puntoVenta.id_lista_precio = id_lista_precio
```

### Route addition (`routes/configs.py`, `puntos_venta`)

```python
# Import already present: from models.articulos import ListasPrecios

# Query line (replace existing):
puntos_venta = PuntosVenta.query.options(
    joinedload(PuntosVenta.sucursal),
    joinedload(PuntosVenta.lista_precio)
).all()

# Add before render_template:
listas_precios = ListasPrecios.query.all()

# Add to render_template kwargs:
listas_precios=listas_precios
```

### Form `<select>` (`_alta-punto-venta.html`)

Add a new `col-md-4` inside the existing `pv-section-general` row, after the `idsucursal` column:

```html
<div class="col-md-4 mb-3">
    <label for="id_lista_precio" class="form-label">Lista de precios</label>
    <select name="id_lista_precio" id="id_lista_precio" class="form-select">
        <option value="">Sin lista</option>
        {% for lista in listas_precios %}
            <option value="{{ lista.id }}"
                {{ 'selected' if puntoVenta and puntoVenta.id_lista_precio == lista.id else '' }}>
                {{ lista.nombre }}
            </option>
        {% endfor %}
    </select>
</div>
```

> Note: the existing row has `col-md-2` + `col-md-3` + `col-md-5` = 10 cols. Resize `col-md-5` (sucursal) to `col-md-3` and add the new `col-md-4` to fill 12.

### List partial (`_lst-puntos-ventas.html`)

**Header** — add after `Sucursal` `<th>`:
```html
<th scope="col">Lista de precios</th>
```

**Row cell** — add after sucursal `<td>`:
```html
<td>
    {% if punto.lista_precio %}
        <span class="badge bg-secondary">{{ punto.lista_precio.nombre }}</span>
    {% else %}
        —
    {% endif %}
</td>
```

**BS5 fixes:**
1. Line 89: `data-dismiss="modal"` → `data-bs-dismiss="modal"`; `class="close text-white"` → `class="btn-close btn-close-white"`; remove `<span aria-hidden="true">&times;</span>`
2. Line 116: `$('#modalLineasComprobantes').modal('show')` → `new bootstrap.Modal(document.getElementById('modalLineasComprobantes')).show()`
3. Line 143: `data-dismiss="alert"` → `data-bs-dismiss="alert"`; `class="close"` → `class="btn-close"`; remove `&times;`
4. Line 148: `$('#modalLineasComprobantes').modal('hide')` → `bootstrap.Modal.getInstance(document.getElementById('modalLineasComprobantes')).hide()`

---

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Manual smoke | Form saves `id_lista_precio`, pre-selects on edit, list shows badge | Load app, create/edit POS |
| Manual smoke | Empty selection saves `None` (not `0`) | Select "Sin lista", save, re-open |
| Manual smoke | Modal opens/closes without BS console errors | Browser devtools |

No automated tests — project has no test runner for this layer.

---

## Migration / Rollout

Column `puntos_venta.id_lista_precio INTEGER NULL` must exist before deploy.  
Verify: `SHOW COLUMNS FROM puntos_venta LIKE 'id_lista_precio';`  
If absent, run: `ALTER TABLE puntos_venta ADD COLUMN id_lista_precio INT NULL, ADD CONSTRAINT fk_pv_lista FOREIGN KEY (id_lista_precio) REFERENCES listas_precio(id);`

---

## Open Questions

- None. All decisions are unambiguous given the codebase patterns.
