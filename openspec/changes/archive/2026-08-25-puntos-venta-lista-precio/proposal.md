# Proposal: Add `id_lista_precio` to Puntos de Venta + UI Modernization

**Date:** 2026-08-25
**Change:** `puntos-venta-lista-precio`

---

## Intent

`PuntosVenta` stores config per point-of-sale but has no price list assignment. The ORM model lacks `id_lista_precio` (column reportedly exists in DB but is not mapped). This causes the price list to be silently ignored during POS configuration. Additionally, `_lst-puntos-ventas.html` mixes BS4 patterns into an otherwise BS5 codebase.

---

## Scope

### In Scope
- Add `id_lista_precio` FK column to `PuntosVenta` ORM model
- Update `grabarDatosPtoVta` service to read and persist `id_lista_precio`
- Pass `listas_precios = ListasPrecios.query.all()` from route to template
- Add `<select>` for `id_lista_precio` in `pv-section-general` form partial
- Fix BS4 → BS5 patterns in `_lst-puntos-ventas.html` (`data-bs-dismiss`, `bootstrap.Modal`)
- Add "Lista de precios" badge column to list table (requires `lista_precio` relationship + `joinedload`)

### Out of Scope
- Branch-scoped filtering of price lists (`listas_precio` has no `idsucursal`)
- Schema migration (assumed column already exists in DB; migration is a prerequisite, not in this change)
- Full visual redesign

---

## Capabilities

### New Capabilities
- `puntos-venta-lista-precio`: POS point-of-sale can be assigned a price list; the assignment is persisted and displayed.

### Modified Capabilities
- None

---

## Approach

Follow the **global list pattern** used in every existing price-list dropdown across the codebase (`routes/ventas.py`, `routes/articulos.py`). No branch filter — data model has no support for it. Add nullable FK to ORM, wire service + route + template, and fix BS4 remnants in the list partial.

---

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `models/configs.py` | Modified | Add `id_lista_precio` FK column + `lista_precio` relationship to `PuntosVenta` |
| `services/configs.py` | Modified | Read `id_lista_precio` from form in `grabarDatosPtoVta()` |
| `routes/configs.py` | Modified | Pass `listas_precios` to template in `puntos_venta()` |
| `templates/configuracion/partials/_alta-punto-venta.html` | Modified | Add `<select>` for `id_lista_precio` inside `pv-section-general` |
| `templates/configuracion/partials/_lst-puntos-ventas.html` | Modified | Fix BS4 → BS5 patterns; add "Lista de precios" column with badge |

---

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Column missing from DB (not yet migrated) | Medium | Verify `SHOW COLUMNS FROM puntos_venta` before apply; add migration SQL if absent |
| `PuntosVenta.__init__` signature breaks existing callers | Low | Column is nullable with no default arg — backward-compatible |
| `joinedload` for `lista_precio` missing from route query | Low | Add alongside existing `joinedload(PuntosVenta.sucursal)` |

---

## Rollback Plan

1. Revert ORM change in `models/configs.py` — column remains in DB, app simply ignores it again
2. Revert service + route + template changes — no data loss, `id_lista_precio` values stay in DB
3. BS5 fix is purely cosmetic — revert independently without functional impact

---

## Dependencies

- DB column `puntos_venta.id_lista_precio INTEGER NULL` must exist before deploy (verify or migrate)

---

## Success Criteria

- [ ] POS form shows price list dropdown populated with all `ListasPrecios`
- [ ] Saving a POS record persists the selected `id_lista_precio`
- [ ] Loading an existing POS record pre-selects the correct price list
- [ ] List view shows the assigned price list name
- [ ] No BS4 modal/dismiss patterns remain in `_lst-puntos-ventas.html`
- [ ] No regression on existing POS create/update flow
