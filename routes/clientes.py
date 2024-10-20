from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify
from datetime import datetime, date
from models.clientes import Clientes
from models.ventas import Factura
from models.configs import TipoDocumento, TipoIva
from services.clientes import save_cliente
from utils.db import db
from utils.utils import check_session

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

@bp_clientes.route('/get_cliente/<id>')
@check_session
def get_cliente(id):
    cliente = Clientes.query.get(id)
    if cliente:
        return jsonify(success=True, cliente={'id': cliente.id, 'nombre': cliente.nombre, 'telefono': cliente.telefono, 'ctacte': cliente.ctacte})
    else:
        return jsonify(success=False)

@bp_clientes.route('/get_clientes')
@check_session
def get_clientes():
    nombre = request.args.get('nombre', '')
    if nombre:
        clientes = Clientes.query.filter(Clientes.nombre.like(f"{nombre}%")).all()
    else:
        clientes = []
    return jsonify([{'id': c.id, 'nombre': c.nombre, 'telefono': c.telefono, 'ctacte': c.ctacte} for c in clientes])

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
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado')
    return redirect(url_for('clientes'))

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