# Design: Dashboard Gerencial ERP — Etapa 1

## Technical Approach

Blueprint Flask独立 con ruta server-side + 6 endpoints JSON para HTMX refresh por sección. Chart.js 4 CDN, datos vía `{{ data|tojson }}` + fetch para updates.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Service layer | 6 funciones (una por widget) | Mega-query | Separa responsabilidades, permite HTMX por sección, sigue patrón `services/reportes.py` |
| HTMX refresh | Endpoints JSON por sección | Un endpoint con param `seccion` | Respuesta más liviana, routing claro |
| Template | Monolithic (patrón existente) | Partials | Consistencia con proyecto; HTMX targets por `id` |
| Data passing | `{{ data|tojson }}` + fetch | Todo fetch | Evita flash, consistente con `reporte-gerencial.html` |
| Charts | Destroy + recreate | Update in-place | Más robusto, patrón estático |
| Sucursal filter | Reutilizar `get_sucursales_lista()` | Nueva función | Ya existe en `services/reportes.py` |

## Data Flow

```
GET /dashboard-gerencial?desde=&hasta=&id_sucursal=
  → Route → 6 service functions → render_template(data)
  → HTMX refresh → GET /api/dashboard-gerencial/{seccion} → JSON → htmx swap
```

## File Changes

| File | Action | Purpose |
|------|--------|---------|
| `routes/dashboard_gerencial.py` | Create | Blueprint + route principal + 6 API endpoints |
| `services/dashboard_gerencial.py` | Create | 6 funciones SQL: kpis, evolucion, sucursales, rubros, top_productos, top_vendedores |
| `templates/dashboard-gerencial.html` | Create | Template con filtros, KPIs, charts, tables |
| `static/js/dashboard-gerencial.js` | Create | Chart.js 4 init, HTMX lifecycle, filter binding |
| `static/css/dashboard-gerencial.css` | Create | KPI cards, charts, tables, print styles |
| `index.py` | Modify | 2 líneas: import + register_blueprint |
| `templates/partials/_sidebar.html` | Modify | 1 línea: nav link |

## Blueprint Registration

```python
from routes.dashboard_gerencial import bp_dashboard_gerencial
app.register_blueprint(bp_dashboard_gerencial, url_prefix='/')
```

## Route Design

**Route principal**: `GET /dashboard-gerencial` — `@check_session` + `@alertas_mensajes`, parsea `desde/hasta/id_sucursal`, llama `get_datos_dashboard()`, renderiza template con `data`, `sucursales`, `desde`, `hasta`, `id_sucursal`.

**6 API endpoints** para HTMX: `/api/dashboard-gerencial/{kpis|evolucion|sucursales|rubros|top-productos|top-vendedores}` — cada uno retorna `jsonify(success=True, data={...})` con los mismos parámetros `?desde=&hasta=&id_sucursal=&comparar=`.

## Service Layer

`services/dashboard_gerencial.py` — 6 funciones + 1 agregador:

```python
def get_kpis(desde, hasta, id_sucursal=None) -> dict
def get_evolucion_ventas(desde, hasta, id_sucursal=None, comparar=False) -> dict
def get_ventas_sucursal(desde, hasta, id_sucursal=None) -> list[dict]
def get_ventas_rubro(desde, hasta, id_sucursal=None) -> dict
def get_top_productos(desde, hasta, id_sucursal=None, limite=10) -> list[dict]
def get_top_vendedores(desde, hasta, id_sucursal=None, limite=10) -> list[dict]
def get_datos_dashboard(desde, hasta, id_sucursal=None) -> dict  # agregador
```

SQL: `db.session.execute(text("..."), params)`, JOINs `facturav→tipo_comprobantes→tipo_comp_aplica→tipo_operacion` (tipos 1,3,4), `Decimal` para monetarios, `format_currency()` para display. Filtro sucursal: `AND f.idsucursal = :id_sucursal` condicional.

## Template Structure

```
{% extends 'base.html' %}
{% block additional_css %} → dashboard-gerencial.css
{% block body %}
  Header + filtros (desde, hasta, sucursal select, comparar toggle)
  #seccion-kpis → 4 cards
  #seccion-evolucion → canvas#chartEvolucion
  #seccion-sucursales → table
  #seccion-rubros → table + canvas#chartRubros
  #seccion-top-productos → table
  #seccion-top-vendedores → table
{% block js_script %}
  dashboard-gerencial.js + <script nonce> con datosDashboard={{ data|tojson }}
```

HTMX: cada sección tiene `<div id="seccion-X">` con `hx-get` a su endpoint, `hx-trigger="change from:#desde, change from:#hasta, change from:#id_sucursal"`, `hx-swap="innerHTML"`.

## JavaScript Design

IIFE module con: paleta `COLORES`/`PALETA` (consistente con `reporte-gerencial.js`), chart instances (`chartEvolucion`, `chartRubros`) para destroy/recreate, `window.inicializarDashboard(datos)` + `window.destruirCharts()`, HTMX events `htmx:beforeSwap` (destroy charts) y `htmx:afterSwap` (recreate charts), formatting helpers `formatearMoneda()`, date presets (Hoy/Semana/Mes/Trimestre), keyboard shortcuts (Alt+H/S/M/T).

## CSS Design

Namespace `.dashboard-gerencial` para specificity. KPI cards (`.card-kpi`, `.border-start-*`), chart containers (fixed height, responsive), tables (`.table-dashboard`), Bootstrap 5 grid (xl:4/ md:2/ sm:1 cols), CSS variables para gradients, `@media print`.

## Error Handling

| Layer | Behavior |
|-------|----------|
| Route | Params inválidos → default 30 días |
| Service | `SQLAlchemyError` → print + return empty structure |
| Service | Data missing → return defaults ($0, 0, []) |
| Template | `{{ data.x|default('$0,00') }}` |
| JS | `if (!ctx) return;` guard |
| HTMX | `jsonify(success=False, message=str(e)), 500` |

## Performance

- Default 30 días, max 90. Queries usan `BETWEEN` con índice.
- Una query por widget (no N+1). HTMX refresh parcial.
- Sin caching Stage 1. Redis opcional en Stage 2.

## Migration

No migration. Todos archivos nuevos. Solo adiciones lineales en `index.py` y `_sidebar.html`.

## Open Questions

None.
