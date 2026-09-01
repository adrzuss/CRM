# Design: Rubros Dual View + Sucursal Reorder

## Technical Approach

Extend the existing dashboard gerencial with a second rubro doughnut chart showing unit quantities alongside the existing revenue chart. Move the sucursal table to full-width above the rubros for better readability. All changes are additive — no new endpoints, SQL queries, or files. The existing `get_ventas_rubro()` already queries both `importe` and `unidades`; we only need to surface `total_unidades` in the return dict.

## Architecture Decisions

### Decision: Add `total_unidades` server-side vs client-side

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Server-side (service return dict) | 1-line change, consistent with existing `total_importe` pattern | **Chosen** |
| Client-side (JS reduce) | Zero backend changes, but duplicates logic and breaks consistency | Rejected |

**Rationale**: The service already computes `total_importe` — adding `total_unidades` in the same spot keeps the data contract consistent and avoids client-side aggregation for a value the DB already provides.

### Decision: Separate chart functions vs parameterized factory

| Option | Tradeoff | Decision |
|--------|----------|----------|
| New `crearGraficoRubrosCantidad()` function | Slight duplication, but matches existing `crearGraficoRubros` pattern exactly — easy to maintain | **Chosen** |
| Parameterized `crearGraficoRubros(target, field, formatter)` | Less duplication, but refactors existing working code — higher risk for a display enhancement | Rejected |

**Rationale**: The codebase uses one function per chart type. Introducing a factory pattern here would be inconsistent and increase review surface. Duplication is ~30 lines — acceptable for clarity.

### Decision: Drill-down table selector parameterization

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Add `tableSelector` param to `configurarDrillDownDoughnut()` | Clean, minimal change, same function serves both charts | **Chosen** |
| Duplicate `configurarDrillDownDoughnut` per chart | More duplication, harder to maintain | Rejected |

**Rationale**: The drill-down logic is identical — only the target table differs. One parameter keeps it DRY.

## Data Flow

```
DB (itemsv + rubros)
  │
  ▼
get_ventas_rubro() ──→ returns { rubros: [...], total_importe, total_unidades }
  │
  ▼
get_datos_dashboard() ──→ data.rubros (unchanged call site)
  │
  ├──→ Template: data.rubros.rubros iterates for BOTH tables
  │     ├── #seccion-rubros-monto table: Rubro | Importe | %
  │     └── #seccion-rubros-cantidad table: Rubro | Unid. | %
  │
  └──→ JS: inicializarDashboard(datos)
        ├── crearGraficoRubros(datos.rubros)        → #chartRubrosMonto
        ├── crearGraficoRubrosCantidad(datos.rubros) → #chartRubrosCantidad
        ├── configurarDrillDownDoughnut(chartRubros, '#seccion-rubros-monto')
        └── configurarDrillDownDoughnut(chartRubrosCantidad, '#seccion-rubros-cantidad')
```

## File Changes

| File | Action | Lines Affected | Description |
|------|--------|---------------|-------------|
| `services/dashboard_gerencial.py` | Modify | ~358, 373 | Add `total_unidades` sum + include in return dict |
| `templates/dashboard-gerencial.html` | Modify | 210-313 | Reorder sucursal to full-width, add second rubro card |
| `static/js/dashboard-gerencial.js` | Modify | 26, 145-190, 215-233, 314-317, 430-456, 487-508 | New chart variable, new function, updated lifecycle |

**No new files created. No files deleted.**

## Interfaces / Contracts

### Service return dict (modified)

```python
# get_ventas_rubro() return — added field
{
    'rubros': [...],           # existing — list of rubro dicts
    'total_importe': float,    # existing
    'total_unidades': int      # NEW — sum of all rubro unidades
}
```

### Per-rubro dict (unchanged)

```python
{
    'rubro': str,              # name
    'importe': str,            # formatted currency
    'importe_raw': float,      # for monto chart
    'unidades': int,           # for cantidad chart
    'participacion': float     # % by importe (monto chart)
}
```

Note: `participacion` stays based on `importe` for the monto chart. The cantidad chart computes its own percentage client-side: `(unidades / total_unidades) * 100`.

### JS function signature (new)

```javascript
crearGraficoRubrosCantidad(rubros)  // mirrors crearGraficoRubros, targets #chartRubrosCantidad
```

### JS function signature (modified)

```javascript
configurarDrillDownDoughnut(chart, tableSelector)  // added tableSelector param
```

## Template Structure (lines 210-313 replacement)

```
<div class="row mb-4">
    <!-- Sucursal: FULL WIDTH, FIRST -->
    <div id="seccion-sucursales" class="col-12 mb-3">
        ... (existing table, unchanged)
    </div>
</div>

<div class="row mb-4">
    <!-- Rubro Monto: col-6 -->
    <div id="seccion-rubros-monto" class="col-xl-6 col-lg-6 mb-3">
        <div class="card shadow h-100">
            <div class="card-header2">Ventas por Rubro — Monto</div>
            <div class="card-body">
                <canvas id="chartRubrosMonto"></canvas>
                <table> Rubro | Importe | % </table>
            </div>
        </div>
    </div>

    <!-- Rubro Cantidad: col-6 -->
    <div id="seccion-rubros-cantidad" class="col-xl-6 col-lg-6 mb-3">
        <div class="card shadow h-100">
            <div class="card-header2">Ventas por Rubro — Cantidad</div>
            <div class="card-body">
                <canvas id="chartRubrosCantidad"></canvas>
                <table> Rubro | Unid. | % </table>
            </div>
        </div>
    </div>
</div>
```

## JS Changes Detail

| Location | Change | Detail |
|----------|--------|--------|
| Line 26 | Add variable | `let chartRubrosCantidad = null;` |
| Line 146 | Rename canvas ref | `'chartRubros'` → `'chartRubrosMonto'` |
| After line 190 | New function | `crearGraficoRubrosCantidad(rubros)` — same structure, uses `r.unidades`, tooltip: `"X uds (Y%)"` with `pct = (unidades / rubros.total_unidades) * 100` |
| Line 222-223 | Update init | Call `crearGraficoRubrosCantidad(datos.rubros)` + `configurarDrillDownDoughnut(chartRubrosCantidad, '#seccion-rubros-cantidad')` |
| Line 223 | Update init | Pass `'#seccion-rubros-monto'` as second arg to existing `configurarDrillDownDoughnut` |
| Line 316 | Update destroy | Add `if (chartRubrosCantidad) { chartRubrosCantidad.destroy(); chartRubrosCantidad = null; }` |
| Line 430 | Add param | `configurarDrillDownDoughnut(chart, tableSelector)` — replace hardcoded `#seccion-rubros` with param |
| Line 437 | Update selector | `document.querySelector(tableSelector + ' table tbody')` |
| Lines 499-507 | Update HTMX | Add handler for `#seccion-rubros-monto` and `#seccion-rubros-cantidad` to re-parse `dataset.json` and recreate both charts |

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Visual | Both doughnut charts render with correct data | Manual: load dashboard, verify monto shows $, cantidad shows units |
| Visual | Sucursal table full-width above rubros | Manual: responsive check at xl, lg, md breakpoints |
| Interaction | Drill-down highlights correct table in each chart | Manual: click monto segment → monto table highlights; click cantidad → cantidad table |
| HTMX | Filter refresh destroys and recreates both charts | Manual: change date range, verify both charts re-render |
| Edge case | Empty rubros data | Verify both sections show "Sin rubros" empty state |
| Edge case | CSP nonce | Verify no console violations for inline scripts |

## Migration / Rollout

No migration required. Pure frontend enhancement + one return dict field. Zero database changes.

Rollback: `git checkout` the 3 modified files.

## Open Questions

None — all technical decisions resolved. The proposal and exploration fully specify the approach.
