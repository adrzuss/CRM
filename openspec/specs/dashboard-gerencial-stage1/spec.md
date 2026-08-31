# Dashboard Gerencial ERP — Etapa 1

## Purpose

Nuevo dashboard gerencial independiente en `/dashboard-gerencial` con filtros globales, 4 KPIs, evolución temporal, ventas por sucursal/rubro, top productos y top vendedores. Blueprint propio, sin modificar el reporte existente en `/tablero-gerencial`.

---

## Functional Requirements

### F1: Filtros Globales

The system SHALL provide filters: Período (desde/hasta, default últimos 30 días), Sucursal (select, default `session['id_sucursal']`, opción "Todas"), Comparar con período anterior (toggle, default off).

| Parameter | Type | Default | Validation |
|-----------|------|---------|------------|
| `desde` | date | hoy - 30 días | `>= 2020-01-01` |
| `hasta` | date | hoy | `<= hoy`, `>= desde` |
| `id_sucursal` | int | `session['id_sucursal']` | FK sucursales.id, NULL = todas |
| `comparar` | bool | false | — |

**Comparison period**: `desde_ant = desde - (hasta - desde + 1) días`, `hasta_ant = desde - 1 día`.

#### Scenario: Filtro por sucursal específica

- GIVEN sucursal "Central" con id=1
- WHEN usuario selecciona sucursal y hace click en "Actualizar"
- THEN todas las queries filtran `WHERE f.idsucursal = 1`
- AND el dashboard muestra solo datos de esa sucursal

#### Scenario: Todas las sucursales

- WHEN usuario selecciona "Todas" en filtro sucursal
- THEN no se aplica filtro `idsucursal` en las queries
- AND se muestran datos agregados de todas las sucursales

---

### F2: KPIs — Ventas Totales

**Data source**: `facturav` → `tipo_comprobantes` → `tipo_comp_aplica` → `tipo_operacion`

**SQL base**:
```sql
SELECT
  COALESCE(SUM(CASE WHEN top.nombre IN ('VENTA','DEBITO') THEN f.total ELSE -f.total END), 0) AS total_ventas,
  COUNT(f.id) AS cantidad_operaciones,
  COALESCE(AVG(f.total), 0) AS ticket_promedio
FROM facturav f
JOIN clientes c ON f.idcliente = c.id
JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
  AND tca.id_iva_entidad = c.id_tipo_iva
JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
WHERE f.fecha BETWEEN :desde AND :hasta
  AND top.nombre IN ('VENTA','CREDITO','DEBITO')
  [AND f.idsucursal = :id_sucursal]  -- solo si filtro activo
```

**Filtro sucursal**: agregar `AND f.idsucursal = :id_sucursal` cuando `id_sucursal IS NOT NULL`.

**Variación %**: `((actual - anterior) / anterior) * 100`. Si `anterior = 0`, mostrar "N/D".

#### Scenario: Cálculo ventas con notas de crédito

- GIVEN período con 3 facturas VENTA ($1000, $500, $2000) y 1 NOTA DE CRÉDITO ($300)
- WHEN se calcula ventas totales
- THEN total = $1000 + $500 + $2000 - $300 = $3200
- AND operaciones = 4

---

### F3: KPIs — Cobranzas

**Data source**: `pagos_fv` → `facturav`

**SQL**:
```sql
SELECT COALESCE(SUM(pf.total), 0) AS total_cobranzas
FROM pagos_fv pf
JOIN facturav f ON pf.idfactura = f.id
WHERE f.fecha BETWEEN :desde AND :hasta
  [AND f.idsucursal = :id_sucursal]
```

**Variación %**: misma fórmula que F2.

#### Scenario: Cobranzas con filtro sucursal

- GIVEN sucursal id=2 con cobranzas de $5000
- WHEN filtro sucursal = 2
- THEN cobranzas muestra $5000
- AND no incluye cobranzas de otras sucursales

---

### F4: KPIs — Margen Bruto

**Data source**: `facturav` + `itemsv` + `articulos`

**SQL** (costo mercadería vendida):
```sql
SELECT COALESCE(SUM(iv.cantidad * a.costo_total), 0) AS costo_total
FROM itemsv iv
JOIN facturav f ON iv.idfactura = f.id
JOIN clientes c ON f.idcliente = c.id
JOIN articulos a ON iv.idarticulo = a.id
JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
  AND tca.id_iva_entidad = c.id_tipo_iva
JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
WHERE f.fecha BETWEEN :desde AND :hasta
  AND top.nombre IN ('VENTA','CREDITO','DEBITO')
  [AND f.idsucursal = :id_sucursal]
```

**Fórmula**: `margen_bruto = ventas_totales - costo_total`. `pct_margen = (margen_bruto / ventas_totales) * 100`. Si `ventas_totales = 0`, `pct_margen = 0`.

#### Scenario: Margen con costo cero

- GIVEN ventas = $10000, costo_total = $0 (artículos sin costo registrado)
- WHEN se calcula margen
- THEN margen_bruto = $10000, pct_margen = 100%
- AND el KPI muestra el valor calculado sin alerta

---

### F5: KPIs — Ticket Promedio

**Fórmula**: `ticket_promedio = total_ventas / cantidad_operaciones`. Si `cantidad_operaciones = 0`, ticket = $0.

Viene del mismo query que F2. No requiere query adicional.

#### Scenario: Ticket promedio con operaciones cero

- GIVEN período sin facturas
- WHEN se calcula ticket promedio
- THEN ticket = $0.00
- AND variación = "N/D"

---

### F6: Evolución de Ventas (Gráfico Línea)

**Data source**: `facturav` → joins tipo_operacion

**Granularidad automática**: ≤31 días → diario, ≤180 días → semanal, >180 días → mensual.

**SQL diario** (ejemplo):
```sql
SELECT
  DATE_FORMAT(f.fecha, '%d/%m') AS periodo,
  f.fecha AS fecha_orden,
  COALESCE(SUM(CASE WHEN top.nombre IN ('VENTA','DEBITO') THEN f.total ELSE -f.total END), 0) AS total
FROM facturav f
JOIN clientes c ON f.idcliente = c.id
JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
  AND tca.id_iva_entidad = c.id_tipo_iva
JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
WHERE f.fecha BETWEEN :desde AND :hasta
  AND top.nombre IN ('VENTA','CREDITO','DEBITO')
  [AND f.idsucursal = :id_sucursal]
GROUP BY f.fecha
ORDER BY f.fecha
```

**Semanal**: `GROUP BY YEAR(f.fecha), WEEK(f.fecha, 1)`, periodo = `CONCAT('Sem ', WEEK(f.fecha, 1))`.

**Mensual**: `GROUP BY DATE_FORMAT(f.fecha, '%Y-%m')`, periodo = `DATE_FORMAT(f.fecha, '%b %Y')`.

**Toggle granularity**: usuario puede cambiar entre diario/semanal/mensual manualmente.

**Overlay período anterior**: si `comparar = true`, ejecutar mismo query con fechas del período anterior y superponer como línea punteada.

#### Scenario: Evolución diaria con comparación

- GIVEN período 01/08/2026 - 15/08/2026, comparar = true
- WHEN se carga el dashboard
- THEN el gráfico muestra línea sólida para agosto 2026
- AND línea punteada para 17/07/2026 - 31/07/2026

---

### F7: Ventas por Sucursal (Tabla)

**Data source**: `facturav` → `sucursales` → joins tipo_operacion

**SQL**:
```sql
SELECT
  s.id, s.nombre,
  COUNT(f.id) AS operaciones,
  COALESCE(SUM(CASE WHEN top.nombre IN ('VENTA','DEBITO') THEN f.total ELSE -f.total END), 0) AS venta_neta,
  COALESCE(AVG(f.total), 0) AS ticket_promedio
FROM facturav f
JOIN sucursales s ON f.idsucursal = s.id
JOIN clientes c ON f.idcliente = c.id
JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
  AND tca.id_iva_entidad = c.id_tipo_iva
JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
WHERE f.fecha BETWEEN :desde AND :hasta
  AND top.nombre IN ('VENTA','CREDITO','DEBITO')
GROUP BY s.id, s.nombre
ORDER BY venta_neta DESC
```

**Participación %**: `(venta_neta / total_todas_sucursales) * 100`. Si `total = 0`, participación = 0%.

**Filtro sucursal**: cuando se selecciona una sucursal, esta tabla muestra solo esa fila (o se oculta si solo hay 1 sucursal).

#### Scenario: Reporte multi-sucursal

- GIVEN 3 sucursales con ventas $5000, $3000, $2000
- WHEN filtro = "Todas"
- THEN tabla muestra 3 filas ordenadas por venta_neta DESC
- AND participaciones: 50%, 30%, 20%

---

### F8: Ventas por Rubro (Tabla + Doughnut)

**Data source**: `facturav` → `itemsv` → `articulos` → `rubros`

**SQL**:
```sql
SELECT
  r.id, r.nombre AS rubro,
  SUM(iv.cantidad) AS unidades,
  SUM(iv.precio_total) AS importe
FROM itemsv iv
JOIN facturav f ON iv.idfactura = f.id
JOIN clientes c ON f.idcliente = c.id
JOIN articulos a ON iv.idarticulo = a.id
LEFT JOIN rubros r ON a.idrubro = r.id
JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
  AND tca.id_iva_entidad = c.id_tipo_iva
JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
WHERE f.fecha BETWEEN :desde AND :hasta
  AND top.nombre IN ('VENTA','CREDITO','DEBITO')
  [AND f.idsucursal = :id_sucursal]
GROUP BY r.id, r.nombre
ORDER BY importe DESC
```

**Participación %**: `(importe / total_rubros) * 100`.

**Doughnut Chart.js config**: tipo `doughnut`, datos = importe por rubro, labels = nombre rubro, colores de paleta definida.

#### Scenario: Rubro sin nombre

- GIVEN artículo con `idrubro = NULL`
- WHEN se agrupa por rubro
- THEN se muestra como "Sin rubro"
- AND se incluye en el doughnut

---

### F9: Top 10 Productos

**Data source**: `itemsv` → `articulos` → `facturav` → joins tipo_operacion

**SQL**:
```sql
SELECT
  a.codigo, a.detalle,
  r.nombre AS rubro,
  SUM(iv.cantidad) AS cantidad_vendida,
  SUM(iv.precio_total) AS total_vendido,
  SUM(iv.cantidad * a.costo_total) AS costo_vendido
FROM itemsv iv
JOIN facturav f ON iv.idfactura = f.id
JOIN clientes c ON f.idcliente = c.id
JOIN articulos a ON iv.idarticulo = a.id
LEFT JOIN rubros r ON a.idrubro = r.id
JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
  AND tca.id_iva_entidad = c.id_tipo_iva
JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
WHERE f.fecha BETWEEN :desde AND :hasta
  AND top.nombre IN ('VENTA','CREDITO','DEBITO')
  [AND f.idsucursal = :id_sucursal]
GROUP BY a.id, a.codigo, a.detalle, r.nombre
ORDER BY total_vendido DESC
LIMIT 10
```

**Margen por producto**: `total_vendido - costo_vendido`.

#### Scenario: Producto sin rubro

- GIVEN artículo sin idrubro
- WHEN se ordena por total_vendido
- THEN rubro muestra "Sin rubro"
- AND el producto se incluye en el ranking

---

### F10: Top 10 Vendedores

**Data source**: `facturav` → `usuarios` (via `idusuario`) → joins tipo_operacion

**SQL**:
```sql
SELECT
  u.id, u.nombre AS vendedor,
  COUNT(f.id) AS operaciones,
  COALESCE(SUM(CASE WHEN top.nombre IN ('VENTA','DEBITO') THEN f.total ELSE -f.total END), 0) AS ventas_totales,
  COALESCE(AVG(f.total), 0) AS ticket_promedio
FROM facturav f
JOIN usuarios u ON f.idusuario = u.id
JOIN clientes c ON f.idcliente = c.id
JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
  AND tca.id_iva_entidad = c.id_tipo_iva
JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
WHERE f.fecha BETWEEN :desde AND :hasta
  AND top.nombre IN ('VENTA','CREDITO','DEBITO')
  [AND f.idsucursal = :id_sucursal]
GROUP BY u.id, u.nombre
ORDER BY ventas_totales DESC
LIMIT 10
```

**Participación %**: `(ventas_totales / total_vendedores) * 100`.

#### Scenario: Vendedor confacturas anuladas

- GIVEN vendedor con 3 ventas ($2000) y 1 crédito ($500)
- WHEN se calcula ventas del vendedor
- THEN ventas_totales = $1500
- AND operaciones = 4

---

### F17: Agregador `get_datos_dashboard()`

The system SHALL extend the aggregator `get_datos_dashboard()` to include creditos section data alongside existing sections AND rubro-sucursal comparison data.

The aggregator SHALL add:
- `creditos_kpis`: result of `get_creditos_kpis(id_sucursal)`
- `creditos_top`: result of `get_creditos_top_deudores(limite=10, id_sucursal=id_sucursal)`
- `rubro_sucursal`: result of `get_rubro_sucursal_comparacion(desde, hasta)`

#### Scenario: Agregador incluye créditos y rubro-sucursal

- GIVEN `get_datos_dashboard()` called with valid params
- WHEN response is assembled
- THEN returned dict contains keys `creditos_kpis`, `creditos_top`, and `rubro_sucursal`
- AND all keys contain valid data structures

---

### F18: Sección Cuentas por Cobrar en Dashboard

The system SHALL display a "Cuentas por Cobrar" section in the dashboard after the "Productos sin Movimiento" section, containing 3 KPI cards (saldo total, vencido, por vencer) and a badge with the count of clients with debt.

The section SHALL load via HTMX from endpoint `/api/dashboard-gerencial/cta-cobrar-kpis`.

#### Scenario: Sección visible en dashboard

- GIVEN usuario accede al dashboard gerencial
- WHEN se carga la página
- THEN la sección "Cuentas por Cobrar" aparece después de "Productos sin Movimiento"
- AND muestra 3 KPI cards con saldos formateados

---

### F19: Top Deudores en Dashboard

The system SHALL display a "Top Deudores" table after the "Cuentas por Cobrar" KPIs section.

The table SHALL load via HTMX from endpoint `/api/dashboard-gerencial/cta-cobrar-top`.

#### Scenario: Tabla de deudores visible

- GIVEN hay clientes con saldo > 0
- WHEN se carga el dashboard
- THEN la tabla "Top Deudores" muestra filas con #, Cliente, Documento, Saldo
- AND está ordenada por saldo DESC

---

### F20: Sección Cuentas por Pagar en Dashboard

The system SHALL display a "Cuentas por Pagar" section containing 3 KPI cards (saldo total, vencido, por vencer).

The section SHALL load via HTMX from endpoint `/api/dashboard-gerencial/cta-pagar-kpis`.

---

### F21: Top Proveedores en Dashboard

The system SHALL display a "Top Proveedores" table after the "Cuentas por Pagar" KPIs section.

The table SHALL load via HTMX from endpoint `/api/dashboard-gerencial/cta-pagar-top`.

#### Scenario: Tabla de proveedores visible

- GIVEN hay proveedores con saldo > 0
- WHEN se carga el dashboard
- THEN la tabla "Top Proveedores" muestra filas con #, Proveedor, FantasÍa, Saldo
- AND está ordenada por saldo DESC

---

### F28: Agregador extiende con Bancos y Caja

The system SHALL extend `get_datos_dashboard()` to include bancos and caja sections. No existing behavior is modified.

The aggregator SHALL add:
- `bancos_kpis`: result of `get_bancos_kpis(desde, hasta)`
- `bancos_detalle`: result of `get_bancos_detalle(desde, hasta)`
- `caja_kpis`: result of `get_caja_kpis(desde, hasta, id_sucursal)`
- `caja_rendiciones`: result of `get_caja_rendiciones_recientes(id_sucursal, limite=10)`

#### Scenario: Agregador incluye bancos y caja

- GIVEN `get_datos_dashboard()` called with valid params
- WHEN response is assembled
- THEN returned dict contains keys `bancos_kpis`, `bancos_detalle`, `caja_kpis`, `caja_rendiciones`
- AND all keys contain valid data structures

---

### F29: Sección Bancos en Dashboard

The system SHALL display a "Bancos" section in the dashboard after "Créditos", containing 3 KPI cards (saldo total, movimientos del mes, ingresos vs egresos) and a table per bank with saldo and participación %.

The section SHALL load via HTMX from endpoint `/api/dashboard-gerencial/bancos-kpis` and `/api/dashboard-gerencial/bancos-detalle`.

#### Scenario: Sección visible en dashboard

- GIVEN usuario accede al dashboard gerencial
- WHEN se carga la página
- THEN la sección "Bancos" aparece después de "Créditos"
- AND muestra 3 KPI cards + tabla por banco

---

### F30: Sección Caja en Dashboard

The system SHALL display a "Caja" section in the dashboard after "Bancos", containing 2 KPI cards (total efectivo, rendiciones del mes) and a table of last 10 rendiciones.

The section SHALL load via HTMX from endpoint `/api/dashboard-gerencial/caja-kpis` and `/api/dashboard-gerencial/caja-rendiciones`.

#### Scenario: Sección visible en dashboard

- GIVEN usuario accede al dashboard gerencial
- WHEN se carga la página
- THEN la sección "Caja" aparece después de "Bancos"
- AND muestra 2 KPI cards + tabla rendiciones recientes

---

## Non-Functional Requirements

| Requirement | Specification |
|-------------|--------------|
| **NF1: Rendimiento** | Queries SHALL ejecutarse en < 2s. Rango de fechas máximo 90 días por defecto. |
| **NF2: Moneda** | Todos los valores monetarios SHALL usar `Decimal`. Formato visual: `$ 1.250.450,50`. |
| **NF3: Multi-sucursal** | Todas las queries SHALL respetar filtro `idsucursal` cuando se especifica. |
| **NF4: Sin datos inventados** | Si no hay datos, mostrar "Este indicador requiere información que actualmente no está disponible". |
| **NF5: Compatibilidad** | Chart.js 4.4.1 CDN. Bootstrap 5.3.3. HTMX 1.9.10. Chrome/Firefox/Edge recientes. |
| **NF6: Seguridad** | Todas las rutas SHALL usar `@check_session`. Scripts inline con `{{ g.nonce }}`. |
| **NF12: Sin inventar datos** | Si `cta_cte_cliente` o `cta_cte_prov` están vacías, los widgets muestran "No disponible" en lugar de $0 |
| **NF13: Decimal monetario** | Todos los saldos de cta_cte SHALL usar `Decimal` internamente. Formato visual: `$ 1.250.450,50` |
| **NF14: Multi-sucursal cta_cte** | Queries de cta_cte SHALL respetar filtro `idsucursal` cuando se especifica |
| **NF15: Días vencimiento default** | Default `dias_vencimiento = 30`. Toggle 30/60/90交互 via HTMX |
| **NF16: Performance** | Queries de cta_cte SHALL usar `LIMIT` en top deudores/proveedores (default 10) |
| **NF17: Bancos sin filtro sucursal** | Queries de bancos SHALL NO usar filtro `idsucursal` (campo no existe en `bancos_propios`) |
| **NF18: Caja con filtro sucursal** | Queries de caja SHALL respetar filtro `idsucursal` cuando se especifica |
| **NF19: Saldo acumulado bancos** | Saldo total bancos SHALL ser acumulado de TODOS los movimientos, sin filtro de período |
| **NF20: Decimal monetario** | Todos los valores de bancos/caja SHALL usar `Decimal` internamente |
| **NF21: Sin datos inventados** | Si no hay movimientos bancarios o rendiciones, mostrar "No hay..." en lugar de $0 |

---

## API Specification

Los endpoints existentes SE MANTIENEN. Se agregan 4 nuevos endpoints HTMX para secciones de cuentas por cobrar/pagar.

### `GET /dashboard-gerencial`

Ruta principal. Renderiza template completo con datos server-side.

**Parámetros query**: `desde`, `hasta`, `id_sucursal`, `comparar`

**Response**: HTML (render_template con data context)

### `GET /api/dashboard-gerencial/datos`

Endpoint JSON para refresh HTMX por sección.

**Parámetros query**: `desde`, `hasta`, `id_sucursal`, `comparar`, `seccion` (uno de: `kpis`, `evolucion`, `sucursales`, `rubros`, `top_productos`, `top_vendedores`, `cta_cobrar_kpis`, `cta_cobrar_top`, `cta_pagar_kpis`, `cta_pagar_top`, `creditos_kpis`, `creditos_top`, `bancos_kpis`, `bancos_detalle`, `caja_kpis`, `caja_rendiciones`)

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "kpis": { ... },
    "evolucion": { ... },
    "sucursales": [...],
    "rubros": [...],
    "top_productos": [...],
    "top_vendedores": [...],
    "cta_cobrar_kpis": { "saldo_total": "...", "saldo_vencido": "...", "saldo_por_vencer": "...", "clientes_con_deuda": "..." },
    "cta_cobrar_top": [...],
    "cta_pagar_kpis": { "saldo_total": "...", "saldo_vencido": "...", "saldo_por_vencer": "..." },
    "cta_pagar_top": [...]
  }
}
```

### `GET /api/dashboard-gerencial/cta-cobrar-kpis`

KPIs de cuentas por cobrar.

**Parámetros query**: `dias_vencimiento` (opcional, default 30)

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "saldo_total": "...",
    "saldo_vencido": "...",
    "saldo_por_vencer": "...",
    "clientes_con_deuda": "..."
  }
}
```

### `GET /api/dashboard-gerencial/cta-cobrar-top`

Top deudores.

**Parámetros query**: `limite` (opcional, default 10), `dias_vencimiento` (opcional, default 30)

**Response JSON**:
```json
{
  "success": true,
  "data": [
    { "nombre": "...", "documento": "...", "saldo": "...", "ultima_fecha": "..." }
  ]
}
```

### `GET /api/dashboard-gerencial/cta-pagar-kpis`

KPIs de cuentas por pagar.

**Parámetros query**: `dias_vencimiento` (opcional, default 30)

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "saldo_total": "...",
    "saldo_vencido": "...",
    "saldo_por_vencer": "...",
    "proveedores_con_deuda": "..."
  }
}
```

### `GET /api/dashboard-gerencial/cta-pagar-top`

Top proveedores.

**Parámetros query**: `limite` (opcional, default 10), `dias_vencimiento` (opcional, default 30)

**Response JSON**:
```json
{
  "success": true,
  "data": [
    { "nombre": "...", "fantasia": "...", "saldo": "...", "ultima_fecha": "..." }
  ]
}
```

**Error**: `{ "success": false, "message": "Error: ..." }` con status 500.

#### Scenario: Endpoints cta_cte responden correctamente

- GIVEN dashboard cargado
- WHEN HTMX hace GET a `/api/dashboard-gerencial/cta-cobrar-kpis`
- THEN response JSON contiene `saldo_total`, `saldo_vencido`, `saldo_por_vencer`, `clientes_con_deuda`
- AND status = 200

#### Scenario: Parámetro dias_vencimiento en endpoints

- GIVEN endpoint `/api/dashboard-gerencial/cta-cobrar-kpis?dias_vencimiento=60`
- WHEN se ejecuta la query
- THEN los saldos vencidos/por vencer se calculan con umbral de 60 días

### `GET /api/dashboard-gerencial/bancos-kpis`

KPIs bancarios: saldo total, movimientos del mes, ingresos vs egresos.

**Parámetros query**: `desde`, `hasta` (NO `id_sucursal` — bancos son globales)

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "saldo_total_bancos": "$ 1.250.000,00",
    "saldo_total_bancos_raw": 1250000.00,
    "movimientos_mes": 45,
    "ingresos_mes": "$ 800.000,00",
    "ingresos_mes_raw": 800000.00,
    "egresos_mes": "$ 350.000,00",
    "egresos_mes_raw": 350000.00
  }
}
```

### `GET /api/dashboard-gerencial/bancos-detalle`

Detalle de saldos por banco con participación %.

**Parámetros query**: `desde`, `hasta` (NO `id_sucursal`)

**Response JSON**:
```json
{
  "success": true,
  "data": [
    {
      "banco": "Banco Nación",
      "id_banco": 1,
      "saldo": "$ 500.000,00",
      "saldo_raw": 500000.00,
      "movimientos": 20,
      "participacion": 40.0
    }
  ]
}
```

### `GET /api/dashboard-gerencial/caja-kpis`

KPIs de rendiciones de caja.

**Parámetros query**: `desde`, `hasta`, `id_sucursal` (opcional)

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "total_efectivo": "$ 250.000,00",
    "total_efectivo_raw": 250000.00,
    "total_otros_valores": "$ 80.000,00",
    "total_otros_valores_raw": 80000.00,
    "cantidad_rendiciones": 12
  }
}
```

### `GET /api/dashboard-gerencial/caja-rendiciones`

Últimas rendiciones de caja.

**Parámetros query**: `desde`, `hasta`, `id_sucursal` (opcional), `limite` (opcional, default 10)

**Response JSON**:
```json
{
  "success": true,
  "data": [
    {
      "fecha": "15/08/2026",
      "usuario": "Juan Pérez",
      "sucursal": "Central",
      "total_ventas": "$ 45.000,00",
      "total_efectivo": "$ 35.000,00",
      "total_otros_valores": "$ 10.000,00"
    }
  ]
}
```

---

## UI Specification

El layout existente SE MANTIENE. Se agregan 4 nuevas secciones al final del dashboard, después de "Productos sin Movimiento".

- **Layout**: Extiende `base.html`. 4 columnas de KPI cards arriba, gráfico evolución full-width, 2 tablas lado a lado (sucursales + rubros), doughnut al lado de rubros, **Comparación Rubro × Sucursal (full-width)**, 2 tablas abajo (top productos + top vendedores), luego secciones de cuentas por cobrar/pagar.

### UI Specification (layout order)

The layout SHALL add a new full-width section "Comparación Rubro × Sucursal" after the existing Sucursales y Rubros cards and before the Top Productos section.

#### Scenario: Layout con sección cross-tab

- GIVEN dashboard completo
- WHEN se renderiza
- THEN la sección "Comparación Rubro × Sucursal" aparece después de Sucursales/Rubros
- AND antes de Top Productos
- **Responsive**: KPI cards → 2 columnas en tablet, 1 en móvil. Tablas → scroll horizontal en móvil.
- **Chart.js**: Línea (evolución), Doughnut (rubros). Paleta de colores consistente.
- **Filtros**: Barra superior con date inputs, select sucursal, toggle comparar, botón actualizar. HTMX `hx-get` para refresh de secciones individuales.
- **Nonce**: Todos los `<script>` usan `nonce="{{ g.nonce }}"`.

#### Scenario: Layout con todas las secciones

- GIVEN dashboard completo con Etapas 1+2+3+4+5+6
- WHEN se renderiza
- THEN el orden de secciones es: KPIs → Evolución → Sucursales → Rubros → Comparación Rubro × Sucursal → Top Productos → Top Vendedores → Stock KPIs → Stock por Sucursal → Sin Movimiento → Ctas por Cobrar → Top Deudores → Ctas por Pagar → Top Proveedores → Créditos KPIs → Top Deudores por Crédito → Bancos KPIs → Saldos por Banco → Caja KPIs → Últimas Rendiciones

#### Scenario: Badges de saldo vencido/por vencer

- GIVEN sección de cuentas por cobrar con datos
- WHEN se muestra el KPI de saldo vencido
- THEN el badge usa clase CSS `badge-danger`
- AND saldo por vencer usa `badge-success`

---

## ADDED Requirements (Stage 6)

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
| Período sin facturas | KPIs = $0, variación = "N/D", gráfico sin datos, tablas vacías |
| `anterior = 0` para variación % | Mostrar "N/D" en lugar de dividir por cero |
| Sucursal sin ventas en período | No aparece en tabla de sucursales |
| Artículo sin rubro | Agrupado como "Sin rubro" |
| `costo_total = 0` en artículos | Margen = ventas totales (100%), sin alerta |
| Comparar activado con período anterior vacío | Línea punteada no se muestra, variaciones = "N/D" |
| Rango > 90 días | Permitir, pero default = 30 días |
| Consumidor Final en top clientes | Se separa: identificados en tabla principal, CF en sección aparte |
| Bancos sin movimientos | saldo_total = $0, tabla vacía, "No hay movimientos bancarios" |
| Caja sin rendiciones | total_efectivo = $0, tabla "No hay rendiciones recientes" |
| Filtro sucursal en bancos | Ignorado — bancos muestran saldo total general |
| Filtro sucursal en caja | Aplica — solo rendiciones de esa sucursal |
| HTMX falla request | Spinner se oculta, sección muestra estado de error |
| Bootstrap tooltip no disponible | JS verifica `typeof bootstrap !== 'undefined'` antes de init |
| Sección lazy-load no existe | drill-down scroll no se ejecuta |
| 0 secciones en navegación | Barra de navegación se oculta |
