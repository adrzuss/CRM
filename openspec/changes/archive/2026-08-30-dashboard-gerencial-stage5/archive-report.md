# Archive Report: Dashboard Gerencial — Etapa 5 (Bancos / Caja)

**Change**: dashboard-gerencial-stage5
**Archived**: 2026-08-30
**Status**: COMPLETE

---

## Summary

Extended the Dashboard Gerencial with two new financial visibility sections: **Bancos** (bank balances, movements, income vs expenses) and **Caja** (cash register closings). Added 4 new service functions, 4 HTMX endpoints, 2 HTML sections, CSS badge styles, and JS initialization. No new files created — all changes are modifications to 5 existing files.

---

## Files Modified

| File | Action | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modified | Added 4 functions: `get_bancos_kpis`, `get_bancos_detalle`, `get_caja_kpis`, `get_caja_rendiciones_recientes`. Updated `get_datos_dashboard` aggregator with 4 new keys. |
| `routes/dashboard_gerencial.py` | Modified | Added 4 imports + 4 HTMX endpoints (`bancos-kpis`, `bancos-detalle`, `caja-kpis`, `caja-rendiciones`). |
| `templates/dashboard-gerencial.html` | Modified | Added 2 sections (Bancos + Caja) after Créditos section with KPI cards and tables. |
| `static/js/dashboard-gerencial.js` | Modified | Added `inicializarBancosCaja()` placeholder called from `inicializarDashboard()`. |
| `static/css/dashboard-gerencial.css` | Modified | Added 4 badge classes: `badge-bancos-ingreso`, `badge-bancos-egreso`, `badge-bancos-saldo-positivo`, `badge-bancos-saldo-negativo`. |

---

## Issues Found and Fixed

### Warnings (no critical issues)

1. **Spec ambiguity: `get_bancos_detalle` saldo date-filter** — The spec note says "Saldo es acumulado (sin filtro de fecha en JOIN de bancos_propios)" but the spec SQL includes `bp.fecha_emision BETWEEN :desde AND :hasta` in the LEFT JOIN. The implementation follows the spec SQL (with date filter), meaning saldo per bank reflects only movements within the selected period. The `get_bancos_kpis` saldo_total IS correctly historical. This creates an inconsistency. **Recommendation**: Decide on one behavior (historical vs filtered) and make both functions consistent.

2. **Spec typo: tipo_operacion 'I'/'E' vs actual 'C'/'D'** — The spec uses `'I'` (Ingreso) and `'E'` (Egreso) but the actual `tipo_mov_bancos.tipo_operacion` column uses `'C'` (Credit) and `'D'` (Debit). The implementation correctly uses `'C'`/`'D'` matching the real database. The spec should be updated to avoid confusion.

### Suggestions

1. **No unit tests for Stage 5 functions** — The 4 new service functions have no unit tests. Consider adding mock-based tests.
2. **`total_otros_valores` double COALESCE** — In `get_caja_rendiciones_recientes` there's a redundant `COALESCE(COALESCE(...))`. Harmless but worth cleaning.
3. **Rendiciones date filter not in spec** — The spec F27 parameters list only `limite` and `id_sucursal`, but the implementation adds `desde`/`hasta` date filtering. This is a reasonable deviation but should be documented.

---

## Verification Verdict

**PASS WITH WARNINGS**

- 20/20 spec scenarios compliant
- All 9 phases (14 sub-tasks) complete
- 74 tests passing (7 pre-existing failures unrelated to Stage 5)
- Stages 1-4 not broken
- No CRITICAL issues found

---

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| `dashboard-gerencial-stage1` | Updated | Added F28 (aggregator), F29 (sección Bancos), F30 (sección Caja), NF17-NF21, 4 new API endpoints, edge cases, layout order |
| `bancos-dashboard` | Created | F24 (KPIs Bancos), F25 (Tabla Bancos por Banco), edge cases |
| `caja-dashboard` | Created | F26 (KPIs Caja), F27 (Rendiciones Recientes), edge cases |

---

## Lessons Learned

1. **Database schema reality vs spec assumptions**: The exploration phase correctly identified that `tipo_operacion` uses 'C'/'D' (Credit/Debit), not 'I'/'E' (Ingreso/Egreso). The implementation matches the real schema.
2. **Bancos have no `idsucursal`**: This is a schema limitation, not a design choice. Bancos queries are global by necessity.
3. **Caja = rendiciones, not movimientos**: There's no dedicated caja or movimientos_caja table. The "Caja" section uses `rendiciones_caja` (end-of-day closings) as the closest available data.
4. **Saldo calculation**: Bank balance is computed from all historical movements (`SUM(CASE WHEN tipo_operacion='C' THEN monto ELSE -monto END)`), not a stored field. This is accurate but should be documented for maintainers.

---

## Archive Contents

- proposal.md ✅
- design.md ✅
- tasks.md ✅ (14/14 tasks complete)
- verify-report.md ✅
- exploration.md ✅
- specs/bancos-dashboard/spec.md ✅
- specs/caja-dashboard/spec.md ✅
- specs/dashboard-gerencial-stage1/spec.md ✅

---

## Source of Truth Updated

The following specs now reflect the new behavior:
- `openspec/specs/dashboard-gerencial-stage1/spec.md` — Updated with F28-F30, NF17-NF21, new API endpoints
- `openspec/specs/bancos-dashboard/spec.md` — New spec (F24-F25)
- `openspec/specs/caja-dashboard/spec.md` — New spec (F26-F27)

---

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived.
Ready for the next change.
