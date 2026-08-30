# Proposal: Dashboard Gerencial ERP — Etapa 6 (Alertas Gerenciales + Drill-Down + Mejoras UX)

## Intent

El dashboard gerencial tiene datos completos (ventas, stock, cta_cte, créditos, bancos, caja) pero carece de un sistema de alertas que señale automáticamente problemas críticos. Un gerente no debería tener que revisar 15 secciones para detectar un banco en saldo negativo o 40 artículos sin stock. Además, las interacciones de drill-down y las mejoras de UX (loading states, empty states, tooltips) elevan la usabilidad de un panel ya funcional.

## Scope

### In Scope
- **4 tipos de alertas gerenciales** en panel superior, basadas en datos reales existentes
- **Drill-down por KPI**: click en card → expandir sección relevante o scroll a detalle
- **Drill-down por gráfico**: click en segmento de doughnut → filtrar tabla de rubros; click en punto de línea → navegar a período
- **Navegación entre secciones**: links internos (sidebar o tabla de contenidos) para saltar entre módulos
- **Loading states**: skeleton/spinner en secciones HTMX durante carga
- **Empty states mejorados**: ilustración + mensaje contextual por sección (no solo texto genérico)
- **Tooltips informativos**: `data-bs-toggle="tooltip"` en KPIs explicando qué representa cada métrica
- **Responsive design**: mejoras en mobile para alertas, navegación, y tablas

### Out of Scope
- Alertas por email/notification push (requiere infraestructura adicional)
- Configuración de umbrales por usuario (umbral hardcodeado o desde `configuracion`)
- Drill-down a nivel de factura individual (requiere módulo de facturación separado)
- Grafana/integración externa
- Refactor del template a componentes reutilizables (cambio demasiado grande)

## Capabilities

### New Capabilities
- `dashboard-alertas-gerenciales`: Panel de alertas críticas basado en métricas reales del dashboard (stock bajo, créditos vencidos, cta_cte vencida, bancos saldo negativo)

### Modified Capabilities
- `dashboard-gerencial-stage1`: Agregar drilling interactions (click en KPIs, gráficos, navegación), loading states, empty states mejorados, tooltips, responsive refinements. No cambia los requisitos funcionales existentes, solo agrega interacciones UX.

## Approach

### Alertas Gerenciales
- **Service**: nueva función `get_alertas_gerenciales()` que reutiliza las funciones existentes (`get_stock_kpis`, `get_creditos_kpis`, `get_cta_cobrar_kpis`, `get_bancos_detalle`) y evalúa condiciones críticas
- **Condiciones de alerta**: `bajo_minimo > 0`, `sin_stock > 0`, `creditos_vencidos > 0`, `saldo_vencido > 0`, bancos con `saldo_raw < 0`
- **Ruta API**: `GET /api/dashboard-gerencial/alertas` para refresh HTMX
- **Template**: sección `#seccion-alertas` al inicio del dashboard, después de filtros, con cards apilables
- **Agregador**: `get_datos_dashboard()` agrega `alertas` al dict

### Drill-Down
- **KPI click**: cada card-kpi obtiene `data-target="seccion-XXX"` y clase `cursor-pointer`. JS intercepta click → `scrollIntoView({ behavior: 'smooth' })` al目标
- **Gráfico doughnut click**: Chart.js `onClick` handler extrae `activeElements[0].index` → identifica rubro → filtro automático en tabla de rubros (resaltar fila, scroll)
- **Gráfico línea click**: `onClick` extrae período → parámetro de filtro, posible futuro drill-down a día específico
- **Navegación**: tabla de contenidos colapsable en sidebar o barra flotante con links a cada sección (`#seccion-xxx`)

### Mejoras UX
- **Loading states**: spinner CSS (`.dg-spinner`) en `card-body` mientras HTMX carga. Usar `htmx:beforeRequest` / `htmx:afterRequest` events
- **Empty states**: reemplazar "No hay datos..." por bloque con ícono Font Awesome grande + título + descripción contextual
- **Tooltips**: `data-bs-toggle="tooltip" data-bs-placement="top" title="..."` en labels de KPIs
- **Responsive**: alertas en columna en mobile, navegación como hamburger menu en `< 768px`

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modified | Agregar `get_alertas_gerenciales()`, extender `get_datos_dashboard()` |
| `routes/dashboard_gerencial.py` | Modified | Agregar endpoint `GET /api/dashboard-gerencial/alertas` |
| `templates/dashboard-gerencial.html` | Modified | Sección alertas, atributos `data-target`, tooltips, empty states, spinner |
| `static/js/dashboard-gerencial.js` | Modified | Drill-down handlers, loading states, navegación, tooltip init |
| `static/css/dashboard-gerencial.css` | Modified | Estilos alertas, spinner, empty states, navegación, responsive |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Performance: `get_alertas_gerenciales()` ejecuta queries extra en cada carga | Medium | Reutilizar funciones existentes que ya se llaman en `get_datos_dashboard()` — las alertas derivan de datos ya cargados, no ejecutan queries adicionales |
| Drill-down scroll falla si sección no está en DOM (HTMX lazy load) | Low | Usar `MutationObserver` o verificar existencia antes de scroll |
| Empty states personalizados rompen patrón existente de `{% else %}` | Low | Mantener mismo patrón Jinja2, solo mejorar contenido visual |
| Tooltip JS puede fallar si Bootstrap tooltip no está inicializado | Low | Verificar `typeof bootstrap !== 'undefined'` antes de init tooltips |

## Rollback Plan

1. Revertir cambios en los 5 archivos afectados (service, routes, template, JS, CSS)
2. El agregador `get_datos_dashboard()` vuelve a no incluir `alertas`
3. El template vuelve a no tener `#seccion-alertas`
4. El JS vuelve a no tener handlers de drill-down
5. No hay migraciones DB ni datos nuevos — rollback es 100% seguro

## Dependencies

- Ninguna dependencia externa nueva
- Bootstrap 5.3.3 tooltips (ya disponible via CDN en `base.html`)
- Font Awesome (ya disponible)

## Success Criteria

- [ ] 4 tipos de alerta se muestran cuando las condiciones se cumplen (no inventadas)
- [ ] Alertas desaparecen cuando no hay condiciones críticas (0 alertas = panel oculto)
- [ ] Click en KPI card hace smooth scroll a la sección correspondiente
- [ ] Click en segmento de doughnut resalta la fila de rubro en la tabla
- [ ] Loading spinner aparece durante carga HTMX y desaparece al completar
- [ ] Empty states muestran ilustración + mensaje contextual por sección
- [ ] Tooltips aparecen al hacer hover sobre labels de KPIs
- [ ] Responsive funciona en 320px, 768px, 1024px, 1440px
- [ ] Dashboard carga en < 3s con datos reales
- [ ] Ningún dato es inventado — todo viene de queries existentes
