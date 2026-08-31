# Tasks: Rubro-Sucursal Comparison

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~175 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Delivery strategy | single-pr |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Backend Service

- [x] 1.1 Add `get_rubro_sucursal_comparacion(desde, hasta, id_sucursal=None)` to `services/dashboard_gerencial.py` — SQL query joining itemsv/facturav/articulos/rubros/sucursales with GROUP BY rubro+sucursal; Python pivot into cross-tab dict with `rubros`, `sucursales`, `cells`, `benchmarks`, `grand_total`; try-except-rollback returning empty structure on error. Follow `get_ventas_rubro` JOIN pattern.
- [x] 1.2 Extend `get_datos_dashboard()` aggregator (line ~1396) — add `'rubro_sucursal': get_rubro_sucursal_comparacion(desde, hasta, id_sucursal)` to the returned dict.

## Phase 2: Routes

- [x] 2.1 Add import of `get_rubro_sucursal_comparacion` to `routes/dashboard_gerencial.py` import block (line ~11).
- [x] 2.2 Add `GET /api/dashboard-gerencial/rubro-sucursal` endpoint — parse filters via `_parsear_filtros()`, call `_api_respuesta(get_rubro_sucursal_comparacion, desde, hasta, id_sucursal)`.

## Phase 3: Template

- [x] 3.1 Add full-width "Comparación Rubro × Sucursal" section to `templates/dashboard-gerencial.html` after line 313 (closing `</div>` of Sucursales/Rubros row), before Top Productos section (line 315). Include: card-header with `fa-table-cells` icon, `table-responsive` wrapper, cross-tab `<table>` iterating `data.rubro_sucursal.rubros` as rows and `data.rubro_sucursal.sucursales` as columns. Each cell: units + percentage + indicator arrow (↑/↓/—). Hide indicator column when `sucursal_count == 1`. Empty state when no data.
- [x] 3.2 Add nav link `<a href="#seccion-rubro-sucursal" class="nav-seccion">` to the floating nav menu (line ~1348).

## Phase 4: CSS

- [x] 4.1 Add indicator arrow styles to `static/css/dashboard-gerencial.css`: `.indicator-up` (green, text-success), `.indicator-down` (red, text-danger), `.indicator-neutral` (muted). Use existing badge pattern.

## Phase 5: Verification

- [ ] 5.1 Verify cross-tab table renders with correct data — load dashboard, confirm table appears after Sucursales/Rubros, cells show units and percentages.
- [ ] 5.2 Verify indicators show ↑ green when over-indexed, ↓ red when under-indexed.
- [ ] 5.3 Verify indicator column hidden when only 1 sucursal selected (use sucursal filter).
- [ ] 5.4 Verify empty state shown when no rubro data (empty date range).
- [ ] 5.5 Verify existing dashboard sections still render correctly — no regressions.
