# Proposal: Tableros Consolidation

## Intent

Consolidate two separate dashboard systems (`tableros.py` and `dashboard_gerencial.py`) into a single unified blueprint. Currently, tablero logic is split across two route files with zero service overlap, creating confusion about which module handles which dashboard. This refactoring consolidates all dashboard/tablero routes under one blueprint for clarity and maintainability.

## Scope

### In Scope
- Merge all routes from `routes/tableros.py` (5 routes) and `routes/dashboard_gerencial.py` (21 routes) into one blueprint
- Create `templates/tableros/` folder with organized subfolders for each dashboard type
- Update all `render_template` calls to new paths
- Update blueprint registration in `index.py`
- Move `dashboard-gerencial.html` into `templates/tableros/gerencial/`
- Move `tablero.html` and `tablero-basico.html` into `templates/tableros/`
- Update sidebar link for dashboard-gerencial
- Keep `services/dashboard_gerencial.py` separate (no service overlap, no benefit to merging)

### Out of Scope
- Merging service layer (zero overlap, different SQL functions)
- Modifying static JS files (shared with fondos module)
- Changing route URLs or API endpoints
- Refactoring business logic within services
- Updating HTMX API endpoint paths

## Capabilities

### New Capabilities
- `tablero-consolidation`: Unified blueprint managing all 3 dashboard types (gerencial, basico, administrativo) plus plan-vencido

### Modified Capabilities
- None — this is a pure structural refactor, no spec-level behavior changes

## Approach

1. Create `templates/tableros/` folder structure:
   ```
   templates/tableros/
   ├── gerencial/
   │   └── dashboard-gerencial.html (moved from templates/)
   ├── basico.html (moved from templates/)
   ├── gerencial.html (moved from templates/tablero.html)
   ├── administrativo.html (reuse gerencial.html with different data)
   └── plan-vencido.html (moved from templates/)
   ```

2. Merge routes into single `routes/tableros.py`:
   - Keep existing `bp_tableros` blueprint name
   - Add all HTMX API endpoints from `dashboard_gerencial.py`
   - Move `_parsear_filtros()` and `_api_respuesta()` helpers
   - Update all `render_template` calls to new paths
   - Keep all existing route URLs unchanged

3. Update `index.py`:
   - Remove `bp_dashboard_gerencial` import and registration
   - Keep only `bp_tableros` registration

4. Update sidebar link for dashboard-gerencial to use `url_for('tableros.dashboard_gerencial')`

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `routes/tableros.py` | Modified | Merge 21 HTMX endpoints + helpers from dashboard_gerencial.py |
| `routes/dashboard_gerencial.py` | Removed | Deleted after merge |
| `templates/tableros/` | New | Organized template folder structure |
| `templates/dashboard-gerencial.html` | Moved | → `templates/tableros/gerencial/dashboard-gerencial.html` |
| `templates/tablero.html` | Moved | → `templates/tableros/gerencial.html` |
| `templates/tablero-basico.html` | Moved | → `templates/tableros/basico.html` |
| `templates/plan-vencido.html` | Moved | → `templates/tableros/plan-vencido.html` |
| `index.py` | Modified | Remove dashboard_gerencial blueprint registration |
| `templates/partials/_sidebar.html` | Modified | Update dashboard-gerencial link |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Broken template paths | Low | Update all render_template calls; test each route |
| URL conflicts | Low | Keep all existing route URLs unchanged |
| Static JS dependency (fondos) | None | JS files stay in `static/js/demo/`, not moved |
| Service import errors | Low | Keep services/dashboard_gerencial.py separate |
| Sidebar link breakage | Low | Update href to use url_for with correct blueprint |

## Rollback Plan

1. Restore `routes/dashboard_gerencial.py` from git
2. Restore original `routes/tableros.py` from git
3. Restore `templates/dashboard-gerencial.html`, `tablero.html`, `tablero-basico.html`, `plan-vencido.html` from git
4. Restore `index.py` blueprint registration from git
5. Restore sidebar link from git
6. Delete `templates/tableros/` folder

All changes are file-level; git checkout restores everything.

## Dependencies

- None — pure structural refactor

## Success Criteria

- [ ] All 26 routes (5 tableros + 21 dashboard) accessible via same URLs
- [ ] All HTMX API endpoints functional
- [ ] No template rendering errors
- [ ] Sidebar link to dashboard-gerencial works
- [ ] Static JS files (chart-pie-demo.js, chart-bar-demo.js) still accessible by fondos module
- [ ] `url_for('tableros.dashboard_gerencial')` resolves correctly
- [ ] `url_for('tableros.tablero_inicial')` resolves correctly
