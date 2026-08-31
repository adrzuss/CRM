# Exploration: Rubro-Sucursal Comparison Table

**Change**: rubro-sucursal-comparison
**Date**: 2026-08-30
**Status**: Exploration Complete

---

## 1. Current State Analysis

### 1.1 How Rubros Are Currently Queried

**Function**: `get_ventas_rubro(desde, hasta, id_sucursal)` -- `services/dashboard_gerencial.py:326-377`

- **Query path**: `itemsv -> facturav -> articulos -> rubros` (LEFT JOIN on `a.idrubro = r.id`)
- **Filter**: Standard sales filter (`top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')`) + optional sucursal filter
- **GROUP BY**: `r.id, r.nombre`
- **Returns**: `{'rubros': [...], 'total_importe': N}` where each rubro has: `rubro`, `importe`, `importe_raw`, `unidades`, `participacion`
- **Key detail**: Units are `SUM(iv.cantidad)` (line 339). Participation is calculated as `importe / total_importe * 100` (line 364).

### 1.2 How Sucursales Are Currently Queried

**Function**: `get_ventas_sucursal(desde, hasta, id_sucursal)` -- `services/dashboard_gerencial.py:262-322`

- **Query path**: `facturav -> sucursales`
- **GROUP BY**: `f.idsucursal, s.nombre`
- **Returns**: list of dicts with `sucursal`, `id_sucursal`, `ventas_totales`, `operaciones`, `ticket_promedio`, `participacion`
- **Key detail**: When `id_sucursal` is set, only that sucursal is returned (filtered out).

### 1.3 What the Template Expects

**Section**: `templates/dashboard-gerencial.html:210-313` ("Sucursales y Rubros")

Currently renders two side-by-side cards:
- **Left (col-xl-7)**: "Ventas por Sucursal" table -- iterates `data.sucursales`
- **Right (col-xl-5)**: "Ventas por Rubro" card with doughnut chart + table -- iterates `data.rubros.rubros`

The new comparison table should go **below** these two existing cards, as a new full-width row.

### 1.4 Database Schema (Key Tables)

| Table | Key Columns | Notes |
|-------|-------------|-------|
| `facturav` | `id`, `fecha`, `total`, `idsucursal`, `idcliente`, `idtipocomprobante` | Sales invoices |
| `itemsv` | `idfactura`, `idarticulo`, `cantidad`, `precio_total` | Invoice line items |
| `articulos` | `id`, `idrubro` | Products with FK to rubros |
| `rubros` | `id`, `nombre` | Product categories |
| `sucursales` | `id`, `nombre` | Branch locations |

**Join chain for rubro x sucursal**:
```
itemsv iv
  JOIN facturav f ON iv.idfactura = f.id
  JOIN articulos a ON iv.idarticulo = a.id
  LEFT JOIN rubros r ON a.idrubro = r.id
  JOIN sucursales s ON f.idsucursal = s.id
  JOIN clientes c ON f.idcliente = c.id
  JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
  JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp AND tca.id_iva_entidad = c.id_tipo_iva
  JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
```

---

## 2. Cross-Tab Query Design

### 2.1 SQL Query

A single query groups by `(rubro_id, rubro_name, sucursal_id, sucursal_name)`, returning units per combination. The pivot to cross-tab is done in Python.

```sql
SELECT
    COALESCE(r.nombre, 'Sin rubro') AS rubro,
    COALESCE(r.id, 0) AS rubro_id,
    s.nombre AS sucursal,
    f.idsucursal AS id_sucursal,
    COALESCE(SUM(iv.cantidad), 0) AS unidades,
    COALESCE(SUM(iv.precio_total), 0) AS importe
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
GROUP BY r.id, r.nombre, f.idsucursal, s.nombre
ORDER BY r.nombre, unidades DESC
```

**Why this approach**: Matches the exact same JOIN chain and filter pattern used in `get_ventas_rubro` (line 335-354) and `get_ventas_sucursal` (line 273-295). No new tables, no new joins.

### 2.2 Python Pivot Logic

After fetching the flat result, the service function pivots into a cross-tab structure:

```python
def get_rubro_sucursal_comparacion(desde, hasta):
    """Cross-tab: rubros (rows) x sucursales (columns) with comparison indicators."""
    # 1. Execute the flat query above
    # 2. Pivot into: {rubro: {sucursal: {unidades, importe}}}
    # 3. Calculate totals per rubro (row total) and per sucursal (column total)
    # 4. For each cell, calculate:
    #    - cell_pct = cell_unidades / row_total_unidades * 100
    #    - benchmark_pct = sucursal_total_units / grand_total_units * 100
    #    - indicator = 'above' if cell_pct > benchmark_pct else 'below' (or 'equal')
    # 5. Return structured data for template
```

### 2.3 Comparison Indicator Logic

The indicator answers: **"Does this sucursal over-index or under-index in this rubro compared to the overall average?"**

For each cell (rubro R, sucursal S):
- **cell_pct** = S's units for R / Total units for R across ALL sucursales x 100
- **benchmark_pct** = S's total units across ALL rubros / Grand total units x 100
- If `cell_pct > benchmark_pct`: **UP** (above average participation for this rubro)
- If `cell_pct < benchmark_pct`: **DOWN** (below average participation)
- If equal: **EQUAL**

**Example**: If "Central" has 40% of total units overall, but only 20% of "Electro" units, then Central is UNDER-indexed in Electro (DOWN indicator).

**Why not simple average (100% / num_sucursales)?** Because sucursales have different sizes. A large sucursal selling 40% of everything should be expected to sell ~40% of Electro too. If it only sells 20%, that is notable.

---

## 3. Data Structure for Template

```python
{
    'rubros': [
        {
            'rubro': 'Blanco',
            'rubro_id': 5,
            'total_unidades': 30,
            'total_pct': 8.0,          # % of grand total
            'sucursales': [
                {
                    'sucursal': 'Central',
                    'id_sucursal': 1,
                    'unidades': 10,
                    'importe_raw': 15000,
                    'pct': 33.3,       # 10/30 = 33.3% of this rubro
                    'indicator': 'below',
                    'indicator_arrow': '↓',
                },
                {
                    'sucursal': 'Norte',
                    'id_sucursal': 2,
                    'unidades': 5,
                    'importe_raw': 8000,
                    'pct': 16.7,
                    'indicator': 'above',
                    'indicator_arrow': '↑',
                },
            ]
        },
        ...
    ],
    'sucursales_headers': [
        {'id_sucursal': 1, 'nombre': 'Central'},
        {'id_sucursal': 2, 'nombre': 'Norte'},
    ],
    'grand_total_unidades': 375,
}
```

**Important**: When `id_sucursal` filter is active, the table should still show **all** sucursales to enable comparison. The date filter applies, but the cross-tab always includes every sucursal. This is the whole point of the feature.

---

## 4. Files to Modify

### 4.1 Service Layer
**File**: `services/dashboard_gerencial.py`
- Add new function: `get_rubro_sucursal_comparacion(desde, hasta)`
- Add it to `get_datos_dashboard()` (line 1386-1417) as a new key in the return dict
- Estimated: ~60-80 lines (query + pivot logic)

### 4.2 Routes Layer
**File**: `routes/dashboard_gerencial.py`
- Import the new function (line 11-33)
- Add new HTMX API endpoint: `/api/dashboard-gerencial/rubro-sucursal`
- Estimated: ~8 lines

### 4.3 Template
**File**: `templates/dashboard-gerencial.html`
- Add a new full-width row after line 313 (after the existing Sucursales y Rubros row)
- Complex table with two-row `<thead>`: first row has group headers (Total + per-sucursal), second row has sub-headers (Unid. % indicator)
- Use `table-responsive` wrapper for horizontal scroll with many sucursales
- Estimated: ~60-80 lines of Jinja2

### 4.4 JavaScript
**File**: `static/js/dashboard-gerencial.js`
- No changes needed. Table is server-rendered with Jinja2, matching the pattern of every other table in the dashboard.

### 4.5 CSS
**File**: `static/css/dashboard-gerencial.css`
- Styles for indicator arrows (green for UP, red for DOWN)
- Styles for grouped column headers (subtle background for sucursal groups)
- Estimated: ~30-40 lines

---

## 5. Edge Cases and Risks

| Case | Handling |
|------|----------|
| **Only 1 sucursal** | Comparison is meaningless -- hide the indicator column or show only Total column |
| **No rubros data** | Empty state message, same pattern as existing tables (line 296-306) |
| **Rubro with 0 units in a sucursal** | Show "0" and "-" indicator (equal, no deviation) |
| **Many sucursales (>6)** | Horizontal scroll via `table-responsive` (already used throughout) |
| **Articles without rubro** | Already handled: `COALESCE(r.nombre, 'Sin rubro')` (same as `get_ventas_rubro`) |
| **id_sucursal filter active** | Table shows ALL sucursales regardless (see Section 3). The filter applies to date range context only. |

---

## 6. Performance Considerations

- **Single query** for the entire cross-tab -- no N+1, no multiple queries
- **Index needed**: Ensure `itemsv(idfactura)`, `facturav(idsucursal, fecha)`, `articulos(idrubro)` are indexed (likely already are from existing queries)
- **Cardinality**: Rubros are typically 10-30, sucursales 3-10. Result set: 30-300 rows max -- trivial for MySQL
- **No stored procedure needed** -- same raw SQL pattern as all other dashboard functions

---

## 7. Recommendations

1. **Use `unidades` (units) as the primary metric**, not `importe`. Units are more meaningful for cross-sucursal comparison (prices may vary by region). Importe can be shown as secondary if needed.

2. **Place the new table as a full-width card below the existing Sucursales y Rubros row**. The existing two cards stay unchanged.

3. **No JS needed** -- server-render with Jinja2, matching the pattern of every other table in the dashboard.

4. **The indicator logic should be computed in Python**, not SQL. The cross-tab pivot + indicator calculation is cleaner in Python than building complex CASE/WHEN in MySQL.

5. **Follow the exact same JOIN chain** as `get_ventas_rubro` (lines 335-354) to ensure data consistency with the existing rubro table.

6. **When `id_sucursal` is set**, the new table should still show all sucursales. The existing sucursal/rubro tables already show filtered data; this table's purpose is comparison.
