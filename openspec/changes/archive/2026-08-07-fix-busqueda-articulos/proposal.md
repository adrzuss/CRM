# Propuesta: fix-busqueda-articulos

## Intent

El listado de artículos (DataTables server-side) devuelve error al buscar/filtrar: cualquier petición muestra "Ocurrió un error al cargar los datos". Causa raíz confirmada y reproducida: `routes/articulos.py:114` lee `request.args.get('order[0][column]', type=int)` sin default → `None`; `services/articulos/reportes.py:23` compara `None < len(columns)` → `TypeError` → HTTP 500 → `ajax.error` de DataTables. El payload completo funciona (200 con JSON válido); solo fallan las peticiones sin parámetro `order`.

## Scope

### In Scope
- Fix primario: defaults en handler `api_articulos` (`draw`=1, `start`=0, `length`=25, `order_column`=0) + guarda None en service (`get_listado_articulos`).
- Recomendado (mismo patrón, barato): `api_lst_precios`, `api_lst_stock`, `api_lst_stock_faltantes` → default `order_column`=0 y `draw`=1 en handlers; guard None en `get_listado_precios`, `get_listado_stock`, `get_listado_stock_faltantes`.
- Corrección adyacente (mismos handlers): los guards "lista vacía" (L439/501/534) construyen `response` pero NO hacen `return` → agregar `return jsonify(response)`.

### Out of Scope
- Doble carga de jQuery (bundle DataTables + base.html) — issue conocido, no se toca.
- Sesión sin `plan`/`dias_vencimiento` al render directo de la pestaña — issue conocido, no se toca.
- Refactor de builders de query, nuevas columnas, cambios de esquema.

## Capabilities

### New Capabilities
- `articulos-api-json`: contrato de los 4 endpoints DataTables (articulos, lst_precios, lst_stock, lst_stock_faltantes): deben devolver JSON DataTables válido (HTTP 200) aunque falten `order`, `draw`, `start`, `length`; default `order_by` = 'codigo'.

### Modified Capabilities
- None

## Approach

Fix mínimo de 4 líneas, no arquitectura:

1. Handler (`routes/articulos.py`): dar defaults a `draw`/`start`/`length`/`order_column` en `api_articulos` (L107-115) y a `draw`/`order_column` en los 3 endpoints de listado (L427-435, L490-497, L523-530).
2. Service: guard None en `order_by` (reportes.py L23, L106, L175; precios.py L20): `order_by = columns[order_column] if order_column is not None and order_column < len(columns) else 'codigo'`.
3. Agregar `return jsonify(response)` en los guards vacíos de los 3 endpoints de listados (1 línea cada uno).

## Affected Areas

| Area | Impact | Descripción |
|------|--------|-------------|
| `routes/articulos.py` L107-115 | Modificado | Defaults en params de `api_articulos` |
| `routes/articulos.py` L423-454 | Modificado | Defaults + return en guard `api_lst_precios` |
| `routes/articulos.py` L485-516 | Modificado | Defaults + return en guard `api_lst_stock` |
| `routes/articulos.py` L518-548 | Modificado | Defaults + return en guard `api_lst_stock_faltantes` |
| `services/articulos/reportes.py` L23, L106, L175 | Modificado | Guard None en `order_by` |
| `services/articulos/precios.py` L20 | Modificado | Guard None en `order_by` |

## Risks

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Especificar tipo/fallback de `order_column` desplaza el orden por defecto | Baja | Fallback `'codigo'` es el comportamiento ya documentado en L22 |
| Conflicto con cambio en vuelo `fix-articulos-listado` (reportes.py L20-41) | Media | Coordinar secuencia; ambos cambios son pequeños, sin migración |

## Rollback Plan

Revert de commit único (`git revert`). Sin cambios de esquema ni migraciones; toca solo 2 archivos Python.

## Dependencies

- Ninguna externa.
- Coordinar con `fix-articulos-listado` (en vuelo, toca `reportes.py` L22-41 y `articulos.html`); no hay bloqueo.

## Success Criteria

- [ ] `GET /api/articulos` sin query string → HTTP 200, JSON DataTables válido (draw, recordsTotal, recordsFiltered, data), sin 500
- [ ] `GET /api/lst_precios|lst_stock|lst_stock_faltantes` sin `order` → 200 con JSON válido
- [ ] Búsqueda/filtro desde la UI no muestra la alerta "Ocurrió un error..."
- [ ] Sort por columnas Imagen/Acciones cae a 'codigo' (sin error)