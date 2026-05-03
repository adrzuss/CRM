# -*- coding: utf-8 -*-
"""
Servicio de Reportes Gerenciales
Funciones para obtener KPIs y métricas del negocio
"""

from flask import session
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import func, text, and_, case
from sqlalchemy.exc import SQLAlchemyError
from utils.db import db
from utils.utils import format_currency


def get_resumen_ejecutivo(desde, hasta):
    """
    Obtiene métricas principales del resumen ejecutivo:
    - Ventas totales, margen bruto estimado, ticket promedio, volumen operaciones
    - Comparación con periodo anterior
    """
    try:
        # Calcular periodo anterior (misma duración hacia atrás)
        dias_periodo = (hasta - desde).days + 1
        desde_ant = desde - timedelta(days=dias_periodo)
        hasta_ant = desde - timedelta(days=1)
        
        # Ventas periodo actual - Solo comprobantes de venta (tipo_oper 1,3,4)
        sql_ventas = text("""
            SELECT 
                COALESCE(SUM(CASE WHEN top.nombre IN ('VENTA', 'DEBITO') THEN f.total ELSE -f.total END), 0) as total_ventas,
                COUNT(f.id) as cantidad_operaciones,
                COALESCE(AVG(f.total), 0) as ticket_promedio,
                COALESCE(SUM(f.neto), 0) as total_neto
            FROM facturav f
            JOIN clientes c ON f.idcliente = c.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp and tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.fecha BETWEEN :desde AND :hasta
            AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
        """)
        
        result_actual = db.session.execute(sql_ventas, {'desde': desde, 'hasta': hasta}).fetchone()
        result_anterior = db.session.execute(sql_ventas, {'desde': desde_ant, 'hasta': hasta_ant}).fetchone()
        
        # Calcular costo de mercadería vendida (estimación basada en costo de artículos)
        sql_costo = text("""
            SELECT COALESCE(SUM(iv.cantidad * a.costo_total), 0) as costo_total
            FROM itemsv iv
            JOIN facturav f ON iv.idfactura = f.id
            JOIN clientes c ON f.idcliente = c.id
            JOIN articulos a ON iv.idarticulo = a.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp and tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.fecha BETWEEN :desde AND :hasta
            AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
        """)
        
        costo_actual = db.session.execute(sql_costo, {'desde': desde, 'hasta': hasta}).fetchone()
        costo_anterior = db.session.execute(sql_costo, {'desde': desde_ant, 'hasta': hasta_ant}).fetchone()
        
        # Calcular variaciones porcentuales
        ventas_actual = float(result_actual.total_ventas or 0)
        ventas_anterior = float(result_anterior.total_ventas or 0)
        var_ventas = ((ventas_actual - ventas_anterior) / ventas_anterior * 100) if ventas_anterior > 0 else 0
        
        costo_act = float(costo_actual.costo_total or 0)
        margen_bruto = ventas_actual - costo_act
        pct_margen = (margen_bruto / ventas_actual * 100) if ventas_actual > 0 else 0
        
        op_actual = int(result_actual.cantidad_operaciones or 0)
        op_anterior = int(result_anterior.cantidad_operaciones or 0)
        var_operaciones = ((op_actual - op_anterior) / op_anterior * 100) if op_anterior > 0 else 0
        
        tkt_actual = float(result_actual.ticket_promedio or 0)
        tkt_anterior = float(result_anterior.ticket_promedio or 0)
        var_ticket = ((tkt_actual - tkt_anterior) / tkt_anterior * 100) if tkt_anterior > 0 else 0
        
        return {
            'ventas_totales': format_currency(ventas_actual),
            'ventas_anteriores': format_currency(ventas_anterior),
            'var_ventas': round(var_ventas, 1),
            'margen_bruto': format_currency(margen_bruto),
            'pct_margen': round(pct_margen, 1),
            'ticket_promedio': format_currency(tkt_actual),
            'var_ticket': round(var_ticket, 1),
            'operaciones': op_actual,
            'var_operaciones': round(var_operaciones, 1),
            'costo_mercaderia': format_currency(costo_act)
        }
    except SQLAlchemyError as e:
        print(f"Error en resumen ejecutivo: {e}")
        return {
            'ventas_totales': '$0,00',
            'ventas_anteriores': '$0,00',
            'var_ventas': 0,
            'margen_bruto': '$0,00',
            'pct_margen': 0,
            'ticket_promedio': '$0,00',
            'var_ticket': 0,
            'operaciones': 0,
            'var_operaciones': 0,
            'costo_mercaderia': '$0,00'
        }


def get_top_productos(desde, hasta, limite=10):
    """
    Obtiene los productos más vendidos por cantidad y por importe
    """
    try:
        sql = text("""
            SELECT 
                a.codigo,
                a.detalle,
                r.nombre as rubro,
                SUM(iv.cantidad) as cantidad_vendida,
                SUM(iv.precio_total) as total_vendido,
                AVG(iv.precio_unitario) as precio_promedio
            FROM itemsv iv
            JOIN facturav f ON iv.idfactura = f.id
            JOIN articulos a ON iv.idarticulo = a.id
            LEFT JOIN rubros r ON a.idrubro = r.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
            WHERE f.fecha BETWEEN :desde AND :hasta
            AND tca.id_tipo_oper IN (1,3,4)
            GROUP BY a.id, a.codigo, a.detalle, r.nombre
            ORDER BY cantidad_vendida DESC
            LIMIT :limite
        """)
        
        result = db.session.execute(sql, {'desde': desde, 'hasta': hasta, 'limite': limite}).fetchall()
        
        productos = []
        for row in result:
            productos.append({
                'codigo': row.codigo,
                'detalle': row.detalle[:40] + '...' if len(row.detalle) > 40 else row.detalle,
                'rubro': row.rubro or 'Sin rubro',
                'cantidad': int(row.cantidad_vendida),
                'total': format_currency(float(row.total_vendido)),
                'precio_prom': format_currency(float(row.precio_promedio))
            })
        
        return productos
    except SQLAlchemyError as e:
        print(f"Error en top productos: {e}")
        return []


def get_evolucion_ventas(desde, hasta):
    """
    Obtiene la evolución temporal de ventas (agrupado por día/semana/mes según período)
    """
    try:
        dias_periodo = (hasta - desde).days + 1
        
        # Si es menos de 60 días, agrupar por día; si es menos de 180, por semana; sino por mes
        if dias_periodo <= 31:
            sql = text("""
                SELECT 
                    DATE_FORMAT(f.fecha, '%d/%m') as periodo,
                    f.fecha as fecha_orden,
                    COALESCE(SUM(CASE WHEN tca.id_tipo_oper IN (1,3) THEN f.total ELSE -f.total END), 0) as total
                FROM facturav f
                JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
                JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                WHERE f.fecha BETWEEN :desde AND :hasta
                AND tca.id_tipo_oper IN (1,3,4)
                GROUP BY f.fecha
                ORDER BY f.fecha
            """)
        elif dias_periodo <= 180:
            sql = text("""
                SELECT 
                    CONCAT('Sem ', WEEK(f.fecha, 1)) as periodo,
                    MIN(f.fecha) as fecha_orden,
                    COALESCE(SUM(CASE WHEN tca.id_tipo_oper IN (1,3) THEN f.total ELSE -f.total END), 0) as total
                FROM facturav f
                JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
                JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                WHERE f.fecha BETWEEN :desde AND :hasta
                AND tca.id_tipo_oper IN (1,3,4)
                GROUP BY YEAR(f.fecha), WEEK(f.fecha, 1)
                ORDER BY fecha_orden
            """)
        else:
            db.session.execute(text("SET lc_time_names = 'es_ES'"))
            sql = text("""
                SELECT 
                    DATE_FORMAT(f.fecha, '%b %Y') as periodo,
                    DATE_FORMAT(f.fecha, '%Y-%m-01') as fecha_orden,
                    COALESCE(SUM(CASE WHEN tca.id_tipo_oper IN (1,3) THEN f.total ELSE -f.total END), 0) as total
                FROM facturav f
                JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
                JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                WHERE f.fecha BETWEEN :desde AND :hasta
                AND tca.id_tipo_oper IN (1,3,4)
                GROUP BY DATE_FORMAT(f.fecha, '%Y-%m')
                ORDER BY fecha_orden
            """)
        
        result = db.session.execute(sql, {'desde': desde, 'hasta': hasta}).fetchall()
        
        periodos = []
        totales = []
        for row in result:
            periodos.append(row.periodo)
            totales.append(round(float(row.total), 2))
        
        return {'periodos': periodos, 'totales': totales}
    except SQLAlchemyError as e:
        print(f"Error en evolución ventas: {e}")
        return {'periodos': [], 'totales': []}


def get_concentracion_clientes(desde, hasta, limite=10):
    """
    Análisis de concentración de clientes (curva ABC)
    """
    try:
        # Total de ventas del período
        sql_total = text("""
            SELECT COALESCE(SUM(CASE WHEN tca.id_tipo_oper IN (1,3) THEN f.total ELSE -f.total END), 0) as total
            FROM facturav f
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
            WHERE f.fecha BETWEEN :desde AND :hasta
            AND tca.id_tipo_oper IN (1,3,4)
        """)
        total_ventas = float(db.session.execute(sql_total, {'desde': desde, 'hasta': hasta}).fetchone().total or 0)
        
        # Top clientes
        sql = text("""
            SELECT 
                c.id,
                c.nombre,
                COUNT(f.id) as operaciones,
                COALESCE(SUM(CASE WHEN tca.id_tipo_oper IN (1,3) THEN f.total ELSE -f.total END), 0) as total_comprado
            FROM facturav f
            JOIN clientes c ON f.idcliente = c.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
            WHERE f.fecha BETWEEN :desde AND :hasta
            AND tca.id_tipo_oper IN (1,3,4)
            GROUP BY c.id, c.nombre
            ORDER BY total_comprado DESC
            LIMIT :limite
        """)
        
        result = db.session.execute(sql, {'desde': desde, 'hasta': hasta, 'limite': limite}).fetchall()
        
        clientes = []
        acumulado = 0
        for row in result:
            total_cli = float(row.total_comprado)
            acumulado += total_cli
            pct = (total_cli / total_ventas * 100) if total_ventas > 0 else 0
            pct_acum = (acumulado / total_ventas * 100) if total_ventas > 0 else 0
            
            clientes.append({
                'id': row.id,
                'nombre': row.nombre[:30] + '...' if len(row.nombre) > 30 else row.nombre,
                'operaciones': row.operaciones,
                'total': format_currency(total_cli),
                'porcentaje': round(pct, 1),
                'pct_acumulado': round(pct_acum, 1)
            })
        
        # Calcular índice de concentración (% que representa top 20% de clientes)
        sql_total_cli = text("""
            SELECT COUNT(DISTINCT f.idcliente) as total_clientes
            FROM facturav f
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
            WHERE f.fecha BETWEEN :desde AND :hasta
            AND tca.id_tipo_oper IN (1,3,4)
        """)
        total_clientes = int(db.session.execute(sql_total_cli, {'desde': desde, 'hasta': hasta}).fetchone().total_clientes or 0)
        
        return {
            'clientes': clientes,
            'total_clientes': total_clientes,
            'total_ventas': format_currency(total_ventas)
        }
    except SQLAlchemyError as e:
        print(f"Error en concentración clientes: {e}")
        return {'clientes': [], 'total_clientes': 0, 'total_ventas': '$0,00'}


def get_analisis_compras(desde, hasta):
    """
    Análisis de compras: compras vs ventas, principales proveedores
    """
    try:
        # Total compras
        sql_compras = text("""
            SELECT 
                COALESCE(SUM(fc.total), 0) as total_compras,
                COUNT(fc.id) as cantidad_compras
            FROM facturac fc
            WHERE fc.fecha BETWEEN :desde AND :hasta
        """)
        
        result_compras = db.session.execute(sql_compras, {'desde': desde, 'hasta': hasta}).fetchone()
        
        # Total ventas (para comparar)
        sql_ventas = text("""
            SELECT COALESCE(SUM(CASE WHEN tca.id_tipo_oper IN (1,3) THEN f.total ELSE -f.total END), 0) as total_ventas
            FROM facturav f
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
            WHERE f.fecha BETWEEN :desde AND :hasta
            AND tca.id_tipo_oper IN (1,3,4)
        """)
        
        total_ventas = float(db.session.execute(sql_ventas, {'desde': desde, 'hasta': hasta}).fetchone().total_ventas or 0)
        total_compras = float(result_compras.total_compras or 0)
        
        # Top proveedores
        sql_proveedores = text("""
            SELECT 
                p.id,
                p.nombre,
                COUNT(fc.id) as cantidad_compras,
                COALESCE(SUM(fc.total), 0) as total_comprado
            FROM facturac fc
            JOIN proveedores p ON fc.idproveedor = p.id
            WHERE fc.fecha BETWEEN :desde AND :hasta
            GROUP BY p.id, p.nombre
            ORDER BY total_comprado DESC
            LIMIT 10
        """)
        
        result_prov = db.session.execute(sql_proveedores, {'desde': desde, 'hasta': hasta}).fetchall()
        
        proveedores = []
        for row in result_prov:
            pct = (float(row.total_comprado) / total_compras * 100) if total_compras > 0 else 0
            proveedores.append({
                'id': row.id,
                'nombre': row.nombre[:30] if row.nombre else 'Sin nombre',
                'compras': row.cantidad_compras,
                'total': format_currency(float(row.total_comprado)),
                'porcentaje': round(pct, 1)
            })
        
        # Ratio compras/ventas
        ratio = (total_compras / total_ventas * 100) if total_ventas > 0 else 0
        
        return {
            'total_compras': format_currency(total_compras),
            'total_compras_raw': total_compras,
            'cantidad_compras': int(result_compras.cantidad_compras or 0),
            'total_ventas': format_currency(total_ventas),
            'total_ventas_raw': total_ventas,
            'ratio_compras_ventas': round(ratio, 1),
            'proveedores': proveedores
        }
    except SQLAlchemyError as e:
        print(f"Error en análisis compras: {e}")
        return {
            'total_compras': '$0,00',
            'total_compras_raw': 0,
            'cantidad_compras': 0,
            'total_ventas': '$0,00',
            'total_ventas_raw': 0,
            'ratio_compras_ventas': 0,
            'proveedores': []
        }


def get_metricas_sucursales(desde, hasta):
    """
    Métricas de rendimiento por sucursal
    """
    try:
        sql = text("""
            SELECT 
                s.id,
                s.nombre,
                COUNT(f.id) as operaciones,
                COALESCE(SUM(CASE WHEN tca.id_tipo_oper IN (1,3) THEN f.total ELSE -f.total END), 0) as venta_neta,
                COALESCE(AVG(f.total), 0) as ticket_promedio
            FROM facturav f
            JOIN sucursales s ON f.idsucursal = s.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
            WHERE f.fecha BETWEEN :desde AND :hasta
            AND tca.id_tipo_oper IN (1,3,4)
            GROUP BY s.id, s.nombre
            ORDER BY venta_neta DESC
        """)
        
        result = db.session.execute(sql, {'desde': desde, 'hasta': hasta}).fetchall()
        
        # Calcular total para porcentajes
        total_ventas = sum(float(row.venta_neta) for row in result)
        
        sucursales = []
        ranking = 1
        for row in result:
            venta = float(row.venta_neta)
            pct = (venta / total_ventas * 100) if total_ventas > 0 else 0
            
            sucursales.append({
                'ranking': ranking,
                'id': row.id,
                'nombre': row.nombre,
                'operaciones': row.operaciones,
                'venta_neta': format_currency(venta),
                'venta_raw': venta,
                'ticket_promedio': format_currency(float(row.ticket_promedio)),
                'porcentaje': round(pct, 1)
            })
            ranking += 1
        
        return sucursales
    except SQLAlchemyError as e:
        print(f"Error en métricas sucursales: {e}")
        return []


def get_estado_inventario():
    """
    Estado del inventario: valor total, productos sin stock, baja rotación
    """
    try:
        # Valor total del inventario
        sql_valor = text("""
            SELECT 
                COALESCE(SUM(st.actual * a.costo_total), 0) as valor_inventario,
                COUNT(DISTINCT a.id) as total_articulos,
                SUM(st.actual) as unidades_totales
            FROM stocks st
            JOIN articulos a ON st.idarticulo = a.id
            WHERE a.baja IS NULL
        """)
        
        result_valor = db.session.execute(sql_valor).fetchone()
        
        # Artículos sin stock (stock <= 0)
        sql_sin_stock = text("""
            SELECT COUNT(DISTINCT a.id) as sin_stock
            FROM articulos a
            LEFT JOIN stocks st ON a.id = st.idarticulo
            WHERE a.baja IS NULL
            AND (st.actual IS NULL OR st.actual <= 0)
        """)
        
        sin_stock = int(db.session.execute(sql_sin_stock).fetchone().sin_stock or 0)
        
        # Artículos con stock crítico (actual < deseable)
        sql_critico = text("""
            SELECT COUNT(DISTINCT a.id) as stock_critico
            FROM articulos a
            JOIN stocks st ON a.id = st.idarticulo
            WHERE a.baja IS NULL
            AND st.actual < st.deseable
            AND st.actual > 0
        """)
        
        stock_critico = int(db.session.execute(sql_critico).fetchone().stock_critico or 0)
        
        # Artículos con exceso de stock (actual > maximo)
        sql_exceso = text("""
            SELECT COUNT(DISTINCT a.id) as stock_exceso
            FROM articulos a
            JOIN stocks st ON a.id = st.idarticulo
            WHERE a.baja IS NULL
            AND st.actual > st.maximo
            AND st.maximo > 0
        """)
        
        stock_exceso = int(db.session.execute(sql_exceso).fetchone().stock_exceso or 0)
        
        return {
            'valor_inventario': format_currency(float(result_valor.valor_inventario or 0)),
            'valor_raw': float(result_valor.valor_inventario or 0),
            'total_articulos': int(result_valor.total_articulos or 0),
            'unidades_totales': int(result_valor.unidades_totales or 0),
            'sin_stock': sin_stock,
            'stock_critico': stock_critico,
            'stock_exceso': stock_exceso
        }
    except SQLAlchemyError as e:
        print(f"Error en estado inventario: {e}")
        return {
            'valor_inventario': '$0,00',
            'valor_raw': 0,
            'total_articulos': 0,
            'unidades_totales': 0,
            'sin_stock': 0,
            'stock_critico': 0,
            'stock_exceso': 0
        }


def get_rotacion_inventario(desde, hasta):
    """
    Análisis de rotación de inventario por rubro/categoría
    """
    try:
        # Rotación por rubro
        sql = text("""
            SELECT 
                r.id,
                r.nombre as rubro,
                COALESCE(SUM(iv.cantidad), 0) as unidades_vendidas,
                COALESCE(SUM(iv.precio_total), 0) as monto_vendido,
                (SELECT COALESCE(SUM(st2.actual), 0) 
                 FROM stocks st2 
                 JOIN articulos a2 ON st2.idarticulo = a2.id 
                 WHERE a2.idrubro = r.id) as stock_actual
            FROM rubros r
            LEFT JOIN articulos a ON a.idrubro = r.id
            LEFT JOIN itemsv iv ON iv.idarticulo = a.id
            LEFT JOIN facturav f ON iv.idfactura = f.id AND f.fecha BETWEEN :desde AND :hasta
            LEFT JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            LEFT JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp AND tca.id_tipo_oper IN (1,3,4)
            GROUP BY r.id, r.nombre
            HAVING stock_actual > 0 OR unidades_vendidas > 0
            ORDER BY monto_vendido DESC
        """)
        
        result = db.session.execute(sql, {'desde': desde, 'hasta': hasta}).fetchall()
        
        rubros = []
        for row in result:
            unidades = float(row.unidades_vendidas or 0)
            monto = float(row.monto_vendido or 0)
            stock = float(row.stock_actual or 0)
            # Días de inventario = Stock actual / (Ventas diarias promedio)
            dias_periodo = max((hasta - desde).days, 1)
            ventas_diarias = unidades / dias_periodo if dias_periodo > 0 else 0
            dias_inventario = (stock / ventas_diarias) if ventas_diarias > 0 else 999
            
            # Rotación = Unidades vendidas / Stock promedio (aprox stock actual)
            rotacion = (unidades / stock) if stock > 0 else 0
            
            rubros.append({
                'id': row.id,
                'nombre': row.rubro,
                'unidades_vendidas': int(unidades),
                'monto': format_currency(monto),
                'monto_raw': round(monto, 2),
                'stock_actual': int(stock),
                'dias_inventario': min(int(dias_inventario), 999),
                'rotacion': round(rotacion, 2)
            })
        
        return rubros
    except SQLAlchemyError as e:
        print(f"Error en rotación inventario: {e}")
        return []


def get_ventas_por_medio_pago(desde, hasta):
    """
    Distribución de ventas por medio de pago
    """
    try:
        sql = text("""
            SELECT 
                pc.pagos_cobros as medio_pago,
                COUNT(DISTINCT pf.idfactura) as cantidad_operaciones,
                COALESCE(SUM(pf.total), 0) as total
            FROM pagos_fv pf
            JOIN facturav f ON pf.idfactura = f.id
            JOIN pagos_cobros pc ON pf.tipo = pc.id
            WHERE f.fecha BETWEEN :desde AND :hasta
            GROUP BY pc.id, pc.pagos_cobros
            ORDER BY total DESC
        """)
        
        result = db.session.execute(sql, {'desde': desde, 'hasta': hasta}).fetchall()
        
        # Calcular total
        total = sum(float(row.total) for row in result)
        
        medios = []
        for row in result:
            monto = float(row.total)
            pct = (monto / total * 100) if total > 0 else 0
            medios.append({
                'nombre': row.medio_pago,
                'operaciones': row.cantidad_operaciones,
                'total': format_currency(monto),
                'total_raw': monto,
                'porcentaje': round(pct, 1)
            })
        
        return medios
    except SQLAlchemyError as e:
        print(f"Error en medios de pago: {e}")
        return []


def get_cuentas_corrientes():
    """
    Estado de cuentas corrientes de clientes
    """
    try:
        # Saldo total de clientes
        sql = text("""
            SELECT 
                COALESCE(SUM(CASE WHEN ccc.debe > 0 THEN ccc.debe ELSE 0 END), 0) as total_debe,
                COALESCE(SUM(CASE WHEN ccc.haber > 0 THEN ccc.haber ELSE 0 END), 0) as total_haber,
                COUNT(DISTINCT ccc.idcliente) as cantidad_clientes
            FROM cta_cte_cli ccc
        """)
        
        result = db.session.execute(sql).fetchone()
        
        debe = float(result.total_debe or 0)
        haber = float(result.total_haber or 0)
        saldo = debe - haber
        
        # Top deudores
        sql_top = text("""
            SELECT 
                c.id,
                c.nombre,
                COALESCE(SUM(ccc.debe - ccc.haber), 0) as saldo
            FROM cta_cte_cli ccc
            JOIN clientes c ON ccc.idcliente = c.id
            GROUP BY c.id, c.nombre
            HAVING saldo > 0
            ORDER BY saldo DESC
            LIMIT 10
        """)
        
        result_top = db.session.execute(sql_top).fetchall()
        
        deudores = []
        for row in result_top:
            deudores.append({
                'id': row.id,
                'nombre': row.nombre[:30] if row.nombre else 'Sin nombre',
                'saldo': format_currency(float(row.saldo))
            })
        
        return {
            'saldo_total': format_currency(saldo),
            'saldo_raw': saldo,
            'cantidad_clientes': int(result.cantidad_clientes or 0),
            'deudores': deudores
        }
    except SQLAlchemyError as e:
        print(f"Error en cuentas corrientes: {e}")
        return {
            'saldo_total': '$0,00',
            'saldo_raw': 0,
            'cantidad_clientes': 0,
            'deudores': []
        }


def get_sucursales_lista():
    """
    Obtiene lista de sucursales activas para el filtro
    """
    try:
        sql = text("SELECT id, nombre FROM sucursales WHERE baja IS NULL ORDER BY nombre")
        result = db.session.execute(sql).fetchall()
        return [{'id': row.id, 'nombre': row.nombre} for row in result]
    except SQLAlchemyError as e:
        print(f"Error en lista sucursales: {e}")
        return []


def get_datos_reporte_gerencial(desde, hasta, sucursal=None):
    """
    Función principal que recopila todos los datos del reporte gerencial
    """
    data = {
        'resumen': get_resumen_ejecutivo(desde, hasta),
        'top_productos': get_top_productos(desde, hasta, 10),
        'evolucion_ventas': get_evolucion_ventas(desde, hasta),
        'concentracion_clientes': get_concentracion_clientes(desde, hasta, 10),
        'analisis_compras': get_analisis_compras(desde, hasta),
        'metricas_sucursales': get_metricas_sucursales(desde, hasta),
        'estado_inventario': get_estado_inventario(),
        'rotacion_inventario': get_rotacion_inventario(desde, hasta),
        'medios_pago': get_ventas_por_medio_pago(desde, hasta),
        'cuentas_corrientes': get_cuentas_corrientes(),
        'sucursales_lista': get_sucursales_lista()
    }
    return data
