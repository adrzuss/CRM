from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, jsonify
from datetime import date, timedelta
from utils.utils import format_currency
from models.articulos import Articulo, Stock, ListasPrecios, Precio
from models.ventas import Factura, Item, PagosFV
from models.ctactecli import CtaCteCli
from models.entidades_cred import EntidadesCred
from models.configs import PagosCobros
from sqlalchemy import func, extract
from utils.db import db

bp_ventas = Blueprint('ventas', __name__, template_folder='../templates/ventas')

@bp_ventas.route('/ventas', methods=['GET', 'POST'])
def ventas():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
    facturas = Factura.query.filter(Factura.fecha >= desde, Factura.fecha <= hasta)
    return render_template('ventas.html', facturas=facturas, desde=desde, hasta=hasta)

@bp_ventas.route('/nueva_venta', methods=['GET', 'POST'])
def nueva_venta():
    if request.method == 'POST':
        idcliente = request.form['idcliente']
        fecha = request.form['fecha']
        idlista = request.form['idlista']
        efectivo = float(request.form['efectivo'])
        tarjeta = float(request.form['tarjeta'])
        ctacte = float(request.form['ctacte'])
        total = 0  # Esto se calculará más tarde

        nueva_factura = Factura(idcliente=idcliente, idlista=idlista, fecha=fecha, total=total)
        db.session.add(nueva_factura)
        db.session.commit()

        idfactura = nueva_factura.id
        
        items = request.form  # Obtener todo el formulario
        item_count = 0  # Contador de items agregados

        item_count = len([key for key in items.keys() if key.startswith('items') and key.endswith('[idarticulo]')])
        idstock = current_app.config['IDSTOCK']

        for i in range(item_count):
            idarticulo = request.form[f'items[{i}][idarticulo]']
            cantidad = int(request.form[f'items[{i}][cantidad]'])
            articulo = Articulo.query.get(idarticulo)
            precio = Precio.query.filter_by(idarticulo=idarticulo, idlista=idlista).first()
            #precio_unitario = articulo.precio if articulo else 0
            precio_unitario = precio.precio if precio else 0
            precio_total = precio_unitario * cantidad

            nuevo_item = Item(idfactura=idfactura, id=i, idarticulo=idarticulo, cantidad=cantidad, precio_unitario=precio_unitario, precio_total=precio_total)
            db.session.add(nuevo_item)
            total += precio_total
             # Actualizar la tabla de stocks
            stock = Stock.query.filter_by(idstock=idstock, idarticulo=idarticulo).first()
            if stock:
                stock.actual -= cantidad
                if stock.actual < 0:
                    stock.actual = 0  # Para evitar cantidades negativas
            else:
                stock = Stock(idstock=idstock, idarticulo=idarticulo, actual=-cantidad, maximo=0, deseable=0)
                db.session.add(stock)
        
        nueva_factura = Factura.query.get(idfactura)
        nueva_factura.total = total
        
        db.session.commit()
        
        if efectivo > 0:
            pagosfv = PagosFV(idfactura, 1, 0, efectivo)
            db.session.add(pagosfv)
            db.session.commit()
        
        if tarjeta > 0:
            entidad = int(request.form['entidad'])
            pagosfv = PagosFV(idfactura, 2, entidad, tarjeta)
            db.session.add(pagosfv)
            db.session.commit()
            
        if ctacte > 0:
            pagosfv = PagosFV(idfactura, 3, 0, ctacte)
            db.session.add(pagosfv)
            db.session.commit()
            
            debe = ctacte
            haber = 0
            try:
                ctactecli = CtaCteCli(idcliente, fecha, debe, haber)
                db.session.add(ctactecli)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Error grabado entidad crediticia: {e}')

        flash('Factura grabada')
        return redirect(url_for('index'))

    hoy = date.today()
    entidades = EntidadesCred.query.all()
    listas_precio = ListasPrecios.query.all()
    return render_template('nueva_venta.html', hoy=hoy, entidades=entidades, listas_precio=listas_precio)

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
    
    