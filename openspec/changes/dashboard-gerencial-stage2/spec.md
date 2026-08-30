# Dashboard Gerencial ERP — Etapa 2: Stock

## Overview

Extender el dashboard gerencial (Etapa 1) con análisis de inventario: KPIs de stock, stock por sucursal con valorización, y productos sin movimiento. Stock es punto-en-el-tiempo (sin filtro de fecha), excepto "sin movimiento" que usa ventana de lookback.

**Campo crítico**: La tabla `stocks` tiene `deseable` (NO `minimo`). Toda lógica de categorías usa `deseable` como umbral mínimo.

**Filtro de artículos**: `a.baja = '1900-01-01'` (activo) e `a.idtipoarticulo IN (1, 3)` (productos e insumos).

---

## ADDED Requirements

### F11: KPIs de Stock

The system SHALL classify each stock record into 4 categories using `stocks.deseable` as the minimum threshold:

| Category | SQL Condition |
|----------|--------------|
| Sin stock | `s.actual <= 0` |
| Bajo mínimo | `s.actual < s.deseable AND s.deseable > 0 AND s.actual > 0` |
| Stock saludable | `s.actual >= s.deseable AND (s.maximo IS NULL OR s.maximo = 0 OR s.actual <= s.maximo)` |
| Exceso | `s.actual > s.maximo AND s.maximo > 0` |

**Query base**:
```sql
SELECT
  COUNT(CASE WHEN s.actual <= 0 THEN 1 END) AS sin_stock,
  COUNT(CASE WHEN s.actual < s.deseable AND s.deseable > 0 AND s.actual > 0 THEN 1 END) AS bajo_minimo,
  COUNT(CASE WHEN s.actual >= s.deseable AND (s.maximo IS NULL OR s.maximo = 0 OR s.actual <= s.maximo) THEN 1 END) AS stock_saludable,
  COUNT(CASE WHEN s.actual > s.maximo AND s.maximo > 0 THEN 1 END) AS exceso,
  COUNT(*) AS total_articulos,
  COALESCE(SUM(s.actual * a.costo_total), 0) AS valor_total_stock
FROM stocks s
JOIN articulos a ON s.idarticulo = a.id
WHERE a.baja = '1900-01-01' AND a.idtipoarticulo IN (1, 3)
  [AND s.idsucursal = :id_sucursal]
```

**Valorización**: `valor_stock = cantidad_actual * costo_total` (costo actual, NO costo promedio histórico).

**Display**: 4 cards — Sin stock (danger), Bajo mínimo (warning), Stock saludable (success), Exceso (info). Badge con conteo + valor total.

#### Scenario: Clasificación con deseable NULL

- GIVEN artículo con `deseable = NULL`, `maximo = NULL`, `actual = 5`
- WHEN se clasifica el stock
- THEN categoría = "Stock saludable" (deseable NULL → sin umbral mínimo, maximo NULL → sin techo)

#### Scenario: Exceso de stock

- GIVEN artículo con `deseable = 10`, `maximo = 50`, `actual = 60`
- WHEN se clasifica
- THEN categoría = "Exceso" (actual > maximo AND maximo > 0)

---

### F12: Stock por Sucursal

The system SHALL return per-sucursal breakdown with units, estimated value, and category counts.

**Query**:
```sql
SELECT
  s.idsucursal,
  suc.nombre AS sucursal,
  COUNT(DISTINCT s.idarticulo) AS total_articulos,
  COALESCE(SUM(s.actual), 0) AS unidades_totales,
  COALESCE(SUM(CASE WHEN s.actual <= 0 THEN 1 ELSE 0 END), 0) AS sin_stock,
  COALESCE(SUM(CASE WHEN s.actual < s.deseable AND s.deseable > 0 AND s.actual > 0 THEN 1 ELSE 0 END), 0) AS bajo_minimo,
  COALESCE(SUM(s.actual * a.costo_total), 0) AS valor_estimado
FROM stocks s
JOIN articulos a ON s.idarticulo = a.id
JOIN sucursales suc ON s.idsucursal = suc.id
WHERE a.baja = '1900-01-01' AND a.idtipoarticulo IN (1, 3)
  [AND s.idsucursal = :id_sucursal]
GROUP BY s.idsucursal, suc.nombre
ORDER BY unidades_totales DESC
```

**Display**: Tabla con columnas Sucursal, Unidades, Valor Estimado ($), Sin Stock, Bajo Mínimo. Badges de color por categoría.

#### Scenario: Filtrado por sucursal

- GIVEN 3 sucursales con stock
- WHEN filtro sucursal = 2
- THEN la tabla muestra solo 1 fila (sucursal 2)
- AND los KPIs de F11 también se filtran por sucursal 2

---

### F13: Productos sin Movimiento

The system SHALL list articles with stock > 0 but no sales in the last N days (30/60/90, default 30). This is the ONLY stock metric that uses the date range (lookback window from today, NOT the global desde/hasta).

**Query**:
```sql
SELECT
  a.codigo, a.detalle,
  s.actual AS stock_actual,
  s.idsucursal,
  COALESCE(r.nombre, 'Sin rubro') AS rubro,
  MAX(f.fecha) AS ultima_venta
FROM articulos a
JOIN stocks s ON a.id = s.idarticulo
LEFT JOIN itemsv iv ON iv.idarticulo = a.id
LEFT JOIN facturav f ON iv.idfactura = f.id
  AND f.fecha >= DATE_SUB(CURDATE(), INTERVAL :dias DAY)
LEFT JOIN rubros r ON a.idrubro = r.id
WHERE a.baja = '1900-01-01' AND a.idtipoarticulo IN (1, 3)
  AND s.actual > 0
  [AND s.idsucursal = :id_sucursal]
GROUP BY a.id, a.codigo, a.detalle, s.actual, s.idsucursal, r.nombre
HAVING ultima_venta IS NULL OR ultima_venta < DATE_SUB(CURDATE(), INTERVAL :dias DAY)
ORDER BY ultima_venta ASC
LIMIT 100
```

**Dias toggle**: 30, 60, 90 —交互 via HTMX, parámetro `dias`.

**Display**: Tabla con columnas Código, Producto, Rubro, Stock Actual, Última Venta (o "Sin ventas"). Toggle de días arriba de la tabla.

#### Scenario: Producto sin ventas nunca

- GIVEN artículo con stock = 10, sin registros en itemsv
- WHEN toggle = 90 días
- THEN aparece en la lista con ultima_venta = "Sin ventas"
- AND se ordena primero (ASC)

#### Scenario: Límite de resultados

- GIVEN sucursal con 200 productos sin movimiento
- WHEN se ejecuta la query
- THEN se muestran máximo 100 filas
- AND indicador "Mostrando 100 de 200+" si hay más

---

## MODIFIED Requirements

### F1: Filtros Globales (Extendido)

Los filtros globales existentes SE MANTIENEN. El filtro de fecha (desde/hasta) NO aplica a KPIs de stock ni stock por sucursal (son punto-en-el-tiempo). Solo aplica a "productos sin movimiento" como ventana de lookback calculada desde la fecha actual.

(Previously: Filtros aplicaban a todas las queries igualmente)

#### Scenario: Filtro fecha ignora stock KPIs

- GIVEN período 01/07/2026 - 31/07/2026
- WHEN se cargan KPIs de stock
- THEN los conteos reflejan estado ACTUAL del inventario, no del período
- AND los datos de stock no cambian al modificar desde/hasta

---

## Non-Functional Requirements

| Requirement | Specification |
|-------------|--------------|
| **NF7: Stock point-in-time** | KPIs de stock y tabla por sucursal SHALL usar datos actuales sin filtro de fecha. |
| **NF8: Performance sin movimiento** | Query F13 SHALL usar `LIMIT 100`. Si >100 resultados, mostrar indicador de truncação. |
| **NF9: Valorización** | `valor_stock = actual * costo_total` (costo actual). Si `costo_total = 0`, mostrar "N/D" en valor de esa fila. |
| **NF10: Multi-sucursal stock** | Todas las queries de stock SHALL respetar filtro `idsucursal` cuando se especifica. |
| **NF11: Sin datos inventados** | Si no hay registros en `stocks`, mostrar "No hay datos de inventario disponibles". |

---

## API Specification

### `GET /api/dashboard-gerencial/stock-kpis`

**Parámetros query**: `id_sucursal` (opcional)

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "sin_stock": 15,
    "bajo_minimo": 42,
    "stock_saludable": 280,
    "exceso": 8,
    "total_articulos": 345,
    "valor_total_stock": "$ 12.500.000,00",
    "valor_total_stock_raw": 12500000.00
  }
}
```

### `GET /api/dashboard-gerencial/stock-sucursal`

**Parámetros query**: `id_sucursal` (opcional)

**Response JSON**:
```json
{
  "success": true,
  "data": [
    {
      "sucursal": "Central",
      "id_sucursal": 1,
      "total_articulos": 200,
      "unidades_totales": 1500,
      "sin_stock": 10,
      "bajo_minimo": 25,
      "valor_estimado": "$ 8.500.000,00",
      "valor_estimado_raw": 8500000.00
    }
  ]
}
```

### `GET /api/dashboard-gerencial/productos-sin-movimiento`

**Parámetros query**: `id_sucursal` (opcional), `dias` (30|60|90, default 30)

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "productos": [
      {
        "codigo": "ART-001",
        "detalle": "Producto ejemplo",
        "rubro": "Rubro A",
        "stock_actual": 15,
        "ultima_venta": "2026-05-15",
        "ultima_venta_display": "15/05/2026"
      }
    ],
    "total": 85,
    "mostrando": 85,
    "tiene_mas": false
  }
}
```

---

## Edge Cases

| Case | Behavior |
|------|----------|
| Sin registros en `stocks` | KPIs = 0 en todas las categorías, tabla sucursales vacía, "No hay datos de inventario" |
| `deseable = 0` o `NULL` | No cuenta como "bajo mínimo" — necesita mínimo explícito configurado |
| `maximo = 0` o `NULL` | No cuenta como "exceso" — necesita máximo explícito configurado |
| `costo_total = 0` en artículo | Valor de esa fila = "N/D", pero se cuenta en categorías |
| Filtro sucursal = NULL | Todas las queries muestran datos de todas las sucursales |
| Producto con stock > 0 y sin ventas | Aparece en F13 con ultima_venta = NULL → "Sin ventas" |
| Tabla `stocks` vacía para sucursal | Sucursal aparece con 0 en todos los campos |
| `articulos.baja != '1900-01-01'` | Artículo excluido de todas las queries de stock |
