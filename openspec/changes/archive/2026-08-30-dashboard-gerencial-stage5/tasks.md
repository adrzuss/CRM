# Tasks: Dashboard Gerencial — Etapa 5 (Bancos / Caja)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~450-500 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Medium

**Note**: Estimated ~480 lines across 5 files. Slightly above 400-line budget but functions are cohesive (all bancos/caja), no natural split point. Recommend single PR with maintainer acceptance.

---

## Phase 1: Backend Service — Bancos

- [x] 1.1 In `services/dashboard_gerencial.py`, add `get_bancos_kpis(desde, hasta, id_sucursal=None)` before `get_datos_dashboard`. Query `bancos_propios` JOIN `tipo_mov_bancos`. Return `saldo_total_bancos`, `saldo_total_bancos_raw`, `movimientos_mes`, `ingresos_mes`, `ingresos_mes_raw`, `egresos_mes`, `egresos_mes_raw`. Saldo is historical (no date filter); movimientos/ingresos/egresos filter by `fecha_emision BETWEEN :desde AND :hasta`. Use `baja = '1900-01-01'`. Use `_formato_moneda` for formatted values.

- [x] 1.2 In `services/dashboard_gerencial.py`, add `get_bancos_detalle(desde, hasta, id_sucursal=None)` before `get_datos_dashboard`. Query `bancos` LEFT JOIN `bancos_propios` (with date filter) LEFT JOIN `tipo_mov_bancos`. GROUP BY `b.id, b.nombre`. Return list of dicts: `{banco, saldo, saldo_raw, movimientos, participacion}`. Saldo is historical (no date filter in JOIN). Participacion = `(saldo / saldo_total_positivo) * 100` where saldo_total_positivo = SUM(saldos where saldo > 0).

## Phase 2: Backend Service — Caja

- [x] 2.1 In `services/dashboard_gerencial.py`, add `get_caja_kpis(desde, hasta, id_sucursal=None)` before `get_datos_dashboard`. Query `rendiciones_caja`. Filter by `fecha BETWEEN :desde AND :hasta` and optional `idsucursal`. Return `total_efectivo`, `total_efectivo_raw`, `total_otros_valores`, `total_otros_valores_raw`, `cantidad_rendiciones`. Use `COALESCE` for null safety on `total_otros_valores`.

- [x] 2.2 In `services/dashboard_gerencial.py`, add `get_caja_rendiciones_recientes(desde, hasta, id_sucursal=None, limite=10)` before `get_datos_dashboard`. Query `rendiciones_caja` JOIN `usuarios` JOIN `sucursales`. Order by `rc.fecha DESC LIMIT :limite`. Optional `idsucursal` filter. Return list of dicts: `{fecha, usuario, sucursal, total_ventas, total_ventas_fmt, total_efectivo, total_efectivo_fmt, total_otros_valores, total_otros_valores_fmt}`.

## Phase 3: Backend Aggregator

- [x] 3.1 Update `get_datos_dashboard` in `services/dashboard_gerencial.py` to include 4 new keys: `bancos_kpis`, `bancos_detalle`, `caja_kpis`, `caja_rendiciones`. Call the new functions with appropriate params (`desde`, `hasta`, `id_sucursal`). Bancos calls ignore `id_sucursal`.

## Phase 4: Routes

- [x] 4.1 In `routes/dashboard_gerencial.py`, add 4 imports: `get_bancos_kpis`, `get_bancos_detalle`, `get_caja_kpis`, `get_caja_rendiciones_recientes` from `services.dashboard_gerencial`.

- [x] 4.2 Add 4 HTMX endpoints following existing pattern (use `_parsear_filtros` + `_api_respuesta` wrapper):
  - `GET /api/dashboard-gerencial/bancos-kpis` → calls `get_bancos_kpis(desde, hasta)` (no `id_sucursal`)
  - `GET /api/dashboard-gerencial/bancos-detalle` → calls `get_bancos_detalle(desde, hasta)` (no `id_sucursal`)
  - `GET /api/dashboard-gerencial/caja-kpis` → calls `get_caja_kpis(desde, hasta, id_sucursal)`
  - `GET /api/dashboard-gerencial/caja-rendiciones` → calls `get_caja_rendiciones_recientes(desde, hasta, id_sucursal, limite)`. Parse `limite` from args (default 10).

## Phase 5: Template — Bancos

- [x] 5.1 In `templates/dashboard-gerencial.html`, add SECCION BANCOS after the Creditos section (after line ~1006, before `</div>` / `{% endblock %}`). Include:
  - Section header with `<h6>` "Bancos" + bank icon
  - 3 KPI cards in a `row`: Saldo Total (border-start-success/danger based on saldo), Movimientos del Mes (count), Ingresos vs Egresos (two sub-values). Use `data.bancos_kpis.*` values.
  - Table card "Saldos por Banco" with columns: #, Banco, Saldo ($), Movimientos, Participación (%). Loop `data.bancos_detalle`. Badge success/danger for saldo. Empty state: "No hay movimientos bancarios."

## Phase 6: Template — Caja

- [x] 6.1 In `templates/dashboard-gerencial.html`, add SECCION CAJA after the Bancos section. Include:
  - Section header with `<h6>` "Caja" + money icon
  - 2 KPI cards: Total Efectivo Rendido, Rendiciones del Mes (count). Use `data.caja_kpis.*` values.
  - Table card "Últimas Rendiciones" with columns: Fecha, Usuario, Sucursal, Total Ventas, Efectivo, Otros Valores. Loop `data.caja_rendiciones`. Format values with `| tojson` or pre-formatted fields. Empty state: "No hay rendiciones en este período."

## Phase 7: CSS

- [x] 7.1 In `static/css/dashboard-gerencial.css`, add badge styles for bancos:
  - `.badge-bancos-ingreso` — green (success) for positive amounts
  - `.badge-bancos-egreso` — red (danger) for negative amounts
  - `.badge-bancos-saldo-positivo` — green background for saldo badges
  - `.badge-bancos-saldo-negativo` — red background for saldo badges
  Follow existing badge pattern (font-size 0.75rem, padding 0.35em 0.65em).

## Phase 8: JS

- [x] 8.1 In `static/js/dashboard-gerencial.js`, add `inicializarBancosCaja()` function (no-op placeholder for future HTMX refresh). Call it from `inicializarDashboard()` after `inicializarCtaCte()`. Bancos/caja tables render server-side via Jinja2, same as creditos.

## Phase 9: Verification

- [x] 9.1 Verify bancos section: KPI cards render with saldo total (formatted), movimientos count, ingresos/egresos. Table shows per-bank breakdown with participation %.
- [x] 9.2 Verify caja section: KPI cards render with total efectivo and rendiciones count. Table shows last 10 rendiciones with all columns.
- [x] 9.3 Verify Stage 1+2+3+4 sections still render correctly (ventas, stock, cta_cte, creditos).
- [x] 9.4 Verify edge cases: empty bancos_propios → "No hay movimientos bancarios"; empty rendiciones_caja → "No hay rendiciones"; saldo negativo shows danger badge.
- [x] 9.5 Verify sucursal filter: selecting a sucursal filters caja rendiciones but NOT bancos.

## Relevant Files

| File | Action | Lines Est. |
|------|--------|-----------|
| `services/dashboard_gerencial.py` | Modify | ~200 |
| `routes/dashboard_gerencial.py` | Modify | ~60 |
| `templates/dashboard-gerencial.html` | Modify | ~180 |
| `static/css/dashboard-gerencial.css` | Modify | ~30 |
| `static/js/dashboard-gerencial.js` | Modify | ~10 |
