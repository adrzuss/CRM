# Tasks: Tableros Consolidation

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~490 (183 added to tableros.py, 311 deleted from dashboard_gerencial.py, ~6 in index.py/sidebar, ~90 template moves) |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Suggested split | Single PR (size:exception) — mechanical refactor, zero logic changes, all changes interdependent |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Full consolidation | PR 1 (size:exception) | All changes are interdependent; splitting would break the app mid-way |

## Phase 1: Templates — Create directory and move files

- [ ] 1.1 Create `templates/tableros/` directory
- [ ] 1.2 Move `templates/tablero.html` → `templates/tableros/tablero.html`
- [ ] 1.3 Move `templates/tablero-basico.html` → `templates/tableros/tablero-basico.html`
- [ ] 1.4 Move `templates/dashboard-gerencial.html` → `templates/tableros/dashboard-gerencial.html`
- [ ] 1.5 Move `templates/plan-vencido.html` → `templates/tableros/plan-vencido.html`

## Phase 2: Routes — Merge dashboard_gerencial.py into tableros.py

- [ ] 2.1 Add missing imports to `routes/tableros.py`: `jsonify`, `session` from flask; `get_sucursales_lista` from `services.reportes`; all 22 functions from `services.dashboard_gerencial`
- [ ] 2.2 Paste `_parsear_filtros()` helper (lines 41-76 of dashboard_gerencial.py) into `routes/tableros.py` after blueprint declaration
- [ ] 2.3 Paste `_api_respuesta()` helper (lines 100-106 of dashboard_gerencial.py) into `routes/tableros.py` after `_parsear_filtros`
- [ ] 2.4 Paste `dashboard_gerencial()` route (lines 80-96) into `routes/tableros.py`, decorated with `@bp_tableros.route('/dashboard-gerencial')`
- [ ] 2.5 Paste all 20 HTMX API endpoints (lines 109-309) into `routes/tableros.py`, changing every `@bp_dashboard_gerencial.route` → `@bp_tableros.route`
- [ ] 2.6 Verify all 26 routes present in consolidated file (5 original + 1 dashboard page + 20 API)

## Phase 3: Wiring — Update index.py and sidebar

- [ ] 3.1 Remove `from routes.dashboard_gerencial import bp_dashboard_gerencial` (line 28) from `index.py`
- [ ] 3.2 Remove `app.register_blueprint(bp_dashboard_gerencial, url_prefix='/')` (line 62) from `index.py`
- [ ] 3.3 Update `templates/partials/_sidebar.html` line 29: change `href="/dashboard-gerencial"` → `href="{{ url_for('tableros.dashboard_gerencial') }}"`

## Phase 4: Cleanup — Delete old file

- [ ] 4.1 Delete `routes/dashboard_gerencial.py`

## Phase 5: Verification

- [ ] 5.1 Start app (`python index.py`) — confirm no import errors or blueprint registration conflicts
- [ ] 5.2 Navigate to `/dashboard-gerencial` — confirm HTTP 200 and template renders
- [ ] 5.3 Navigate to `/tablero-inicial`, `/tablero-gerencial`, `/tablero-administrativo`, `/tablero-basico`, `/plan-vencido` — confirm all HTTP 200
- [ ] 5.4 Hit 3 API endpoints (`/api/dashboard-gerencial/kpis`, `/api/dashboard-gerencial/stock-kpis`, `/api/dashboard-gerencial/alertas`) — confirm JSON responses
- [ ] 5.5 Inspect sidebar HTML — confirm `href` resolves to `/dashboard-gerencial` via `url_for`
- [ ] 5.6 Confirm `services/dashboard_gerencial.py` is untouched
- [ ] 5.7 Confirm `static/js/demo/chart-pie-demo.js` still exists and fondos page loads
