from flask import session, jsonify, json, Response, current_app
import os
import tempfile
from decimal import Decimal
from datetime import date, timedelta, datetime
from services.articulos import actualizarStock, get_articulo_by_codigo
from services.configs import discrimina_iva

from utils.utils import format_currency, precio
from models.ventas import Factura, Item, PagosFV, ControlNc, Presupuesto, ItemP, PresupuestoFactura, RemitosVtaFactura
from models.clientes import Clientes
from models.articulos import Articulo, ListasPrecios, Stock, Colores, DetallesArticulos
from models.entidades_cred import MovEntidades
from models.ctactecli import CtaCteCli
from models.configs import Configuracion, PagosCobros, AlcIva, AlcIB, PuntosVenta, TipoComprobantes, TipoIva, \
                           TipoCompAplica, Localidades, Provincias
from models.creditos import Creditos 
from sqlalchemy import func, extract, text, and_
from sqlalchemy.exc import SQLAlchemyError
from utils.db import db
from utils.config import Config
from services.facturador import Facturador
from services.generar_factura import generar_factura_pdf


def get_vta_hoy():
    hoy = date.today()
    try:
        vta_hoy = db.session.query(func.sum(Factura.total).label('total')).filter(Factura.fecha == hoy).all()
        return format_currency(vta_hoy[0][0])
    except:
        return 0.0


def get_vta_semana():
    hoy = date.today()
    # Calcular el inicio de la semana (lunes)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    try:
        # Realizar la consulta para obtener el total de ventas de la semana
        vta_semana = db.session.query(
            func.sum(Factura.total).label('total_ventas')
        ).filter(
            Factura.fecha >= inicio_semana,
            Factura.fecha <= hoy
        ).scalar()
        return format_currency(vta_semana)
    except:
        return 0.0


def get_vta_desde_hasta(desde, hasta):
    try:
        # Realizar la consulta para obtener el total de ventas de la semana
        vta_desde_hasta = db.session.query(
            func.sum(Factura.total).label('total_ventas'),
            func.count(Factura.id).label('cantidad_ventas')
        ).filter(
            Factura.fecha >= desde,
            Factura.fecha <= hasta
        ).all()
        return vta_desde_hasta
    except:
        return []


def ventas_desde_hasta(desde, hasta):
    try:
        ventas = db.session.query(Factura.id,
                                Factura.fecha,
                                Factura.total,
                                Factura.nro_comprobante,
                                Factura.cae,
                                Clientes.nombre.label('cliente'),
                                TipoComprobantes.nombre.label('tipo_comprobante'),
                                ControlNc.id_comprobante.label('id_nc')
                                ).join(Clientes, Factura.idcliente == Clientes.id 
                                ).join(TipoComprobantes, Factura.idtipocomprobante == TipoComprobantes.id
                                ).outerjoin(ControlNc, ControlNc.id_comprobante_org == Factura.id
                                ).filter(Factura.fecha >= desde, Factura.fecha <= hasta, Factura.idsucursal == session['id_sucursal']).order_by(Factura.id.desc()).all()
        return ventas                        
    except Exception as e:
        print(f'error: {e}')
        return []


def get_operaciones_hoy():
    hoy = date.today()
    try:
        op_hoy = db.session.query(func.count(Factura.id).label('operaciones')).filter(
                 and_(
                        Factura.fecha == hoy,
                        Factura.idsucursal == session['id_sucursal']
                    )
                ).all()
        return op_hoy[0][0]
    except Exception as e:
        print(f'error: {e}')
        return 0
    

def get_operaciones_semana():
    hoy = date.today()
    # Calcular el inicio de la semana (lunes)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    try:
        # Realizar la consulta para obtener el total de ventas de la semana
        vta_semana = db.session.query(
            func.count(Factura.id).label('total_op')
        ).filter(
            Factura.fecha >= inicio_semana,
            Factura.fecha <= hoy,
            Factura.idsucursal == session['id_sucursal']
        ).scalar()
        return vta_semana
    except:
        return 0.0
    

def get_op_este_mes():
    hoy = date.today()
    # Calcular el inicio de la semana (lunes)
    inicio_mes = hoy.replace(day=1)
    try:
        # Realizar la consulta para obtener el total de ventas de la semana
        op_este_mes = db.session.query(
            func.count(Factura.id).label('total_op')
        ).filter(
            Factura.fecha >= inicio_mes,
            Factura.fecha <= hoy,
            Factura.idsucursal == session['id_sucursal']
        ).scalar()
        return op_este_mes
    except:
        return 0.0


def get_op_este_mes_anterior():
    hoy = date.today()
    hoy = hoy.replace(year=hoy.year-1)
    # Calcular el inicio de la semana (lunes)
    inicio_mes = hoy.replace(day=1)
    try:
        # Realizar la consulta para obtener el total de ventas de la semana
        op_este_mes_ant = db.session.query(
            func.count(Factura.id).label('total_op')
        ).filter(
            Factura.fecha >= inicio_mes,
            Factura.fecha <= hoy,
            Factura.idsucursal == session['id_sucursal']
        ).scalar()
        return op_este_mes_ant
    except:
        return 0.0
    

def operaciones_por_mes():
    # Obtener la fecha de hoy
    fecha_hoy = date.today()

    # Calcular la fecha 6 meses atrás
    fecha_inicio = fecha_hoy - timedelta(days=180)

    # Crear listas para los nombres de los meses y la cantidad de operaciones
    nombres_meses = []
    cantidades_operaciones = []
    try:
        # Realizar la consulta para obtener la cantidad de operaciones por mes
        resultados = db.session.query(
            func.date_format(Factura.fecha, '%M').label('mes'),
            func.count(Factura.id).label('cantidad_operaciones')
        ).filter(
            Factura.fecha >= fecha_inicio
        ).group_by(
            extract('month', Factura.fecha)
        ).order_by(
            extract('year', Factura.fecha), extract('month', Factura.fecha)
        ).all()

        # Procesar los resultados para llenar las listas
        for resultado in resultados:
            nombres_meses.append(resultado.mes)
            cantidades_operaciones.append(resultado.cantidad_operaciones)

        # Devolver las listas como respuesta
        return {
            'meses': nombres_meses,
            'operaciones': cantidades_operaciones
        }
    except:  
        nombres_meses = []
        cantidades_operaciones = []  
        return {
            'meses': nombres_meses,
            'operaciones': cantidades_operaciones
        }
        

def get_ultimas_operaciones():
    try:
        sucursal = session['id_sucursal']
        resultado = db.session.execute(text("CALL ultimas_10_ventas(:sucursal)"), {'sucursal': sucursal})
    except Exception as e:
        print(f'error: {e}')
        resultado = []
    return resultado


def get_10_mas_vendidos():
    #obtiene los 10 articulos mas vendidos
    try:
        sucursal = session['id_sucursal']
        # Obtener la fecha de hoy
        hasta = date.today()
        # Calcular la fecha 6 meses atrás
        desde = hasta - timedelta(days=180)
        cantidad = 10
        det_arts = []
        vtas_arts = []
        sql = text("CALL mas_vendidos(:sucursal, :desde, :hasta, :cantidad)")
        params = {'sucursal': sucursal, 'desde': desde, 'hasta': hasta, 'cantidad': cantidad}
        resultados = db.session.execute(sql, params)
        resultados = resultados.fetchall()
        for resultado in resultados:
            det_arts.append(resultado.detalle)
            vtas_arts.append(resultado.cantidad)
        return {
            'det_arts': det_arts,
            'vta_arts': vtas_arts
        }    
    except Exception as e:
        print(f'error: {e}')
        det_arts = []
        vtas_arts = []
        return {
            'det_arts': det_arts,
            'vta_arts': vtas_arts
        }


def ventas_por_mes():
    # Obtener la fecha de hoy
    fecha_hoy = date.today()

    # Calcular la fecha 6 meses atrás
    fecha_inicio = fecha_hoy - timedelta(days=180)

    # Crear listas para los nombres de los meses y la cantidad de operaciones
    nombres_meses = []
    cantidades_operaciones = []
    try:
        # Realizar la consulta para obtener la cantidad de operaciones por mes
        db.session.execute(text("SET lc_time_names = 'es_ES'"))
        resultados = db.session.execute(text("CALL get_vta_desde_hasta(:desde, :hasta)"),
                         {'desde': fecha_inicio, 'hasta': fecha_hoy}).fetchall()
        # Procesar los resultados para llenar las listas
        for resultado in resultados:
            nombres_meses.append(resultado.mes)
            cantidades_operaciones.append(resultado.cantidad_operaciones)
        # Devolver las listas como respuesta
        return {
            'meses': nombres_meses,
            'operaciones': cantidades_operaciones
        }
    except Exception as e:  
        print('Error calculando ventas por mes:', str(e))
        nombres_meses = []
        cantidades_operaciones = []  
        return {
            'meses': nombres_meses,
            'operaciones': cantidades_operaciones
        }
        

def get_vta_rubros(desde_vend, hasta_vend):
    nombres_rubros = []
    ventas_rubros = []
    cantidad_rubros = []
    db.session.execute(text("SET lc_time_names = 'es_ES'"))
    resultados = db.session.execute(text("CALL venta_rubros(:desde, :hasta)"),
                         {'desde': desde_vend, 'hasta': hasta_vend}).fetchall()
    for resultado in resultados:
        nombres_rubros.append(resultado.rubro)
        ventas_rubros.append(round(resultado.vtaRubro, 2))
        cantidad_rubros.append(round(resultado.cantRubro, 2))
    return {
            'rubros': nombres_rubros,
            'vtaRubros': ventas_rubros,
            'cantRubros': cantidad_rubros
        }
        

def pagos_hoy():
    fecha = date.today()
    try:
        resultados = db.session.query(
                    func.sum(PagosFV.total).label('total_pago'),
                    PagosCobros.pagos_cobros
                    ).join(Factura, Factura.id == PagosFV.idfactura) \
                    .join(PagosCobros, PagosFV.idpago == PagosCobros.id) \
                    .filter(Factura.fecha == fecha) \
                    .group_by(PagosCobros.pagos_cobros).all()

        # Convertir el resultado a una lista de diccionarios
        tipo_pago = []
        total_pago = []
        
        for resultado in resultados:
            tipo_pago.append(resultado.pagos_cobros)
            total_pago.append(round(resultado.total_pago, 2))

            # Devolver las listas como respuesta
        return {
            'tipo_pago': tipo_pago,
            'total_pago': total_pago
        }
    except Exception as e:  
        print('Error calculando pagos:', str(e))
        tipo_pago = []
        total_pago = []
        return {
            'tipo_pago': tipo_pago,
            'total_pago': total_pago
        }    


def get_factura(id):
    factura = db.session.query(
                Factura.id,
                Factura.fecha,
                Factura.total,
                Factura.bonificacion,
                Factura.iva,
                Factura.exento,
                Factura.impint,
                Factura.nro_comprobante,
                Factura.punto_vta,
                Factura.cae,
                Factura.cae_vto,
                Factura.fecha_emision,
                Factura.idtipocomprobante,
                Clientes.id.label('idcliente'),
                Clientes.nombre,
                Clientes.direccion,
                ListasPrecios.nombre.label('lista'),
                TipoComprobantes.nombre.label('tipo_comprobante'),
                TipoComprobantes.letra.label('letra_comprobante'),
                TipoCompAplica.id_tipo_oper.label('tipo_oper')) \
            .join(Clientes, Clientes.id == Factura.idcliente) \
            .outerjoin(ListasPrecios, ListasPrecios.id == Factura.idlista) \
            .join(TipoComprobantes, TipoComprobantes.id == Factura.idtipocomprobante) \
            .join(TipoCompAplica, TipoCompAplica.id_tipo_comp == Factura.idtipocomprobante) \
            .filter(Factura.id == id).all()
   #Factura.query.get(id)
    items = db.session.query(
            Item.id,
            Item.cantidad,
            Item.precio_unitario,
            Item.precio_total,
            Item.iva,
            Item.exento,
            Item.impint,
            Item.bonificacion,
            Item.idoferta,
            Colores.nombre.label('color'),
            Colores.color.label('codigo_color'),
            DetallesArticulos.nombre.label('detalle_articulo'),
            Articulo.codigo,
            Articulo.detalle) \
            .join(Articulo, Articulo.id == Item.idarticulo) \
            .outerjoin(Colores, Colores.id == Item.id_color) \
            .outerjoin(DetallesArticulos, DetallesArticulos.id == Item.id_detalle) \
            .filter(Item.idfactura == id)
    pagos = db.session.query(
            PagosFV.total,
            PagosCobros.pagos_cobros
            ).join(PagosCobros, PagosCobros.id == PagosFV.idpago
            ).filter(PagosFV.idfactura == id
            ).all()
    return factura[0], items, pagos


def get_vta_sucursales_data(desde, hasta):
    ventas = db.session.execute(text("CALL get_vta_sucursales(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
    ventas_list = []
    for venta in ventas:
        ventas_list.append({
            'sucursal': venta[0],
            'total': format_currency(venta[1]),
            'cantidad': venta[2],
            'tktProm': format_currency(venta[3])
        })
    return ventas_list    


def get_vta_vendedores_data(desde, hasta):
    ventas = db.session.execute(text("CALL get_vta_vendedores(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
    ventas_list = []
    for venta in ventas:
        ventas_list.append({
            'vendedor': venta[0],
            'total': format_currency(venta[1]),
            'cantidad': venta[2],
            'tktProm': format_currency(venta[3])
        })
    return ventas_list
