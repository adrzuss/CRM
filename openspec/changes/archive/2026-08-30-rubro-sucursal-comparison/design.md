# Design: Rubro-Sucursal Comparison

## Technical Approach

Extend the existing dashboard service with a single new function that performs a grouped SQL query (rubro × sucursal), then pivots results in Python to produce a cross‑tab matrix. The cross‑tab is served via a dedicated HTMX endpoint and rendered as a full‑width table below the existing Sucursales/Rubros cards. The table includes participation percentages and a comparison indicator (↑/↓) that highlights whether a sucursal over‑ or under‑indexes in a given rubro relative to its overall sales share. The implementation reuses the same JOIN chain and helper functions (`_params_base`, `_sucursal_filter`, `_formato_moneda`) already present in `services/dashboard_gerencial.py`.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Data aggregation | Single SQL `GROUP BY rubro, sucursal` | Separate queries per sucursal or per rubro | One round‑trip, consistent totals, leverages existing query pattern |
| Pivot logic | Python dictionary comprehension | Database `PIVOT` (MySQL lacks native) | MySQL does not support PIVOT; Python pivot is straightforward and keeps SQL simple |
| Indicator calculation | `cell_pct` vs `benchmark_pct` (sucursal’s overall share) | Absolute difference, z‑score | Simple percentage comparison matches proposal; z‑score over‑engineered for current need |
| Template rendering | Server‑rendered Jinja2 cross‑tab | Client‑side JS (Chart.js, DataTables) | Keeps CSP strict, matches existing pattern (tables are Jinja‑rendered) |
| Endpoint style | HTMX GET returning HTML fragment | Full JSON endpoint + client render | HTMX fragment matches other dashboard sections, reduces JS |
| Responsive layout | `table‑responsive` wrapper (existing pattern) | Fixed column widths, horizontal scroll polyfill | Existing pattern proven in Sucursales table; no new dependencies |

## Data Flow

```
MySQL (GROUP BY rubro, sucursal)
        │
        ▼
get_rubro_sucursal_comparacion()
  • executes single query
  • computes total_ventas
  • builds cross‑tab dict:
      { rubro: { sucursal: { cell_pct, benchmark_pct, indicator } } }
        │
        ▼
/api/dashboard-gerencial/rubro-sucursal (HTMX GET)
  • calls service function
  • returns JSON to _api_respuesta wrapper
        │
        ▼
dashboard-gerencial.html (Jinja2)
  • iterates rubros → rows
  • iterates sucursales → columns
  • renders cell_pct with ↑/↓ indicator
  • hides indicator column when only 1 sucursal
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modify | Add `get_rubro_sucursal_comparacion(desde, hasta, id_sucursal=None)` (~70 lines); add call in `get_datos_dashboard()` |
| `routes/dashboard_gerencial.py` | Modify | Import new function, add `GET /api/dashboard-gerencial/rubro-sucursal` endpoint (~8 lines) |
| `templates/dashboard-gerencial.html` | Modify | Insert full‑width row after line 313 with cross‑tab table (~70 lines Jinja2) |
| `static/css/dashboard-gerencial.css` | Modify | Add indicator arrow styles, grouped column headers (~30 lines) |

## Interfaces / Contracts

### Service function

```python
def get_rubro_sucursal_comparacion(desde, hasta, id_sucursal=None):
    """
    Returns cross‑tab data: rubros as rows, sucursales as columns.
    Structure:
    {
        'rubros': ['Electro', 'Blanco', ...],
        'sucursales': ['Central', 'Norte', ...],
        'matrix': {
            'Electro': {
                'Central': {'cell_pct': 45.2, 'benchmark_pct': 38.0, 'indicator': 'up'},
                'Norte':   {'cell_pct': 12.1, 'benchmark_pct': 22.0, 'indicator': 'down'},
            },
            ...
        },
        'total_ventas': 123456.78,
        'sucursal_count': 2
    }
    """
```

### API endpoint

```
GET /api/dashboard-gerencial/rubro-sucursal?desde=YYYY-MM-DD&hasta=YYYY-MM-DD&id_sucursal=<optional>
→ JSON { success: true, data: { rubros, sucursales, matrix, total_ventas, sucursal_count } }
```

### Template data key

`data.rubro_sucursal` – same structure as service return.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `get_rubro_sucursal_comparacion` returns correct cross‑tab | Mock `db.session.execute` with known rows, assert matrix structure and indicator logic |
| Unit | Indicator hidden when `sucursal_count == 1` | Call with `id_sucursal` filter, verify `sucursal_count` == 1 |
| Integration | HTMX endpoint returns valid JSON | Test client GET with session, assert `success: true` and data shape |
| E2E | Table renders in browser | Manual: load dashboard, verify cross‑tab appears, indicators show, responsive scroll works |

## Migration / Rollout

No migration required. Pure code addition; feature is opt‑in via existing date/sucursal filters.

## Open Questions

- None – all technical decisions are resolved by the proposal and existing codebase patterns.