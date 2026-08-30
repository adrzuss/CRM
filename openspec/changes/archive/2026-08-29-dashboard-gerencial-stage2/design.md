# Design: Dashboard Gerencial — Etapa 2 (Stock)

## Technical Approach

Extiende el dashboard Stage 1 con una sección de análisis de stock usando el patrón existente: service functions → route endpoints → Jinja2 rendering. Las queries SQL se escriben directamente con `text()` (patrón del proyecto). Stock es point-in-time (sin rango de fechas), excepto "sin movimiento" que usa lookback de N días. Se reutilizan `_formato_moneda()`, `_sucursal_filter()`, y la respuesta wrapper `_api_respuesta()`.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|-------------|-----------|
| Campo mínimo de stock | `deseable` (no `minimo`) | Renombrar en DB | Exploration found `stocks.deseable` is the real field. All existing SPs use it. Renaming DB column is out of scope. |
| Filtro sucursal para stock | `_sucursal_filter(alias='s', params)` | Custom filter | Reutiliza función existente; stocks usa alias `s` para JOIN con `sucursales` |
| Sin movimiento loading | Lazy load via HTMX fetch | Render server-side | Tabla potencialmente grande. Lazy load evita bloquear carga inicial del dashboard. Primer load solo muestra 30 días. |
| Gráfico stock por sucursal | Solo tabla (sin chart) | Bar chart | Proposal especifica tablas. No hay suficientes sucursales para justificar chart. |
| Filtro de fechas | No aplica a stock KPIs | Ignorar | Stock es snapshot actual. Solo "sin movimiento" necesita lookback window. |
| Límite sin movimiento | LIMIT 100 en query | Paginación completa | Balance entre utilidad y performance. Tabla scrollable. |

## Data Flow

```
MySQL (stocks, articulos, sucursales, itemsv, facturav)
    │
    ▼
services/dashboard_gerencial.py
    ├── get_stock_kpis(id_sucursal)         → dict {sin_stock, bajo_minimo, saludable, exceso, total, valor}
    ├── get_stock_sucursal(id_sucursal)     → list [{sucursal, unidades, valor, sin_stock, bajo_minimo}]
    └── get_productos_sin_movimiento(id_sucursal, dias) → list [{codigo, detalle, stock, rubro, ultima_venta}]
    │
    ▼
routes/dashboard_gerencial.py
    ├── GET /api/dashboard-gerencial/stock-kpis
    ├── GET /api/dashboard-gerencial/stock-sucursales
    └── GET /api/dashboard-gerencial/stock-sin-movimiento
    │
    ▼
templates/dashboard-gerencial.html (secciones HTML embebidas + HTMX lazy)
    │
    ▼
static/js/dashboard-gerencial.js (toggle días sin movimiento)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modify | Agregar 3 funciones: `get_stock_kpis`, `get_stock_sucursal`, `get_productos_sin_movimiento` |
| `routes/dashboard_gerencial.py` | Modify | Agregar 3 endpoints HTMX + imports + actualización `get_datos_dashboard()` |
| `templates/dashboard-gerencial.html` | Modify | Agregar 3 secciones HTML después de Top Vendedores |
| `static/js/dashboard-gerencial.js` | Modify | Agregar event listener para toggle días en sin-movimiento |
| `static/css/dashboard-gerencial.css` | Modify | Agregar estilos para badges de estado de stock |

## Interfaces / Contracts

### Service Functions

```python
# Retorna dict con 4 categorías + totales
def get_stock_kpis(id_sucursal=None) -> dict:
    # Keys: sin_stock, bajo_minimo, saludable, exceso, total_articulos, valor_estimado
    # Query: SELECT con CASE WHEN sobre stocks + articulos

# Retorna lista de dicts por sucursal
def get_stock_sucursal(id_sucursal=None) -> list[dict]:
    # Keys: sucursal, id_sucursal, unidades, valor, sin_stock, bajo_minimo

# Retorna lista de artículos sin movimiento
def get_productos_sin_movimiento(id_sucursal=None, dias=30) -> list[dict]:
    # Keys: codigo, detalle, stock_actual, rubro, ultima_venta
    # Query: LEFT JOIN itemsv + facturav, HAVING ultima_venta IS NULL OR < threshold
```

### Route Endpoints

```python
GET /api/dashboard-gerencial/stock-kpis?id_sucursal=
GET /api/dashboard-gerencial/stock-sucursales?id_sucursal=
GET /api/dashboard-gerencial/stock-sin-movimiento?id_sucursal=&dias=30
```

### SQL Patterns (Key Queries)

```sql
-- Stock KPIs: clasificar artículos por estado
SELECT
  SUM(CASE WHEN s.actual <= 0 THEN 1 ELSE 0 END) AS sin_stock,
  SUM(CASE WHEN s.actual > 0 AND s.deseable > 0 AND s.actual < s.deseable THEN 1 ELSE 0 END) AS bajo_minimo,
  SUM(CASE WHEN s.actual >= s.deseable AND (s.maximo IS NULL OR s.maximo = 0 OR s.actual <= s.maximo) THEN 1 ELSE 0 END) AS saludable,
  SUM(CASE WHEN s.maximo > 0 AND s.actual > s.maximo THEN 1 ELSE 0 END) AS exceso,
  COUNT(DISTINCT s.idarticulo) AS total,
  SUM(CASE WHEN a.costo_total > 0 THEN s.actual * a.costo_total ELSE 0 END) AS valor
FROM stocks s
JOIN articulos a ON s.idarticulo = a.id
WHERE a.baja = '1900-01-01' AND a.idtipoarticulo IN (1, 3)
  [AND s.idsucursal = :id_sucursal]

-- Sin movimiento: LEFT JOIN con facturav para última venta
SELECT a.codigo, a.detalle, s.actual, COALESCE(r.nombre, 'Sin rubro'),
  MAX(f.fecha) AS ultima_venta
FROM stocks s
JOIN articulos a ON s.idarticulo = a.id
LEFT JOIN itemsv iv ON iv.idarticulo = a.id
LEFT JOIN facturav f ON iv.idfactura = f.id
LEFT JOIN rubros r ON a.idrubro = r.id
WHERE a.baja = '1900-01-01' AND s.actual > 0
  [AND s.idsucursal = :id_sucursal]
GROUP BY a.id, a.codigo, a.detalle, s.actual, r.nombre
HAVING ultima_venta IS NULL OR ultima_venta < DATE_SUB(CURDATE(), INTERVAL :dias DAY)
ORDER BY ultima_venta ASC
LIMIT 100
```

## CSS Additions

```css
/* Badges de estado de stock */
.badge-stock-sin-stock   { background-color: #e74a3b; }  /* danger */
.badge-stock-bajo-minimo { background-color: #f6c23e; color: #000; }  /* warning */
.badge-stock-saludable   { background-color: #1cc88a; }  /* success */
.badge-stock-exceso      { background-color: #36b9cc; }  /* info */

/* Tabla sin-movimiento: columna de días toggle */
.btn-dias-activo { background-color: #4e73df; color: #fff; }
```

## JS Additions

```javascript
// Toggle días para productos sin movimiento
document.querySelectorAll('.dias-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const dias = this.dataset.dias;
        // Fetch /api/dashboard-gerencial/stock-sin-movimiento?dias=X
        // Re-renderizar tabla sin-movimiento
    });
});
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | 3 service functions | Mock `db.session.execute`, verify SQL params, test edge cases (sin_stock=0, deseable=NULL) |
| Integration | Route endpoints | pytest + test client, verify JSON response structure |
| E2E | Dashboard loads with stock section | Verify template renders, HTMX lazy load works |

## Migration / Rollout

No migration required. All tables and columns already exist. Feature is additive — no changes to existing Stage 1 behavior.

## Open Questions

- None. All design decisions resolved from exploration findings.
