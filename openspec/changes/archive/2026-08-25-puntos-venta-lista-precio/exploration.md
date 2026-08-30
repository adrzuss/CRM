# Exploration: Add `id_lista_precio` to Puntos de Venta + UI Modernization

**Date:** 2026-08-25  
**Change:** `puntos-venta-lista-precio`

---

## Current State

### Form partial (`_alta-punto-venta.html`)

The form is well-structured with named CSS sections:
- `pv-section-general` — ID display, punto de venta number, sucursal dropdown
- `pv-section-comprobantes` — invoice counters (A/B or C, conditional on `session['tipo_iva']`)
- `pv-section-remitos` — remito/recibo counters
- `pv-section-factura-e` — electronic invoice toggle + certificate fields
- `pv-section-impresoras` — POS printer toggle

The `pv-section-general` ends at line 37 (after the sucursal `<select>`). The new `id_lista_precio` dropdown should be inserted inside this section, after the `idsucursal` field.

### Model (`models/configs.py` — `PuntosVenta`)

```python
class PuntosVenta(db.Model):
    __tablename__ = 'puntos_venta'
    id, punto_vta, idsucursal,
    ultima_fac_a/b/c, ultima_deb_a/b/c, ultima_nc_a/b/c,
    ultimo_rem_x, ultimo_rec_x,
    fac_electronica, pos_printer, certificado_p12, clave_certificado,
    token, sign, expiration
    sucursal = relationship('Sucursales')
```

**⚠️ CRITICAL GAP:** `id_lista_precio` is NOT defined in the ORM model (`PuntosVenta`). It is claimed to exist in the DB table but is absent from the Python class. The model needs a new column declaration:
```python
id_lista_precio = db.Column(db.Integer, db.ForeignKey('listas_precio.id'), nullable=True)
```

### `ListasPrecios` model (`models/articulos.py`)

```python
class ListasPrecios(db.Model):
    __tablename__ = 'listas_precio'
    id   = Integer PK
    nombre = String(100)
    markup = Numeric(20,6)
```

**⚠️ KEY FINDING: No `idsucursal` column in `listas_precio`.** Lists are global — not branch-scoped. The requirement to "populate with price lists for the relevant branch" has **no data-model support**. All lists are available to all branches.

### Route (`routes/configs.py` — `puntos_venta`)

```python
@bp_configuraciones.route('/puntos_venta/<int:id>', methods=['GET', 'POST'])
def puntos_venta(id=0):
    # POST  → calls grabarDatosPtoVta(request.form)
    # GET   → loads puntoVenta by id or None
    sucursales = Sucursales.query.all()
    puntos_venta = PuntosVenta.query.options(joinedload(...)).all()
    return render_template('puntos-venta.html', puntos_venta=..., puntoVenta=..., sucursales=...)
```

**Missing context variable:** `listas_precios` is NOT passed to the template. It needs to be added (already imported from `models.articulos` at the top of `routes/configs.py`).

### Service (`services/configs.py` — `grabarDatosPtoVta`)

Manually reads form fields and sets ORM attributes. Does NOT handle `id_lista_precio` today. Both create and update paths need a line like:
```python
id_lista_precio = form.get('id_lista_precio') or None
puntoVenta.id_lista_precio = id_lista_precio
```

### How other dropdowns use `ListasPrecios`

All existing usages are **global** (no branch filter):
```python
listas_precio = ListasPrecios.query.all()
```
Examples: `routes/ventas.py` lines 112, 140, 548, 615; `routes/articulos.py` lines 151, 287, 418.

The dropdown pattern used everywhere:
```html
<select name="idlista" class="form-select">
    {% for lista in listas_precio %}
        <option value="{{ lista.id }}" {{ 'selected' if venta.idlista == lista.id }}>{{ lista.nombre }}</option>
    {% endfor %}
</select>
```

---

## Affected Areas

| File | Change needed |
|------|--------------|
| `models/configs.py` | Add `id_lista_precio` column + optional FK relationship to `PuntosVenta` |
| `routes/configs.py` | Pass `listas_precios` to template in `puntos_venta()` route |
| `services/configs.py` | Read `id_lista_precio` from form in `grabarDatosPtoVta()`, assign to model |
| `templates/configuracion/partials/_alta-punto-venta.html` | Add `<select>` for `id_lista_precio` inside `pv-section-general` |
| `templates/configuracion/partials/_lst-puntos-ventas.html` | Optional: add "Lista de precios" column to the list table |

---

## Approaches

### Approach 1 — Global list (no branch filter) — **Recommended**
Add the dropdown populated with ALL `ListasPrecios`, matching how every other form in the system works.

- **Pros:** Consistent with all existing patterns; simple; no data model changes to `listas_precio`
- **Cons:** Does not implement the "per branch" filtering mentioned in the requirement
- **Effort:** Low

### Approach 2 — Branch-scoped list via dynamic HTMX / JS
When `idsucursal` changes, call an HTMX endpoint that returns filtered lists. Would require adding `idsucursal` to `listas_precio` table and model.

- **Pros:** Fulfills the literal requirement for branch-scoped filtering
- **Cons:** `listas_precio` table has no `idsucursal` column (schema migration required); no prior pattern in the codebase; disproportionate effort for a config screen
- **Effort:** High

### Approach 3 — Branch-scoped via server-side preload (static at page load)
Pass `listas_precios` filtered by the selected sucursal when loading for edit. For new records, pass all.

- **Pros:** No JS needed, cleaner than HTMX for a config form
- **Cons:** Still requires `listas_precio.idsucursal` which doesn't exist; same schema gap as Approach 2
- **Effort:** Medium-High

---

## Recommendation

**Use Approach 1** — global list, all `ListasPrecios`, no branch filter. This is how every other dropdown in the codebase works. The requirement text says "for the relevant branch" but the data model provides no basis for that filtering. Confirm with the user whether branch-scoped lists are actually needed **before** attempting Approach 2 or 3.

---

## Risks and Gaps

1. **DB vs ORM gap**: `id_lista_precio` is reportedly in the DB but not in the ORM model. This must be added. If the column doesn't exist in the DB yet, a migration is needed.
2. **No branch filter on `listas_precio`**: Table is global. If filtering by branch is a real requirement, `listas_precio` needs a new column (`idsucursal`) and a schema migration.
3. **`__init__` signature**: `PuntosVenta.__init__` does not include `id_lista_precio`. Adding as a nullable column with default `None` keeps it backward-compatible without touching `__init__`.
4. **List display**: The current `_lst-puntos-ventas.html` table doesn't show the price list. A "Lista de precios" column could be added but requires the `lista_precio` relationship on `PuntosVenta` and `joinedload` in the query.

---

## UI Modernization Observations

The templates are already on Bootstrap 5 with Font Awesome icons. The overall structure is clean. Notable opportunities:

1. **List partial** (`_lst-puntos-ventas.html`) still uses Bootstrap 4 modal patterns (`data-dismiss`, `$(...).modal('show')` via jQuery). The rest of the app uses BS5 (`data-bs-dismiss`, `bootstrap.Modal`). This is a **compatibility inconsistency** — not a blocker but worth noting.
2. The form sections (`pv-section-*`) use custom CSS classes, not Bootstrap utility classes. Style is consistent internally but diverges from the HTMX-driven configuracion pages.
3. No immediate major redesign opportunity — the form is functionally clean. Possible small win: display the `id_lista_precio` in the list table with a badge (matching how `punto_vta` is shown as a `badge bg-primary`).

---

## Ready for Proposal

**Yes** — with one clarification needed: confirm whether `id_lista_precio` already exists in the DB table `puntos_venta`. If yes, Approach 1 can proceed immediately. If no, a DB migration is part of scope. Branch-level filtering is a separate, larger scope item and should NOT block this change.
