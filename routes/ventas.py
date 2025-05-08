from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, session, g
from models.articulos import ListasPrecios
from models.clientes import Clientes
from models.entidades_cred import EntidadesCred
from models.configs import PuntosVenta
from services.ventas import get_factura, procesar_nueva_venta, get_vta_sucursales_data, get_vta_vendedores_data, procesar_nuevo_remito, \
                            ventas_desde_hasta, facturar_fe
from utils.db import db
from utils.utils import check_session, format_currency, alertas_mensajes
from utils.print_send_invoices import generar_factura_pdf, enviar_factura_por_email
from datetime import date
from sqlalchemy import text
import requests

bp_ventas = Blueprint('ventas', __name__, template_folder='../templates/ventas', static_folder='../static')


@bp_ventas.route('/ventas', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ventas():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
    facturas = ventas_desde_hasta(desde, hasta)
    #facturas =  Factura.query.filter(Factura.fecha >= desde, Factura.fecha <= hasta)
    return render_template('ventas.html', facturas=facturas, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

@bp_ventas.route('/get_punto_vta', methods=['GET'])
@check_session
def get_punto_vta():
    punto_vta = session.get('idPuntoVenta', None)
    return jsonify({'punto_vta': punto_vta})

@bp_ventas.route('/get_puntos_vta_sucursal', methods=['GET'])
@check_session
def get_puntos_vta_sucursal():
    puntosVtaSucursal = db.session.query(PuntosVenta.id, PuntosVenta.punto_vta).filter(PuntosVenta.idsucursal == session['id_sucursal']).all()
    return jsonify([{'id': pv.id, 'puntoVta': pv.punto_vta} for pv in puntosVtaSucursal])

@bp_ventas.route('/set_punto_vta', methods=['POST'])
@check_session
def set_punto_vta():
    try:
        # Obtener el ID del punto de venta desde la solicitud
        punto_vta_id = request.json.get('punto_vta_id')
        if not punto_vta_id:
            return jsonify({'success': False, 'message': 'ID de punto de venta no proporcionado'}), 400

        # Asignar el valor a la sesión
        session['idPuntoVenta'] = punto_vta_id
        
        return jsonify({'success': True, 'message': 'Punto de venta asignado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al asignar el punto de venta: {str(e)}'}), 500
    
@bp_ventas.route('/nueva_venta', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nueva_venta():
    if request.method == 'POST':
        try:
            nro_comprobante = procesar_nueva_venta(request.form, session['id_sucursal'])
            flash(f'Factura grabada exitosamente: {nro_comprobante}')
            return redirect(url_for('ventas.nueva_venta'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar la venta: {e}')
            return redirect(url_for('ventas.nueva_venta'))
    hoy = date.today()
    entidades = EntidadesCred.query.all()
    listas_precio = ListasPrecios.query.all()
    return render_template('nueva_venta.html', hoy=hoy, entidades=entidades, listas_precio=listas_precio, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

@bp_ventas.route('/nuevo_remito', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nuevo_remito():
    if request.method == 'POST':
        try:
            nro_comprobante = procesar_nuevo_remito(request.form, session['id_sucursal'])
            flash(f'Remito grabado exitosamente: {nro_comprobante}')
            return redirect(url_for('ventas.nuevo_remito'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar el remito: {e}')
            return redirect(url_for('ventas.nuevo_remito'))
    hoy = date.today()
    return render_template('nuevo_remito.html', hoy=hoy, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)
    
@bp_ventas.route('/ver_factura_vta/<id>') 
@check_session
@alertas_mensajes
def ver_factura_vta(id):
    factura, items, pagos = get_factura(id)
    return render_template('factura-vta.html', factura=factura, items=items, pagos=pagos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

#----------------- factura electronica ------------------#

@bp_ventas.route('/facturar/<ptovta>/<idfactura>', methods=['GET', 'POST'])
def facturar(ptovta, idfactura):
    try:
        response, statuscode = facturar_fe(ptovta, idfactura)  
        print(response)
        print(statuscode)
        data = response.get_json()
        print(data)
        if data.get('success') == True:
            cae = data.get('result', {}).get('cae')
            nro_cbte = data.get('result', {}).get('nro_cbte')
            flash(f'Factura {nro_cbte} emitida correctamente. CAE: {cae}')
            # Generar PDF
            return redirect(url_for('ventas.ver_factura_vta', id=idfactura))
        else:
            flash(f'Ocurrió un error al procesar la venta: {data.get("error")}', 'error')
            return redirect(url_for('ventas.ver_factura_vta', id=idfactura))
    except Exception as e:
        print(f'Error al generar factura electrónica: {e}')
        return redirect(url_for('ventas.ver_factura_vta', id=idfactura))

#----------------- fin factura electronica ------------------#

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
@alertas_mensajes
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
    return render_template('ventas-articulos.html', articulos=articulos, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

@bp_ventas.route('/ventasClientes', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ventasClientes():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
        ventas = []
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        ventas = db.session.execute(text("CALL venta_clientes(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
    return render_template('ventas-clientes.html', ventas=ventas, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

@bp_ventas.route('/ventasUnCliente', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ventasUnCliente():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
        cliente = {}
        ventas = []
        articulos = []
    else:
        id = request.form['idCliente']
        desde = request.form['fechaDesde']
        hasta = request.form['fechaHasta']
        
        cliente = Clientes.query.get(id)
        ventas = db.session.execute(text("CALL ventas_un_cliente(:idcliente, :desde, :hasta)"),
                         {'idcliente': id, 'desde': desde, 'hasta': hasta}).fetchall()
        articulos = db.session.execute(text("CALL ventas_art_un_cliente(:idcliente, :desde, :hasta)"),
                         {'idcliente': id, 'desde': desde, 'hasta': hasta}).fetchall()
    return render_template('ventas-un-cliente.html', cliente=cliente, ventas=ventas, articulos=articulos, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)


@bp_ventas.route('/get_vta_sucursales/<desde>/<hasta>')
@check_session
def get_vta_sucursales(desde, hasta):
    ventas = get_vta_sucursales_data(desde, hasta)
    return jsonify(success=True, ventas=ventas) 

        
@bp_ventas.route('/get_vta_vendedores/<desde>/<hasta>')
@check_session
def get_vta_vendedores(desde, hasta):
    ventas = get_vta_vendedores_data(desde, hasta)
    return jsonify(success=True, ventas=ventas) 