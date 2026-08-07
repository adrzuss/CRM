# Proposal: fix-articulos-listado

## Intent

Fix 6 confirmed bugs in the articles listing that cause: silent data filtering (only rubro/marca id=1 visible when no filter is selected), potential `IndexError` crashes on sort, a non-functional sort-disable flag, broken Spanish translation, an incorrect article counter, and a `BASE_URL` reference without fallback.

## Scope

### In Scope
- Fix JOIN filter logic in `get_listado_articulos()` so no-filter shows all records
- Guard against `IndexError` when `order_column` references Imagen (col 8) or Acciones (col 9)
- Fix typo `ordereable` → `orderable: false` on Acciones column
- Remove duplicate `language` key (keep inline Spanish, drop CDN URL)
- Fix counter to use `tabla.page.info().recordsTotal` instead of `tabla.data().count()`
- Define `BASE_URL` fallback in template or confirm it is injected

### Out of Scope
- Refactoring the query builder to a repository pattern
- Adding new columns, filters, or features to the listing
- Changes to `get_listado_stock` or `get_listado_stock_faltantes`

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- None

## Approach

Pure bugfix pass — no architectural changes:

1. **Backend** (`services/articulos/reportes.py` line 38–40): Replace inline ternary in JOIN condition with explicit `.filter()` calls. When `idrubro`/`idmarca` is falsy, omit the filter clause entirely — do not embed it in the JOIN `ON`.
2. **Backend** (line 22): `columns` array has 8 entries; table has 10 cols. Columns index 8 (Imagen) and 9 (Acciones) have no DB mapping. Guard already exists (`if order_column < len(columns) else 'codigo'`) — verify it covers the full range (0-based index 8/9 are both ≥ 8, so guard is correct but columns mapping should be explicit).
3. **Frontend** (`articulos.html` line 169): Fix typo `ordereable` → `orderable`.
4. **Frontend** (lines 183–206): Remove the first `language` block (CDN URL, line 183–185) — keep the second inline Spanish block (lines 195–206).
5. **Frontend** (line 211): Replace `tabla.data().count()` with `tabla.page.info().recordsTotal`.
6. **Frontend** (line 160/176): Add `const BASE_URL = "{{ url_for('index') | replace('/index', '') }}";` or use Flask's `request.host_url` injected via a template variable — confirm scope and define before DataTable init.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/articulos/reportes.py` L38–40 | Modified | Fix JOIN filter — move rubro/marca conditions to `.filter()` |
| `services/articulos/reportes.py` L21–22 | Modified | Verify column index guard covers cols 8 & 9 |
| `templates/articulos/articulos.html` L169 | Modified | Fix `ordereable` typo |
| `templates/articulos/articulos.html` L183–185 | Modified | Remove duplicate `language` key (CDN URL) |
| `templates/articulos/articulos.html` L211 | Modified | Fix counter to use `recordsTotal` |
| `templates/articulos/articulos.html` L127 | Modified | Define `BASE_URL` before DataTable init |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| JOIN refactor changes result set (adds/excludes rows) | Low | Test with rubro=None, marca=None; compare row count to DB total |
| Removing CDN `language` key breaks translation | Low | Inline Spanish block already covers all needed keys |
| `BASE_URL` definition approach differs per deployment | Med | Use `{{ request.host_url }}` stripped of trailing slash via Jinja filter |

## Rollback Plan

All changes are in 2 files with no schema or migration dependency. Git revert of the commit is sufficient. No DB changes involved.

## Dependencies

- None

## Success Criteria

- [ ] Loading the article list with no rubro/marca selected returns ALL articles (not just id=1)
- [ ] Clicking "Imagen" or "Acciones" column header to sort does not return HTTP 500
- [ ] DataTables renders column headers in Spanish
- [ ] Counter badge shows total records matching current filter, not just current page
- [ ] Delete button URL resolves correctly in all deployment environments
