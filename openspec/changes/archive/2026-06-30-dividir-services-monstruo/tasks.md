# Tasks: Dividir Services Monstruo

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~250 (nuevos archivos) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Delivery strategy | ask-always |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: single-pr
400-line budget risk: Low

## Phase 1: services/ventas/ — Paquete

- [x] 1.1 Crear `services/ventas/__init__.py` con re-exportaciones de todos los submódulos
- [x] 1.2 Crear `services/ventas/facturacion.py` — mover `facturar_fe`, `generar_factura`, `getNroComprobante`, `get_certificado_clave_fe`
- [x] 1.3 Crear `services/ventas/ventas.py` — mover `procesar_nueva_venta`, `procesar_items`, `procesar_pagos`, `procesar_recibo_cta_cte`, `procesar_recibo_cuota_credito`
- [x] 1.4 Crear `services/ventas/notas_credito.py` — mover `procesar_nueva_nc`, `get_comprobantes_para_nc`, `get_items_comprobante_venta`, `get_vale_disponible`
- [x] 1.5 Crear `services/ventas/remitos.py` — mover `procesar_nuevo_remito`, `procesar_items_remito`, `get_remito`
- [x] 1.6 Crear `services/ventas/presupuestos.py` — mover `procesar_nuevo_presupuesto`, `procesar_itemsP`, `get_presupuesto`, `generar_presupuesto`
- [x] 1.7 Crear `services/ventas/reportes.py` — mover 17 funciones de reportes/estadísticas
- [x] 1.8 Eliminar `services/ventas.py`

## Phase 2: services/articulos/ — Paquete

- [x] 2.1 Crear `services/articulos/__init__.py` con re-exportaciones
- [x] 2.2 Crear `services/articulos/articulos.py` — mover CRUD y helpers
- [x] 2.3 Crear `services/articulos/stock.py` — mover funciones de stock
- [x] 2.4 Crear `services/articulos/precios.py` — mover funciones de precios
- [x] 2.5 Crear `services/articulos/remitos.py` — mover funciones de remitos a sucursal
- [x] 2.6 Crear `services/articulos/reportes.py` — mover listados, alertas, balance, detalles
- [x] 2.7 Eliminar `services/articulos.py`

## Phase 3: Verificación

- [x] 3.1 `python index.py` arranca sin errores
- [x] 3.2 `pytest tests/` — 19 tests pasan
- [x] 3.3 Verificar imports de routes que usan services.ventas y services.articulos
- [x] 3.4 Verificar imports de otros services que usan services.ventas y services.articulos
