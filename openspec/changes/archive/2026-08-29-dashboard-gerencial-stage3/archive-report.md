# Archive Report: Dashboard Gerencial ERP — Etapa 3 (Cuentas por Cobrar / Por Pagar)

**Change**: dashboard-gerencial-stage3
**Archived**: 2026-08-29
**Final Status**: COMPLETE

## Summary

Extended the existing gerencial dashboard (Stages 1+2) with sections for accounts receivable and accounts payable. Added KPI cards for saldo total, vencido, por vencer, and ranking tables for top debtors and top suppliers. Implemented 4 new service functions, 4 HTMX endpoints, and 6 new template sections. Used `MAX(fecha)` per entity for aging classification (no contractual due date field). Configurable `dias_vto_cta_cte` from configuration table (default 30 days).

## Files Modified

| File | Action | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modified | Added `get_cta_cobrar_kpis`, `get_cta_cobrar_top`, `get_cta_pagar_kpis`, `get_cta_pagar_top`. Updated `get_datos_dashboard()` aggregator. |
| `routes/dashboard_gerencial.py` | Modified | Added 4 HTMX endpoints: `/api/dashboard-gerencial/cta-cobrar-kpis`, `/cta-cobrar-top`, `/cta-pagar-kpis`, `/cta-pagar-top`. Added imports. |
| `templates/dashboard-gerencial.html` | Modified | Added 6 new HTML sections after "Productos sin Movimiento": 4 KPI cards + 2 tables. |
| `static/js/dashboard-gerencial.js` | Modified | Added placeholder `inicializarCtaCte()` function. |
| `static/css/dashboard-gerencial.css` | Modified | Added badge styles `.badge-cta-vencido` and `.badge-cta-por-vencer`. |

## Issues Found and Fixed

**CRITICAL**: None
**WARNING**: None
**SUGGESTIONS** (from verification report):
1. No `spec.md` existed in the change directory (only design.md + exploration.md) — now merged into main specs.
2. No dashboard-specific tests for the 4 new service functions or endpoints.
3. `inicializarCtaCte()` placeholder does nothing; consider removing or implementing if HTMX live refresh is planned.

## Verification Verdict

**PASS** — All 20 verification checklist items compliant. Implementation matches design decisions. SQL queries reference valid tables/columns confirmed by ORM models. Templates handle empty data gracefully. HTMX endpoints return correct JSON structure. No functional, correctness, or coherence issues found.

## Lessons Learned

1. **Approximation of vencimiento**: Using `MAX(fecha)` per entity as proxy for due date is consistent with existing stored procedures but not contractual due date. UI labels clarify "Saldo > N días".
2. **Configuration bug**: Existing stored procedures fetch `dias_vto_cta_cte` but hardcode `INTERVAL 30 DAY`. The dashboard correctly reads and uses the configuration value.
3. **No sucursal filter**: `cta_cte` tables lack `idsucursal`; filtering through invoice joins is unreliable. Dashboard shows consolidated data across all branches.
4. **Decimal handling**: All monetary calculations wrapped in `Decimal(str(...))` to avoid floating-point errors.
5. **Empty data handling**: All widgets gracefully show "No disponible" or "No hay..." messages when no data exists.

## Archive Contents

- proposal.md ✅
- specs/ ✅ (3 domains: cta-cobrar, cta-pagar, dashboard-gerencial-stage1)
- design.md ✅
- tasks.md ✅ (16/16 tasks complete)
- verify-report.md ✅
- exploration.md ✅

## Source of Truth Updated

The following specs now reflect the new behavior:
- `openspec/specs/cta-cobrar/spec.md` (new)
- `openspec/specs/cta-pagar/spec.md` (new)
- `openspec/specs/dashboard-gerencial-stage1/spec.md` (updated with F18-F21, NF12-NF16, extended API/UI specs)

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived.
Ready for the next change.