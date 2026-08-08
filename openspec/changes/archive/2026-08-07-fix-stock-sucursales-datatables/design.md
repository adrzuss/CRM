# Design: fix-stock-sucursales-datatables

## Technical Approach

Fix mínimo de 3 sitios (sin arquitectura), réplica exacta del patrón del hermano `fix-busqueda-articulos` (2026-08-07): (1) defaults `draw`=1 y `order_column`=0 en el handler, (2) guard `is not None` **con rango offset `+1`** en `order_by` del servicio, (3) `return jsonify(response)` en el guard de filtro vacío. Respeta convenciones del proyecto: snake_case español, `request.args.get(default, type=int)`, `jsonify`, try-except. Líneas verificadas contra el fuente real en el árbol de trabajo actual.

## Architecture Decisions

| # | Decisión | Opciones | Elegida | Razón |
|---|----------|----------|---------|-------|
| 1 | Defaults `draw`/`order_column` | guard en service / default en handler | Default en handler | Patrón ya aplicado en los 4 endpoints hermanos; el echo de `draw` es contrato HTTP; `start`/`length` ya tenían default. |
| 2 | `None`-guard en service | solo handler / handler + service | Ambos (defensa en profundidad) | El handler cubre el caso real; el guard del service protege llamadas directas (tests, otros callers) — mismo criterio que fix-busqueda-articulos. |
| 3 | Rango con offset `+1` | `order_column < len(...)` (actual y roto) / `order_column+1 < len(...)` | Offset `+1` | `columns_names[0]` es `Articulo.id` oculto (link del frontend usa `row.id`); el índice DataTables k mapea a `columns_names[k+1]`. El guard actual permite `index = len` → `IndexError` en el borde. |
| 4 | Orden de respaldo | `'codigo'` / `'id'` | `'codigo'` | Primer columna visible (índice DataTables 0), patrón del módulo. |
| 5 | Guard filtro vacío | 404 / seguir al query / retornar | `return jsonify(response)` (200) | Spec aprobada: HTTP 200 `data: []`, recuentos 0, nunca ejecuta `obtener_stock_sucursales`. |
| 6 | Typo `resposne` (L617) | corregir / no tocar | No tocar | Funcional (define+y usa); el diff no alcanza esa línea; fuera de alcance del proposal. |

## Data Flow

    DataTables (serverSide) ──► GET /api/lst_stock_sucursales
      handler: draw=1, start=0, length=25, order_column=0 (defaults)
      │  guard: (not idmarca) or (not idrubro)
      │    └─► return jsonify {draw, 0, 0, []}   ← HTTP 200, nunca 500
      ▼
    obtener_stock_sucursales(idmarca, idrubro, draw, search, start, length, order_column, order_dir)
      │  order_by = columns_names[order_column+1]
      │    si order_column is not None y order_column+1 < len(columns_names)
      │    si no → 'codigo'
      ▼
    HTTP 200 · {draw, recordsTotal, recordsFiltered, data (dicts planos con id)}
    ```

## File Changes

| Archivo | Acción | Líneas | Descripción |
|---------|--------|--------|-------------|
| `routes/articulos.py` | Modificar | 595, 602 | Defaults `draw`=1, `order_column`=0 en `api_lst_stock_sucursales` |
| `routes/articulos.py` | Modificar | 606–612 | `return jsonify(response)` al final del guard de filtro vacío |
| `services/articulos/stock.py` | Modificar | 119 | Guard `is not None` + rango `order_column+1 < len(columns_names)` en `order_by` |

## Exact Code Edits (antes → después)

### 1. `api_lst_stock_sucursales` — routes/articulos.py L595

```python
# Antes
draw = request.args.get('draw', type=int)
# Después
draw = request.args.get('draw', 1, type=int)
```

### 2. routes/articulos.py L602

```python
# Antes
order_column = request.args.get('order[0][column]', type=int)  # Índice de la columna
# Después
order_column = request.args.get('order[0][column]', 0, type=int)  # Índice de la columna
```

### 3. Guard de filtro vacío — routes/articulos.py L606–612

```python
# Antes
if (not idmarca)or(not idrubro) :
    response = {
        'draw': draw,
        'recordsTotal': 0,
        'recordsFiltered': 0,  # Cambiar si aplicas filtros
        'data': []
    }
try:
# Después (agregar return al final del bloque, antes de try:)
if (not idmarca)or(not idrubro) :
    response = {
        'draw': draw,
        'recordsTotal': 0,
        'recordsFiltered': 0,  # Cambiar si aplicas filtros
        'data': []
    }
    return jsonify(response)
try:
```

> El `try` sigue existiendo para el error real del query; el guard retorna antes. El typo `resposne` (L617) NO se toca.

### 4. `obtener_stock_sucursales` — services/articulos/stock.py L119

```python
# Antes
order_by = columns_names[order_column+1] if order_column < len(columns_names) else 'codigo'
# Después
order_by = columns_names[order_column+1] if order_column is not None and order_column+1 < len(columns_names) else 'codigo'
```

**Racional offset `+1`**: `columns_names` parte con `Articulo.id.label("id")` (L53, oculto en la tabla, lo usa el link `update_articulo/${row.id}` del frontend). DataTables numera columnas visibles desde 0 (`codigo`, `marca`, `rubro`, `detalle`, sucursales…), o sea índice k ↔ `columns_names[k+1]`. El rango válido de `order_column` es `[0, len-2]`; el guard nuevo exige `order_column+1 < len(columns_names)` → acepta `index = len-1` como máximo y deriva a `'codigo'` ante `None` o borde (`IndexError` eliminado).

## UI behavior (nota, sin rediseño)

`templates/articulos/stock-sucursales.html` L134–155: DataTables inicializa `serverSide: true` y dispara la **primera carga al `document ready`** con `#idmarca`/`#idrubro` en "TODOS" (value `""`); el botón "Consultar" (L157–159) solo hace `table.ajax.reload()` y **no bloquea la carga con filtros vacíos**. Con la semántica aprobada esto es correcto: la carga inicial responde HTTP 200 `data: []` (tabla vacía, sin `alert` de error L144–146) y "Consultar" la recarga con filtros — mismo comportamiento que `lst_stock`/`lst_stock_faltantes`. No se rediseña la UI. Nota: el service conserva ramas para filtros parciales (stock.py L83–102) que quedan inalcanzables vía este endpoint por el guard; se dejan como defensa (out of scope).

## Interfaces / Contracts

`GET /api/lst_stock_sucursales` (GET, `@check_session`, `@alertas_mensajes`):

| Entrada | Sin enviar → |
|---------|--------------|
| `draw` | echo con default 1 |
| `start` / `length` | 0 / 25 (ya existían) |
| `order[0][column]` | `0` → orden `'codigo'` |
| `order[0][column]` fuera de rango o `None` (service) | fallback `'codigo'`, HTTP 200 |
| `idmarca` o `idrubro` vacío | HTTP 200 `{draw, recordsTotal:0, recordsFiltered:0, data:[]}` |

Salida: JSON plano `{draw, recordsTotal, recordsFiltered, data}`; filas = dicts aplanados `{id, codigo, marca, rubro, detalle, <sucursal>:…}`.

## Testing Strategy

pytest instalado (9.x) y suite `tests/` con conftest (Flask test client, SQLite in-memory); los checks manuales son primarios, pytest es regresión complementaria (config.yaml está desactualizado, ignora "no test runner").

| Capa | Qué | Cómo |
|------|-----|------|
| Handler (pytest) | Sin query string → 200, `draw`=1, `data:[]`; guard no invoca el service | `tests/test_articulos.py` siguiendo `test_api_articulos_datatables` (patch `get_alertas` + `get_mensajes` + `obtener_stock_sucursales`) |
| Handler (pytest) | Con filtros y sin `order[0][column]` → `order_column=0` pasado al service | idem, assert en la mock |
| Manual (test client real) | Sin `order` con filtros → 200, orden `'codigo'` | `client.get('/articulos/api/lst_stock_sucursales?idmarca=..&idrubro=..&draw=1')` |
| Manual (borde) | Sort por la última sucursal y por índice `len-1`/`len` → 200, fallback, sin `TypeError`/`IndexError` | curl con `order[0][column]=N` |
| Manual (filtro vacío) | Sin `idmarca`/`idrubro` → 200 `data:[]`, sin `alert` en UI | navegación real + consola |
| Regresión | `pytest tests/` completo | suite existente |

## Migration / Rollout

Sin migración ni esquema; commit único en `routes/articulos.py` + `services/articulos/stock.py` (2 archivos, sin dependencias). Rollback: `git revert <hash>` del commit (el diff es ortogonal al archivo `fix-busqueda-articulos`, líneas disjuntas; no toca el árbol sucio `app.log`/`__pycache__`).

## Open Questions

- Ninguna bloqueante: causa raíz confirmada y línea a línea verificado contra el fuente real.