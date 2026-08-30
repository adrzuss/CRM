# Exploration: Dashboard Gerencial — Etapa 2 (Stock)

**Date**: 2026-08-29
**Status**: COMPLETE

---

## 1. Stocks Table Structure

**Table**: stocks
**Model**: models/articulos.py line 81, class Stock

`sql
CREATE TABLE stocks (
  idstock         INT NOT NULL AUTO_INCREMENT,
  idarticulo      INT NOT NULL,
  idsucursal      INT NOT NULL,
  actual          DECIMAL(20,6) NOT NULL,
  maximo          DECIMAL(20,6) DEFAULT NULL,
  deseable        DECIMAL(20,6) DEFAULT NULL,
  en_transito_entrada DECIMAL(20,6) NOT NULL,
  en_transito_salida  DECIMAL(20,6) NOT NULL,
  PRIMARY KEY (idstock, idarticulo, idsucursal)
);
`

### Key Findings

| Field | Purpose | Nullable |
|-------|---------|----------|
| ctual | Current stock quantity | NO |
| deseable | Desired minimum level (NOT minimo) | YES |
| maximo | Maximum stock level | YES |
| en_transito_entrada | Units inbound (transfer) | NO |
| en_transito_salida | Units outbound (transfer) | NO |

**CRITICAL**: There is NO minimo field. The field is deseable. This is consistent with:
- get_stock_faltantes() stored procedure (line 190306 erp-tienda.sql): uses s.deseable > s.actual
- lerta_stocks_limite() (stock.py line 29): uses Stock.deseable > 0, Stock.actual < Stock.deseable
- get_estado_inventario() (reportes.py line 462): uses st.actual < st.deseable

### Indexes

| Index | Columns | Type |
|-------|---------|------|
| PRIMARY | (idstock, idarticulo, idsucursal) | Composite PK |
| idarticulo | (idarticulo) | FK index |
| idsucursal | (idsucursal) | FK index |

**Missing index**: No composite index on (idsucursal, actual) — queries filtering by sucursal + stock conditions will need to scan.

---

## 2. Stock Category Mapping

The prompt master defined 4 categories. Here is the mapping using the actual schema:

| Category | SQL Condition | Notes |
|----------|--------------|-------|
| **Sin stock** | s.actual <= 0 | Matches existing lerta_stocks_faltante() |
| **Bajo minimo** | s.actual < s.deseable AND s.deseable > 0 AND s.actual > 0 | Uses deseable not minimo. Matches get_stock_faltantes() SP |
| **Stock saludable** | s.actual >= s.deseable AND (s.maximo IS NULL OR s.maximo = 0 OR s.actual <= s.maximo) | Between deseable and maximo |
| **Exceso** | s.actual > s.maximo AND s.maximo > 0 | Matches get_estado_inventario() |

**Observation**: The prompt master's reference to stocks.minimo does not exist. The correct field is stocks.deseable. This must be called out in the spec.

### Article Filtering

- Only include .baja = date(1900, 1, 1) (active articles, NOT aja IS NULL — see inconsistency in reportes.py)
- Existing stored procedures filter by .idtipoarticulo IN (1, 3) (productos e insumos)
- The dashboard gerencial should match this pattern for consistency

---

## 3. Stock Per Sucursal

The stocks table is **already per-sucursal**. Each row = one article + one sucursal.

### Aggregation Logic

**When id_sucursal is provided (single sucursal filter)**:
`sql
WHERE s.idsucursal = :id_sucursal
`

**When id_sucursal is NULL (all sucursales)**:
- For category counts: aggregate COUNT(DISTINCT s.idarticulo)
- For sucursal breakdown: GROUP BY s.idsucursal, suc.nombre
- For valuation: SUM(s.actual * a.costo_total) grouped by sucursal

---

## 4. Productos Sin Movimiento

### Detection Strategy

"Sin movimiento" = articles with stock but no sales in the last 30/60/90 days.

**Approach**: LEFT JOIN articles with their last sale date via itemsv + acturav.

`sql
SELECT
  a.id, a.codigo, a.detalle,
  s.actual, s.idsucursal,
  COALESCE(r.nombre, 'Sin rubro') AS rubro,
  MAX(f.fecha) AS ultima_venta
FROM articulos a
JOIN stocks s ON a.id = s.idarticulo
LEFT JOIN itemsv iv ON iv.idarticulo = a.id
LEFT JOIN facturav f ON iv.idfactura = f.id
  AND f.fecha >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
LEFT JOIN rubros r ON a.idrubro = r.id
WHERE a.baja = '1900-01-01'
  AND s.actual > 0
  [AND s.idsucursal = :id_sucursal]
GROUP BY a.id, a.codigo, a.detalle, s.actual, s.idsucursal, r.nombre
HAVING ultima_venta IS NULL OR ultima_venta < DATE_SUB(CURDATE(), INTERVAL :dias DAY)
`

**Alternative**: Pre-compute last sale date per article, then filter. But the JOIN approach is simpler and sufficient.

**Dias options**: 30, 60, 90 — could be a toggle in the UI.

### Performance Concern

This query joins itemsv (which can be large) with acturav for date filtering. Need an index on acturav.fecha (should exist since Stage 1 uses it heavily) and itemsv.idarticulo.

**Existing indexes to verify**:
- itemsv: primary key includes idfactura and id, plus idarticulo FK
- acturav: PK on id, likely index on echa

---

## 5. Existing Code Patterns to Reuse

### From services/reportes.py (get_estado_inventario, line 427)

Already computes sin_stock, stock_critico (bajo deseable), and exceso. **Can be refactored** to work with the dashboard gerencial's filtering (by sucursal, date-independent).

### From services/articulos/stock.py

- lerta_stocks_faltante(): counts articles with ctual <= 0 per sucursal
- lerta_stocks_limite(): counts articles with ctual < deseable per sucursal
- get_stocks_negativos(): calls SP get_stock_negativos(sucursal)
- get_stocks_faltantes(): calls SP get_stock_faltantes(sucursal)

### From outes/dashboard_gerencial.py

- _parsear_filtros() — reuse for stock endpoints (date range less relevant for stock, but sucursal filter is)
- _api_respuesta() — reuse wrapper for JSON responses

### From 	emplates/dashboard-gerencial.html

- Section pattern: <div id="seccion-{name}" class="row mb-4"> with card headers
- KPI cards: card-kpi border-start-{color} pattern
- Tables: 	able-dashboard table-sm with consistent header styling

---

## 6. New Service Functions Needed

| Function | Purpose | Dependencies |
|----------|---------|-------------|
| get_resumen_stock(id_sucursal) | 4 category counts + total value + total articles | stocks, articulos |
| get_stock_por_sucursal(id_sucursal) | Per-sucursal breakdown: units, value, sin_stock count, bajo_minimo count | stocks, articulos, sucursales |
| get_productos_sin_movimiento(id_sucursal, dias) | Articles with stock but no sales in N days | stocks, articulos, itemsv, facturav |
| get_datos_stock(id_sucursal) | Aggregator for all stock data | above 3 functions |

### Route Endpoints Needed

| Route | Method | Purpose |
|-------|--------|---------|
| /api/dashboard-gerencial/stock-resumen | GET | Returns 4 category KPIs + valuation |
| /api/dashboard-gerencial/stock-sucursales | GET | Returns per-sucursal stock table |
| /api/dashboard-gerencial/stock-sin-movimiento | GET | Returns sin movimiento table |

---

## 7. Template Section Structure

### Recommended Layout

`
<!-- SECCIÓN: Stock KPIs (4 cards) -->
<div id="seccion-stock-kpis" class="row mb-4">
  <!-- Sin Stock card (danger) -->
  <!-- Bajo Mínimo card (warning) -->
  <!-- Stock Saludable card (success) -->
  <!-- Exceso card (info) -->
</div>

<!-- SECCIÓN: Stock por Sucursal + Valorización -->
<div class="row mb-4">
  <!-- Stock por Sucursal (table with progress bars) — col-7 -->
  <!-- Valorización del Inventario (summary card) — col-5 -->
</div>

<!-- SECCIÓN: Productos sin Movimiento -->
<div id="seccion-stock-sin-movimiento" class="row mb-4">
  <!-- Full-width table with toggle 30/60/90 days -->
</div>
`

### KPI Card Colors (matching Stage 1 palette)

| Category | Border Color | Icon | Badge Color |
|----------|-------------|------|-------------|
| Sin Stock | danger (#e74a3b) | fa-exclamation-triangle | bg-danger |
| Bajo Mínimo | warning (#f6c23e) | fa-arrow-down | bg-warning |
| Stock Saludable | success (#1cc88a) | fa-check-circle | bg-success |
| Exceso | info (#36b9cc) | fa-arrow-up | bg-info |

---

## 8. JS/Chart.js Additions

- No new chart types needed for Stage 2 stock section
- Sin movimiento table: interactive toggle (30/60/90 days) via HTMX or fetch
- Stock per sucursal: horizontal bar chart optional (could be table-only)

---

## 9. Inconsistencies Found

### aja Field Convention

- **Model default**: aja = date(1900, 1, 1) means "active" (not deleted)
- **reportes.py get_estado_inventario()**: Uses WHERE a.baja IS NULL — this is WRONG for this codebase
- **services/articulos/reportes.py**: Uses Articulo.baja == date(1900, 1, 1) — CORRECT
- **Stored procedures**: Use .idtipoarticulo IN (1, 3) but don't filter baja at all

**Decision needed**: Should Stage 2 use .baja = '1900-01-01' (correct pattern) or .baja IS NULL (matches reportes.py)? Recommend .baja = '1900-01-01' for consistency with the actual application pattern.

### 	ipo_articulos Filter

- Stored procedures filter idtipoarticulo IN (1, 3) (productos e insumos)
- get_estado_inventario() doesn't filter by type
- Stage 2 should match the stored procedure pattern for consistency

---

## 10. Edge Cases

| Case | Behavior |
|------|----------|
| Sucursal sin stock records | Show 0 for all categories |
| Todos los artículos sin stock | Sin Stock = total articles, others = 0 |
| deseable = 0 or NULL | Don't count as "bajo mínimo" — need explicit minimum set |
| maximo = 0 or NULL | Don't count as "exceso" — need explicit maximum set |
| Artículos con colores/talles | Stocks exist per artículo, not per color/talle variant |
| Sin movimiento with no sales ever | Include in 90-day bucket (ultima_venta IS NULL) |
| Filtro sucursal applied | Filter stock by idsucursal, ignore sucursal table |

---

## 11. Recommendations

1. **Use deseable not minimo**: All references should say "bajo mínimo" but the field is deseable
2. **Add composite index** on (idsucursal, actual) if query performance is poor
3. **Filter by aja = '1900-01-01'** not aja IS NULL
4. **Filter by idtipoarticulo IN (1, 3)** for consistency with existing stock queries
5. **Sin movimiento**: Use LEFT JOIN approach, not subquery, for readability
6. **Date filters**: Stock data is point-in-time, not date-range based. The desde/hasta filter doesn't apply to stock KPIs — only to "sin movimiento" (which needs a lookback window)
7. **Evaluator note**: sin movimiento is the only stock metric that depends on the date range filters
