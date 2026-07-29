from .facturacion import facturar_fe, generar_factura, getNroComprobante, get_certificado_clave_fe
from .ventas import procesar_nueva_venta, procesar_items, procesar_pagos, procesar_recibo_cta_cte, procesar_recibo_cuota_credito
from .notas_credito import procesar_nueva_nc, get_comprobantes_para_nc, get_items_comprobante_venta, get_vale_disponible
from .remitos import procesar_nuevo_remito, procesar_items_remito, get_remito
from .presupuestos import procesar_nuevo_presupuesto, procesar_itemsP, get_presupuesto, generar_presupuesto
from .reportes import get_vta_hoy, get_vta_semana, get_vta_desde_hasta, ventas_desde_hasta, get_operaciones_hoy, get_operaciones_semana, get_op_este_mes, get_op_este_mes_anterior, operaciones_por_mes, get_ultimas_operaciones, get_10_mas_vendidos, ventas_por_mes, get_vta_rubros, pagos_hoy, get_factura, get_vta_sucursales_data, get_vta_vendedores_data
