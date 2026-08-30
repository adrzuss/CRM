## Exploration: Dashboard Gerencial ERP

### Current State

El proyecto CRM/ERP tiene **tres tableros** existentes y **un reporte gerencial**:

1. **`/tablero-inicial`** (route `tableros.tablero_inicial`) — Dashboard principal para usuarios tipo 1. Muestra KPIs (ventas hoy/semana, créditos, cta. cte. clientes/proveedores), gráficos de barras (ventas 6 meses), pie de pagos, ventas por rubros, tablas de sucursales/vendedores con filtros de fecha. Template: `templates/tablero.html`.

2. **`/tablero-gerencial`** (route `tableros.tablero_gerencial`) — Reporte gerencial completo con date-range picker. Usa `services.reportes.get_datos_reporte_gerencial()`. Template: `templates/reports/reporte-gerencial.html`. Ya tiene **7 secciones** con KPIs, gráficos Chart.js 4, tablas detalladas, filtros de fecha.

3. **`/tablero-administrativo`** (route `tableros.tablero_administrativo`) — Versión simplificada del tablero inicial.

4. **`/tablero-basico`** (route `tableros.tablero_basico`) — Para usuarios sin permisos elevados.

**Hallazgo crítico: YA EXISTE un "Dashboard Gerencial" funcional** en `/tablero-gerencial` con servicio completo en `services/reportes.py` (692 líneas) que incluye:
- Resumen ejecutivo (ventas, margen bruto, ticket promedio, operaciones con variaciones %)
- Top productos
- Evolución temporal de ventas
- Concentración de clientes ABC
- Análisis de compras vs ventas
- Métricas por sucursal con ranking
- Estado e rotación de inventario
- Distribución por medios de pago
- Cuentas corrientes y deudores
- Filtros de fecha (desde/hasta)

### Affected Areas

- `routes/tableros.py` — Route registration (línea 14: `bp_tableros`), existing dashboard routes
- `routes/reportes.py` — Minimal route file, only has `/reporte_gerencial`
- `services/reportes.py` — **692 líneas** con 10 funciones de consultas SQL complejas
- `services/ventas/reportes.py` — Additional sales report functions
- `templates/tablero.html` — Main dashboard template (586 lines)
- `templates/reports/reporte-gerencial.html` — Report template (626 lines)
- `templates/tablero-basico.html` — Basic dashboard template
- `static/js/reporte-gerencial.js` — Chart.js 4 initialization (407 lines)
- `static/js/tablero_gerencial.js` — AJAX fetching for sucursal/vendedor tables
- `static/js/demo/chart-bar-demo.js` — Legacy Chart.js 2/3 bar chart
- `static/js/demo/chart-pie-demo.js` — Legacy pie chart
- `static/css/reporte-gerencial.css` — Report-specific styles (289 lines)
- `static/vendor/chart.js/` — Chart.js (legacy v2/3 bundled version)

### Findings per Investigation Point

#### 1. Flask Structure
- **Blueprints**: 14 blueprints registered in `index.py`, each in `routes/{name}.py`, prefixed with `bp_`. Example: `bp_tableros = Blueprint('tableros', __name__, template_folder='../templates/tableros')`
- **Pattern**: Route files import services, call them, pass data to `render_template()`
- **Models**: One file per domain in `models/` (ventas.py, clientes.py, etc.)
- **Services**: Business logic in `services/`. Some are packages (`services/ventas/`), some single files (`services/reportes.py`, `services/configs.py`)
- **Utils**: `utils/db.py` (SQLAlchemy), `utils/config.py` (Config class), `utils/utils.py` (check_session, format_currency), `utils/msg_alertas.py` (alertas_mensajes decorator)

#### 2. Existing Dashboards
- **3 dashboards + 1 report**: `tablero-inicial`, `tablero-administrativo`, `tablero-basico`, `tablero-gerencial`
- `tablero-inicial` uses Chart.js from `static/vendor/chart.js/Chart.min.js` (legacy v2/3) with `demo/chart-bar-demo.js` and `demo/chart-pie-demo.js`
- `tablero-gerencial` uses Chart.js 4 from CDN `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js` with dedicated `static/js/reporte-gerencial.js`
- Both use `{% extends "base.html" %}` with `{% block body %}` and `{% block js_script %}`
- Data is passed server-side via `render_template()` variables, then injected into JS via `{{ data|tojson }}`

#### 3. Chart.js Usage
- **Two versions coexisting**: Legacy Chart.js 2/3 bundled in `static/vendor/chart.js/` (used by `tablero.html`) and Chart.js 4.4.1 via CDN (used by `reporte-gerencial.html`)
- **Chart types used**: Bar, Pie, Doughnut, Line/Area, Bubble
- **Pattern**: Canvas elements in templates, data injected via inline `<script nonce="{{ g.nonce }}">` blocks using `|tojson`, chart creation in separate JS files
- **Color palette**: Defined in `reporte-gerencial.js` as `COLORES` and `PALETA_GRAFICOS` constants
- **Formatting helpers**: `formatearMoneda()` and `formatearMonedaCorta()` in reporte-gerencial.js

#### 4. Authentication/Authorization
- **Auth decorator**: `@check_session` from `utils/utils.py` — redirects to login if no `session['user_id']`
- **Alerts/messages**: `@alertas_mensajes` from `utils/msg_alertas.py` — injects `g.alertas`, `g.mensajes` etc.
- **Menu permissions**: `tiene_permiso(codigo)` function injected via `@app.context_processor`, used in sidebar template as `tiene_permiso('ABM de clientes')`
- **Session keys**: `user_id`, `user_name`, `id_sucursal`, `nombre_sucursal`, `id_empresa`, `idPuntoVenta`, `owner`, `company`, `tipo_iva`, `permisos_menu`, `plan`, `dias_vencimiento`
- **Plan expiry**: Checks `session['dias_vencimiento'] <= -30` for expired plans

#### 5. CSS Architecture
- **SB Admin 2 base**: `static/css/sb-admin-2.min.css` — the SB Admin 2 theme (Bootstrap-based admin template)
- **Bootstrap 5.3.3**: Loaded via CDN
- **Main custom CSS**: `static/css/main.css` (3178+ lines) — extensive custom styles including gradients, buttons, modals, tables, forms
- **Feature-specific CSS**: `static/css/reporte-gerencial.css`, `static/css/nueva_venta.css`, `static/css/permisos-menu.css`, etc.
- **Pattern**: Base in `base.html` via `{% block additional_css %}` for per-page extra CSS

#### 6. JavaScript Architecture
- **45 JS files** in `static/js/` — feature-specific (one per module)
- **Shared utilities**: `main.js` (module), `swal-helpers.js` (SweetAlert2 helpers), `sb-admin-2.min.js` (theme JS)
- **jQuery**: Available (`static/vendor/jquery/jquery.min.js`), used in some places
- **HTMX**: Available (`htmx.org@1.9.10` via CDN)
- **CSRF**: Handled globally in `base.html` via nonce-protected script that injects CSRF tokens in forms, jQuery AJAX, fetch(), and HTMX
- **Pattern**: Per-page JS files loaded in `{% block js_script %}`, data injected via inline `<script nonce="{{ g.nonce }}">` blocks

#### 7. MySQL Connection
- **SQLAlchemy**: `flask_sqlalchemy` with `SQLAlchemy()` in `utils/db.py`
- **URI**: `SQLALCHEMY_DATABASE_URI` from `.env` file
- **Pattern**: Raw SQL via `text()` with named parameters for stored procedures: `db.session.execute(text("CALL ..."), {'param': value})`
- **ORM queries**: `Model.query.filter_by()` for simple lookups
- **Transactions**: Always wrapped in `try/except` with `db.session.rollback()` on `SQLAlchemyError`
- **No explicit connection pooling config** — relies on SQLAlchemy defaults

#### 8. Template Patterns
- **Base template**: `base.html` — full SB Admin 2 layout with sidebar, topbar, footer
- **Second layout**: `layout.html` — minimal Bootstrap layout (no sidebar) used for simpler pages
- **Partials**: `partials/_sidebar.html`, `partials/_topbar.html`, `partials/_messages.html`, `partials/_modal-busqueda-universal.html`
- **Blocks**: `{% block body %}` for content, `{% block additional_css %}` for extra CSS, `{% block js_script %}` for page JS
- **Nonce**: All inline scripts use `{{ g.nonce }}` for CSP compliance
- **Template inheritance**: All dashboard pages use `{% extends "base.html" %}`

#### 9. API Patterns
- **JSON endpoints**: Several routes return `jsonify()` for AJAX — e.g., `/ventas/get_vta_sucursales/<desde>/<hasta>`, `/ventas/get_vta_vendedores/<desde>/<hasta>`
- **Response pattern**: `jsonify(success=True, data=...)` or `jsonify(success=False, error=str(e))`
- **No REST API framework** — all custom Flask routes
- **CORS**: Not configured (same-origin only)
- **CSRF**: Global protection via `CSRFProtect(app)` + X-CSRFToken header for AJAX

#### 10. Multi-Sucursal
- **`session['id_sucursal']`**: Current branch, set during login
- **`session['nombre_sucursal']`**: Branch name
- **`session['id_empresa']`**: Company ID (default 1)
- **Sucursal model**: `models/sucursales.py` — `Sucursales` table with `id`, `nombre`
- **Sales filtering**: Many queries filter by `facturav.idsucursal == session['id_sucursal']` for per-branch views
- **Cross-sucursal reporting**: `services/reportes.py` functions (`get_metricas_sucursales`, `get_vta_sucursales_data`) aggregate across all branches for gerencial view
- **Sucursal list**: `get_sucursales_lista()` returns all active branches for filters

### Reusable Components

| Component | Path | Notes |
|-----------|------|-------|
| **Report service** | `services/reportes.py` | 10 functions already built: resumen ejecutivo, top productos, evolución ventas, concentración clientes, análisis compras, métricas sucursales, inventario, rotación, medios pago, ctacte |
| **Report route** | `routes/tableros.py:56-87` | `tablero_gerencial()` already routes to `reporte-gerencial.html` |
| **Report template** | `templates/reports/reporte-gerencial.html` | 626-line comprehensive template with 7 sections |
| **Chart.js 4 module** | `static/js/reporte-gerencial.js` | Full chart initialization, color palette, formatting helpers |
| **Report CSS** | `static/css/reporte-gerencial.css` | KPI cards, chart areas, table styles, print styles |
| **check_session** | `utils/utils.py` | Auth decorator |
| **alertas_mensajes** | `utils/msg_alertas.py` | Alert/message injection |
| **format_currency** | `utils/utils.py` | `$X,XXX.XX` formatting |
| **Base template** | `templates/base.html` | Full SB Admin 2 layout |
| **Sidebar** | `templates/partials/_sidebar.html` | Navigation with permission checks |
| **DB** | `utils/db.py` | SQLAlchemy instance |

### Gaps

1. **No JSON API for dashboard data**: The existing `tablero-gerencial` is fully server-rendered. There's no REST endpoint to fetch dashboard data dynamically (for HTMX or client-side refresh). Only the sucursal/vendedor tables in `tablero.html` have AJAX endpoints.

2. **No dedicated "Dashboard Gerencial" route namespace**: Currently the gerencial report lives under `bp_tableros` with a route `/tablero-gerencial`. If we want a distinct "Dashboard Gerencial" feature, we need to decide whether to extend this or create a new blueprint.

3. **Two Chart.js versions**: The project loads both legacy Chart.js 2/3 (vendor bundle) and Chart.js 4 (CDN) on different pages. The gerencial report uses Chart.js 4, but the main tablero uses the old version. Should standardize.

4. **No auto-refresh / real-time**: Dashboards use `<meta http-equiv="refresh" content="300">` for 5-minute refresh. No WebSocket or polling mechanism exists.

5. **No dashboard-specific permission**: The `tiene_permiso` system checks menu codes. There's no specific permission for "ver dashboard gerencial" — all authenticated users can access it.

6. **No date-range presets**: The existing gerencial report has manual date inputs. No quick presets (hoy, semana, mes, trimestre, año) — though `reporte-gerencial.js` has keyboard shortcuts (Alt+H, Alt+S, etc.) not discoverable by users.

7. **Chart data not cached**: Every page load executes ~10 SQL queries. No caching layer exists.

### Approaches

1. **Extend existing `/tablero-gerencial`** — Enhance the already-complete report with new sections, interactivity, and HTMX partial updates
   - Pros: Minimal duplication, leverages existing 692-line service, existing template and CSS
   - Cons: Template already 626 lines, adding more sections risks becoming unwieldy
   - Effort: Low

2. **Create new dashboard blueprint** — New `routes/dashboard.py` with its own template, service, and static files
   - Pros: Clean separation, can design from scratch, no risk to existing pages
   - Cons: Significant duplication of `services/reportes.py` logic, new URL to register, new sidebar entry
   - Effort: Medium

3. **Modularize existing gerencial into partials + HTMX sections** — Refactor `reporte-gerencial.html` into reusable Jinja2 partials with HTMX lazy-loading for each section
   - Pros: Better maintainability, partial updates (no full page refresh), reuses all existing backend logic
   - Cons: Template refactor needed, HTMX adds complexity
   - Effort: Medium

### Recommendation

**Approach 1 (extend existing) + partial HTMX modularization** — The existing `/tablero-gerencial` already has a comprehensive service layer, template, CSS, and Chart.js integration. The most pragmatic path is:

1. Add new sections/KPIs to `services/reportes.py` (e.g., hourly trends, comparison periods, alerts)
2. Break `reporte-gerencial.html` into partials (`templates/reportes/partials/`) for each section
3. Add HTMX endpoints for section-level refresh instead of full page reload
4. Add date-range quick-select buttons (Hoy, Semana, Mes, Trimestre, Año)
5. Standardize on Chart.js 4 (remove legacy vendor bundle or migrate tablero.html)

This avoids duplication and builds on the solid foundation that already exists.

### Risks

- **Performance**: 10+ SQL queries per load with no caching. Adding more sections will slow down the page. Consider adding server-side caching (e.g., `@lru_cache` or Redis) for expensive queries.
- **Template complexity**: `reporte-gerencial.html` is already 626 lines. Must modularize into partials before adding more content.
- **Chart.js version conflict**: Both Chart.js 2/3 and 4 are loaded across the application. Standardizing is needed to avoid confusion but may break existing dashboards.
- **CSP compliance**: All inline scripts need `{{ g.nonce }}` — new HTMX partials with embedded scripts must pass the nonce.

### Ready for Proposal

Yes — the exploration is complete. The orchestrator should:
1. Confirm whether to extend the existing `/tablero-gerencial` or create a separate dashboard
2. Identify what NEW KPIs/sections are needed beyond what already exists (resumen ejecutivo, top productos, evolución ventas, concentración clientes, análisis compras, métricas sucursales, inventario, rotación, medios pago, ctacte)
3. Clarify whether the goal is real-time updates, better UX, or entirely new analytical dimensions
4. Proceed to SDD proposal phase
