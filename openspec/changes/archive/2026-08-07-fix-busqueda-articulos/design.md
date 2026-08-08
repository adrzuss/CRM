# Design: fix-busqueda-articulos

## Technical Approach

Fix mínimo de 4 patrones (sin arquitectura): (1) defaults en handlers, (2) guard `None` en services, (3) `return` en guards de lista vacía. Se respetan los patrones existentes del proyecto (snake_case español, `request.args.get` con default + `type=int`, `jsonify`).

## Architecture Decisions

| # | Decisión | Opciones | Elegida | Razón |
|---|----------|----------|---------|-------|
| 1 | Default `draw` en handler | guard en service / default en handler | Default en handler | El echo de `draw` es responsabilidad del contrato HTTP; DataTables lo requiere entero. Patrón ya usado en `api_lst_precios` L428 (`start`, 0). |
| 2 | Fallback `order_column` | solo handler / handler + service | Handler + service (double guard) | El handler cubre el caso real; el guard del service es defensa en profundidad y cubre llamadas internas directas (tests, otros callers). |
| 3 | Orden de respaldo | `'codigo'` / `'id'` | `'codigo'` | Comportamiento ya documentado en reportes.py L22; primer índice de `columns`. |
| 4 | `draw` fijo vs echo | forzar 1 siempre | Echo del valor recibido | Spec `articulos-api-json`: "draw en el JSON DEBE replicar el valor recibido (3)". Default solo cuando falta. |
| 5 | Guard de lista vacía | cerrar endpoint en 404 / retornar JSON | `return jsonify(response)` | Spec: HTTP 200 con `data: []` y recuentos 0; nunca ejecutar el query subyacente. |

## Data Flow

    DataTables (sin order) ──► GET /api/articulos
        │  handler: draw=1, start=0, length=25, order_column=0
        ▼
    get_listado_articulos() ──► order_column es int ──► columns[0]='codigo'
        │  (guard: None u out-of-range ──► 'codigo')
        ▼
    HTTP 200 + JSON {draw, recordsTotal, recordsFiltered, data}

## File Changes

| Archivo | Acción | Líneas | Descripción |
|---------|--------|--------|-------------|
| `routes/articulos.py` | Modificar | 107–115 | Defaults en `api_articulos` (draw=1, start=0, length=25, order_column=0) |
| `routes/articulos.py` | Modificar | 427, 435 | Defaults `draw`=1, `order_column`=0 en `api_lst_precios` |
| `routes/articulos.py` | Modificar | 439–446 | `return jsonify(response)` en guard `if not idlista` |
| `routes/articulos.py` | Modificar | 490, 497 | Defaults `draw`=1, `order_column`=0 en `api_lst_stock` |
| `routes/articulos.py` | Modificar | 501–508 | `return jsonify(response)` en guard |
| `routes/articulos.py` | Modificar | 523, 530 | Defaults `draw`=1, `order_column`=0 en `api_lst_stock_faltantes` |
| `routes/articulos.py` | Modificar | 534–540 | `return jsonify(response)` en guard |
| `services/articulos/reportes.py` | Modificar | 23, 106, 175 | Guard None en `order_by` |
| `services/articulos/precios.py` | Modificar | 20 | Guard None en `order_by` |

## Exact Code Edits (antes → después)

### 1. `api_articulos` — routes/articulos.py L107–115

```python
# Antes
draw = request.args.get('draw', type=int)
start = request.args.get('start', type=int)  # Índice del primer registro
length = request.args.get('length', type=int)
...
order_column = request.args.get('order[0][column]', type=int)

# Después
draw = request.args.get('draw', 1, type=int)
start = request.args.get('start', 0, type=int)
length = request.args.get('length', 25, type=int)
...
order_column = request.args.get('order[0][column]', 0, type=int)
```

### 2. Sibling endpoints (mismo patrón) — L427, L435 / L490, L497 / L523, L530

```python
# Antes
draw = request.args.get('draw', type=int)
...
order_column = request.args.get('order[0][column]', type=int)

# Después
draw = request.args.get('draw', 1, type=int)
...
order_column = request.args.get('order[0][column]', 0, type=int)
```

### 3. Guard de lista vacía — L439–445, L501–508, L534–540

```python
# Antes
if not idlista:   # o: if (not idmarca) or (not idrubro) — en los de stock
    response = {
        'draw': draw,
        'recordsTotal': 0,
        'recordsFiltered': 0,
        'data': []
    }
    # SIN return → continúa a la consulta real

# Después — agregar al final del bloque:
    return jsonify(response)
```

### 4. Guard `order_by` en services — reportes.py L23/106/175, precios.py L20

```python
# Antes
order_by = columns[order_column] if order_column < len(columns) else 'codigo'

# Después
order_by = columns[order_column] if order_column is not None and order_column < len(columns) else 'codigo'
```

## Interfaces / Contracts

Endpoints DataTables (sin cambios en firma, solo comportamiento):

| Endpoint | Sin `order` → | Sin `draw` → | Sin `start/length` → | Filtro vacío → |
|----------|---------------|--------------|------------------------|----------------|
| `GET /api/articulos` | 200, JSON válido | draw echo (default 1) | start=0, length=25 | n/a |
| `GET /api/lst_precios` | 200, JSON válido | draw=1 | ya existían defaults | 200 `data:[]` |
| `GET /api/lst_stock` | 200, JSON válido | draw=1 | ya existían | 200 `data:[]` |
| `GET /api/lst_stock_faltantes` | 200, JSON válido | draw=1 | ya existían | 200 `data:[]` |

- `draw` recibido se responde tal cual (echo); el default solo aplica cuando falta.
- Fallback de orden: `'codigo'` para `null`/ausente/out-of-range (índices 8/9 Imagen/Acciones).

## Testing Strategy

**Contexto real**: config.yaml dice "no test runner", pero pytest 9.1.1 YA está instalado y `tests/` existe con conftest (Flask test client) + `test_articulos.py`, `test_services_articulos.py`. Los checks manuales son primarios; pytest es verificación automatizada complementaria.

| Capa | Qué | Cómo |
|------|-----|------|
| Manual rutas | 4 endpoints sin query string | `python index.py` + curl; o test client pytest |
| Manual sin `order` | `/api/articulos`, `lst_*` | HTTP 200, JSON con draw/recordsTotal/recordsFiltered/data |
| Manual filtro vacío | `lst_*` sin `idlista`/`idmarca`/`idrubro` | 200 + `data: []`, no ejecuta query |
| Manual seco | `order[0][column]=8|9` | 200, fallback 'codigo' |
| Automatizado | `pytest tests/` (suite existente) | Regresión de rutas/servicios de artículos |

## Migration / Rollout

Sin migración ni cambios de esquema. Commit único; `git revert` revierte por completo, sin importar el orden de aplicación (3 archivos Python: `routes/articulos.py`, `services/articulos/reportes.py`, `services/articulos/precios.py`; sin dependencias externas).

## Coordination / Apply Sequence (con `fix-articulos-listado`)

1. **Estado real (verificado en repo, HEAD `d7e89c0` 2026-08-07)**: `fix-articulos-listado` YA ESTÁ aplicado y commiteado. Sus cambios (`reportes.py` L22 comentario guard, L37–44 refactor JOIN→filter; `articulos.html`: BASE_URL, orderable, idioma, counter) están en el árbol de trabajo actual. No hay nada pendiente de aplicar para ese cambio.
2. **Compatibilidad de líneas**: nuestros edits tocan `reportes.py` L23 (una línea distinta al L22 comentado por el otro cambio) y rutas `articulos.py` L107–540; el otro cambio NO modifica esas líneas de `routes/articulos.py`. Comparten el MISMO archivo (`reportes.py`), pero en líneas disjuntas (22 vs 23; 37-44 vs nada nuestro). **Sin conflictos textuales, sin rebase**; el commit de este cambio aplica limpio sobre HEAD.
3. **Estrategia de verificación integrada**: tras aplicar nuestro diff, correr la suite completa `pytest tests/` (includes tests de routes/servicios de artículos) más verificación manual: (a) listado sin filtros → todos los artículos (regresión del JOIN de fix-articulos-listado), (b) sort por Imagen/Acciones → 200 (regresión del arreglo listado), (c) búsqueda sin `order` → 200 (nuestra corrección). Ambos cambios se prueban juntos porque tocan la misma función `get_listado_articulos` (colisión de comportamiento, no textual).

## Open Questions

- Ninguna: la causa raíz es clara y confirmada (proposal); los line numbers fueron verificados contra el fuente real en HEAD. Como todo está committeado, no depende de la secuencia del otro cambio.