from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, current_app, session
from datetime import date
from models.proveedores import Proveedores, FacturaC
from models.configs import TipoDocumento, TipoIva, TipoComprobantes
from services.proveedores import procesar_nueva_compra, procesar_nuevo_gasto
from utils.utils import check_session
from utils.db import db
from sqlalchemy import and_

bp_proveedores = Blueprint('proveedores', __name__, template_folder='../templates/proveedores')

#------------------ proveedores --------------

@bp_proveedores.route('/proveedores')
@check_session
def proveedores():
    tipo_docs = TipoDocumento.query.all()
    tipo_ivas = TipoIva.query.all()
    proveedores = Proveedores.query.all()
    return render_template('proveedores.html', tipo_docs=tipo_docs, tipo_ivas=tipo_ivas, proveedores=proveedores)

@bp_proveedores.route('/add_proveedor', methods=['POST'])
@check_session
def add_proveedor():
    nombre = request.form['nombre']
    mail = request.form['mail']
    telefono = request.form['telefono']
    documento = request.form['documento']
    tipo_doc = request.form['tipoDoc']
    tipo_iva = request.form['tipoIva']
    proveedores = Proveedores(nombre, mail, telefono, documento, tipo_doc, tipo_iva)
    db.session.add(proveedores)
    db.session.commit()
    flash('Proveedor agregado')
    return redirect(url_for('proveedores.proveedores'))

@bp_proveedores.route('/proveedor/<id>')
@check_session
def proveedor(id):
    proveedor = Proveedores.query.get(id)
    if proveedor:
        return jsonify(success=True, proveedor={"id": proveedor.id, "nombre": proveedor.nombre})
    else:
        return jsonify(success=False)

@bp_proveedores.route('/get_proveedor/<id>/<tipo_operacion>')
@check_session
def get_proveedor(id, tipo_operacion):
    proveedor = db.session.query(
        Proveedores.id.label('id'),
        Proveedores.nombre.label('nombre'),
        Proveedores.documento.label('documento'),
        Proveedores.email.label('email'),
        Proveedores.telefono.label('telefono'),
        Proveedores.id_tipo_doc.label('id_tipo_doc'),
        Proveedores.id_tipo_iva.label('id_tipo_iva'),
        TipoComprobantes.id.label('id_tipo_comprobante'),
        TipoComprobantes.nombre.label('tipo_comprobante'))\
        .outerjoin(TipoComprobantes, and_(Proveedores.id_tipo_iva == TipoComprobantes.id_tipo_iva, TipoComprobantes.id_tipo_iva_owner == 1, TipoComprobantes.id_tipo_operacion == tipo_operacion))\
        .filter(Proveedores.id == id).first()
    print(proveedor)  
    if proveedor:
        return jsonify(success=True, proveedor={'id': proveedor.id, 'nombre': proveedor.nombre, 'telefono': proveedor.telefono, 'id_tipo_comprobante': proveedor.id_tipo_comprobante, 'tipo_comprobante':proveedor.tipo_comprobante, 'tipo_doc':proveedor.id_tipo_doc, 'tipo_iva':proveedor.id_tipo_iva}) 
    else:
        return jsonify(success=False)

@bp_proveedores.route('/update_proveedor/<id>', methods=['GET', 'POST'])
@check_session
def update_proveedor(id):
    proveedor = Proveedores.query.get(id)
    if request.method == 'GET':
        tipo_docs = TipoDocumento.query.all()
        tipo_ivas = TipoIva.query.all()
        return render_template('upd-proveedor.html', tipo_docs=tipo_docs, tipo_ivas=tipo_ivas, proveedor = proveedor)
    if request.method == 'POST':
        proveedor.nombre = request.form['nombre']
        proveedor.email = request.form['mail']
        proveedor.telefono = request.form['telefono']
        proveedor.docuemto = request.form['documento']
        db.session.commit()
        flash('Proveedor grabado')
        return redirect(url_for('proveedores.proveedores'))

@bp_proveedores.route('/delete_proveedor/<id>')
@check_session
def delete_proveedor(id):
    proveedor = Proveedores.query.get(id)
    db.session.delete(proveedor)
    db.session.commit()
    flash('Proveedor eliminado')
    return redirect(url_for('home'))

# ----------------- compras ------------------
@bp_proveedores.route('/compras', methods=['GET', 'POST'])
@check_session
def compras():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
    facturas = FacturaC.query.filter(FacturaC.fecha >= desde, FacturaC.fecha <= hasta)
    return render_template('compras.html', facturas=facturas, desde=desde, hasta=hasta)
    
@bp_proveedores.route('/nueva_compra', methods=['GET', 'POST'])
@check_session
def nueva_compra():
    if request.method == 'POST':
        try:
            procesar_nueva_compra(request.form, session['id_sucursal'])
            flash('Factura grabada exitosamente')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar la compra: {e}')
            return redirect(url_for('proveedores.nueva_compra'))
    hoy = date.today()
    return render_template('nueva_compra.html', hoy=hoy)

@bp_proveedores.route('/nuevo_gasto', methods=['GET', 'POST'])
@check_session
def nuevo_gasto():
    if request.method == 'POST':
        procesar_nuevo_gasto(request.form, session['id_sucursal']) 
        flash('Gasto grabado')
        return redirect(url_for('index'))
    else:
        return render_template('nuevo_gasto.html')
        
        