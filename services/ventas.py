from flask import request, session
from decimal import Decimal
from datetime import date, timedelta
from utils.utils import format_currency
from services.articulos import actualizarStock

from utils.utils import format_currency, precio
from models.ventas import Factura, Item, PagosFV
from models.clientes import Clientes
from models.articulos import Articulo, ListasPrecios, Stock, Precio
from models.ctactecli import CtaCteCli
from models.configs import PagosCobros, AlcIva, AlcIB
from sqlalchemy import func, extract, text, and_
from sqlalchemy.exc import SQLAlchemyError
from utils.db import db

def procesar_nueva_venta(form, id_sucursal):
    try:
        idcliente = request.form['idcliente']
        fecha = request.form['fecha']
        idlista = request.form['idlista']
        id_tipo_comprobante = request.form['id_tipo_comprobante']
        efectivo = float(request.form['efectivo'])
        tarjeta = float(request.form['tarjeta'])
        entidad = request.form['entidad']
        ctacte = float(request.form['ctacte'])

        # Crear la factura
        nueva_factura = Factura(
            idcliente=idcliente,
            idlista=idlista,
            fecha=fecha,
            total=0,  # Se calculará más adelante
            id_tipo_comprobante=id_tipo_comprobante,
            idsucursal=id_sucursal,
            idusuario=session['user_id']
        )
        db.session.add(nueva_factura)
        db.session.flush()
        idfactura = nueva_factura.id

        # Procesar los items
        total = 0
        total, total_iva, total_exento, total_impint = procesar_items(form, idfactura, idlista, id_sucursal)
        nueva_factura.total = total
        nueva_factura.iva = total_iva
        nueva_factura.exento = total_exento
        nueva_factura.impint = total_impint
        # Registrar los pagos
        procesar_pagos(idfactura, idcliente, fecha, efectivo, tarjeta, entidad, ctacte)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Error grabando venta: {e}")

def procesar_items(form, idfactura, idlista, id_sucursal):
    total = Decimal(0)
    total_iva = Decimal(0)
    total_exento = Decimal(0)
    total_impint = Decimal(0)
    stock = db.session.query(Stock).filter_by(idsucursal=id_sucursal).first()
    for key, value in form.items():
        if key.startswith('items') and key.endswith('[codigo]'):
            precio_total = Decimal(0)
            index = key.split('[')[1].split(']')[0]
            codigo = value
            cantidad = Decimal(form[f'items[{index}][cantidad]'])
            precioUnit = Decimal(form[f'items[{index}][precio_unitario]'])
            articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
            iva = AlcIva.query.get(articulo.idiva)
            ingbto = AlcIB.query.get(articulo.idib)
            precios = precio(precioUnit, articulo.impint, articulo.exento, Decimal(0), Decimal(0), Decimal(iva.alicuota), Decimal(ingbto.alicuota))
            #precio = Precio.query.filter_by(idarticulo=articulo.id, idlista=idlista).first()
            #precio_unitario = precio.precio if precio else Decimal(0)
            precio_total = precios['PFinal'] * cantidad
            idalciva = articulo.idiva
            iva = precios['Iva'] * cantidad
            exento = precios['Exento'] * cantidad
            impint = precios['ImpInt'] * cantidad
            ingbrutos = precios['IngBto'] * cantidad
            nuevo_item = Item(
                idfactura=idfactura,
                id=index,
                idarticulo=articulo.id,
                cantidad=cantidad,
                precio_unitario=precios['PFinal'],
                precio_total=precio_total,
                iva=iva,
                idalciva=idalciva,
                ingbto=ingbrutos,
                idingbto=ingbto.id,
                exento=exento,  
                impint=impint
            )
            db.session.add(nuevo_item)
            total += precio_total
            total_iva += iva
            total_exento += exento
            total_impint += impint

            # Actualizar el stock
            actualizarStock(stock.idstock, articulo.id, -cantidad, id_sucursal)
    
    return total, total_iva, total_exento, total_impint

def procesar_pagos(idfactura, idcliente, fecha, efectivo, tarjeta, entidad, ctacte):
    try:
        if efectivo > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=1, tipo=1, entidad=0, total=Decimal(efectivo)))
        if tarjeta > 0:
            entidad = int(request.form['entidad'])
            db.session.add(PagosFV(idfactura=idfactura, idpago=2, tipo=2, entidad=entidad, total=Decimal(tarjeta)))
        if ctacte > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=3, tipo=3, entidad=0, total=Decimal(ctacte)))
            db.session.add(CtaCteCli(idcliente=idcliente, fecha=fecha, debe=Decimal(ctacte), haber=Decimal(0)))
        #db.session.commit()
    except SQLAlchemyError as e:
        raise Exception(f"Error procesando pagos: {e}")

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

def get_operaciones_hoy():
    hoy = date.today()
    try:
        op_hoy = db.session.query(func.count(Factura.id).label('operaciones')).filter(
                 and_(
                        Factura.fecha == hoy,
                        Factura.idsucursal == session['id_sucursal']
                    )
                ).all()
        print(f"Calculo Op hoy: {op_hoy}")
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
                Factura.iva,
                Factura.exento,
                Factura.impint,
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

