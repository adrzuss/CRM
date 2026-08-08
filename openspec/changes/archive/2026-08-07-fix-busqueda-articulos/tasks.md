# Tasks: fix-busqueda-articulos

## Review Workload Forecast

| Campo | Valor |
|-------|-------|
| Líneas estimadas | ~17 en 3 archivos (routes/articulos.py, services/articulos/reportes.py, services/articulos/precios.py) |
| Presupuesto 400 líneas | Low |
| PRs encadenados | No |
| Split sugerido | PR único, 1 commit |
| Delivery strategy | ask-always |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Work Units Sugeridas

| Unidad | Meta | PR | Notas |
|--------|------|----|-------|
| 1 | Defaults en handlers + guard None en services + returns en guards vacíos (3 archivos) + verificación | PR 1 | Commit único, base HEAD 02ad8f0; incluye verificación; no incluir `app.log` (dirty) |

## Fase 1: Defaults en handlers — `routes/articulos.py`

- [x] 1.1 `api_articulos` (L107-114): `draw = request.args.get('draw', 1, type=int)`, `start = request.args.get('start', 0, type=int)`, `length = request.args.get('length', 25, type=int)`, `order_column = request.args.get('order[0][column]', 0, type=int)`
- [x] 1.2 `api_lst_precios` (L427, L435): defaults `draw`=1 y `order_column`=0
- [x] 1.3 `api_lst_stock` (L490, L497): defaults `draw`=1 y `order_column`=0
- [x] 1.4 `api_lst_stock_faltantes` (L523, L530): defaults `draw`=1 y `order_column`=0
- [x] 1.5 Guards vacíos: agregar `return jsonify(response)` al final del bloque tras L445 (`if not idlista`), tras L507 (`if (not idmarca)or(not idrubro)` stock) y tras L540 (stock faltantes) — misma indentación que el dict

## Fase 2: Guard None en services

- [x] 2.1 `services/articulos/reportes.py` L23, L106, L175: `order_by = columns[order_column] if order_column is not None and order_column < len(columns) else 'codigo'`
- [x] 2.2 `services/articulos/precios.py` L20: mismo guard None (precios)

## Fase 3: Verificación

- [x] 3.1 `pytest tests/` — regresión suite existente (incluye `test_articulos.py`, `test_services_articulos.py`; pytest 9.1.1 confirmado instalado, config.yaml desactualizado)
- [x] 3.2 Manual API: 4 endpoints sin query string → HTTP 200 con claves `draw`, `recordsTotal`, `recordsFiltered`, `data`
- [x] 3.3 Manual: `search[value]=...` sin `order` → 200 con `recordsFiltered` = coincidencias; `draw=3` enviado → echo `3` en respuesta
- [x] 3.4 Manual: filtros vacíos (`lst_precios` sin `idlista`; `lst_stock`/`lst_stock_faltantes` sin `idmarca`/`idrubro`) → 200 con `data: []` y recuentos 0
- [x] 3.5 Regresión `fix-articulos-listado`: listado sin filtros muestra todos los artículos; `order[0][column]=8|9` → 200 con orden fallback 'codigo'; UI sin alerta "Ocurrió un error"

## Fase 4: Commit

- [x] 4.1 Commit único conventional (ej. `fix(articulos): endpoints DataTables responden 200 sin parametro order`); stage solo los 3 archivos Python; nunca `app.log`