# Propuesta: fix-stock-sucursales-datatables

## Intent

La vista "Stock por Sucursal" falla al cargar: DataTables muestra "Ocurrió un error al cargar los datos" (`templates/articulos/stock-sucursales.html:146`). Causa raíz confirmada: `api_lst_stock_sucursales` (`routes/articulos.py:590`) lee `order[0][column]` sin default → `None`; `obtener_stock_sucursales` (`services/articulos/stock.py:119`) hace `order_column+1` / `None < len` → `TypeError` → HTTP 500. Es el ÚLTIMO endpoint del módulo sin el patrón ya aplicado en `fix-busqueda-articulos` (verificado: el resto de `order[0][column]` ya tiene default `0`). Sumado: el guard de filtro vacío (L606–612) construye `response` sin `return` (mismo defecto que los 3 corregidos).

## Scope

### In Scope
- Defaults en handler: `draw`=1 y `order_column`=0 (`routes/articulos.py` L595, L602; `start`/`length` ya tienen default).
- Guard `None` en `order_by` de `obtener_stock_sucursales` (`services/articulos/stock.py:119`), respetando el offset `+1` por la columna oculta `id`.
- `return jsonify(response)` en el guard de filtro vacío (L606–612) — mismo patrón que los 3 endpoints corregidos.

### Out of Scope
- Otros endpoints, refactor del pivot de sucursales, perf.
- Suciedad del árbol de trabajo (app.log/.pyc), claves de sesión ajenas.
- El typo `resposne` (L617) es funcional (define+y usa); se corrige solo si el diff lo toca.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `articulos-api-json`: extiende el contrato DataTables a un 5.º endpoint, `api_lst_stock_sucursales` — defaults (`draw`=1, `order_column`=0), fallback de orden `'codigo'`, echo de `draw` y guard de filtro vacío con `return`. La forma de la respuesta es el MISMO JSON aplanado `{draw, recordsTotal, recordsFiltered, data}` (filas tipo dict, claves `codigo|marca|rubro|detalle` + un campo por sucursal), NO anidado; incluye `id` oculto (lo usa el link del frontend).

## Approach

Fix mínimo de 3 sitios, sin arquitectura, réplica exacta del patrón del hermano `fix-busqueda-articulos`: (1) defaults en el handler, (2) guard `is not None` en `order_by` del servicio con offset `+1`, (3) `return` en el guard de filtro vacío. Spanish snake_case, `request.args.get(..., type=int)`.

## Affected Areas

| Área | Impacto | Descripción |
|------|--------|-------------|
| `routes/articulos.py` L595, L602 | Modificado | Defaults `draw`=1, `order_column`=0 en `api_lst_stock_sucursales` |
| `routes/articulos.py` L606–612 | Modificado | `return jsonify(response)` en guard |
| `services/articulos/stock.py` L119 | Modificado | Guard `is not None` + rango en `order_by` (offset `+1`) |

## Risks

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Guard de vacío cambia semántica: los selects tienen default "TODOS" (`idmarca`/`idrubro` vacíos) → con `return`, la carga inicial devolvería `data: []` (hoy cae al branch "todos" del pivot). | Media | Mantener la semántica del hermano (`lst_stock`/`faltantes`: filtro requerido → 200 vacío). Confirmar en design que la UI exige ambos filtros antes de "Consultar" (no es regresión respecto al comportamiento comprometido del módulo). |
| Offset `+1`: el guard original usa `order_column < len(columns)`, que permite `index = len` → `IndexError` en el borde. | Baja | El guard nuevo incluirá `order_column+1 < len(columns_names)` — el fallback `'codigo'` incluye rango + `None`. |

## Rollback Plan

`git revert` del commit único. Sin migraciones ni esquema; 2 archivos Python, sin dependencias externas; el diff es ortogonal al archivo `fix-busqueda-articulos` (no toca `reportes.py`/`precios.py`).

## Dependencies

- Ninguna externa. No conflictos con cambios ya archiveados (líneas disjuntas).

## Success Criteria

- [ ] `GET /api/lst_stock_sucursales` sin query string → HTTP 200, JSON con `draw`/`recordsTotal`/`recordsFiltered`/`data` (sin 500)
- [ ] Sin `order[0][column]` pero con filtros → 200 con datos, orden `'codigo'`
- [ ] Con ambos filtros seleccionados → la UI muestra datos; sin que aparezca la alerta `ajax.error`
- [ ] Sort por cualquier columna (última sucursal incluida) → 200, sin `TypeError`/`IndexError`
- [ ] `draw` recibido se responde igual (echo)