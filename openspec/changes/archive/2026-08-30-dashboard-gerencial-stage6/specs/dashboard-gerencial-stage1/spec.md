# Dashboard Gerencial ERP — Etapa 1 (Modified by Stage 6)

## ADDED Requirements

### F33: Drill-Down por KPI Cards

The system SHALL add `data-target="seccion-{nombre}"` attribute and `cursor-pointer` class to each KPI card. Click SHALL trigger smooth scroll to the target section.

**Targets mapping**:

| KPI Card | `data-target` | Scrolls to |
|----------|---------------|------------|
| Ventas Totales | `seccion-ventas` | Gráfico de evolución |
| Cobranzas | `seccion-cobranzas` | Top vendedores |
| Margen Bruto | `seccion-margen` | Top productos |
| Ticket Promedio | `seccion-ticket` | Ventas por sucursal |

#### Scenario: Click en KPI ventas

- GIVEN dashboard cargado con KPI "Ventas Totales" visible
- WHEN usuario hace click en la card de Ventas
- THEN scroll suave hasta `#seccion-ventas` (gráfico evolución)
- AND sección destino queda visible en viewport

#### Scenario: Sección destino no existe en DOM

- GIVEN KPI card con `data-target="seccion-xxx"` pero sección no renderizada (HTMX lazy)
- WHEN usuario hace click
- THEN scroll NO se ejecuta (JS verifica `document.getElementById(target)` antes de scroll)

---

### F34: Drill-Down por Gráfico Doughnut

The system SHALL add Chart.js `onClick` handler to the rubros doughnut. Click on a segment SHALL highlight the corresponding row in the rubros table and scroll to it.

#### Scenario: Click en segmento de rubro

- GIVEN doughnut con 5 rubros, tabla rubros visible
- WHEN usuario hace click en segmento "Electrónica"
- THEN fila "Electrónica" en tabla recibe clase `table-active` (resaltado)
- AND scroll suave hasta la tabla de rubros

#### Scenario: Click fuera de segmento

- GIVEN doughnut interactivo
- WHEN usuario hace click en área vacía del gráfico
- THEN no se ejecuta ninguna acción de highlight

---

### F35: Drill-Down por Gráfico Línea

The system SHALL add Chart.js `onClick` handler to the evolución line chart. Click on a data point SHALL extract the period and navigate to filtered view.

#### Scenario: Click en punto del gráfico

- GIVEN gráfico de evolución con datos diarios
- WHEN usuario hace click en punto del 15/08/2026
- THEN se agrega parámetro `periodo=15/08/2026` a la URL
- AND dashboard recarga con ese período seleccionado

---

### F36: Navegación entre Secciones

The system SHALL provide a collapsible navigation bar (table of contents) with links to each dashboard section. Navigation SHALL be a sticky element positioned below the filter bar.

**Sections in navigation**: KPIs, Evolución, Sucursales, Rubros, Top Productos, Top Vendedores, Stock, Cta Cobrar, Cta Pagar, Créditos, Bancos, Caja.

#### Scenario: Navegación visible en desktop

- GIVEN dashboard en viewport > 768px
- WHEN página carga
- THEN barra de navegación sticky aparece debajo de filtros
- AND muestra links a cada sección

#### Scenario: Navegación colapsable en mobile

- GIVEN dashboard en viewport < 768px
- WHEN página carga
- THEN navegación se muestra como botón hamburger
- AND click abre dropdown con links a secciones

---

### F37: Loading States HTMX

The system SHALL show a loading spinner in each HTMX-powered section during fetch. Spinner SHALL use class `.dg-spinner` with CSS animation.

**Implementation**: CSS spinner en `card-body` de cada sección. JS escucha eventos `htmx:beforeRequest` → muestra spinner, `htmx:afterRequest` → oculta spinner.

#### Scenario: Spinner durante carga HTMX

- GIVEN sección "Cuentas por Cobrar" con HTMX `hx-get`
- WHEN HTMX inicia request
- THEN spinner `.dg-spinner` aparece dentro de `card-body`
- AND datos originales se ocultan

#### Scenario: Spinner desaparece al completar

- GIVEN spinner visible durante carga
- WHEN HTMX completa request exitosamente
- THEN spinner se oculta
- AND datos cargados se muestran

---

### F38: Empty States Mejorados

The system SHALL replace generic "No hay datos..." messages with contextual empty states per section. Each empty state SHALL include: Font Awesome icon (48px), title, and descriptive message.

**Empty states por sección**:

| Sección | Icono | Título | Mensaje |
|---------|-------|--------|---------|
| KPIs Ventas | `fa-chart-line` | Sin ventas en este período | "No se registraron operaciones en el rango seleccionado" |
| Stock | `fa-boxes-stacked` | Inventario no disponible | "No hay datos de inventario para esta sucursal" |
| Cta Cobrar | `fa-hand-holding-dollar` | Sin deudores | "Todos los clientes están al día con sus pagos" |
| Cta Pagar | `fa-file-invoice-dollar` | Sin proveedores con deuda | "No hay facturas pendientes de pago" |
| Créditos | `fa-credit-card` | Sin créditos activos | "No hay créditos registrados en el sistema" |
| Bancos | `fa-building-columns` | Sin movimientos bancarios | "No se registraron movimientos en el período" |
| Caja | `fa-cash-register` | Sin rendiciones | "No hay rendiciones de caja en este período" |

#### Scenario: Empty state cta cobrar sin deudores

- GIVEN no hay clientes con saldo > 0
- WHEN se carga sección cta cobrar
- THEN se muestra ícono `fa-hand-holding-dollar`, título "Sin deudores", mensaje "Todos los clientes están al día"
- AND NO se muestra tabla vacía

---

### F39: Tooltips en KPIs

The system SHALL add Bootstrap 5 tooltips to KPI card labels using `data-bs-toggle="tooltip"`.

**Tooltips**:

| KPI | Tooltip Text |
|-----|-------------|
| Ventas Totales | "Suma neta de ventas y débitos menos notas de crédito" |
| Cobranzas | "Total de pagos recibidos de clientes en el período" |
| Margen Bruto | "Ventas menos costo de mercadería vendida" |
| Ticket Promedio | "Promedio de ventas por operación" |
| Stock Saludable | "Artículos con stock entre mínimo y máximo configurado" |

#### Scenario: Tooltip al hover

- GIVEN KPI card con label "Ventas Totales"
- WHEN usuario hace hover sobre el label
- THEN tooltip aparece con texto "Suma neta de ventas y débitos menos notas de crédito"
- AND tooltip desaparece al quitar hover

---

### F40: Responsive Design

The system SHALL provide responsive refinements for alerts, navigation, and tables across breakpoints.

| Breakpoint | Alertas | Navegación | Tablas |
|------------|---------|------------|--------|
| < 576px | 1 columna, apiladas | Hamburger dropdown | Scroll horizontal |
| 576–768px | 1 columna | Hamburger dropdown | Scroll horizontal |
| 768–1024px | 2 columnas | Barra visible | Scroll horizontal |
| > 1024px | 2–3 columnas | Barra sticky | Scroll horizontal |

#### Scenario: Alertas en mobile

- GIVEN viewport 375px (iPhone)
- WHEN se muestran 3 alertas
- THEN alertas se apilan en 1 columna
- AND cada alerta ocupa ancho completo

#### Scenario: Tabla responsive

- GIVEN tabla "Ventas por Sucursal" con 6 columnas
- WHEN viewport < 768px
- THEN tabla tiene scroll horizontal
- AND columnas no se apilan (maintain table structure)

---

## Edge Cases

| Case | Behavior |
|------|----------|
| HTMX falla request | Spinner se oculta, sección muestra estado de error |
| Bootstrap tooltip no disponible | JS verifica `typeof bootstrap !== 'undefined'` antes de init |
| Sección lazy-load no existe | drill-down scroll no se ejecuta |
| 0 secciones en navegación | Barra de navegación se oculta |
