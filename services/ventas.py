from datetime import date, timedelta
from utils.utils import format_currency
from models.ventas import Factura, Item, PagosFV
from models.clientes import Clientes
from models.articulos import Articulo, ListasPrecios
from models.configs import PagosCobros
from sqlalchemy import func, extract
from utils.db import db

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
        print(f'venta desde hasat: {vta_desde_hasta}')
        return vta_desde_hasta
    except:
        return []

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
        
def pagos_hoy():
    fecha = date.today()
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
        total_pago.append(resultado.total_pago)

        # Devolver las listas como respuesta
    return {
        'tipo_pago': tipo_pago,
        'total_pago': total_pago
    }

def get_factura(id):
    factura = db.session.query(
                Factura.id,
                Factura.fecha,
                Factura.total,
                Clientes.id.label('idcliente'),
                Clientes.nombre,
                Clientes.direccion,
                ListasPrecios.nombre.label('lista')) \
            .join(Clientes, Clientes.id == Factura.idcliente) \
            .join(ListasPrecios, ListasPrecios.id == Factura.idlista) \
            .filter(Factura.id == id).all()
   #Factura.query.get(id)
    items = db.session.query(
            Item.id,
            Item.cantidad,
            Item.precio_unitario,
            Item.precio_total,
            Articulo.codigo,
            Articulo.detalle) \
            .join(Articulo, Articulo.id == Item.idarticulo) \
            .filter(Item.idfactura == id)
    pagos = db.session.query(
            PagosFV.total,
            PagosCobros.pagos_cobros
            ).join(PagosCobros, PagosCobros.id == PagosFV.idpago
            ).filter(PagosFV.idfactura == id
            ).all()
    return factura[0], items, pagos

