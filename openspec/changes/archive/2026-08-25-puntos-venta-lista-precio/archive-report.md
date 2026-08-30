# Archive Report: puntos-venta-lista-precio

**Change**: `puntos-venta-lista-precio`
**Archived**: 2026-08-25
**Final Status**: SHIPPED ✅

---

## Change Intent

Add `id_lista_precio` FK column to the `PuntosVenta` ORM model, wire it through the service and route layers, expose a price-list selector in the POS creation/edit form, display the assigned list in the list view, and fix residual BS4 patterns in `_lst-puntos-ventas.html`.

The column reportedly existed in the DB already but was unmapped — silently ignored on every POS save/load.

---

## Scope

### In Scope (delivered)
- `PuntosVenta` ORM: `id_lista_precio` FK nullable + `lista_precio` relationship
- `grabarDatosPtoVta` service: reads and persists `id_lista_precio` (UPDATE + INSERT paths)
- `puntos_venta` route: `joinedload(PuntosVenta.lista_precio)` + `listas_precios` context var
- `_alta-punto-venta.html`: `<select name="id_lista_precio">` with "Sin lista" default and pre-select on edit
- `_lst-puntos-ventas.html`: "Lista de precios" column + BS4 → BS5 fixes (4 patterns)

### Out of Scope
- Branch-scoped filtering of price lists (`listas_precio` has no `idsucursal`)
- DB schema migration (assumed column exists; migration is a prerequisite)
- Full visual redesign

---

## Files Modified (5)

| File | Change |
|------|--------|
| `models/configs.py` | Added `id_lista_precio` FK column + `lista_precio` relationship to `PuntosVenta` |
| `services/configs.py` | `grabarDatosPtoVta`: reads `id_lista_precio` with `or None` coercion; assigns in UPDATE + INSERT paths |
| `routes/configs.py` | Adds `joinedload(PuntosVenta.lista_precio)` to query; adds `listas_precios = ListasPrecios.query.all()` + template kwarg |
| `templates/configuracion/partials/_alta-punto-venta.html` | New `col-md-4` block with price-list `<select>`; resized sucursal col from `col-md-5` → `col-md-3` |
| `templates/configuracion/partials/_lst-puntos-ventas.html` | "Lista de precios" `<th>`/`<td>` with badge; 4× BS5 modal/dismiss fixes |

---

## Key Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | FK `nullable=True`, no default | Existing POS records have no list — `None` is semantically correct and backward-compatible |
| 2 | `joinedload` in route | Avoids N+1 on list view; consistent with existing `joinedload(PuntosVenta.sucursal)` |
| 3 | `__init__` NOT modified | Constructor is positional-heavy; post-init assignment avoids breaking all callers |
| 4 | `form.get(...) or None` coercion | Empty string from form must become `None`, not `0`; matches `pos_printer`/`fac_electronica` pattern |
| 5 | BS5 all-4-patterns fix | Mixed BS4/BS5 causes silent modal failures; replaced `data-dismiss`, `close &times;`, `$(...).modal()`, `$(...).modal('hide')` |

---

## DB Migration Required

The column must exist before deploy. If absent:

```sql
ALTER TABLE puntos_venta
  ADD COLUMN id_lista_precio INT NULL,
  ADD CONSTRAINT fk_pv_lista FOREIGN KEY (id_lista_precio) REFERENCES listas_precio(id);
```

Verify: `SHOW COLUMNS FROM puntos_venta LIKE 'id_lista_precio';`

---

## Warnings (for future reference)

1. **POST path re-fetch without joinedload** (`routes/configs.py:257-258`): After `grabarDatosPtoVta`, the route re-fetches `puntoVenta` via `db.session.get(PuntosVenta, idPuntoVenta)` without `joinedload(PuntosVenta.lista_precio)`. If the template accesses `puntoVenta.lista_precio` post-POST, it triggers a lazy-load (N+1 on single record). Pre-existing pattern — not a regression introduced by this change.

2. **Type coercion not explicit**: `form.get('id_lista_precio') or None` stores a string `"2"` in the column before SQLAlchemy coerces it to `int` on commit. If any code ever reads the form value and compares before commit, `"2" != 2` would fail. Current Jinja comparison (`puntoVenta.id_lista_precio == lista.id`) works on ORM-loaded ints — not a current bug. Hardening: `int(v) if v else None`.

3. **No migration guard**: No startup check for the column's existence. Missing migration will cause a runtime failure on any `puntos_venta` route. Acceptable for this project's style.

---

## Verification Summary

- **CRITICAL issues**: None
- **Spec compliance**: 11/11 scenarios statically compliant
- **Implementation tasks**: 15/15 complete
- **Manual smoke tasks**: 3/3 pending (require DB migration + live app — confirmed PASSED by user)
- **Design decisions followed**: 8/8 without deviation

---

## SDD Cycle

| Phase | Status |
|-------|--------|
| Proposal | ✅ Done |
| Spec | ✅ Done |
| Design | ✅ Done |
| Tasks | ✅ Done (15/15) |
| Apply | ✅ Done |
| Verify | ✅ PASS WITH WARNINGS |
| Archive | ✅ Done |

**Status: SHIPPED**
