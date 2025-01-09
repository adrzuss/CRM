from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, session
from datetime import datetime, date
from models.clientes import Clientes
from models.ventas import Factura
from models.configs import TipoDocumento, TipoIva, TipoComprobantes
from services.clientes import save_cliente
from services.ctactecli import saldo_ctacte
from utils.db import db
from utils.utils import check_session
from sqlalchemy import and_

bp_clientes = Blueprint('clientes', __name__, template_folder='../templates/clientes')

@bp_clientes.route('/clientes')
@check_session
def clientes():
    clientes = Clientes.query.all()
    tipo_docs = TipoDocumento.query.all()
    tipo_ivas = TipoIva.query.all()
    return render_template('clientes.html', clientes=clientes, tipo_docs=tipo_docs, tipo_ivas=tipo_ivas)

@bp_clientes.route('/new_cliente', methods=['POST'])
@check_session
def add_cliente():
    nombre = request.form['nombre']
    documento = request.form['documento']
    mail = request.form['mail']
    telefono = request.form['telefono']
    direccion = request.form['direccion']
    ctacte = request.form.get("ctacte") != None
    id_tipo_doc = request.form['tipo_doc']
    id_tipo_iva = request.form['tipo_iva']
    id_cliente = save_cliente(nombre, documento, mail, telefono, direccion, ctacte, id_tipo_doc, id_tipo_iva)
    flash(f'Cliente agregado: {id_cliente}')
    return redirect('/')

@bp_clientes.route('/get_cliente/<id>/<tipo_operacion>')
@check_session
def get_cliente(id, tipo_operacion):
    #cliente = Clientes.query.get(id)
    print(f'tipo iva owner: {session["tipo_iva"]}')
    cliente = db.session.query(
        Clientes.id.label('id'),
        Clientes.nombre.label('nombre'),
        Clientes.documento.label('documento'),
        Clientes.email.label('email'),
        Clientes.telefono.label('telefono'),
        Clientes.direccion.label('direccion'),
        Clientes.ctacte.label('ctacte'),
        Clientes.id_tipo_doc.label('id_tipo_doc'),
        Clientes.id_tipo_iva.label('id_tipo_iva'),
        TipoComprobantes.id.label('id_tipo_comprobante'),
        TipoComprobantes.nombre.label('tipo_comprobante'))\
        .outerjoin(TipoComprobantes, and_(Clientes.id_tipo_iva == TipoComprobantes.id_tipo_iva, TipoComprobantes.id_tipo_iva_owner == session['tipo_iva'], TipoComprobantes.id_tipo_operacion == tipo_operacion))\
        .filter(Clientes.id == id).first()
      
    if cliente:
        return jsonify(success=True, cliente={'id': cliente.id, 'nombre': cliente.nombre, 'telefono': cliente.telefono, 'ctacte': cliente.ctacte, 'id_tipo_comprobante': cliente.id_tipo_comprobante, 'tipo_comprobante':cliente.tipo_comprobante, 'tipo_doc':cliente.id_tipo_doc, 'tipo_iva':cliente.id_tipo_iva}) 
    else:
        return jsonify(success=False)

@bp_clientes.route('/get_clientes')
@check_session
def get_clientes():
    nombre = request.args.get('nombre', '')
    tipo_operacion = request.args.get('tipo_operacion', '')
    if nombre:
        clientes = db.session.query(
        Clientes.id.label('id'),
        Clientes.nombre.label('nombre'),
        Clientes.documento.label('documento'),
        Clientes.email.label('email'),
        Clientes.telefono.label('telefono'),
        Clientes.direccion.label('direccion'),
        Clientes.ctacte.label('ctacte'),
        Clientes.id_tipo_doc.label('id_tipo_doc'),
        Clientes.id_tipo_iva.label('id_tipo_iva'),
        TipoComprobantes.nombre.label('tipo_comprobante'))\
        .outerjoin(TipoComprobantes, and_(Clientes.id_tipo_iva == TipoComprobantes.id_tipo_iva, TipoComprobantes.id_tipo_iva_owner == session['tipo_iva'], TipoComprobantes.id_tipo_operacion == tipo_operacion))\
        .filter(Clientes.nombre.like(f"{nombre}%")).all()
    else:
        clientes = []
    return jsonify([{'id': c.id, 'nombre': c.nombre, 'telefono': c.telefono, 'ctacte': c.ctacte, 'tipo_comprobante':c.tipo_comprobante, 'tipo_doc':c.id_tipo_doc, 'tipo_iva':c.id_tipo_iva} for c in clientes]) 

@bp_clientes.route('/update_cliente/<id>', methods=['GET', 'POST'])
@check_session
def update_cliente(id):
    cliente = Clientes.query.get(id)
    tipo_docs = TipoDocumento.query.all()
    tipo_ivas = TipoIva.query.all()
    if request.method == 'GET':
        return render_template('upd-cliente.html', cliente = cliente, tipo_docs=tipo_docs, tipo_ivas=tipo_ivas)
    if request.method == 'POST':
        ctacte = request.form.get("ctacte") != None
        cliente.nombre = request.form['nombre']
        cliente.documento = request.form['documento']
        cliente.email = request.form['mail']
        cliente.telefono = request.form['telefono']
        cliente.direccion = request.form['direccion']
        cliente.id_tipo_doc = request.form['tipo_doc']
        cliente.id_tipo_iva = request.form['tipo_iva']
        cliente.ctacte = ctacte
        db.session.commit()
        flash('Cliente grabado')
        return redirect(url_for('clientes.clientes'))

@bp_clientes.route('/delete_cliente/<id>')
@check_session
def delete_cliente(id):
    cliente = Clientes.query.get(id)
    if cliente.ctacte == True:
        saldo = saldo_ctacte(id)
        if saldo['total_debe'] > 0 or saldo['total_haber'] > 0:
            flash('No se puede eliminar un cliente con saldo en cta. cte.')
        return redirect(url_for('clientes.clientes'))
    
    cliente.baja = date.today()
    db.session.commit()
    flash('Cliente dado de baja')
    return redirect(url_for('clientes.clientes'))

@bp_clientes.route('/facturas_cliente/<id>', methods=['GET', 'POST'])
@check_session
def facturas_cliente(id):
    cliente = Clientes.query.get(id)
    if request.method == 'POST':
        # Obtener las fechas del formulario
        desde_str = request.form['desde']
        hasta_str = request.form['hasta']

        # Convertir las fechas a objetos datetime
        desde = datetime.strptime(desde_str, '%Y-%m-%d')
        hasta = datetime.strptime(hasta_str, '%Y-%m-%d')
        
        # Realizar la consulta con join y filtro por fechas
        facturas = db.session.query(Factura).join(Clientes).filter(
            Factura.idcliente == cliente.id,
            Factura.fecha >= desde,
            Factura.fecha <= hasta
        ).all()
        
        # Pasar los resultados a la plantilla
        return render_template('facturas-cli.html', facturas=facturas, cliente=cliente, desde=desde_str, hasta=hasta_str)
    desde = date.today()
    hasta = date.today()
    facturas = db.session.query(Factura).join(Clientes).filter(
            Factura.idcliente == cliente.id,
            Factura.fecha >= desde,
            Factura.fecha <= hasta
        ).all()
    return render_template('facturas-cli.html', facturas=facturas, cliente=cliente, desde=desde, hasta=hasta)