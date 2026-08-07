# Articulos Listado — Fix Specification

## Purpose

Correct 6 confirmed bugs in the articles listing: silent data filtering, unsafe column index, non-functional sort flag, broken Spanish translation, incorrect record counter, and undefined `BASE_URL`.

---

## Requirements

### Requirement: JOIN Filter Must Not Restrict Unfiltered Results

When `idrubro` or `idmarca` is falsy, the query MUST NOT embed a filter condition inside the JOIN `ON` clause. The JOIN MUST use only the FK equality (`Articulo.idrubro == Rubro.id`); rubro/marca filtering MUST be applied via separate `.filter()` calls only when a value is provided.

#### Scenario: No filter selected — all articles visible

- GIVEN no rubro and no marca are selected
- WHEN the listing is requested
- THEN the response MUST include all active articles, not only those with rubro/marca id=1

#### Scenario: Filter selected — results are scoped

- GIVEN a specific `idrubro` value is provided
- WHEN the listing is requested
- THEN only articles belonging to that rubro MUST be returned

---

### Requirement: Column Index Guard Must Cover All Non-DB Columns

The `columns` array in `get_listado_articulos()` MUST map only sortable DB-backed columns (indices 0–7). Columns 8 (Imagen) and 9 (Acciones) have no DB mapping. When `order_column` is ≥ `len(columns)`, the sort MUST fall back to `'codigo'` without raising an `IndexError`.

#### Scenario: Sort on Imagen column (index 8)

- GIVEN the client sends `order_column=8`
- WHEN the backend processes the request
- THEN the query MUST sort by `codigo` and return HTTP 200

#### Scenario: Sort on Acciones column (index 9)

- GIVEN the client sends `order_column=9`
- WHEN the backend processes the request
- THEN the query MUST sort by `codigo` and return HTTP 200

---

### Requirement: Acciones Column MUST Disable Sorting

The DataTable column definition for Acciones MUST use the key `orderable: false` (not `ordereable`).

#### Scenario: Acciones column header clicked

- GIVEN the table is rendered
- WHEN the user clicks the Acciones column header
- THEN the column MUST NOT trigger a sort request to the server

---

### Requirement: DataTable Language MUST Use Inline Spanish Definition

The DataTable initialisation MUST contain exactly one `language` key. The CDN-based `language.url` entry MUST be removed. The inline Spanish `language` block MUST be the only language configuration.

#### Scenario: Table loads without CDN language request

- GIVEN the page is loaded in any network environment
- WHEN the DataTable initialises
- THEN column headers and UI controls MUST render in Spanish without any external CDN request for a language file

---

### Requirement: Record Counter MUST Reflect Total Filtered Records

The `#contadorArticulos` element MUST display `tabla.page.info().recordsTotal` on every `draw` event. Using `tabla.data().count()` (which counts current-page rows only) is prohibited.

#### Scenario: Counter on first page load

- GIVEN the table loads with 200 matching articles across 4 pages
- WHEN the `draw` event fires on page 1
- THEN `#contadorArticulos` MUST show `200`, not `50`

#### Scenario: Counter after filter change

- GIVEN the user applies a rubro filter that narrows results to 30 articles
- WHEN the table redraws
- THEN `#contadorArticulos` MUST show `30`

---

### Requirement: BASE_URL MUST Be Defined Before DataTable Initialisation

`BASE_URL` MUST be declared as a JavaScript constant before the DataTable initialisation block. Its value MUST be derived from Flask's `request.host_url` (trailing slash stripped) or an equivalent server-side variable injected via Jinja2.

#### Scenario: Image thumbnail renders correctly

- GIVEN an article has an `imagen` value
- WHEN the table renders the Imagen column
- THEN the `<img>` `src` MUST resolve to a valid URL using the defined `BASE_URL`

#### Scenario: Delete button URL resolves correctly

- GIVEN the delete action uses `BASE_URL` in its href or onclick
- WHEN the page loads in any deployment environment (root path or subdirectory)
- THEN the URL MUST resolve correctly without a JavaScript `ReferenceError`
