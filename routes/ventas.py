from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, jsonify, session
from models.articulos import ListasPrecios
from models.ventas import Factura
from models.clientes import Clientes
from models.entidades_cred import EntidadesCred
from models.articulos import Articulo
from models.configs import TipoComprobantes
from services.ventas import get_factura, procesar_nueva_venta
from utils.db import db
from utils.utils import check_session   
from utils.print_send_invoices import generar_factura_pdf, enviar_factura_por_email
from datetime import date
from sqlalchemy import text

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
        try:
            procesar_nueva_venta(request.form, session['id_sucursal'])
            flash('Factura grabada exitosamente')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar la venta: {e}')
            return redirect(url_for('ventas.nueva_venta'))
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

@bp_ventas.route('/ventasArticulos', methods=['GET', 'POST'])
@check_session
def ventasArticulos():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
        articulos = []
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        articulos = db.session.execute(text("CALL venta_articulos(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()


    return render_template('ventas-articulos.html', articulos=articulos, desde=desde, hasta=hasta)
