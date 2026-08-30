# Proposal: Dashboard Gerencial ERP — Etapa 4: Créditos

## Intent

Extender el dashboard gerencial con una sección de análisis de créditos: KPIs de cartera activa, morosidad, y ranking de deudores por crédito. La sección complementa las existentes de cuentas por cobrar (ctacte) y por pagar, aportando visibilidad específica del módulo de créditos.

## Scope

### In Scope
- `get_creditos_kpis()`: total créditos activos, créditos vencidos (cuota vencida sin pago), monto total en cartera, % morosidad
- `get_creditos_top_deudores()`: top deudores por saldo impago (monto cuotas - pagos realizados)
- 2 endpoints HTMX: `/api/dashboard-gerencial/creditos-kpis`, `/api/dashboard-gerencial/creditos-top`
- Sección HTML en template con 4 KPI cards + tabla top deudores
- Wire-up en `get_datos_dashboard()` agregador

### Out of Scope
- Detalle individual de crédito (ya existe en módulo creditos)
- Gráficos de evolución de cartera
- Alertas de vencimiento (ya existe `alerta_creditos_atrasados`)
- Modificación de estados de crédito

## Capabilities

### New Capabilities
- `dashboard-gerencial-creditos`: KPIs de cartera de créditos y ranking de deudores por crédito en el dashboard gerencial

### Modified Capabilities
- `dashboard-gerencial-stage1`: Agregador `get_datos_dashboard()` extiende con sección créditos

## Approach

**Data source**: `creditos` (monto_total, estado, idsucursal), `vencimientos_creditos` (monto, fecha_vencimiento), `pagos_creditos` (monto). No se inventa vencimiento: se usa `fecha_vencimiento` real de `vencimientos_creditos`.

**Saldo por crédito**: `SUM(vencimientos.monto) - SUM(pagos.monto)`. Crédito con saldo > 0 es "con deuda".

**Vencido**: Cuota con `fecha_vencimiento < CURDATE()` y sin pago registrado en `pagos_creditos` para ese `idvencimiento`. Se reutiliza la lógica existente de `ver_cuotas_creditos_vencidas()`.

**Multi-sucursal**: Filtro `c.idsucursal = :id_sucursal` cuando se especifica.

**Decimal**: Todos los valores monetarios usan `Decimal` internamente, formato visual `$ 1.250.450,50`.

**Orden de sección en template**: Después de "Cuentas por Pagar" / "Top Proveedores".

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modified | Agregar `get_creditos_kpis()`, `get_creditos_top_deudores()`, wire-up en `get_datos_dashboard()` |
| `routes/dashboard_gerencial.py` | Modified | Agregar imports, 2 endpoints HTMX, wire-up en main route |
| `templates/dashboard-gerencial.html` | Modified | Agregar sección HTML Créditos (4 KPI cards + tabla) |
| `static/js/dashboard-gerencial.js` | Modified | Función de inicialización para sección créditos (si se usa HTMX lazy-load) |
| `static/css/dashboard-gerencial.css` | Modified | Estilos para badges de estado de crédito si es necesario |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Stored procedures no documentados (`get_cant_cuotas_vencidas`, `get_cuotas_creditos_vencidas`) | Med | Implementar queries SQL directas en servicio, no depender de SP |
| Rendimiento de query con JOINs 3 tablas (creditos + vencimientos + pagos) | Bajo | Usar `GROUP BY` + `HAVING saldo > 0`, `LIMIT 10` en top deudores |
| Estados de crédito no estandarizados (ids pueden variar) | Bajo | Usar `estados_creditos.nombre` para clasificar, no hardcoded IDs |

## Rollback Plan

1. Revertir cambios en `services/dashboard_gerencial.py` (eliminar 2 funciones)
2. Revertir cambios en `routes/dashboard_gerencial.py` (eliminar 2 endpoints + imports)
3. Revertir cambios en template (eliminar sección HTML)
4. No hay dependencias de datos — rollback es limpio

## Dependencies

- Tablas `creditos`, `vencimientos_creditos`, `pagos_creditos`, `estados_creditos` existen en la BD
- `utils/utils.py` → `check_session` y `utils/msg_alertas.py` → `alertas_mensajes` (ya disponibles)

## Success Criteria

- [ ] KPIs muestran: total créditos activos, créditos vencidos, monto total cartera, % morosidad
- [ ] Top deudores muestra ranking por saldo impago con nombre, documento, saldo
- [ ] Multi-sucursal funciona: filtro idsucursal afecta todas las queries
- [ ] Sin datos inventados: si no hay créditos, sección muestra "No hay datos de créditos disponibles"
- [ ] Valores monetarios usan Decimal, formato visual argentino
