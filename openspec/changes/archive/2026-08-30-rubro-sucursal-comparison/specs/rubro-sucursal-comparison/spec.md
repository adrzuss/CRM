# Rubro-Sucursal Comparison — Specification

## Purpose

Cross-tab table showing rubro participation by sucursal with comparison indicators. Each cell shows units count and percentage. Indicator compares sucursal's rubro % vs. its overall benchmark participation.

## Requirements

### F1: Service Function `get_rubro_sucursal_comparacion`

The system SHALL provide a function `get_rubro_sucursal_comparacion(desde, hasta)` that returns cross-tab data.

**SQL**: Single query grouping by `(rubro, sucursal)` using the same JOIN chain as `get_ventas_rubro`:

```sql
SELECT
  COALESCE(r.nombre, 'Sin rubro') AS rubro,
  s.nombre AS sucursal,
  s.id AS id_sucursal,
  COALESCE(SUM(iv.cantidad), 0) AS unidades
FROM itemsv iv
JOIN facturav f ON iv.idfactura = f.id
JOIN articulos a ON iv.idarticulo = a.id
LEFT JOIN rubros r ON a.idrubro = r.id
JOIN sucursales s ON f.idsucursal = s.id
JOIN clientes c ON f.idcliente = c.id
JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
  AND tca.id_iva_entidad = c.id_tipo_iva
JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
WHERE f.fecha BETWEEN :desde AND :hasta
  AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
GROUP BY r.id, r.nombre, s.id, s.nombre
ORDER BY r.nombre, s.nombre
```

**Python pivot**: The system SHALL pivot query results into cross-tab structure:
- Rows: rubros (unique names, sorted alphabetically)
- Columns: sucursales (unique names, sorted alphabetically)
- Each cell: `{ 'unidades': int, 'porcentaje': float }`

**Percentage calculation**: `porcentaje = (cell_unidades / total_unidades_sucursal) * 100`. Where `total_unidades_sucursal` is the sum of all rubro units for that specific sucursal. If `total_unidades_sucursal = 0`, percentage = 0.

**Benchmark**: The system SHALL calculate each sucursal's overall participation across all rubros: `benchmark_sucursal = (total_unidades_sucursal / grand_total_units) * 100`.

**Indicator**: The system SHALL compare each cell's `porcentaje` vs. the cell's sucursal `benchmark`:
- If `porcentaje > benchmark`: indicator = `"up"` (↑)
- If `porcentaje < benchmark`: indicator = `"down"` (↓)
- If `porcentaje == benchmark`: indicator = `"neutral"` (—)

**Return structure**:

```python
{
  'rubros': ['Electrónica', 'Blanco', 'Sin rubro'],       # sorted alphabetically
  'sucursales': ['Central', 'Norte'],                       # sorted alphabetically
  'cells': {                                                # nested dict
    'Electrónica': {
      'Central': { 'unidades': 150, 'porcentaje': 35.2, 'indicator': 'up' },
      'Norte':   { 'unidades': 80,  'porcentaje': 22.1, 'indicator': 'down' }
    }
  },
  'benchmarks': {                                           # per-sucursal overall %
    'Central': 28.5,
    'Norte': 31.2
  },
  'grand_total': 425
}
```

#### Scenario: Cross-tab con 2 sucursales y 3 rubros

- GIVEN período con ventas en 2 sucursales (Central, Norte) y 3 rubros (Electrónica, Blanco, Sin rubro)
- WHEN se ejecuta `get_rubro_sucursal_comparacion(desde, hasta)`
- THEN se retorna dict con `rubros` = 3 nombres, `sucursales` = 2 nombres
- AND `cells` contiene 6 entradas (3 rubros × 2 sucursales)
- AND cada celda tiene `unidades`, `porcentaje`, `indicator`

#### Scenario: Cálculo de porcentaje por sucursal

- GIVEN Central con 100 unidades Electrónica y 50 unidades Blanco (total 150)
- WHEN se calcula porcentaje Electrónica/Central
- THEN porcentaje = (100 / 150) × 100 = 66.7%

#### Scenario: Cálculo de benchmark

- GIVEN Central con 150 unidades total, Norte con 120 unidades total, grand_total = 270
- WHEN se calcula benchmark Central
- THEN benchmark Central = (150 / 270) × 100 = 55.6%

#### Scenario: Indicador up cuando porcentaje > benchmark

- GIVEN Electrónica/Central porcentaje = 66.7%, benchmark Central = 55.6%
- WHEN se compara porcentaje vs benchmark
- THEN indicator = "up"

#### Scenario: Indicador down cuando porcentaje < benchmark

- GIVEN Blanco/Central porcentaje = 33.3%, benchmark Central = 55.6%
- WHEN se compara porcentaje vs benchmark
- THEN indicator = "down"

#### Scenario: Sucursal sin ventas en rubro

- GIVEN Norte no tiene ventas de Electrónica en el período
- THEN celda Norte/Electrónica tiene unidades=0, porcentaje=0, indicator="down"
- AND la celda existe en `cells` con valores por defecto

#### Scenario: Sin datos de ventas

- GIVEN período sin facturas
- WHEN se ejecuta la función
- THEN se retorna estructura vacía: rubros=[], sucursales=[], cells={}, grand_total=0

#### Scenario: Error SQL

- GIVEN error de conexión a base de datos
- WHEN se ejecuta la función
- THEN se retorna estructura vacía: rubros=[], sucursales=[], cells={}, grand_total=0

---

### F2: HTMX API Endpoint

The system SHALL provide endpoint `GET /api/dashboard-gerencial/rubro-sucursal`.

**Parameters query**: `desde`, `hasta` (mismos que dashboard principal).

**Response JSON**:

```json
{
  "success": true,
  "data": {
    "rubros": ["Electrónica", "Blanco"],
    "sucursales": ["Central", "Norte"],
    "cells": { ... },
    "benchmarks": { "Central": 55.6, "Norte": 44.4 },
    "grand_total": 270
  }
}
```

**Error**: `{ "success": false, "message": "Error: ..." }` con status 500.

#### Scenario: Endpoint responde correctamente

- GIVEN dashboard cargado
- WHEN HTMX hace GET a `/api/dashboard-gerencial/rubro-sucursal?desde=2026-08-01&hasta=2026-08-30`
- THEN response JSON contiene `rubros`, `sucursales`, `cells`, `benchmarks`, `grand_total`
- AND status = 200

#### Scenario: Parámetros faltantes

- GIVEN endpoint sin parámetros desde/hasta
- WHEN se ejecuta
- THEN se usan defaults del dashboard (últimos 30 días)

---

### F3: Template Cross-Tab Table

The system SHALL render a full-width cross-tab table section after the existing Sucursales y Rubros cards.

**Table structure**:
- Header row: "Rubro" | sucursal_1 | sucursal_2 | ... | sucursal_N
- Each sucursal column header: sucursal name
- Each data row: rubro name | cell(sucursal_1) | cell(sucursal_2) | ...
- Cell content: units count + percentage (e.g., "150 uds (35.2%)")
- Indicator: arrow icon next to percentage (↑ green, ↓ red, — neutral)

**Single sucursal behavior**: When `len(sucursales) == 1`, the system SHALL hide the indicator column (since comparison is meaningless). Table shows rubro | units | percentage only.

**Empty state**: When no rubro data available, the system SHALL show contextual empty state: icon `fa-table-cells`, title "Sin datos de comparación", message "No hay ventas de rubros en el período seleccionado".

**Responsive**: Table SHALL use `table-responsive` wrapper for horizontal scroll on mobile.

#### Scenario: Tabla con 2 sucursales

- GIVEN cross-tab con 2 sucursales y 3 rubros
- WHEN se renderiza el template
- THEN tabla tiene 4 columnas: Rubro | Central | Norte
- AND cada celda muestra "150 uds (66.7%) ↑"

#### Scenario: Una sola sucursal

- GIVEN cross-tab con 1 sola sucursal (Central)
- WHEN se renderiza el template
- THEN columna de indicador se oculta
- AND tabla muestra: Rubro | Central
- AND celdas muestran "100 uds (66.7%)" sin indicador

#### Scenario: Sin datos

- GIVEN período sin ventas
- WHEN se carga la sección
- THEN se muestra empty state con ícono y mensaje
- AND NO se muestra tabla vacía

#### Scenario: Responsive en mobile

- GIVEN tabla cross-tab con 4+ columnas
- WHEN viewport < 768px
- THEN tabla tiene scroll horizontal
- AND primera columna (Rubro) queda fija si es posible

---

### F4: CSS Indicator Styles

The system SHALL provide CSS rules for indicator arrows:

- `.indicator-up`: color green (Bootstrap `text-success`), arrow ↑
- `.indicator-down`: color red (Bootstrap `text-danger`), arrow ↓
- `.indicator-neutral`: color muted (Bootstrap `text-muted`), dash —

#### Scenario: Estilos aplicados

- GIVEN celda con indicator="up"
- WHEN se renderiza
- THEN flecha ↑ usa color green y clase `indicator-up`

---

### F5: Dashboard Aggregator Extension

The system SHALL extend `get_datos_dashboard()` to include rubro-sucursal comparison data. The aggregator SHALL add:

- `rubro_sucursal`: result of `get_rubro_sucursal_comparacion(desde, hasta)`

#### Scenario: Agregador incluye rubro-sucursal

- GIVEN `get_datos_dashboard()` called with valid params
- WHEN response is assembled
- THEN returned dict contains key `rubro_sucursal`
- AND key contains valid cross-tab data structure
