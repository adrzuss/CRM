# Archive Report: Dashboard Gerencial — Etapa 4: Créditos

**Change Name**: dashboard-gerencial-stage4  
**Date**: 2026-08-29  
**Status**: COMPLETE  

---

## Summary

Extended the gerencial dashboard with a new "Créditos" section providing credit portfolio analysis. Implemented 4 KPI cards (active credits, overdue credits, total portfolio amount, delinquency rate) and a top debtors table ranked by outstanding balance. Two new HTMX endpoints serve the data, and the section is positioned after "Cuentas por Pagar" / "Top Proveedores".

## What Was Implemented

### Service Layer (`services/dashboard_gerencial.py`)
- **`get_creditos_kpis(id_sucursal=None)`**: Computes 4 metrics from credit, installment, and payment tables
- **`get_creditos_top_deudores(limite=10, id_sucursal=None)`**: Returns top N clients ranked by outstanding balance
- **Wire-up in `get_datos_dashboard()`**: Added `creditos_kpis` and `creditos_top_deudores` to aggregator return dict

### Routes (`routes/dashboard_gerencial.py`)
- **`GET /api/dashboard-gerencial/creditos-kpis`**: HTMX endpoint for credit KPIs
- **`GET /api/dashboard-gerencial/creditos-top`**: HTMX endpoint for top debtors
- Added imports for new service functions

### Template (`templates/dashboard-gerencial.html`)
- Added "Créditos" section after "Top Proveedores" with:
  - 4 KPI cards: Créditos Activos, Créditos Vencidos, Monto Cartera, % Morosidad
  - Top Deudores por Crédito table
  - Fallback for empty data: "No hay datos de créditos disponibles"

### CSS (`static/css/dashboard-gerencial.css`)
- Added `.badge-creditos-vigente` (green #1cc88a)
- Added `.badge-creditos-vencido` (red #e74a3b)

## Files Modified

| File | Changes |
|------|---------|
| `services/dashboard_gerencial.py` | +2 functions, wire-up in aggregator |
| `routes/dashboard_gerencial.py` | +2 imports, +2 endpoints |
| `templates/dashboard-gerencial.html` | +1 HTML section (~120 lines) |
| `static/css/dashboard-gerencial.css` | +2 badge styles (~12 lines) |

## Issues Found and Fixed

### Issues Found During Implementation
None critical. The implementation followed the design specification closely.

### Documentation Issues (Non-blocking)
1. **Spec table name mismatch**: `spec.md` referenced `pagos_credito` (no 's') but actual table is `pagos_creditos` (with 's')
2. **Spec API key mismatch**: `spec.md` example used `"morosidad"` but implementation returns `"porcentaje_morosidad"`
3. **Spec extra columns**: `spec.md` top deudores example showed extra columns not in implementation (Plan, Cuotas, Vencidas, Próx. Vto)

### Pre-existing Issues (Unrelated)
- 7 test failures in `tests/test_redondeo.py` and `tests/test_services_articulos.py` (Decimal/float mixing)

## Verification Verdict

**PASS** — 14/14 spec scenarios compliant

All requirements implemented correctly:
- KPIs compute correctly using direct SQL queries
- State filtering by name (not hardcoded IDs)
- Multi-sucursal filter works via `idsucursal`
- Decimal precision maintained for monetary values
- Empty data fallbacks display appropriate messages
- No existing Stage 1+2+3 functionality broken

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| `dashboard-gerencial-creditos` | Created | New spec for credit portfolio analysis |
| `dashboard-gerencial-stage1` | Updated | Added F17 (aggregator), updated API spec and UI spec with creditos sections |

## Archive Contents

- ✅ proposal.md
- ✅ exploration.md  
- ✅ specs/ (2 delta specs)
- ✅ design.md
- ✅ tasks.md (8/8 tasks complete)
- ✅ verify-report.md
- ✅ archive-report.md

## Lessons Learned

1. **Direct SQL over stored procedures**: Using direct SQL queries gave full control over credit status filtering and saldo calculation, avoiding dependencies on undocumented SPs.
2. **Name-based state filtering**: Filtering by `estados_creditos.nombre` instead of hardcoded IDs makes the solution robust across installations with different state configurations.
3. **Saldo calculation**: The absence of a `saldo` field in the `creditos` table required careful aggregation of vencimientos and pagos tables using LEFT JOIN with GROUP BY.
4. **Section positioning**: Placing creditos after cta_cte/pagar maintains logical grouping: general AR first, then installment-specific analysis.

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived.
Ready for the next change.