# Proposal: Dividir Services Monstruo

## Intent

`services/ventas.py` (1.479 líneas, 37 funciones) y `services/articulos.py` (1.289 líneas, 33 funciones) son archivos demasiado grandes que mezclan lógica de facturación, stock, reportes, presupuestos, AFIP, etc. Dificultan la navegación, el testing y el mantenimiento. Se propone convertirlos en paquetes con sub-módulos por dominio.

## Scope

### In Scope
- Convertir `services/ventas.py` en paquete `services/ventas/` con 6 módulos
- Convertir `services/articulos.py` en paquete `services/articulos/` con 5 módulos
- Mantener `__init__.py` con re-exportaciones para que imports existentes no se rompan
- Mover imports inline (circulares) dentro del paquete

### Out of Scope
- Refactorizar lógica interna o cambiar firmas de funciones
- Agregar tests nuevos (los existentes alcanzan para verificar)
- Convertir a clases/objetos
- Tocar routes u otros services

## Capabilities

### New Capabilities
None

### Modified Capabilities
None

## Approach

### services/ventas/ (6 módulos)
| Módulo | Funciones |
|--------|-----------|
| `__init__.py` | Re-exportaciones de todos los submódulos |
| `facturacion.py` | `facturar_fe`, `generar_factura`, `getNroComprobante` |
| `ventas.py` | `procesar_nueva_venta`, `procesar_items`, `procesar_pagos`, `procesar_recibo_cta_cte`, `procesar_recibo_cuota_credito` |
| `notas_credito.py` | `procesar_nueva_nc`, `get_comprobantes_para_nc`, `get_items_comprobante_venta`, `get_vale_disponible` |
| `remitos.py` | `procesar_nuevo_remito`, `procesar_items_remito`, `get_remito` |
| `presupuestos.py` | `procesar_nuevo_presupuesto`, `procesar_itemsP`, `get_presupuesto`, `generar_presupuesto` |
| `reportes.py` | 14 funciones estadísticas (`get_vta_hoy`, `ventas_por_mes`, `pagos_hoy`, etc.) |

### services/articulos/ (5 módulos)
| Módulo | Funciones |
|--------|-----------|
| `__init__.py` | Re-exportaciones |
| `articulos.py` | `guardar_articulo`, helpers privados, `get_articulo_by_codigo`, `obtenerArticulosMarcaRubro` |
| `stock.py` | `actualizarStock`, `get_stocks_negativos`, `get_stocks_faltantes`, `obtener_stock_sucursales`, `alerta_stocks_*` |
| `precios.py` | `get_listado_precios`, `actualizarPrecio`, `procesar_cambio_precio` |
| `remitos.py` | `procesar_remito_a_sucursal`, `enviar_remito_sucursal`, `recibir_remito_sucursal`, `get_remitos_sucursales`, etc. |
| `reportes.py` | `get_listado_articulos`, `get_listado_stock`, `procesar_nuevo_balance`, `get_detalle_articulo`, `get_detalle_full_articulo` |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Funciones con import cruzado entre submódulos | Media | Los imports inline ya existen hoy, se mantienen igual |
| Se cuela una función duplicada o faltante | Baja | `__init__.py` re-exporta explícitamente; grep de imports existentes vs exports |
| Tests rompen | Baja | Los 19 tests existentes validan que las importaciones funcionan |

## Rollback Plan

Revertir commit. Mientras tanto, `services/ventas.py` y `services/articulos.py` originales existen en git.

## Success Criteria

- [ ] `from services.ventas import X` funciona para todas las funciones existentes
- [ ] `from services.articulos import Y` funciona para todas las funciones existentes
- [ ] `pytest tests/` pasa (19 tests)
- [ ] `python index.py` arranca sin errores
- [ ] Los routes que importan de services.ventas y services.articulos siguen funcionando
- [ ] No hay cambios en `routes/` ni en `services/*.py` (excepto ventas y articulos)
