# Proposal: Dashboard Gerencial ERP — Etapa 2 (Stock)

## Intent

Extender el dashboard gerencial existente (Etapa 1) con una sección de análisis de stock: resumen de KPIs de inventario, stock por sucursal, y productos sin movimiento. El usuario necesita visibilidad en tiempo real del estado de inventario para tomar decisiones de reposición y detectar obsolescencia.

## Scope

### In Scope

- **KPIs de stock**: artículos sin stock (`actual <= 0`), bajo mínimo (`actual < maximo`), stock saludable (entre minimo y maximo), exceso de stock (`actual > maximo`)
- **Stock por sucursal**: tabla con unidades totales, valor estimado (`cantidad * costo`), artículos sin stock, artículos bajo mínimo
- **Productos sin movimiento**: artículos con stock pero sin ventas en 30/60/90 días (requiere JOIN con `itemsv` + `facturav`)
- **Modificación de archivos existentes**: service, routes, template, JS, CSS

### Out of Scope

- Gráficos de tendencia de stock (solo snapshots actuales)
- Alertas automáticas de reposición
- Historial de movimientos de stock (solo estado actual + última venta)
- Stock de insumos o materias primas
- Modificación de la sección de filtros globales

## Capabilities

### New Capabilities

- `stock-kpis`: KPIs de resumen de inventario (sin stock, bajo mínimo, saludable, exceso)
- `stock-por-sucursal`: Tabla de stock agrupada por sucursal con valor estimado
- `productos-sin-movimiento`: Listado de artículos sin ventas recientes

### Modified Capabilities

- `dashboard-gerencial-stage1`: Se agregan nuevas secciones al dashboard existente (sin modificar comportamiento existente)

## Approach

### Service Layer (`services/dashboard_gerencial.py`)

Agregar 3 funciones:
1. `get_stock_kpis(id_sucursal)` — Query sobre `stocks` + `articulos` para clasificar artículos por estado de stock
2. `get_stock_sucursal(id_sucursal)` — Query con GROUP BY `stocks.idsucursal`, JOIN `sucursales`, `articulos` para unidades, valor, conteos
3. `productos_sin_movimiento(dias=30, id_sucursal=None)` — Query que busca artículos con `stocks.actual > 0` pero sin `itemsv` en los últimos N días (LEFT JOIN + IS NULL)

Reutilizar `_formato_moneda()`, `_params_base()`, `_sucursal_filter()` existentes.

### Routes (`routes/dashboard_gerencial.py`)

- Agregar imports de las 3 nuevas funciones
- Agregar 3 endpoints HTMX: `/api/dashboard-gerencial/stock-kpis`, `/api/dashboard-gerencial/stock-sucursal`, `/api/dashboard-gerencial/productos-sin-movimiento`
- Actualizar `get_datos_dashboard()` para incluir las 3 nuevas secciones en el dict de respuesta

### Template (`templates/dashboard-gerencial.html`)

Agregar después de la sección de Top Vendedores:
- **SECCIÓN: Resumen de Stock** — 4 KPI cards (sin stock, bajo mínimo, saludable, exceso) en fila
- **SECCIÓN: Stock por Sucursal** — Tabla con columnas: Sucursal, Unidades, Valor Estimado, Sin Stock, Bajo Mínimo
- **SECCIÓN: Productos sin Movimiento** — Tabla con selector de días (30/60/90), columnas: Código, Producto, Stock Actual, Última Venta

### JS (`static/js/dashboard-gerencial.js`)

- Agregar inicialización de la nueva sección en `inicializarDashboard()`
- Agregar event listeners para selector de días en productos sin movimiento
- No se requieren nuevos charts (solo tablas)

### CSS (`static/css/dashboard-gerencial.css`)

- Agregar estilos para badges de estado de stock (sin stock = danger, bajo mínimo = warning, saludable = success, exceso = info)

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modified | Agregar 3 funciones: stock_kpis, stock_sucursal, productos_sin_movimiento |
| `routes/dashboard_gerencial.py` | Modified | Agregar 3 endpoints HTMX + imports |
| `templates/dashboard-gerencial.html` | Modified | Agregar 3 secciones HTML al final del dashboard |
| `static/js/dashboard-gerencial.js` | Modified | Agregar init y event listeners para secciones de stock |
| `static/css/dashboard-gerencial.css` | Modified | Agregar estilos para badges de estado |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Query `productos_sin_movimiento` lenta con muchos artículos | Medium | LIMIT explícito + índice en `itemsv(idarticulo, idfactura)` + considerar subquery |
| `stocks.actual` no tiene historia — solo estado actual | Low | Documentar que valor es snapshot; no intentar calcular tendencias |
| Costo de artículo en 0 distorsiona valor estimado | Medium | Filtrar `articulos.costo > 0` en cálculo de valor, mostrar "N/D" si costo es 0 |
| Breaking Stage 1 existente | Low | Las nuevas funciones son independientes; solo se extiende `get_datos_dashboard()` |

## Rollback Plan

1. Eliminar las 3 nuevas funciones del service
2. Eliminar los 3 nuevos endpoints del routes
3. Eliminar las 3 secciones HTML del template
4. Eliminar estilos y JS agregados
5. Restaurar `get_datos_dashboard()` original
6. Verificar que Stage 1 funciona correctamente

## Dependencies

- Tablas `stocks`, `articulos`, `sucursales` (ya existentes en el esquema)
- Tablas `itemsv`, `facturav` (ya usadas en Stage 1)
- `_formato_moneda()`, `_params_base()`, `_sucursal_filter()` (reutilizar existentes)
- `get_sucursales_lista()` de `services/reportes.py` (ya importado)

## Success Criteria

- [ ] KPIs de stock muestran conteos correctos por estado
- [ ] Tabla de stock por sucursal muestra unidades, valor, sin stock, bajo mínimo
- [ ] Productos sin movimiento lista artículos con stock pero sin ventas en N días
- [ ] Filtro sucursal aplica correctamente a todas las queries de stock
- [ ] Stage 1 existente no se rompe (KPIs, evolución, sucursales, rubros, top productos, top vendedores)
- [ ] No se inventan datos — si falta información, se muestra "No disponible"
- [ ] Decimal se usa para valores monetarios
