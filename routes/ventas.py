from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, jsonify
from datetime import date, timedelta
from utils.utils import format_currency
from models.articulos import Articulo, Stock, ListasPrecios, Precio
from models.ventas import Factura, Item, PagosFV
from models.ctactecli import CtaCteCli
from models.entidades_cred import EntidadesCred
from services.ventas import get_factura
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
    
@bp_ventas.route('/ver_factura_vta/<id>') 
def ver_factura_vta(id):
    factura, items, pagos = get_factura(id)
    return render_template('factura-vta.html', factura=factura, items=items, pagos=pagos)