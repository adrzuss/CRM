# Tasks: Add `id_lista_precio` to Puntos de Venta + UI Modernization

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~120–160 lines |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr-default |
| Chain strategy | size-exception (not needed) |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | All 5 files in one PR | PR 1 | ~120–160 lines; well under 400-line budget |

---

## Phase 1: Foundation — ORM Model

- [x] 1.1 `models/configs.py` — Add `id_lista_precio = db.Column(db.Integer, db.ForeignKey('listas_precio.id'), nullable=True)` to `PuntosVenta`, after existing columns and before the `sucursal` relationship.
- [x] 1.2 `models/configs.py` — Add `lista_precio = db.relationship('ListasPrecios', foreign_keys=[id_lista_precio], lazy='select')` to `PuntosVenta`. Do NOT modify `__init__`.

## Phase 2: Core Implementation — Service + Route

- [x] 2.1 `services/configs.py` — In `grabarDatosPtoVta`, add `id_lista_precio = form.get('id_lista_precio') or None` near the top alongside existing `form.get` calls.
- [x] 2.2 `services/configs.py` — In the UPDATE path, assign `puntoVenta.id_lista_precio = id_lista_precio` after `clave_certificado`.
- [x] 2.3 `services/configs.py` — In the INSERT path, assign `puntoVenta.id_lista_precio = id_lista_precio` after `fac_electronica`.
- [x] 2.4 `routes/configs.py` — Confirm `ListasPrecios` is already imported; if not, add `from models.articulos import ListasPrecios`.
- [x] 2.5 `routes/configs.py` — In `puntos_venta`, extend the query: add `joinedload(PuntosVenta.lista_precio)` alongside the existing `joinedload(PuntosVenta.sucursal)`.
- [x] 2.6 `routes/configs.py` — Add `listas_precios = ListasPrecios.query.all()` before `render_template` and pass it as `listas_precios=listas_precios`.

## Phase 3: Integration — Templates

- [x] 3.1 `_alta-punto-venta.html` — In the `pv-section-general` row, resize the `idsucursal` column from `col-md-5` to `col-md-3`, then add a new `col-md-4` block with `<select name="id_lista_precio">` containing "Sin lista" default option and a `{% for lista in listas_precios %}` loop that sets `selected` when `puntoVenta.id_lista_precio == lista.id`.
- [x] 3.2 `_lst-puntos-ventas.html` — Add `<th scope="col">Lista de precios</th>` after the `Sucursal` header.
- [x] 3.3 `_lst-puntos-ventas.html` — Add `<td>` with badge or `—` fallback after each `sucursal` cell, using `punto.lista_precio`.
- [x] 3.4 `_lst-puntos-ventas.html` — BS5 fix line ~89: `data-dismiss="modal"` → `data-bs-dismiss="modal"`; replace close `<span>&times;</span>` button with `<button class="btn-close btn-close-white">`.
- [x] 3.5 `_lst-puntos-ventas.html` — BS5 fix line ~116: `$('#modalLineasComprobantes').modal('show')` → `new bootstrap.Modal(document.getElementById('modalLineasComprobantes')).show()`.
- [x] 3.6 `_lst-puntos-ventas.html` — BS5 fix line ~143: `data-dismiss="alert"` → `data-bs-dismiss="alert"`; replace close button markup.
- [x] 3.7 `_lst-puntos-ventas.html` — BS5 fix line ~148: `$('#modalLineasComprobantes').modal('hide')` → `bootstrap.Modal.getInstance(document.getElementById('modalLineasComprobantes')).hide()`.

## Phase 4: Verification (Manual Smoke)

- [ ] 4.1 Verify DB: `SHOW COLUMNS FROM puntos_venta LIKE 'id_lista_precio';` — if absent, run the `ALTER TABLE` from design.md before testing.
- [ ] 4.2 Create a new POS — confirm dropdown shows all `ListasPrecios`, "Sin lista" pre-selected; save and verify `id_lista_precio` stored correctly.
- [ ] 4.3 Edit existing POS with a list assigned — confirm the correct option is pre-selected.
- [ ] 4.4 Select "Sin lista", save — confirm `id_lista_precio` is `NULL` in DB (not `0`).
- [ ] 4.5 Load list view — confirm "Lista de precios" column shows badge for assigned rows and "—" for unassigned.
- [ ] 4.6 Open/close modal in list view — confirm no BS4-related console errors.
