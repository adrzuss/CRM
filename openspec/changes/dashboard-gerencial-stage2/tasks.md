# Tasks: Dashboard Gerencial — Etapa 2 (Stock)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~410 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Medium

> Estimated ~410 changed lines across 5 files. Close to budget but no test files
> (no runner). Each task is small and completable in one session. Single PR is
> safe with size:exception. Orchestrator must confirm before sdd-apply.

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Backend service + routes + template + JS/CSS | PR 1 | All 5 files modified; tight coupling between service→route→template. Splitting adds coordination overhead with no real benefit. |

## Phase 1: Backend Service (~165 lines)

- [x] 1.1 Add `get_stock_kpis(id_sucursal=None)` to `services/dashboard_gerencial.py` — Query `stocks` + `articulos` with CASE WHEN classification using `deseable` as minimum threshold. Return dict: sin_stock, bajo_minimo, saludable, exceso, total_articulos, valor_total_stock + raw. Reuse `_formato_moneda()` and `_sucursal_filter(alias='s')`. Handle `deseable=NULL/0` and `maximo=NULL/0` edge cases. (~55 lines)
- [x] 1.2 Add `get_stock_sucursal(id_sucursal=None)` to same file — Query with GROUP BY `stocks.idsucursal`, JOIN `sucursales`, `articulos` for units, estimated value (`actual * costo_total`), sin_stock, bajo_minimo counts. Return list of dicts. Filter `costo_total=0` → "N/D" in valor display. (~55 lines)
- [x] 1.3 Add `get_productos_sin_movimiento(id_sucursal=None, dias=30)` to same file — Query with LEFT JOIN `itemsv` + `facturav` for last sale date. HAVING `ultima_venta IS NULL OR < threshold`. LIMIT 100. Return dict with productos list + total + tiene_mas flag. Format ultima_venta as "Sin ventas" when NULL. (~55 lines)

## Phase 2: Routes (~60 lines)

- [x] 2.1 Add imports of 3 new functions to `routes/dashboard_gerencial.py` (add to existing import block from `services.dashboard_gerencial`) (~3 lines)
- [x] 2.2 Add 3 HTMX endpoints: `GET /api/dashboard-gerencial/stock-kpis`, `GET /api/dashboard-gerencial/stock-sucursales`, `GET /api/dashboard-gerencial/stock-sin-movimiento`. Parse `id_sucursal` and `dias` params. Use `_api_respuesta()` wrapper. (~45 lines)
- [x] 2.3 Update `get_datos_dashboard()` in `services/dashboard_gerencial.py` to include 3 new sections: `stock_kpis`, `stock_sucursal`, `productos_sin_movimiento` in returned dict (~8 lines)

## Phase 3: Template (~130 lines)

- [x] 3.1 Add **SECCIÓN: Resumen de Stock** after Top Vendedores — 4 KPI cards (sin_stock=danger, bajo_minimo=warning, saludable=success, exceso=info) showing count + valor_total_stock. Use same card-kpi pattern as Stage 1. (~45 lines)
- [x] 3.2 Add **SECCIÓN: Stock por Sucursal** — Table with columns: Sucursal, Unidades, Valor Estimado, Sin Stock, Bajo Mínimo. Badges for sin_stock (danger) and bajo_minimo (warning). Iterate `data.stock_sucursal`. (~40 lines)
- [x] 3.3 Add **SECCIÓN: Productos sin Movimiento** — Toggle buttons (30/60/90 días), table with columns: Código, Producto, Rubro, Stock Actual, Última Venta. HTMX lazy-load on toggle. Show "Sin ventas" when ultima_venta is null. Show truncation indicator if tiene_mas. (~45 lines)

## Phase 4: JS + CSS (~55 lines)

- [x] 4.1 Add stock section init to `inicializarDashboard()` in `static/js/dashboard-gerencial.js` — No new charts needed (only tables). Add event listener for `.dias-btn` toggle: fetch `/api/dashboard-gerencial/stock-sin-movimiento?dias=X` and re-render table body. (~35 lines)
- [x] 4.2 Add stock badge styles to `static/css/dashboard-gerencial.css`: `.badge-stock-sin-stock` (danger), `.badge-stock-bajo-minimo` (warning), `.badge-stock-saludable` (success), `.badge-stock-exceso` (info), `.btn-dias-activo` (active toggle). (~20 lines)

## Phase 5: Verification (~0 lines, manual)

- [x] 5.1 Verify stock KPIs display: load dashboard, confirm 4 cards show correct counts and formatted value. Test with sucursal filter.
- [x] 5.2 Verify stock por sucursal table: confirm rows match expected sucursales, valor estimated shows "N/D" for costo=0 items.
- [x] 5.3 Verify sin movimiento toggle: click 30/60/90 days, confirm table updates via HTMX, check "Sin ventas" label for never-sold products.
- [x] 5.4 Verify Stage 1 regression: KPIs, evolución chart, sucursales table, rubros chart, top productos, top vendedores all still render correctly.

## Relevant Files

| File | Action | Lines est. |
|------|--------|-----------|
| `services/dashboard_gerencial.py` | Modify (3 funcs + update aggregator) | +173 |
| `routes/dashboard_gerencial.py` | Modify (3 endpoints + imports) | +48 |
| `templates/dashboard-gerencial.html` | Modify (3 HTML sections) | +130 |
| `static/js/dashboard-gerencial.js` | Modify (toggle listener) | +35 |
| `static/css/dashboard-gerencial.css` | Modify (badge styles) | +20 |
| **Total** | | **~406** |
