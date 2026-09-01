# Design: Tableros Consolidation

## Technical Approach

Merge `routes/dashboard_gerencial.py` (21 endpoints + 2 helpers) into `routes/tableros.py` (5 endpoints), forming a single `bp_tableros` blueprint. Move 4 templates into `templates/tableros/`. Update `index.py` registration and sidebar link. Zero URL changes, zero service changes.

The current `tableros.py` blueprint already declares `template_folder='../templates/tableros'` but that directory does not exist — Flask falls back to the app root `templates/` folder. After the migration, moving templates into `templates/tableros/` makes them resolve directly without fallback, which is the correct long-term pattern.

## Architecture Decisions

### Decision: Blueprint name stays `tableros`

**Choice**: Keep blueprint name `tableros`, register as `bp_tableros`
**Alternatives considered**: Rename to `dashboard`, create a new `bp_dashboard`
**Rationale**: 6 existing `url_for('tableros.*')` calls in `index.py` and 1 in `tablero.html`. Renaming breaks all of them for zero benefit. The function `dashboard_gerencial()` becomes `tableros.dashboard_gerencial` in url_for, which is clean and unambiguous.

### Decision: Templates flat inside `templates/tableros/`

**Choice**: All 4 templates flat at `templates/tableros/{name}.html`
**Alternatives considered**: Subfolders per type (`gerencial/`, `basico/`)
**Rationale**: Only 4 files. Subfolders add nesting with no organizational benefit. Matches spec R3 exactly. `reportes/reporte-gerencial.html` stays in `templates/reportes/` since it's shared with the `reportes` blueprint.

### Decision: `_parsear_filtros()` stays module-level private

**Choice**: Keep `_parsear_filtros()` and `_api_respuesta()` as module-level functions in `routes/tableros.py`
**Alternatives considered**: Move to `utils/` or create a shared helpers module
**Rationale**: Both are private (`_` prefix), only used within this one file. Extracting them would create a dependency for two functions that serve exactly one module. Follows spec R4.

### Decision: Static files stay in `static/`

**Choice**: No moves for `dashboard-gerencial.js`, `dashboard-gerencial.css`, or any `static/js/demo/*` files
**Alternatives considered**: Move into `static/js/tableros/`
**Rationale**: `static/js/demo/chart-pie-demo.js` is shared with fondos module. `dashboard-gerencial.js` uses hardcoded URL paths (`/api/dashboard-gerencial/...`) that won't change. Moving would break fondos and the JS fetch calls for no benefit.

### Decision: Sidebar uses `url_for()` instead of hardcoded path

**Choice**: Change `href="/dashboard-gerencial"` to `href="{{ url_for('tableros.dashboard_gerencial') }}"`
**Alternatives considered**: Keep hardcoded path
**Rationale**: Hardcoded paths break silently if URL ever changes. `url_for` is the Flask convention used everywhere else in this codebase (see `index.py` line 182-189).

## Data Flow

```
index.py registers bp_tableros (url_prefix='/')
         │
         ├── /tablero-inicial        → tableros/tablero.html
         ├── /tablero-gerencial      → reportes/reporte-gerencial.html (fallback)
         ├── /tablero-administrativo → tableros/tablero.html
         ├── /tablero-basico         → tableros/tablero-basico.html
         ├── /plan-vencido           → tableros/plan-vencido.html
         ├── /dashboard-gerencial    → tableros/dashboard-gerencial.html
         └── /api/dashboard-gerencial/* (20 endpoints)
                    │
                    └── services/dashboard_gerencial.py (unchanged)
```

Template resolution after migration:
```
render_template('tablero.html')
  → templates/tableros/tablero.html       ← found directly

render_template('dashboard-gerencial.html')
  → templates/tableros/dashboard-gerencial.html  ← found directly

render_template('reportes/reporte-gerencial.html')
  → templates/tableros/reportes/...        ← NOT found
  → templates/reportes/reporte-gerencial.html  ← fallback to app root
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `routes/tableros.py` | Modify | Add imports from `dashboard_gerencial.py` (services + helpers), paste 21 endpoints + 2 helpers (~185 lines added) |
| `routes/dashboard_gerencial.py` | Delete | All content merged into `routes/tableros.py` |
| `templates/tableros/` | Create | New directory |
| `templates/tableros/tablero.html` | Move | From `templates/tablero.html` |
| `templates/tableros/tablero-basico.html` | Move | From `templates/tablero-basico.html` |
| `templates/tableros/dashboard-gerencial.html` | Move | From `templates/dashboard-gerencial.html` |
| `templates/tableros/plan-vencido.html` | Move | From `templates/plan-vencido.html` |
| `index.py` | Modify | Remove `from routes.dashboard_gerencial import bp_dashboard_gerencial` and `app.register_blueprint(bp_dashboard_gerencial, url_prefix='/')` |
| `templates/partials/_sidebar.html` | Modify | Line 29: change hardcoded `/dashboard-gerencial` to `{{ url_for('tableros.dashboard_gerencial') }}` |

## Import Consolidation

Merged imports in `routes/tableros.py`:

```python
from flask import render_template, request, Blueprint, g, jsonify, session
from datetime import date, timedelta, datetime

# Services — tableros originals
from services.ventas import (get_vta_hoy, get_vta_semana, ventas_por_mes, pagos_hoy,
    get_operaciones_hoy, get_operaciones_semana, get_ultimas_operaciones,
    get_10_mas_vendidos, get_op_este_mes, get_op_este_mes_anterior,
    get_vta_sucursales_data, get_vta_vendedores_data, get_vta_rubros)
from services.reportes import get_datos_reporte_gerencial, get_sucursales_lista
from services.articulos import get_stocks_negativos, get_stocks_faltantes
from services.ctactecli import get_saldo_clientes
from services.ctacteprov import get_saldo_proveedores
from services.creditos import get_datos_creditos

# Services — from dashboard_gerencial
from services.dashboard_gerencial import (
    get_datos_dashboard, get_kpis, get_evolucion_ventas,
    get_ventas_sucursal, get_ventas_rubro,
    get_rubro_sucursal_comparacion, get_top_productos,
    get_top_vendedores, get_stock_kpis, get_stock_sucursal,
    get_productos_sin_movimiento, get_cta_cobrar_kpis,
    get_cta_cobrar_top, get_cta_pagar_kpis, get_cta_pagar_top,
    get_creditos_kpis, get_creditos_top_deudores,
    get_bancos_kpis, get_bancos_detalle,
    get_caja_kpis, get_caja_rendiciones_recientes,
    get_alertas_gerenciales)

# Utils
from utils.utils import check_session, format_currency
from utils.msg_alertas import alertas_mensajes
```

Key additions vs current `tableros.py`:
- `jsonify`, `session` from flask (used by API endpoints)
- `get_sucursales_lista` from `services.reportes`
- All 22 functions from `services.dashboard_gerencial`

## Route Structure in Consolidated File

```python
# ─── Helpers ─────────────────────────────────────────────────────────────────
def _parsear_filtros(): ...      # From dashboard_gerencial.py, unchanged
def _api_respuesta(funcion, *args, **kwargs): ...  # From dashboard_gerencial.py, unchanged

# ─── Tableros originales (5 rutas) ──────────────────────────────────────────
@bp_tableros.route('/tablero-inicial')        # tablero_inicial()
@bp_tableros.route('/tablero-gerencial')      # tablero_gerencial()
@bp_tableros.route('/tablero-administrativo') # tablero_administrativo()
@bp_tableros.route('/tablero-basico')         # tablero_basico()
@bp_tableros.route('/plan-vencido')           # plan_vencido()

# ─── Dashboard Gerencial — ruta principal ────────────────────────────────────
@bp_tableros.route('/dashboard-gerencial')    # dashboard_gerencial()

# ─── API endpoints HTMX — Ventas ─────────────────────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/kpis')
@bp_tableros.route('/api/dashboard-gerencial/evolucion')
@bp_tableros.route('/api/dashboard-gerencial/sucursales')
@bp_tableros.route('/api/dashboard-gerencial/rubros')
@bp_tableros.route('/api/dashboard-gerencial/rubro-sucursal')
@bp_tableros.route('/api/dashboard-gerencial/top-productos')
@bp_tableros.route('/api/dashboard-gerencial/top-vendedores')

# ─── API endpoints Stock ─────────────────────────────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/stock-kpis')
@bp_tableros.route('/api/dashboard-gerencial/stock-sucursales')
@bp_tableros.route('/api/dashboard-gerencial/stock-sin-movimiento')

# ─── API endpoints Cuentas por Cobrar / Pagar ────────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/cta-cobrar-kpis')
@bp_tableros.route('/api/dashboard-gerencial/cta-cobrar-top')
@bp_tableros.route('/api/dashboard-gerencial/cta-pagar-kpis')
@bp_tableros.route('/api/dashboard-gerencial/cta-pagar-top')

# ─── API endpoints Créditos ──────────────────────────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/creditos-kpis')
@bp_tableros.route('/api/dashboard-gerencial/creditos-top')

# ─── API endpoints Bancos / Caja ─────────────────────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/bancos-kpis')
@bp_tableros.route('/api/dashboard-gerencial/bancos-detalle')
@bp_tableros.route('/api/dashboard-gerencial/caja-kpis')
@bp_tableros.route('/api/dashboard-gerencial/caja-rendiciones')

# ─── API endpoint Alertas ────────────────────────────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/alertas')
```

All routes use `bp_tableros` decorator. Function names unchanged. URL paths unchanged.

## Error Handling Patterns

Standardize the API response pattern from `dashboard_gerencial.py`:

```python
def _api_respuesta(funcion, *args, **kwargs):
    """Wrapper para endpoints JSON con manejo de errores."""
    try:
        resultado = funcion(*args, **kwargs)
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

This pattern stays as-is. The 5 tablero page routes continue using `@check_session` + `@alertas_mensajes` for error/auth handling, which is unchanged. The API endpoints use `@check_session` only (no `@alertas_mensajes` since they return JSON, not pages) — this is the current behavior and remains correct.

## Blueprint Registration

**Before** (`index.py` lines 14, 28, 48, 62):
```python
from routes.tableros import bp_tableros
from routes.dashboard_gerencial import bp_dashboard_gerencial
...
app.register_blueprint(bp_tableros, url_prefix='/')
...
app.register_blueprint(bp_dashboard_gerencial, url_prefix='/')
```

**After**:
```python
from routes.tableros import bp_tableros
...
app.register_blueprint(bp_tableros, url_prefix='/')
```

Remove lines 28 and 62. Keep `bp_tableros` import (line 14) and registration (line 48) unchanged.

## Sidebar Change

**Before** (`templates/partials/_sidebar.html` line 29):
```html
<a class="nav-link" href="/dashboard-gerencial">
```

**After**:
```html
<a class="nav-link" href="{{ url_for('tableros.dashboard_gerencial') }}">
```

## JS File Impact (None)

`static/js/dashboard-gerencial.js` uses hardcoded fetch paths:
```javascript
fetch('/api/dashboard-gerencial/' + seccion + '?' + params)
```
These are URL paths, not `url_for` calls. Since URL paths don't change, the JS works identically.

`tablero.html` uses `url_for('tableros.tablero_gerencial')` — the function name and blueprint name both stay the same, so this resolves correctly.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Smoke | All 26 routes respond HTTP 200 | Manual browser navigation or curl |
| Template | Templates resolve without `TemplateNotFound` | Hit each page route, check console for warnings |
| API | All 20 API endpoints return valid JSON | Hit each endpoint, verify `success: true` |
| url_for | Sidebar link resolves to `/dashboard-gerencial` | Inspect rendered sidebar HTML |
| Fondos | `chart-pie-demo.js` still loads | Navigate to fondos flujo page, check console |

## Migration / Rollout

No data migration required. All changes are file-level:

1. Create `templates/tableros/` directory
2. Move 4 template files into it
3. Paste 21 endpoints + 2 helpers + merged imports into `routes/tableros.py`
4. Delete `routes/dashboard_gerencial.py`
5. Remove blueprint import + registration from `index.py`
6. Update sidebar link in `_sidebar.html`

**Rollback**: `git checkout` of all affected files + delete `templates/tableros/` directory.

## Open Questions

None — all technical decisions have clear answers based on codebase analysis.
