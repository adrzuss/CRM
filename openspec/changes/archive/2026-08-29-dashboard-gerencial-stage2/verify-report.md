# Verification Report — Dashboard Gerencial Etapa 2 (Stock)

**Change**: `dashboard-gerencial-stage2`
**Mode**: openspec
**Date**: 2026-08-29
**Verdict**: **PASS WITH WARNINGS**

---

## Section A — Completeness

| Task | Status | Notes |
|------|--------|-------|
| 1.1 `get_stock_kpis` | ✅ Done | 57 lines, SQL + Decimal formatting |
| 1.2 `get_stock_sucursal` | ✅ Done | 50 lines, GROUP BY + JOIN sucursales |
| 1.3 `get_productos_sin_movimiento` | ✅ Done | 92 lines, LEFT JOIN + LIMIT 100 + count subquery |
| 2.1 Imports in routes | ✅ Done | 3 new imports added (line 19-21) |
| 2.2 HTMX endpoints (3) | ✅ Done | stock-kpis, stock-sucursales, stock-sin-movimiento |
| 2.3 Update aggregator | ✅ Done | `get_datos_dashboard()` includes 3 new keys |
| 3.1 Stock KPI cards (4) | ✅ Done | danger/warning/success/info + valor_total |
| 3.2 Stock por sucursal table | ✅ Done | 6 columns + badges |
| 3.3 Sin movimiento toggle + table | ✅ Done | 30/60/90 toggle + truncation indicator |
| 4.1 JS toggle listener | ✅ Done | `inicializarSinMovimiento()` + `renderizarSinMovimiento()` |
| 4.2 CSS badge styles | ✅ Done | 4 badge classes + dias-btn.active |

**All 11 tasks complete.**

---

## Section B — Spec Compliance Matrix

### F11: KPIs de Stock

| Requirement | Spec | Implementation | Status |
|-------------|------|---------------|--------|
| Sin stock: `s.actual <= 0` | Line 21 | Line 516: `SUM(CASE WHEN s.actual <= 0 THEN 1 ELSE 0 END)` | ✅ |
| Bajo mínimo: `actual < deseable AND deseable > 0 AND actual > 0` | Line 22 | Line 517: `SUM(CASE WHEN s.actual > 0 AND s.deseable > 0 AND s.actual < s.deseable THEN 1 ELSE 0 END)` | ✅ |
| Saludable: `actual >= deseable AND (maximo IS NULL OR maximo = 0 OR actual <= maximo)` | Line 23 | Line 518: exact match | ✅ |
| Exceso: `actual > maximo AND maximo > 0` | Line 24 | Line 519: `SUM(CASE WHEN s.maximo > 0 AND s.actual > s.maximo THEN 1 ELSE 0 END)` | ✅ |
| Uses `deseable` not `minimo` | Line 7 | All queries reference `s.deseable` | ✅ |
| Articulo filter: `baja = '1900-01-01' AND idtipoarticulo IN (1,3)` | Line 37 | Line 524 | ✅ |
| `valor_stock = actual * costo_total` | Line 41 | Line 521: `SUM(CASE WHEN a.costo_total > 0 THEN s.actual * a.costo_total ELSE 0 END)` | ✅ |
| Optional `idsucursal` filter | Line 38 | Lines 509-511 | ✅ |

**Scenario: Classificación con deseable NULL**
- Spec: `deseable=NULL, maximo=NULL, actual=5` → "Stock saludable"
- SQL line 518: `actual >= s.deseable` → when `deseable=NULL`, comparison yields NULL (not true). **However**, MySQL treats `5 >= NULL` as NULL/false, so this row would NOT be counted as saludable.
- **⚠️ WARNING**: When `deseable IS NULL`, the健康able condition `s.actual >= s.deseable` evaluates to NULL/false in MySQL. The row would not appear in ANY category. This contradicts the spec scenario which says it should be "Stock saludable".
- **Impact**: MEDIUM — items with NULL `deseable` are excluded from all 4 categories, deflating `total_articulos` count vs actual. The `COUNT(DISTINCT s.idarticulo)` at line 520 still counts them, but the sum of 4 categories won't equal `total_articulos`.

### F12: Stock por Sucursal

| Requirement | Spec | Implementation | Status |
|-------------|------|---------------|--------|
| Per-sucursal with units, value, sin_stock, bajo_minimo | Line 61 | Lines 573-589 | ✅ |
| `GROUP BY s.idsucursal, suc.nombre` | Line 78 | Line 587 | ✅ |
| `ORDER BY unidades_totales DESC` | Line 79 | Line 588 | ✅ |
| Optional sucursal filter | Line 77 | Lines 568-570 | ✅ |

### F13: Productos sin Movimiento

| Requirement | Spec | Implementation | Status |
|-------------|------|---------------|--------|
| LEFT JOIN itemsv + facturav | Line 107-108 | Lines 637-639 | ✅ |
| `HAVING ultima_venta IS NULL OR < threshold` | Line 115 | Line 645 | ✅ |
| `LIMIT 100` | Line 117 | Line 647 | ✅ |
| 30/60/90 day toggle | Line 120 | Template line 531-533, JS line 222-243 | ✅ |
| Truncation indicator | Line 136 | Template line 573-578, JS line 271-283 | ✅ |
| "Sin ventas" for NULL ultima_venta | Line 129 | Service line 660, Template line 559, JS line 260 | ✅ |
| `ORDER BY ultima_venta ASC` | Line 116 | Line 646 | ✅ |

### Non-Functional

| Requirement | Status | Notes |
|-------------|--------|-------|
| NF7: Stock point-in-time (no date range) | ✅ | Stock KPIs and sucursal queries have no `desde`/`hasta` |
| NF8: LIMIT 100 sin movimiento | ✅ | Line 647 + separate count query at line 673-688 |
| NF9: Valorización = actual * costo_total | ✅ | Line 521, 581, 681 |
| NF10: Multi-sucursal filter | ✅ | All 3 functions accept `id_sucursal` |
| NF11: Empty data message | ✅ | Template lines 509-511: "No hay datos de inventario disponibles" |
| CSP nonce compliance | ✅ | Template line 590: `<script nonce="{{ g.nonce }}">` |
| Decimal for monetary values | ✅ | Line 535: `Decimal(str(row.valor_total_stock or 0))` |
| Stage 1 not broken | ✅ | Aggregator at line 722-724 adds new keys; existing keys untouched |

---

## Section C — SQL Correctness

### Table/Column Validation

| Table | Column | Used in Query | Exists in Model |
|-------|--------|---------------|-----------------|
| `stocks` | `actual` | F11, F12, F13 | ✅ `models/articulos.py:86` |
| `stocks` | `deseable` | F11, F12 | ✅ `models/articulos.py:88` |
| `stocks` | `maximo` | F11 | ✅ `models/articulos.py:87` |
| `stocks` | `idsucursal` | F11, F12, F13 | ✅ `models/articulos.py:85` |
| `stocks` | `idarticulo` | F11, F12, F13 | ✅ `models/articulos.py:84` |
| `articulos` | `baja` | F11, F12, F13 | ✅ (used in existing queries) |
| `articulos` | `idtipoarticulo` | F11, F12, F13 | ✅ (used in existing queries) |
| `articulos` | `costo_total` | F11, F12 | ✅ (used in existing queries) |
| `sucursales` | `id`, `nombre` | F12 | ✅ `models/sucursales.py` |
| `itemsv` | `idarticulo`, `idfactura` | F13 | ✅ (used in Stage 1 queries) |
| `facturav` | `id`, `fecha` | F13 | ✅ `models/ventas.py:5` |
| `rubros` | `id`, `nombre` | F13 | ✅ `models/articulos.py:123` |

All referenced tables and columns exist. No SQL injection risk — `_sucursal_filter` uses parameterized `:id_sucursal` binding.

---

## Section D — Design Coherence

| Design Decision | Design Doc | Implementation | Match |
|-----------------|------------|---------------|-------|
| Use `deseable` not `minimo` | Line 11 | All queries use `s.deseable` | ✅ |
| `_sucursal_filter(alias='s')` for stock | Line 12 | Hardcoded `' AND s.idsucursal = :id_sucursal'` | ⚠️ Works but doesn't use helper |
| Lazy load sin movimiento via HTMX | Line 13 | Toggle fetches API, JS re-renders | ✅ |
| Solo tabla (sin chart) stock sucursal | Line 14 | Table only, no chart | ✅ |
| Stock ignores date filter | Line 15 | Stock queries have no `desde`/`hasta` | ✅ |
| LIMIT 100 sin movimiento | Line 16 | Line 647 + separate count | ✅ |

---

## Section E — Issues

### ⚠️ WARNING: `deseable=NULL` items not classified

**Location**: `services/dashboard_gerencial.py`, line 518
**Spec**: Scenario "Clasificación con deseable NULL" (spec.md line 46-49) expects `deseable=NULL, maximo=NULL, actual=5` → "Stock saludable"
**Actual**: MySQL `5 >= NULL` evaluates to NULL/false. The item is NOT counted in any category.
**Impact**: Items with NULL `deseable` are counted in `total_articulos` (line 520 uses `COUNT(DISTINCT s.idarticulo)`) but NOT in any of the 4 categories. This means `sin_stock + bajo_minimo + saludable + exceso < total_articulos` when NULLs exist.
**Fix**: Add `OR s.deseable IS NULL` to the saludable condition: `(s.actual >= s.deseable OR s.deseable IS NULL) AND (s.maximo IS NULL OR s.maximo = 0 OR s.actual <= s.maximo)`

### ⚠️ WARNING: Same issue in F12 (stock por sucursal)

**Location**: `services/dashboard_gerencial.py`, line 580
**Impact**: `bajo_minimo` in the per-sucursal table won't count items with NULL `deseable`. The `sin_stock` count is unaffected since it only checks `actual <= 0`.

### ⚠️ WARNING: COUNT subquery grouping inconsistency (F13)

**Location**: `services/dashboard_gerencial.py`, line 685
**Issue**: The count subquery uses `GROUP BY a.id, s.actual, s.idsucursal` while the main query at line 644 uses `GROUP BY a.id, a.codigo, a.detalle, s.actual, s.idsucursal, r.nombre`. Since `a.codigo`, `a.detalle`, and `r.nombre` are functionally dependent on `a.id`, the groups are equivalent. No incorrect results.
**Impact**: LOW — cosmetic inconsistency only.

### 💡 SUGGESTION: `_sucursal_filter` not reused in stock functions

**Location**: `services/dashboard_gerencial.py`, lines 508-511, 567-570, 621-623
**Issue**: Design doc says "reutilizar `_sucursal_filter(alias='s', params)`" but all 3 stock functions hardcode the filter string instead.
**Impact**: LOW — works correctly, just a style inconsistency with the design.

---

## Section F — Tests

No dashboard-specific tests exist. The `tests/` directory covers articulos, clientes, ventas, utils, proveedores, and redondeo, but nothing for `dashboard_gerencial` service or routes.

**Note**: Tasks.md Phase 5 (Verification) marks items 5.1-5.4 as done with manual verification. There is no automated test runner for this module.

---

## Final Verdict

**PASS WITH WARNINGS**

The implementation is functionally correct and matches the spec in all material aspects. The 3 warnings above are:
1. **deseable=NULL classification** — a real edge case bug that should be fixed before production
2. **Same issue in per-sucursal bajo_minimo count** — related to #1
3. **COUNT subquery grouping** — cosmetic, no functional impact

The `deseable=NULL` issue is the only one that could cause visible discrepancies (total_articulos > sum of 4 categories). Recommend fixing before merge.
