# Proposal: Dashboard Filter Fixes

## Intent

Fix three bugs in the dashboard gerencial filters that prevent sucursal selection from working and make keyboard shortcuts non-functional. Root causes: SQL query excludes active sucursales with `baja = '0000-00-00 00:00:00'`, keyboard shortcuts update dates but don't dispatch form submit, and model `__init__` defaults `baja` to `timedelta(0)` instead of `None`.

## Scope

### In Scope

- Fix `get_sucursales_lista()` SQL to include sucursales where `baja = '0000-00-00 00:00:00'`
- Fix keyboard shortcuts to dispatch form submit after updating dates
- Fix `Sucursales.__init__` to default `baja = None` instead of `timedelta(0)`

### Out of Scope

- JS error detection/diagnosis on page load (needs browser console investigation)
- HTMX-based filter submission (future improvement)
- Loading indicators for full page reloads

## Capabilities

### New Capabilities

None

### Modified Capabilities

- `dashboard-gerencial-stage1` — F1 (Filtros Globales): sucursal dropdown query corrected to handle both `NULL` and zero-date `baja` values

## Approach

Three minimal, targeted fixes to existing files:

1. **`services/reportes.py:667`** — Change SQL from `WHERE baja IS NULL` to `WHERE (baja IS NULL OR baja = '0000-00-00 00:00:00')` so sucursales created via ORM (which sets `baja = timedelta(0)`) are included.

2. **`static/js/dashboard-gerencial.js:636-640`** — Add `form.dispatchEvent(new Event('submit'))` after each `setRangoFechas()` call in the keydown handler so keyboard shortcuts (Alt+H/S/M/T) actually reload the dashboard.

3. **`models/sucursales.py:22`** — Change `self.baja = timedelta(0)` to `self.baja = None` so new sucursales get a proper `NULL` value. Existing rows with zero-date are handled by fix #1.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/reportes.py` | Modified | `get_sucursales_lista()` SQL query — 1 line change |
| `static/js/dashboard-gerencial.js` | Modified | Keydown handler — add submit dispatch after each shortcut |
| `models/sucursales.py` | Modified | `__init__` default for `baja` field |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Existing rows with `baja = '0000-00-00 00:00:00'` still excluded if query is wrong | Low | Fix #1 handles both NULL and zero-date explicitly |
| Model change affects existing code paths that check `baja` | Low | Only `__init__` default changes; existing rows in DB are unaffected |
| Form submit dispatch causes double submission | Low | `dispatchEvent(new Event('submit'))` fires once; form handler does `e.preventDefault()` + redirect |

## Rollback Plan

Revert the three file changes via `git checkout`:
```bash
git checkout -- services/reportes.py static/js/dashboard-gerencial.js models/sucursales.py
```
No database migrations required.

## Dependencies

None

## Success Criteria

- [ ] Sucursal dropdown shows active sucursales (those with `baja = NULL` OR `baja = '0000-00-00 00:00:00'`)
- [ ] Keyboard shortcuts Alt+H/S/M/T update dates AND reload the dashboard
- [ ] Newly created sucursales via ORM have `baja = NULL` in the database
- [ ] No regressions in existing filter behavior (button clicks, HTMX refresh)
