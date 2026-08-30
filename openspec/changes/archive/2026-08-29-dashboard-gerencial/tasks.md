# Tasks: Dashboard Gerencial ERP — Etapa 1

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~780 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Delivery strategy | single-pr |
| Suggested split | PR 1: Backend (service + route + blueprint registration) ~380 lines; PR 2: Frontend (template + JS + CSS + sidebar) ~400 lines |
| Decision needed before apply | Yes |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Backend: service layer + route + blueprint registration | PR 1 | base: main; ~380 lines; no template dependency |
| 2 | Frontend: template + JS + CSS + sidebar link | PR 2 | base: PR 1 branch; ~400 lines; depends on PR 1 endpoints |

## Phase 1: Backend Service Layer

- [ ] 1.1 Create `services/dashboard_gerencial.py` with `get_kpis()` — query ventas + cobranzas + margen + ticket promedio, period comparison logic (~70 lines)
- [ ] 1.2 Add `get_evolucion_ventas()` — daily/weekly/monthly granularity toggle, comparison period overlay (~50 lines)
- [ ] 1.3 Add `get_ventas_sucursal()` — grouped by sucursal with participation % (~35 lines)
- [ ] 1.4 Add `get_ventas_rubro()` — grouped by rubro with units + participation %, NULL rubro → "Sin rubro" (~35 lines)
- [ ] 1.5 Add `get_top_productos()` — top 10 by total_vendido with margen calculation (~35 lines)
- [ ] 1.6 Add `get_top_vendedores()` — top 10 by ventas_totales with participation % (~35 lines)
- [ ] 1.7 Add `get_datos_dashboard()` aggregator calling all 6 functions, returns single dict (~20 lines)

## Phase 2: Route + Blueprint

- [ ] 2.1 Create `routes/dashboard_gerencial.py` with `bp_dashboard_gerencial` — main route `GET /dashboard-gerencial` parsing filters and calling `get_datos_dashboard()` (~40 lines)
- [ ] 2.2 Add 6 JSON API endpoints `/api/dashboard-gerencial/{seccion}` for HTMX refresh (~45 lines)
- [ ] 2.3 Register blueprint in `index.py` — import + `app.register_blueprint(bp_dashboard_gerencial, url_prefix='/')` (~2 lines)

## Phase 3: Frontend Template

- [ ] 3.1 Create `templates/dashboard-gerencial.html` — extends `base.html`, filter bar (desde/hasta/sucursal/comparar), 4 KPI cards in `#seccion-kpis` (~70 lines)
- [ ] 3.2 Add `#seccion-evolucion` with `<canvas id="chartEvolucion">` + granularity toggle buttons (~25 lines)
- [ ] 3.3 Add `#seccion-sucursales` table and `#seccion-rubros` table + `<canvas id="chartRubros">` (~55 lines)
- [ ] 3.4 Add `#seccion-top-productos` and `#seccion-top-vendedores` tables (~50 lines)
- [ ] 3.5 Add inline `<script nonce="{{ g.nonce }}">` with `datosDashboard={{ data|tojson }}` + JS/CSS includes (~15 lines)

## Phase 4: JavaScript

- [ ] 4.1 Create `static/js/dashboard-gerencial.js` — IIFE module, chart instances, `inicializarDashboard()`, `destruirCharts()` (~40 lines)
- [ ] 4.2 Add Chart.js line config for evolución (dual-line overlay) + doughnut config for rubros (~45 lines)
- [ ] 4.3 Add HTMX lifecycle: `htmx:beforeSwap` destroy charts, `htmx:afterSwap` recreate + data parse (~25 lines)
- [ ] 4.4 Add filter binding, date presets (Hoy/Semana/Mes/Trimestre), `formatearMoneda()` helper (~35 lines)

## Phase 5: CSS + Sidebar

- [ ] 5.1 Create `static/css/dashboard-gerencial.css` — `.dashboard-gerencial` namespace, `.card-kpi` styles, chart containers, table styles, `@media print` (~70 lines)
- [ ] 5.2 Add nav link to `templates/partials/_sidebar.html` — new item pointing to `/dashboard-gerencial` (~3 lines)

## Phase 6: Integration & Verification

- [ ] 6.1 Verify route loads without 500 — check `@check_session`, `@alertas_mensajes` decorators, filter defaults
- [ ] 6.2 Verify HTMX refresh — each seccion endpoint returns valid JSON, templates render sections
- [ ] 6.3 Verify edge cases — empty period (all $0, "N/D"), single sucursal hides table, "Sin rubro" grouping
- [ ] 6.4 Verify existing report `/tablero-gerencial` still works (no regressions)
