# Delta Spec: fix-cambio-precio-product-loading

## Domain: product-filtering

### MODIFIED Requirements

#### Requirement: Filter products by optional marca, rubro, lista_precio, porcentaje via query params

The system MUST accept GET requests to `/articulos/filtrar_articulos` with optional query parameters `marca`, `rubro`, `lista_precio`, `porcentaje`. The `lista_precio` parameter MUST be provided (required); all others are optional and default to `None` when omitted. The endpoint MUST return 200 with filtered products (empty array if no matches) or 400 if `lista_precio` is missing.
(Previously: Route required `marca` and `rubro` as path parameters `/filtrar_articulos/<marca>/<rubro>` and did not support `lista_precio`/`porcentaje` filters)

##### Scenario: SCE-001 - Filter with all parameters provided

- GIVEN client sends GET `/articulos/filtrar_articulos?marca=1&rubro=2&lista_precio=3&porcentaje=10`
- WHEN server processes request
- THEN server calls `obtenerArticulosMarcaRubro` with all four parameters
- AND server returns 200 with filtered product list

##### Scenario: SCE-002 - Filter with only required lista_precio

- GIVEN client sends GET `/articulos/filtrar_articulos?lista_precio=3`
- WHEN server processes request
- THEN server calls `obtenerArticulosMarcaRubro` with `marca=None`, `rubro=None`, `lista_precio=3`, `porcentaje=None`
- AND server returns 200 with all products for that price list

##### Scenario: SCE-003 - Filter with only marca (no rubro)

- GIVEN client sends GET `/articulos/filtrar_articulos?marca=1&lista_precio=3`
- WHEN server processes request
- THEN server calls `obtenerArticulosMarcaRubro` with `marca=1`, `rubro=None`, `lista_precio=3`
- AND server returns 200 with products matching marca and price list

##### Scenario: SCE-004 - Filter with only rubro (no marca)

- GIVEN client sends GET `/articulos/filtrar_articulos?rubro=2&lista_precio=3`
- WHEN server processes request
- THEN server calls `obtenerArticulosMarcaRubro` with `marca=None`, `rubro=2`, `lista_precio=3`
- AND server returns 200 with products matching rubro and price list

##### Scenario: SCE-005 - Missing required lista_precio returns 400

- GIVEN client sends GET `/articulos/filtrar_articulos?marca=1&rubro=2`
- WHEN server processes request
- THEN server returns 400 with error message indicating `lista_precio` is required

##### Scenario: SCE-006 - Empty result returns 200 with empty array

- GIVEN client sends GET with filters that match no products
- WHEN server processes request
- THEN server returns 200 with empty JSON array `[]`

---

## Domain: price-change-processing

### MODIFIED Requirements

#### Requirement: Reject price change requests with zero items

The system MUST validate that the `detalle` (items) array contains at least one element before processing a price change. If the array is empty, the system MUST return an error response without modifying any data.
(Previously: No server-side validation; `procesar_cambio_precio` would process empty item arrays)

##### Scenario: SCE-007 - Process price change with valid items succeeds

- GIVEN client sends POST to `/procesar_cambio_precio` with `detalle` containing 1+ items
- WHEN server processes request
- THEN server applies price changes to all items
- AND server returns success response with updated data

##### Scenario: SCE-008 - Process price change with empty items returns error

- GIVEN client sends POST to `/procesar_cambio_precio` with `detalle: []`
- WHEN server processes request
- THEN server returns error response (400 or JSON with `success: false`)
- AND no price changes are persisted to database

##### Scenario: SCE-009 - Manual row addition with items passes validation

- GIVEN user manually adds rows to price change table via UI (not via filter flow)
- WHEN user submits price change
- THEN server validates `detalle.length > 0` passes
- AND server processes the price change normally

---

## Domain: frontend-cambio-precio

### ADDED Requirements

#### Requirement: JavaScript fetches products using query parameters

The system MUST construct the fetch URL for product filtering using query parameters (`?marca=X&rubro=Y&lista_precio=Z&porcentaje=P`) instead of path parameters. The `marca` and `rubro` parameters MUST be included only when selected (non-empty); `lista_precio` MUST always be included.

##### Scenario: SCE-010 - Click cargarRubroMarca with both filters selected

- GIVEN user selects marca=1, rubro=2, lista_precio=3, porcentaje=10
- WHEN user clicks #cargarRubroMarca button
- THEN JS calls `fetch('/articulos/filtrar_articulos?marca=1&rubro=2&lista_precio=3&porcentaje=10')`
- AND table populates with returned products

##### Scenario: SCE-011 - Click cargarRubroMarca with only marca selected

- GIVEN user selects marca=1, lista_precio=3 (rubro not selected)
- WHEN user clicks #cargarRubroMarca button
- THEN JS calls `fetch('/articulos/filtrar_articulos?marca=1&lista_precio=3')`
- AND table populates with filtered products

##### Scenario: SCE-012 - Click cargarRubroMarca with only rubro selected

- GIVEN user selects rubro=2, lista_precio=3 (marca not selected)
- WHEN user clicks #cargarRubroMarca button
- THEN JS calls `fetch('/articulos/filtrar_articulos?rubro=2&lista_precio=3')`
- AND table populates with filtered products

##### Scenario: SCE-013 - Click cargarRubroMarca with neither marca nor rubro

- GIVEN user selects only lista_precio=3
- WHEN user clicks #cargarRubroMarca button
- THEN JS calls `fetch('/articulos/filtrar_articulos?lista_precio=3')`
- AND table populates with all products for that price list

##### Scenario: SCE-014 - Empty result shows empty table (no error)

- GIVEN API returns 200 with empty array `[]`
- WHEN JS receives response
- THEN table is cleared and shows no rows (no error toast)

---

## Traceability Matrix

| Requirement | Proposal Intent | Affected Files |
|-------------|-----------------|----------------|
| product-filtering (MODIFIED) | Bug 1: Route accepts optional filters as query params | `routes/articulos.py` |
| price-change-processing (MODIFIED) | Bug 2: Server validates at least one item exists | `services/articulos/precios.py` |
| frontend-cambio-precio (ADDED) | Bug 1: JS calls API with query params, optional marca/rubro | `static/js/cambio_precio.js` |