# Tasks: Más Tests 🧪

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~350–450 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Suggested split | Single PR |

## Task 1: Test de rutas de ventas

- [x] Test GET /ventas/ventas con fechas — verifica que renderiza ventas.html con facturas
- [x] Test GET /ventas/ver_factura_vta/<id> — verifica que renderiza factura-vta.html con datos mockeados
- [x] Test POST /ventas/buscar_comprobantes_nc — verifica JSON endpoint (reemplaza a /api/buscar_articulos_venta que no existe en el código)
- [x] Test POST /ventas/buscar_comprobantes_nc sin fecha — verifica error 400

## Task 2: Test de rutas de artículos

- [x] Test GET /articulos/articulos — verifica listado con marcas y rubros
- [x] Test GET /articulos/api/articulos — verifica paginación (DataTables params: draw, start, length)
- [x] Test GET /articulos/api/articulos sin resultados — verifica respuesta vacía
- [x] Test GET /articulos/update_articulo/1 — verifica detalle de artículo existente (ruta real, `/upd-articulo/1` no existe)
- [x] Test GET /articulos/update_articulo/0 — verifica nuevo artículo (id=0)
- [x] Test GET /articulos/api/1/colores-detalles — verifica JSON con colores y detalles
- [x] Test GET /articulos/api/999/colores-detalles — verifica 404 cuando no existe

## Task 3: Test de rutas de proveedores

- [x] Test GET /proveedores/proveedores/1 — verifica listado con proveedor existente
- [x] Test GET /proveedores/proveedores/0 — verifica listado sin proveedor seleccionado
- [x] Test GET /proveedores/compras?desde=X&hasta=Y — verifica compras con filtro de fechas
- [x] Test GET /proveedores/compras sin fechas — verifica defaults
- [x] Test GET /proveedores/ver_factura_comp/1 — verifica factura de compra con datos mockeados

## Task 4: Test de services de ventas

- [x] Test services/ventas/facturacion: getNroComprobante — 5 tests: Factura A, B, C, NC A, Remito
- [x] Test services/ventas: funciones con cálculos matemáticos — 2 tests: intereses sin tarjeta, intereses con tarjeta y vuelto

## Task 5: Test de services de artículos

- [x] Identificar funciones con dependencia parcial de DB y agregar tests unitarios
  - obtenerArticulosMarcaRubro: test de cálculo de precios con porcentaje (3 tests)
  - _guardar_precios: test de procesamiento de formulario de precios (1 test)
  - Nota: No hay funciones 100% puras (sin DB) en services/articulos; todas requieren mocking de db.session
