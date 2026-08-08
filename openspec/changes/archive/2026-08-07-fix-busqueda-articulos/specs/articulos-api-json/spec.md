# Articulos API JSON — Spec de bugfix

## Propósito

Contrato de comportamiento de los 4 endpoints DataTables del módulo artículos (`api_articulos`, `api_lst_precios`, `api_lst_stock`, `api_lst_stock_faltantes`): deben responder JSON DataTables válido con HTTP 200 aunque la petición no incluya `order`, `draw`, `start` o `length`, sin disparar la alerta de error del frontend.

---

## ADDED Requirements

### Requirement: Respuesta DataTables válida sin parámetro `order`

Cada endpoint DEBE responder HTTP 200 con un JSON que incluya las claves `draw`, `recordsTotal`, `recordsFiltered` y `data` cuando la petición no contenga `order[0][column]` (también cuando falten `draw`, `start` o `length`). El sistema DEBE aplicar los defaults `draw`=1, `start`=0, `length`=25 y `order_column`=0, y DEBE usar `'codigo'` como orden de respaldo si `order_column` es `None` o supera las columnas ordenables. DEBE devolver HTTP 200, nunca HTTP 500 (TypeError/IndexError de `order_column`).

#### Scenario: Carga inicial sin query string

- GIVEN el endpoint `GET /api/articulos` se solicita sin query string
- WHEN el handler procesa la petición
- THEN la respuesta DEBE ser HTTP 200
- AND el JSON DEBE contener `draw` (entero), `recordsTotal`, `recordsFiltered` y `data`
- AND el frontend NO DEBE mostrar el bloque `ajax.error` "Ocurrió un error al cargar los datos..."

#### Scenario: Búsqueda sin parámetro de orden

- GIVEN el usuario escribe en el buscador de la tabla
- WHEN el cliente envía `search[value]` sin `order[0][column]`
- THEN la respuesta DEBE ser HTTP 200 con `data` filtrado
- AND `recordsFiltered` DEBE reflejar la cantidad de coincidencias

#### Scenario: Fallback de orden a 'codigo'

- GIVEN `order_column` ausente o con valor `None` (o índice fuera de rango, p. ej. columnas Imagen/Acciones)
- WHEN el servicio construye `order_by`
- THEN DEBE usar `'codigo'` como columna de ordenamiento sin lanzar `TypeError` ni `IndexError`

#### Scenario: Echo de `draw`

- GIVEN el cliente envía un valor `draw` (p. ej. 3)
- WHEN el endpoint responde
- THEN `draw` en el JSON DEBE replicar el valor recibido (3), no un valor fijo

#### Scenario: Recuento de registros

- GIVEN una búsqueda deja 12 de 200 artículos
- WHEN el endpoint responde con la página pedida
- THEN `recordsTotal` DEBE reflejar el total sin filtro y `recordsFiltered` el total filtrado

---

### Requirement: Guards de filtro vacío retornan la respuesta vacía

En `api_lst_precios`, `api_lst_stock` y `api_lst_stock_faltantes`, cuando el filtro requerido (`idlista`, `idmarca`/`idrubro`) es `None` o falsy, el handler DEBE retornar `jsonify(response)` con `data: []`, `recordsTotal: 0` y `recordsFiltered: 0`, y NO debe continuar ejecutando la consulta subyacente.

#### Scenario: Lista de precios sin `idlista`

- GIVEN `GET /api/lst_precios` sin `idlista`
- WHEN el guard de lista vacía se evalúa
- THEN la respuesta DEBE ser HTTP 200 con `data: []` y recuentos en 0
- AND el handler DEBE retornar ahí (no ejecutar `get_listado_precios`)

#### Scenario: Stock sin `idmarca` o sin `idrubro`

- GIVEN `GET /api/lst_stock` (o `/api/lst_stock_faltantes`) sin `idmarca` o sin `idrubro`
- WHEN el guard de lista vacía se evalúa
- THEN la respuesta DEBE ser HTTP 200 con `data: []` y recuentos en 0
- AND el handler DEBE retornar ahí (no ejecutar el query posterior)