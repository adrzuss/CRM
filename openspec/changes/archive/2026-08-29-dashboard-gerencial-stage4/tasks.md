# Tasks: Dashboard Gerencial — Etapa 4: Créditos

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~280 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Delivery strategy | single-pr |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Backend Service

- [x] 1.1 Add `get_creditos_kpis(id_sucursal=None)` → dict in `services/dashboard_gerencial.py`. Query: COUNT(DISTINCT) activos, vencidos (cuota vencida sin pago), SUM saldo, morosidad %. Filtro `estados_creditos.nombre NOT IN ('ANULADO','CANCELADO','RECHAZADO')`. Reutilizar `_formato_moneda` para `monto_total_cartera`. Retorna `creditos_activos`, `creditos_vencidos`, `monto_total_cartera`, `monto_total_cartera_raw`, `porcentaje_morosidad`, `cantidad_deudores`.
- [x] 1.2 Add `get_creditos_top_deudores(limite=10, id_sucursal=None)` → list[dict] in `services/dashboard_gerencial.py`. Query: JOIN creditos+vencimientos+pagos+estados+clientes, GROUP BY idcredito, HAVING saldo>0, ORDER BY saldo DESC, LIMIT. Retorna `nombre`, `documento`, `cantidad_creditos`, `saldo_total`, `saldo_total_raw`.
- [x] 1.3 Wire-up `get_datos_dashboard()`: agregar `'creditos_kpis': get_creditos_kpis(id_sucursal)` y `'creditos_top_deudores': get_creditos_top_deudores(10, id_sucursal)` al dict de retorno (línea ~944).

## Phase 2: Routes

- [x] 2.1 Add imports `get_creditos_kpis, get_creditos_top_deudores` al bloque de imports en `routes/dashboard_gerencial.py` (línea ~26).
- [x] 2.2 Add endpoint `GET /api/dashboard-gerencial/creditos-kpis` con `@check_session`. Parsea `id_sucursal` del request.args (mismo patrón que stock endpoints). Retorna `_api_respuesta(get_creditos_kpis, id_sucursal)`.
- [x] 2.3 Add endpoint `GET /api/dashboard-gerencial/creditos-top` con `@check_session`. Parsea `limite` (default 10) e `id_sucursal`. Retorna `_api_respuesta(get_creditos_top_deudores, limite, id_sucursal)`.

## Phase 3: Template

- [x] 3.1 Insertar sección HTML en `templates/dashboard-gerencial.html` después de `<!-- Top Proveedores -->` tabla (línea ~864), antes del cierre `</div>`. Incluir: header "Créditos", 4 KPI cards (`border-start-primary/danger/info/warning`), tabla top deudores (columns: #, Cliente, Doc, Plan, Saldo, Cuotas, Vencidas, Próx. Vto). Usar `data.creditos_kpis` y `data.creditos_top_deudores`. Fallback `{% else %}`: "No hay datos de créditos disponibles".

## Phase 4: CSS

- [x] 4.1 Add `.badge-creditos-vigente` (green `#1cc88a`) y `.badge-creditos-vencido` (red `#e74a3b`) en `static/css/dashboard-gerencial.css` después de `.badge-cta-por-vencer` (línea ~138). Mismo patrón de font-size/padding que badges existentes.

## Phase 5: Verification

- [x] 5.1 Verificar sección créditos: navegar a `/dashboard-gerencial`, confirmar 4 KPI cards con datos o "No hay datos", tabla top deudores con datos o vacía.
- [x] 5.2 Verificar que Stages 1+2+3 siguen funcionando: KPIs ventas, stock, cta_cte, cta_pagar — sin errores de import ni template.
- [x] 5.3 Verificar multi-sucursal: filtrar por sucursal y confirmar que KPIs créditos cambian.
