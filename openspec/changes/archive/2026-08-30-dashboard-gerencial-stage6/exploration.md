# Exploration: Dashboard Gerencial ERP — Etapa 6
# Alertas Gerenciales + Drill-Down + Mejoras UX

**Fecha**: 2026-08-30
**Cambio**: dashboard-gerencial-stage6

---

## 1. Estado Actual del Dashboard (Stages 1-5)

### Arquitectura
- **Backend**: 1 archivo de servicio (services/dashboard_gerencial.py, ~1336 líneas, 20 funciones) + 1 blueprint de rutas (outes/dashboard_gerencial.py, 293 líneas, 19 endpoints)
- **Frontend**: 1 template Jinja2 (~1254 líneas), 1 JS (~412 líneas), 1 CSS (~209 líneas)
- **Data flow**: Server-side render con Jinja2 + fetch API para actualizaciones parciales (sin HTMX en dashboard)

### Secciones Existentes
| Etapa | Secciones | KPIs | Tablas/Gráficos |
|-------|-----------|------|-----------------|
| 1 | KPIs, Evolución, Sucursales, Rubros, Top Productos, Top Vendedores | 4 (Ventas, Cobranzas, Margen, Ticket) | 4 tablas + 2 gráficos (line, doughnut) |
| 2 | Stock KPIs, Stock Sucursal, Sin Movimiento | 4 (Sin Stock, Bajo Mínimo, Saludable, Exceso) | 2 tablas |
| 3 | Cta Cobrar KPIs, Top Deudores, Cta Pagar KPIs, Top Proveedores | 8 (4 cobrar + 4 pagar) | 2 tablas |
| 4 | Créditos KPIs, Top Deudores Créditos | 4 (Activos, Vencidos, Cartera, Morosidad) | 1 tabla |
| 5 | Bancos KPIs, Detalle Bancos, Caja KPIs, Rendiciones | 6 (3 bancos + 3 caja) | 2 tablas |

### Datos Disponibles por Sección
- **Ventas**: get_kpis(), get_evolucion_ventas(), get_ventas_sucursal(), get_ventas_rubro(), get_top_productos(), get_top_vendedores()
- **Stock**: get_stock_kpis(), get_stock_sucursal(), get_productos_sin_movimiento()
- **Cta Cobrar**: get_cta_cobrar_kpis(), get_cta_cobrar_top()
- **Cta Pagar**: get_cta_pagar_kpis(), get_cta_pagar_top()
- **Créditos**: get_creditos_kpis(), get_creditos_top_deudores()
- **Bancos**: get_bancos_kpis(), get_bancos_detalle()
- **Caja**: get_caja_kpis(), get_caja_rendiciones_recientes()

---

## 2. Análisis de Alertas Gerenciales

### 2.1 Alertas Requeridas

| # | Alerta | Umbral | Datos ya disponibles | Nueva función necesaria |
|---|--------|--------|---------------------|------------------------|
| A1 | Stock bajo | sin_stock > 0 OR bajo_minimo > 0 | Sí — get_stock_kpis() ya retorna sin_stock y ajo_minimo | NO — reutilizar KPIs |
| A2 | Créditos vencidos | creditos_vencidos > 0 | Sí — get_creditos_kpis() ya retorna creditos_vencidos | NO — reutilizar KPIs |
| A3 | Cuentas por cobrar vencidas | saldo_vencido > 0 | Sí — get_cta_cobrar_kpis() ya retorna saldo_vencido | NO — reutilizar KPIs |
| A4 | Bancos con saldo negativo | saldo_total_bancos_raw < 0 | Sí — get_bancos_kpis() ya retorna saldo_total_bancos_raw | NO — reutilizar KPIs |

### 2.2 Estrategia de Implementación: Alertas sin Nuevas Tablas

**Hallazgo clave**: Todas las 4 alertas se pueden calcular con datos que YA existen en las funciones de servicio actuales. No se necesitan tablas nuevas ni stored procedures.

**Enfoque propuesto**: Nueva función get_alertas_gerenciales() en services/dashboard_gerencial.py que:
1. Reutiliza las funciones existentes (ya llamadas en get_datos_dashboard())
2. Evalúa umbrales contra los raw values
3. Retorna lista de alertas con severidad, título, detalle y link de drill-down

`python
# Firma propuesta
def get_alertas_gerenciales(data_dashboard):
    """
    Evalúa los datos del dashboard contra umbrales y retorna alertas gerenciales.
    Recibe el dict completo de get_datos_dashboard() para reutilizar sus valores.
    Retorna lista de dicts con: id, tipo, severidad, titulo, detalle, valor, icono, drill_down_url
    """
`

**Severidad**: critico (rojo), dvertencia (amarillo), info (azul)

**Drill-down targets** (rutas existentes):
| Alerta | URL de drill-down | Ruta Flask existente |
|--------|-------------------|---------------------|
| Stock bajo | /articulos/stock-art-faltantes | p_articulos.route('/articulos/stock-art-faltantes') |
| Créditos vencidos | /creditos/cuotas-atrasadas | p_creditos.route('/creditos/cuotas-atrasadas') |
| Cta cobrar vencidas | /ctacte-clientes (con filtro vencidas) | p_ctactecli |
| Bancos saldo negativo | /bancos | p_bancos.route('/bancos') |

### 2.3 API de Alertas

**Nuevo endpoint**:
`
GET /api/dashboard-gerencial/alertas
`

Retorna JSON:
`json
{
    "success": true,
    "data": {
        "alertas": [
            {
                "id": "stock_bajo",
                "tipo": "stock",
                "severidad": "advertencia",
                "titulo": "Stock Bajo",
                "detalle": "12 artículos sin stock + 8 bajo mínimo",
                "valor": 20,
                "icono": "fas fa-exclamation-triangle",
                "drill_down_url": "/articulos/stock-art-faltantes",
                "drill_down_label": "Ver artículos"
            }
        ],
        "total": 3,
        "criticos": 1,
        "advertencias": 2
    }
}
`

### 2.4 Presentación de Alertas en el Dashboard

**Ubicación propuesta**: Barra de alertas horizontal debajo de los filtros, antes de los KPIs.

**Componente HTML**:
- Container #alertas-bar con display: flex; gap: 0.5rem;
- Cada alerta: badge clickable con icono + texto + link
- Colores: danger para críticos, warning para advertencias, info para info
- Si no hay alertas: ocultar la barra completa
- Click en badge → navega a la URL de drill-down

---

## 3. Análisis de Drill-Down

### 3.1 Oportunidades de Drill-Down

| # | Elemento Origen | Drill-Down Destino | Mecanismo |
|---|-----------------|---------------------|-----------|
| D1 | KPI "Ventas Totales" | Lista de facturas del período | Click en card → window.location |
| D2 | KPI "Cobranzas" | Lista de cobranzas del período | Click en card |
| D3 | KPI "Cta Cobrar Vencido" | CTACTE clientes con filtro vencidas | Click en card |
| D4 | KPI "Créditos Vencidos" | Créditos cuotas atrasadas | Click en card |
| D5 | Fila en tabla "Ventas por Sucursal" | Dashboard filtrado por esa sucursal | Click en fila → setear filtro |
| D6 | Fila en tabla "Ventas por Rubro" | Filtro de rubro en evolución (futuro) | Click en fila |
| D7 | Gráfico de evolución (click punto) | Detalle del día/semana seleccionada | Click en punto del chart |
| D8 | Gráfico rubros (click segmento) | Filtrar tabla por ese rubro | Click en segmento doughnut |
| D9 | Fila "Top Deudores" | CTACTE de ese cliente | Click en fila → /ctacte-clientes/{idcliente} |
| D10 | Fila "Top Productos" | Ficha del artículo | Click en fila → /articulos/{id} |
| D11 | Fila "Bancos" | Movimientos de ese banco | Click en fila |

### 3.2 Implementación JS para Drill-Down

**Patrón recomendado**: Data attributes en elementos clickeables + delegación de eventos.

`html
<!-- Ejemplo: KPI card con drill-down -->
<div class="card card-kpi border-start-primary drill-down"
     data-drill-url="/dashboard-gerencial?desde=...&hasta=...&seccion=facturas">
`

`javascript
// Delegación de eventos para drill-down
document.addEventListener('click', function(e) {
    var target = e.target.closest('.drill-down');
    if (target) {
        var url = target.dataset.drillUrl;
        if (url) window.location.href = url;
    }
});
`

### 3.3 Navegación entre Secciones (scroll spy)

**Hallazgo**: El dashboard es una página larga con muchas secciones. Actualmente no hay navegación interna.

**Solución**: Navbar lateral o barra de tabs sticky con scroll-smooth a cada sección.

`javascript
// Ejemplo de scroll a sección
document.querySelectorAll('.nav-seccion').forEach(function(link) {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        var target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});
`

---

## 4. Análisis de Mejoras UX

### 4.1 Loading States

**Situación actual**: Las llamadas fetch no muestran feedback al usuario.

**Implementación propuesta**:

1. **Skeleton loaders** para tablas y gráficos:
   - CSS animation de shimmer sobre placeholders
   - Se activa antes del fetch, se remueve al llegar la data

2. **Spinner en cards KPI** cuando se refrescan vía API:
   - Overlay semi-transparente con as fa-spinner fa-spin
   - Se aplica por sección, no global

3. **Botón "Actualizar"** con estado de loading:
   - Cambiar icono de a-sync-alt a a-spinner fa-spin
   - Deshabilitar durante la request

**CSS necesario** (~30 líneas):
`css
/* Skeleton animation */
.skeleton { background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200% 100%; animation: skeleton-shimmer 1.5s infinite; }
@keyframes skeleton-shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* Loading overlay */
.loading-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.7); display: flex; align-items: center; justify-content: center; z-index: 10; }
`

### 4.2 Empty States Mejorados

**Situación actual**: Cada tabla tiene un <tr> con "No hay datos" como fallback. Es funcional pero visualmente plano.

**Mejora propuesta**: Empty state con icono grande + texto descriptivo + CTA sugerido.

`html
<!-- Empty state mejorado -->
<div class="empty-state text-center py-5">
    <i class="fas fa-chart-line fa-3x text-gray-300 mb-3"></i>
    <h6 class="text-muted">No hay ventas en este período</h6>
    <p class="text-muted small mb-0">
        Intenta ampliar el rango de fechas o seleccionar otra sucursal.
    </p>
</div>
`

**Para tablas**: Reemplazar el patrón actual {% else %}<tr><td...>No hay datos</td></tr> con un empty state visual más rico.

**Prioridad de empty states por impacto**:
1. Evolución de ventas (gráfico vacío es lo más impactante)
2. Tablas de sucursales/rubros
3. Top productos/vendedores
4. Tablas de detalle (ctacte, créditos, bancos)

### 4.3 Tooltips Informativos

**Situación actual**: Los KPI cards tienen texto descriptivo estático pero no tooltips interactivos.

**Implementación propuesta**: Usar data-bs-toggle="tooltip" de Bootstrap 5 (ya incluido en el proyecto).

`html
<!-- Ejemplo: tooltip en KPI -->
<h4 class="h5 mb-0 font-weight-bold text-gray-800"
    data-bs-toggle="tooltip"
    data-bs-placement="top"
    title="Suma de ventas netas menos notas de crédito del período">
    {{ data.kpis.ventas_totales }}
</h4>
`

**Tooltips sugeridos por KPI**:

| KPI | Tooltip |
|-----|---------|
| Ventas Totales | "Suma de facturas de venta + débitos - notas de crédito" |
| Cobranzas | "Total de pagos recibidos de clientes en el período" |
| Margen Bruto | "Ventas - Costo de mercadería vendida" |
| Ticket Promedio | "Ventas totales / cantidad de operaciones" |
| Stock Sin Stock | "Artículos con unidades = 0 en el inventario" |
| Saldo Vencido | "Saldos con fecha de movimiento mayor a {dias_vto} días" |
| Morosidad % | "Créditos con al menos 1 cuota vencida / total créditos activos" |
| Saldo Total Bancos | "Acumulado histórico de todos los movimientos bancarios" |

### 4.4 Responsive Design

**Situación actual**: Usa Bootstrap 5 grid (col-xl-3, col-md-6). Ya es responsive en columnas.

**Problemas detectados**:
1. **Filtros**: El form de filtros puede desbordar en pantallas pequeñas
2. **Tablas**: Usan 	able-responsive (scroll horizontal), pero columns como "Participación" con progress bar pueden ser difíciles de leer
3. **Gráficos**: Canvas de Chart.js ya es responsive, pero el height fijo de 300px puede ser problemático en mobile

**Mejoras propuestas**:
1. **Filtros**: Stack vertical en mobile con lex-column flex-sm-row
2. **Tabla sucursales**: Ocultar columna "Participación" en mobile, mostrar solo badge
3. **Gráficos**: Usar min-height en vez de height fijo
4. **Cards KPI**: En mobile, 2 columnas en vez de 4

---

## 5. Análisis de Impacto y Complejidad

### 5.1 Estimación por Feature

| Feature | Service | Routes | Template | JS | CSS | Complejidad |
|---------|---------|--------|----------|----|----|-------------|
| Alertas gerenciales | 1 func nueva | 1 endpoint | ~50 líneas | ~80 líneas | ~40 líneas | Baja |
| Drill-down en KPIs | 0 | 0 | ~20 líneas attrs | ~30 líneas | 0 | Baja |
| Drill-down en tablas | 0 | 0 | ~30 líneas attrs | ~20 líneas | ~10 líneas | Baja |
| Drill-down en gráficos | 0 | 0 | 0 | ~40 líneas | 0 | Media |
| Navegación secciones | 0 | 0 | ~40 líneas nav | ~30 líneas | ~30 líneas | Baja |
| Loading states | 0 | 0 | ~20 líneas | ~60 líneas | ~50 líneas | Baja |
| Empty states mejorados | 0 | 0 | ~80 líneas | 0 | ~20 líneas | Baja |
| Tooltips informativos | 0 | 0 | ~30 líneas attrs | 0 | 0 | Muy baja |
| Responsive fixes | 0 | 0 | ~15 líneas | 0 | ~30 líneas | Baja |

### 5.2 Archivos a Modificar

| Archivo | Cambio | Líneas estimadas |
|---------|--------|------------------|
| services/dashboard_gerencial.py | +1 función get_alertas_gerenciales() | ~80 |
| outes/dashboard_gerencial.py | +1 endpoint /api/dashboard-gerencial/alertas | ~15 |
| 	emplates/dashboard-gerencial.html | Alertas bar + drill-down attrs + empty states + tooltips + nav + responsive | ~200 |
| static/js/dashboard-gerencial.js | Alertas fetch + drill-down + loading states + nav + chart drill | ~180 |
| static/css/dashboard-gerencial.css | Skeletons + empty states + nav + responsive | ~100 |

**Total estimado**: ~575 líneas nuevas/modificadas

---

## 6. Dependencias y Consideraciones

### 6.1 No depende de
- Nuevas tablas en la base de datos
- Nuevos stored procedures
- Nuevas librerías (SweetAlert2, HTMX, Chart.js y Bootstrap 5 ya están cargados)

### 6.2 Reutiliza
- get_stock_kpis() — sin_stock, bajo_minimo
- get_creditos_kpis() — creditos_vencidos
- get_cta_cobrar_kpis() — saldo_vencido
- get_bancos_kpis() — saldo_total_bancos_raw
- get_datos_dashboard() — el dict completo como input

### 6.3 Patrones existentes a seguir
- **Alertas**: Seguir patrón de utils/msg_alertas.py (dict con titulo, subtitulo, tipo, url)
- **Tooltips**: Usar data-bs-toggle="tooltip" de Bootstrap 5
- **Fetch API**: Mantener patrón de ctualizarSeccion() existente
- **CSS**: Mantener namespace .dashboard-gerencial

---

## 7. Riesgos

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Performance: 20 funciones en get_datos_dashboard() | Alto — carga inicial lenta | Las alertas reutilizan datos ya calculados; no agregan queries |
| Alertas generan ruido si umbrales son bajos | Medio | Configurar umbrales conservadores; permitir desactivar |
| Drill-down a rutas que requieren otros permisos | Bajo | Links con 	arget="_blank" o validación de permisos |
| Template crece demasiado (~1450+ líneas) | Medio | Considerar extraer a partials en futuras etapas |

---

## 8. Recomendaciones de Implementación

### Orden sugerido (por dependencias)
1. **Tooltips** (sin dependencias, cambio mínimo)
2. **Empty states mejorados** (solo template + CSS)
3. **Loading states** (JS + CSS, sin backend)
4. **Navegación entre secciones** (template + JS + CSS)
5. **Alertas gerenciales** (service + route + template + JS)
6. **Drill-down en KPIs y tablas** (template + JS)
7. **Drill-down en gráficos** (JS, más complejo)
8. **Responsive fixes** (CSS + template)

### Decisión de arquitectura
- Las alertas se calculan server-side pero se muestran inline en el template (ya renderizados)
- Opcionalmente, se puede hacer refresh vía API (endpoint /api/dashboard-gerencial/alertas)
- El JS de alertas se encarga de la interacción (click → navegación)
- Loading states se implementan solo para las llamadas fetch (no para la carga inicial server-side)

---

## 9. Preguntas Pendientes

1. **¿Las alertas deben ser configurables?** (ej: umbral de stock bajo configurable por usuario)
2. **¿El drill-down a tablas debe mantener filtros activos?** (ej: click en sucursal → filtrar dashboard)
3. **¿La navegación de secciones debe ser persistente (sticky) o solo inline?**
4. **¿Se debe usar HTMX para alguna actualización en Stage 6?** (actualmente el dashboard usa fetch puro)