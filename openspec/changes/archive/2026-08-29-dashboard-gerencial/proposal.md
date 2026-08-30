# Proposal: Dashboard Gerencial ERP — Etapa 1

## Intent

Crear un **nuevo** dashboard gerencial en `/dashboard-gerencial` separado del reporte existente en `/tablero-gerencial`. Motivo: el reporte actual es un render server-side completo (626 líneas de template, 692 líneas de servicio) que ya funciona; extenderlo arriesga regresiones y lo vuelve innavegable. El nuevo dashboard tiene su propio blueprint, ruta, template, servicio y archivos estáticos.

Stage 1: filtros globales, 4 KPIs principales, evolución de ventas, ventas por sucursal/rubro, top productos y top vendedores.

## Scope

### In Scope (Stage 1)
- Filtros globales: Período (rango fechas), Sucursal (select), Comparar con (toggle período anterior), Actualizar (botón refresh)
- KPIs: Ventas totales, Cobranzas, Margen bruto, Ticket promedio — con variación % vs período anterior
- Evolución de ventas: gráfico línea (diario/semanal/mensual), toggle granularity, overlay período comparado
- Ventas por sucursal: tabla con importe, operaciones, ticket promedio, participación %
- Ventas por rubro: tabla + gráfico doughnut, importe, unidades, participación %
- Top 10 productos: facturación, cantidad, margen
- Top 10 vendedores: ventas, operaciones, ticket promedio, participación %

### Out of Scope (Stages 2-6)
- Concentración clientes ABC
- Análisis compras vs ventas
- Inventario y rotación
- Medios de pago
- Cuentas corrientes y deudores
- Alertas y notificaciones
- Exportación PDF/Excel
- Real-time / WebSocket updates

## Capabilities

### New Capabilities
- `dashboard-gerencial-stage1`: Nuevo dashboard gerencial con filtros, KPIs, evolución temporal, ventas por sucursal/rubro y rankings

### Modified Capabilities
- None (no existing specs are altered)

## Approach

### Architecture
- **Blueprint**: `bp_dashboard_gerencial` en `routes/dashboard_gerencial.py` — registrado en `index.py`
- **Ruta principal**: `GET /dashboard-gerencial` — renderiza template con datos server-side
- **API parcial**: `GET /api/dashboard-gerencial/datos` — endpoint JSON para HTMX refresh por sección
- **Servicio**: `services/dashboard_gerencial.py` — funciones SQL independientes, reutiliza patrón de `services/reportes.py`
- **Template**: `templates/dashboard-gerencial.html` — extiende `base.html`, usa Chart.js 4 CDN
- **JS**: `static/js/dashboard-gerencial.js` — inicialización Chart.js, bind filtros, HTMX refresh
- **CSS**: `static/css/dashboard-gerencial.css` — estilos específicos del dashboard

### Key Decisions
1. Chart.js 4.4.1 via CDN (consistente con gerencial report, NO el vendor bundle legacy)
2. Datos server-side via `render_template()` + `{{ data|tojson }}` — same pattern as existing dashboards
3. HTMX para refresh de secciones individuales (filtros → actualiza solo las tablas/gráficos)
4. Multi-sucursal: `session['id_sucursal']` como default, select carga `get_sucursales_lista()`
5. Comparar con período anterior: mismo rango de días hacia atrás desde fecha inicio
6. Agregaciones en MySQL, NO en Python — `Decimal` para monetarios
7. Nunca inventar datos: si falta info, mostrar "Este indicador requiere información que actualmente no está disponible"

### SQL Queries Required
| Widget | Query Base |
|--------|-----------|
| KPIs (ventas, cobranzas, margen, ticket) | `facturav` + `tipo_operacion` filter, `cobranzas` table, `detalles_factura` for margin |
| Evolución temporal | `facturav` grouped by `DATE(fecha_emision)` / `WEEK()` / `MONTH()` |
| Ventas por sucursal | `facturav` grouped by `idsucursal` + `sucursales.nombre` |
| Ventas por rubro | `facturav` → `detalles_factura` → `articulos` → `rubros` |
| Top productos | `detalles_factura` → `articulos`, aggregated by `cantidad * precio_unitario` |
| Top vendedores | `facturav.vendedor` field, aggregated |

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `routes/dashboard_gerencial.py` | **New** | Blueprint + route + API endpoint |
| `services/dashboard_gerencial.py` | **New** | Service layer with SQL queries |
| `templates/dashboard-gerencial.html` | **New** | Template with KPIs, charts, tables |
| `static/js/dashboard-gerencial.js` | **New** | Chart.js 4 init, filters, HTMX |
| `static/css/dashboard-gerencial.css` | **New** | Dashboard-specific styles |
| `index.py` | **Modified** | Register new blueprint (1 line) |
| `templates/partials/_sidebar.html` | **Modified** | Add nav link for new dashboard |

## Dependencies

- `@check_session` from `utils/utils.py` — auth
- `@alertas_mensajes` from `utils/msg_alertas.py` — alerts
- `get_sucursales_lista()` from existing services — sucursal filter
- `db.session.execute(text(...))` from `utils/db.py` — SQL execution
- Chart.js 4.4.1 CDN — charting
- `base.html` template — layout inheritance
- Bootstrap 5.3.3 — UI components
- HTMX 1.9.10 — partial page updates

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SQL queries lentas en grandes volúmenes | Med | Limitar rango de fechas a 90 días por defecto; indexar `fecha_emision` si no existe |
| Duplicación lógica con `services/reportes.py` | Baja | Mantener servicios separados; el existente no se modifica |
| CSP nonce en scripts HTMX | Baja | Seguir patrón existente: `{{ g.nonce }}` en todos los inline scripts |
| Chart.js conflicto con versión legacy | Baja | Cargar solo Chart.js 4 CDN, NO el vendor bundle |

## Rollback Plan

1. Eliminar `routes/dashboard_gerencial.py`, `services/dashboard_gerencial.py`, `templates/dashboard-gerencial.html`, `static/js/dashboard-gerencial.js`, `static/css/dashboard-gerencial.css`
2. Revertir cambio en `index.py` (quitar registro de blueprint)
3. Revertir cambio en `_sidebar.html` (quitar nav link)
4. Ningún archivo existente fue modificado de forma destructiva — solo se agregaron líneas

## Success Criteria

- [ ] Ruta `/dashboard-gerencial` carga sin errores HTTP 500
- [ ] Los 4 KPIs muestran datos reales con variación % correcta
- [ ] Gráfico de evolución renderiza con datos del período seleccionado
- [ ] Tabla de sucursales muestra todas las sucursales con métricas
- [ ] Tabla de rubros + doughnut muestra distribución correcta
- [ ] Top 10 productos y vendedores se ordenan correctamente
- [ ] Filtros de fecha y sucursal actualizan las secciones vía HTMX
- [ ] El reporte existente `/tablero-gerencial` funciona sin cambios
- [ ] Sidebar muestra link al nuevo dashboard
