from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, jsonify, session
from datetime import date, timedelta
from utils.utils import format_currency
from models.articulos import Articulo, ListasPrecios, Precio
from models.ventas import Factura, Item, PagosFV
from models.clientes import Clientes
from models.ctactecli import CtaCteCli
from models.entidades_cred import EntidadesCred
from models.configs import TipoComprobantes
from services.ventas import get_factura, actualizarStock
from sqlalchemy import func, extract
from utils.db import db
from utils.utils import check_session   
from utils.print_send_invoices import generar_factura_pdf, enviar_factura_por_email

bp_ventas = Blueprint('ventas', __name__, template_folder='../templates/ventas')

@bp_ventas.route('/ventas', methods=['GET', 'POST'])
@check_session
def ventas():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
    facturas = db.session.query(Factura.id,
                                Factura.fecha,
                                Factura.total,
                                Clientes.nombre.label('cliente'),
                                TipoComprobantes.nombre.label('tipo_comprobante')
                                ).join(Clientes, Factura.idcliente == Clientes.id 
                                ).join(TipoComprobantes, Factura.idtipocomprobante == TipoComprobantes.id
                                ).filter(Factura.fecha >= desde, Factura.fecha <= hasta).all()
    #facturas =  Factura.query.filter(Factura.fecha >= desde, Factura.fecha <= hasta)
    return render_template('ventas.html', facturas=facturas, desde=desde, hasta=hasta)

@bp_ventas.route('/nueva_venta', methods=['GET', 'POST'])
@check_session
def nueva_venta():
    if request.method == 'POST':
        idcliente = request.form['idcliente']
        fecha = request.form['fecha']
        idlista = request.form['idlista']
        id_tipo_comprobante = request.form['id_tipo_comprobante']
        efectivo = float(request.form['efectivo'])
        tarjeta = float(request.form['tarjeta'])
        ctacte = float(request.form['ctacte'])
        total = 0  # Esto se calculará más tarde

        nueva_factura = Factura(idcliente=idcliente, idlista=idlista, fecha=fecha, total=total, id_tipo_comprobante=id_tipo_comprobante, idsucursal=session['id_sucursal'])
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
            articulo = db.session.query(Articulo.id).filter(Articulo.codigo == idarticulo).first()
            precio = Precio.query.filter_by(idarticulo=articulo.id, idlista=idlista).first()
            #precio_unitario = articulo.precio if articulo else 0
            precio_unitario = precio.precio if precio else 0
            precio_total = precio_unitario * cantidad

            nuevo_item = Item(idfactura=idfactura, id=i, idarticulo=articulo.id, cantidad=cantidad, precio_unitario=precio_unitario, precio_total=precio_total)
            db.session.add(nuevo_item)
            total += precio_total
            # Actualizar la tabla de stocks
            actualizarStock(idstock, articulo.id, cantidad)
            
        
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
        generar_factura_pdf(idfactura)
        cliente = Clientes.query.get(idcliente)
        if cliente.email != None:
            pdf_path = f"factura-{idfactura}.pdf"
            enviar_factura_por_email(cliente.email, pdf_path)
        return redirect(url_for('index'))

    hoy = date.today()
    entidades = EntidadesCred.query.all()
    listas_precio = ListasPrecios.query.all()
    return render_template('nueva_venta.html', hoy=hoy, entidades=entidades, listas_precio=listas_precio)
    
@bp_ventas.route('/ver_factura_vta/<id>') 
@check_session
def ver_factura_vta(id):
    factura, items, pagos = get_factura(id)
    return render_template('factura-vta.html', factura=factura, items=items, pagos=pagos)

@bp_ventas.route('/imprimir_factura_vta/<id>') 
@check_session
def imprimir_factura_vta(id):
    generar_factura_pdf(id, footer_text="")
    return redirect(url_for('ventas.ver_factura_vta', id=id))

@bp_ventas.route('/enivar_factura_vta_mail/<id>/<idcliente>') 
@check_session
def enivar_factura_vta_mail(id, idcliente):
    generar_factura_pdf(id, footer_text="")
    cliente = Clientes.query.get(idcliente)
    if cliente.email != None:
        pdf_path = f"factura-{id}.pdf"
        enviar_factura_por_email(cliente.email, pdf_path)
    return redirect(url_for('ventas.ver_factura_vta', id=id))