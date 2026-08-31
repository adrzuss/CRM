# Apply Progress: Rubro-Sucursal Comparison

## Status
**Phase**: Implementation Complete
**Date**: 2026-08-30

## Completed Tasks

### Phase 1: Backend Service
- [x] 1.1 Added `get_rubro_sucursal_comparacion(desde, hasta, id_sucursal=None)` to `services/dashboard_gerencial.py`
  - SQL query with GROUP BY rubro+sucursal using same JOIN pattern as `get_ventas_rubro`
  - Python pivot into cross-tab dict with `rubros`, `sucursales`, `cells`, `benchmarks`, `grand_total`
  - try-except-rollback returning empty structure on error
- [x] 1.2 Extended `get_datos_dashboard()` aggregator with `'rubro_sucursal': get_rubro_sucursal_comparacion(desde, hasta, id_sucursal)`

### Phase 2: Routes
- [x] 2.1 Added import of `get_rubro_sucursal_comparacion` to `routes/dashboard_gerencial.py` import block
- [x] 2.2 Added `GET /api/dashboard-gerencial/rubro-sucursal` endpoint
  - Parse filters via `_parsear_filtros()`
  - Call `_api_respuesta(get_rubro_sucursal_comparacion, desde, hasta, id_sucursal)`

### Phase 3: Template
- [x] 3.1 Added full-width "Comparación Rubro × Sucursal" section to `templates/dashboard-gerencial.html`
  - Card-header with `fa-table-cells` icon
  - `table-responsive` wrapper for horizontal scroll
  - Cross-tab table iterating `data.rubro_sucursal.rubros` as rows and `data.rubro_sucursal.sucursales` as columns
  - Each cell shows units + percentage
  - Indicator column with ↑/↓/— arrows
  - Indicator column hidden when `sucursales|length == 1`
  - Empty state when no data
- [x] 3.2 Added nav link `<a href="#seccion-rubro-sucursal" class="nav-seccion">` to floating nav menu

### Phase 4: CSS
- [x] 4.1 Added indicator arrow styles to `static/css/dashboard-gerencial.css`
  - `.indicator-up`: green (#1cc88a)
  - `.indicator-down`: red (#e74a3b)
  - `.indicator-neutral`: muted (#6c757d)

## Files Changed

| File | Action | What Was Done |
|------|--------|---------------|
| `services/dashboard_gerencial.py` | Modified | Added `get_rubro_sucursal_comparacion()` function (~90 lines); added `rubro_sucursal` key to `get_datos_dashboard()` return dict |
| `routes/dashboard_gerencial.py` | Modified | Added import; added `/api/dashboard-gerencial/rubro-sucursal` endpoint |
| `templates/dashboard-gerencial.html` | Modified | Added cross-tab section (~50 lines Jinja2); added nav link |
| `static/css/dashboard-gerencial.css` | Modified | Added indicator styles (~15 lines) |
| `openspec/changes/rubro-sucursal-comparison/tasks.md` | Modified | Marked tasks 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1 as complete [x] |

## Remaining Tasks

### Phase 5: Verification (Manual)
- [ ] 5.1 Verify cross-tab table renders with correct data — load dashboard, confirm table appears after Sucursales/Rubros, cells show units and percentages.
- [ ] 5.2 Verify indicators show ↑ green when over-indexed, ↓ red when under-indexed.
- [ ] 5.3 Verify indicator column hidden when only 1 sucursal selected (use sucursal filter).
- [ ] 5.4 Verify empty state shown when no rubro data (empty date range).
- [ ] 5.5 Verify existing dashboard sections still render correctly — no regressions.

## Implementation Notes

### Design Compliance
- **SQL Pattern**: Used same JOIN chain as `get_ventas_rubro` (itemsv → facturav → articulos → rubros → sucursales → clientes → tipo_comprobantes → tipo_comp_aplica → tipo_operacion)
- **Pivot Logic**: Python dictionary comprehension after SQL execution (MySQL doesn't support native PIVOT)
- **Indicator Calculation**: Compares `cell_porcentaje` vs `benchmark_porcentaje` (sucursal's overall share)
- **CSP Compliance**: All inline scripts use `{{ g.nonce }}` (no new scripts added)
- **Currency Format**: Monetary values use `Decimal` type and `$ 1.250.450,50` format

### Technical Decisions
- **Single SQL Query**: Groups by (rubro, sucursal) for consistency and performance
- **Python Pivot**: Collects unique rubros/sucursales from result set, builds nested dict structure
- **Benchmark Calculation**: `(sucursal_total / grand_total) * 100` for each sucursal
- **Empty State**: Shows "Sin datos de comparación" with `fa-table-cells` icon when no data

### Code Quality
- Follows existing project conventions (snake_case, Spanish comments, PEP 8)
- Error handling with try-except and SQLAlchemyError
- Returns empty structure on error (graceful degradation)
- No type hints (matches codebase style)

## Status Summary

**8/13 tasks complete** (Phases 1-4: implementation)
**5/13 tasks remaining** (Phase 5: manual verification)

Ready for manual verification by developer.
