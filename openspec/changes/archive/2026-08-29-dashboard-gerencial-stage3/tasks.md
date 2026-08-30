# Tasks: Dashboard Gerencial — Etapa 3 (Cuentas por Cobrar / Por Pagar)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~385 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Delivery strategy | single-pr |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Stage 3 full implementation | PR 1 | Service + routes + template + JS/CSS. Under 400 lines, single PR acceptable |

## Phase 1: Backend Service (~150 lines)

- [ ] 1.1 Add `get_dias_vto_cta_cte()` helper in `services/dashboard_gerencial.py` — reads `Configuracion.query.get(1).dias_vto_cta_cte`, returns 30 if value is 0. Import `Configuracion` from `models.configs`. (~15 lines)
- [ ] 1.2 Add `get_cta_cobrar_kpis(dias_vto=None)` — subquery groups `cta_cte_cli` by `idcliente`, computes `SUM(debe-haber)` as saldo and `MAX(fecha)` as ultima_fecha. Outer query: saldo_total (saldo>0), saldo_vencido (ultima_fecha < CURDATE() - INTERVAL), saldo_por_vencer, cantidad_deudores. Returns dict with formatted + raw values. (~35 lines)
- [ ] 1.3 Add `get_cta_cobrar_top(limite=10, dias_vto=None)` — JOIN `cta_cte_cli` with `clientes`, GROUP BY id/nombre/documento, HAVING saldo>0, ORDER BY saldo DESC, LIMIT. Returns list of dicts with nombre, documento, saldo formatted, saldo_raw, ultima_fecha. (~30 lines)
- [ ] 1.4 Add `get_cta_pagar_kpis(dias_vto=None)` — mirror of 1.2 using `cta_cte_prov` + `proveedores`. Subquery groups by `idproveedor`. Returns same structure. (~35 lines)
- [ ] 1.5 Add `get_cta_pagar_top(limite=10, dias_vto=None)` — mirror of 1.3 using `cta_cte_prov` + `proveedores`, uses `p.fantasia` (fallback `p.nombre`). (~30 lines)
- [ ] 1.6 Update `get_datos_dashboard()` aggregator — add `cta_cobrar_kpis`, `cta_cobrar_top`, `cta_pagar_kpis`, `cta_pagar_top` keys calling the new functions. (~5 lines)

## Phase 2: Routes (~40 lines)

- [ ] 2.1 Add imports of 4 new functions to `routes/dashboard_gerencial.py`. (~1 line)
- [ ] 2.2 Add `api_cta_cobrar_kpis` endpoint — GET `/api/dashboard-gerencial/cta-cobrar-kpis`, parse optional `dias_vto` param (default from config), call `get_cta_cobrar_kpis`. (~8 lines)
- [ ] 2.3 Add `api_cta_cobrar_top` endpoint — GET `/api/dashboard-gerencial/cta-cobrar-top`, parse `limite` and `dias_vto`, call `get_cta_cobrar_top`. (~8 lines)
- [ ] 2.4 Add `api_cta_pagar_kpis` endpoint — GET `/api/dashboard-gerencial/cta-pagar-kpis`. (~8 lines)
- [ ] 2.5 Add `api_cta_pagar_top` endpoint — GET `/api/dashboard-gerencial/cta-pagar-top`. (~8 lines)

## Phase 3: Template (~180 lines)

- [ ] 3.1 Add **SECCIÓN: Cuentas por Cobrar** in `templates/dashboard-gerencial.html` after "Productos sin Movimiento" — 4 KPI cards (Saldo Total primary, Saldo Vencido danger, Saldo por Vencer success, Clientes con Deuda warning) + subtitle "Basado en fecha del movimiento". (~50 lines)
- [ ] 3.2 Add **Top Deudores** table — columns: #, Cliente, Documento, Saldo, Último Mov. Use `data.cta_cobrar_top` loop. Empty state: "No hay clientes con saldo positivo". (~40 lines)
- [ ] 3.3 Add **SECCIÓN: Cuentas por Pagar** — 4 KPI cards (Saldo Total, Vencido, Por Vencer, Proveedores con Deuda). (~50 lines)
- [ ] 3.4 Add **Top Proveedores** table — columns: #, Proveedor, Fantasía, Saldo, Último Mov. Use `data.cta_pagar_top` loop. Empty state. (~40 lines)

## Phase 4: JS + CSS (~15 lines)

- [ ] 4.1 Add `inicializarCtaCte()` function in `static/js/dashboard-gerencial.js` — placeholder for future HTMX live refresh of cta_cte sections. Call from `inicializarDashboard()`. (~5 lines)
- [ ] 4.2 Add badge styles `.badge-cta-vencido` (danger) and `.badge-cta-por-vencer` (success) in `static/css/dashboard-gerencial.css`. (~10 lines)

## Phase 5: Verification (~manual)

- [ ] 5.1 Load `/dashboard-gerencial` — verify 8 new KPI cards render (4 cobrar + 4 pagar), 2 tables show data
- [ ] 5.2 Verify Stage 1 KPIs, evolución, sucursales, rubros, top productos, top vendedores still render correctly
- [ ] 5.3 Verify Stage 2 stock KPIs, stock sucursal, sin movimiento still render correctly
- [ ] 5.4 Test edge case: empty cta_cte data shows "No hay..." messages, no crashes
