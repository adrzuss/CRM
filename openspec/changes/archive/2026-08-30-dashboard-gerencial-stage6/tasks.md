# Tasks: Dashboard Gerencial — Etapa 6 (Alertas + Drill-Down + UX)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~575 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Medium

> Budget is 800 lines for this project. 575 estimated is within budget.
> Single PR delivery. No chained PRs required.

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | All changes (service + route + template + JS + CSS + verify) | PR 1 | Single PR, all phases |

## Phase 1: Backend Service

- [x] 1.1 Add `get_alertas_gerenciales(stock_kpis, creditos_kpis, cta_cobrar_kpis, bancos_detalle)` in `services/dashboard_gerencial.py` — evaluates thresholds, returns list of alert dicts with `{tipo, titulo, mensaje, severidad, icono, seccion_target, drill_down_url, detalle_raw}`
- [x] 1.2 Extend `get_datos_dashboard()` in `services/dashboard_gerencial.py` — add `'alertas': get_alertas_gerenciales(...)` using the sub-dicts already returned by the existing function calls (no new queries)

## Phase 2: Routes

- [x] 2.1 Add import of `get_alertas_gerenciales` in `routes/dashboard_gerencial.py` (from `services.dashboard_gerencial`)
- [x] 2.2 Add endpoint `GET /api/dashboard-gerencial/alertas` in `routes/dashboard_gerencial.py` — calls `_parsear_filtros()`, calls the 4 KPI functions, passes results to `get_alertas_gerenciales()`, returns `jsonify({'success': True, 'data': alertas})`

## Phase 3: Template

- [x] 3.1 Add `#seccion-alertas` block after filters in `templates/dashboard-gerencial.html` — loop over `data.alertas`, render Bootstrap alert cards with icon + title + message, hide when `data.alertas` is empty (`{% if data.alertas %}`)
- [x] 3.2 Add `data-target="seccion-XXX"` and class `drill-down` to each KPI card container in `templates/dashboard-gerencial.html` (4 cards in `#seccion-kpis`, stock/cta/creditos/bancos KPIs)
- [x] 3.3 Add `data-bs-toggle="tooltip" data-bs-placement="top" title="..."` to KPI label divs in `templates/dashboard-gerencial.html` — tooltips for Ventas Totales, Cobranzas, Margen Bruto, Ticket Promedio, Sin Stock, Bajo Mínimo, Saldo Vencido, Morosidad %, Saldo Bancos
- [x] 3.4 Replace generic `{% else %}` empty-state text in tables with contextual empty-state blocks (icon `fa-3x text-gray-300` + title + description) in `templates/dashboard-gerencial.html` — prioritize: evolución, sucursales, rubros, top productos, top vendedores, sin movimiento, cta cobrar top, cta pagar top, creditos top, bancos detalle, caja rendiciones
- [x] 3.5 Add `#nav-secciones` floating navigation bar at the end of `templates/dashboard-gerencial.html` — links to each `#seccion-xxx` with `class="nav-seccion"` and `href="#seccion-xxx"`, hamburger toggle on mobile

## Phase 4: JavaScript

- [x] 4.1 Add drill-down click handler in `static/js/dashboard-gerencial.js` — delegate event on `.drill-down` elements, `scrollIntoView({ behavior: 'smooth', block: 'start' })` to `data-target`
- [x] 4.2 Add doughnut chart `onClick` handler in `static/js/dashboard-gerencial.js` — extract `activeElements[0].index`, identify rubro label, highlight matching row in `#seccion-rubros` table (add/remove `.table-active` class + scrollIntoView)
- [x] 4.3 Add line chart `onClick` handler in `static/js/dashboard-gerencial.js` — extract `activeElements[0].index`, show period in a temporary badge near the chart
- [x] 4.4 Add loading state handler in `static/js/dashboard-gerencial.js` — on `htmx:beforeRequest` show `.dg-spinner` overlay in target section; on `htmx:afterRequest` hide it
- [x] 4.5 Add tooltip initialization in `static/js/dashboard-gerencial.js` — `DOMContentLoaded` → `document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(...)` with `typeof bootstrap !== 'undefined'` guard
- [x] 4.6 Add nav-seccion smooth scroll in `static/js/dashboard-gerencial.js` — delegate event on `.nav-seccion`, `e.preventDefault()`, scroll to `href` target

## Phase 5: CSS

- [x] 5.1 Add `.dg-alerta-*` styles in `static/css/dashboard-gerencial.css` — alert container, alert cards with left border color per severity (danger/warning/info), icon sizing, responsive flex-wrap
- [x] 5.2 Add `.dg-spinner` loading overlay styles in `static/css/dashboard-gerencial.css` — absolute positioned overlay with spinner animation, z-index above card content
- [x] 5.3 Add `.empty-state-dg` styles in `static/css/dashboard-gerencial.css` — centered layout, large icon, muted text, padding
- [x] 5.4 Add `.drill-down` cursor-pointer style and `.nav-secciones` floating nav styles in `static/css/dashboard-gerencial.css` — sticky bottom-right, hamburger on mobile, scroll-spy active state
- [x] 5.5 Add responsive rules in `static/css/dashboard-gerencial.css` — `@media (max-width: 767.98px)`: alertas stacked column, nav-secciones as offcanvas/hamburger, KPI cards 2-column, hide rubro participation bar on mobile

## Phase 6: Verification

- [ ] 6.1 Verify alertas panel: load dashboard with data that triggers each alert type (stock bajo, sin stock, creditos vencidos, cta vencida, banco negativo); confirm alert cards appear; confirm 0 alertas hides the panel
- [ ] 6.2 Verify alertas API: `GET /api/dashboard-gerencial/alertas` returns JSON with correct structure and matching alert types
- [ ] 6.3 Verify drill-down on KPIs: click each KPI card, confirm smooth scroll to the corresponding section
- [ ] 6.4 Verify doughnut drill-down: click a segment, confirm table row highlights and scrolls into view
- [ ] 6.5 Verify loading states: trigger an HTMX request, confirm spinner appears then disappears
- [ ] 6.6 Verify tooltips: hover over KPI labels, confirm tooltip text appears
- [ ] 6.7 Verify empty states: filter to a period with no data, confirm contextual empty state renders (icon + text)
- [ ] 6.8 Verify navigation: click nav-seccion links, confirm scroll to correct section
- [ ] 6.9 Verify responsive: test at 320px, 768px, 1024px, 1440px widths
- [ ] 6.10 Verify Stages 1-5 regression: all existing KPIs, charts, tables, and fetch updates still work unchanged
