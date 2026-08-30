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

## Non-Functional Requirements

| Requirement | Specification |
|-------------|--------------|
| **NF1: Rendimiento** | Queries SHALL ejecutarse en < 2s. Rango de fechas máximo 90 días por defecto. |
| **NF2: Moneda** | Todos los valores monetarios SHALL usar `Decimal`. Formato visual: `$ 1.250.450,50`. |
| **NF3: Multi-sucursal** | Todas las queries SHALL respetar filtro `idsucursal` cuando se especifica. |
| **NF4: Sin datos inventados** | Si no hay datos, mostrar "Este indicador requiere información que actualmente no está disponible". |
| **NF5: Compatibilidad** | Chart.js 4.4.1 CDN. Bootstrap 5.3.3. HTMX 1.9.10. Chrome/Firefox/Edge recientes. |
| **NF6: Seguridad** | Todas las rutas SHALL usar `@check_session`. Scripts inline con `{{ g.nonce }}`. |

---

## API Specification

### `GET /dashboard-gerencial`

Ruta principal. Renderiza template completo con datos server-side.

**Parámetros query**: `desde`, `hasta`, `id_sucursal`, `comparar`

**Response**: HTML (render_template con data context)

### `GET /api/dashboard-gerencial/datos`

Endpoint JSON para refresh HTMX por sección.

**Parámetros query**: `desde`, `hasta`, `id_sucursal`, `comparar`, `seccion` (uno de: `kpis`, `evolucion`, `sucursales`, `rubros`, `top_productos`, `top_vendedores`)

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "kpis": { "ventas_totales": "...", "cobranzas": "...", "margen_bruto": "...", "ticket_promedio": "...", "variaciones": {...} },
    "evolucion": { "periodos": [...], "totales": [...], "periodos_anterior": [...], "totales_anterior": [...] },
    "sucursales": [...],
    "rubros": [...],
    "top_productos": [...],
    "top_vendedores": [...]
  }
}
```

**Error**: `{ "success": false, "message": "Error: ..." }` con status 500.

---

## UI Specification

- **Layout**: Extiende `base.html`. 4 columnas de KPI cards arriba, gráfico evolución full-width, 2 tablas lado a lado (sucursales + rubros), doughnut al lado de rubros, 2 tablasabajo (top productos + top vendedores).
- **Responsive**: KPI cards → 2 columnas en tablet, 1 en móvil. Tablas → scroll horizontal en móvil.
- **Chart.js**: Línea (evolución), Doughnut (rubros). Paleta de colores consistente.
- **Filtros**: Barra superior con date inputs, select sucursal, toggle comparar, botón actualizar. HTMX `hx-get` para refresh de secciones individuales.
- **Nonce**: Todos los `<script>` usan `nonce="{{ g.nonce }}"`.

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
