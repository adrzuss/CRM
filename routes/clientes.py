from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, session
from flask import g
from datetime import datetime, date
from models.clientes import Clientes
from models.ventas import Factura
from models.configs import TipoDocumento, TipoIva, TipoComprobantes, TipoCompAplica, Categorias, Provincias, Localidades
from services.clientes import save_cliente, get_abc_operaciones, get_abc_montos, get_abc_productos
from services.ctactecli import saldo_ctacte
from services.configs import validar_cuit
from utils.db import db
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes
from sqlalchemy import and_

bp_clientes = Blueprint('clientes', __name__, template_folder='../templates/clientes')

@bp_clientes.route('/clientes/<id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def clientes(id):
    if request.method == 'POST':
        cliente = []
    else:
        cliente = Clientes.query.get(id)
    clientes = Clientes.query.all()
    tipo_docs = TipoDocumento.query.all()
    tipo_ivas = TipoIva.query.all()
    categorias = Categorias.query.all()
    provincias = Provincias.query.all()
    if cliente:
        localidades = Localidades.query.filter_by(id_provincia=cliente.idprovincia).all()
    else:
        localidades = []
    return render_template('clientes.html', clientes=clientes, cliente=cliente, tipo_docs=tipo_docs, tipo_ivas=tipo_ivas, categorias=categorias, provincias=provincias, localidades=localidades, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_clientes.route('/new_cliente', methods=['POST'])
@check_session
def add_cliente():
    id_cliente = request.form['idcliente']
    if id_cliente:
        cliente = Clientes.query.get(id_cliente)
        ctacte = request.form.get("ctacte") != None
        cliente.nombre = request.form['nombre']
        cliente.documento = request.form['documento']
        cliente.email = request.form['mail']
        cliente.idcategoria = request.form['categoria']
        cliente.telefono = request.form['telefono']
        cliente.direccion = request.form['direccion']
        cliente.idlocalidad = request.form['localidad']
        cliente.idprovincia = request.form['provincia']
        cliente.id_tipo_doc = request.form['tipo_doc']
        cliente.id_tipo_iva = request.form['tipo_iva']
        cliente.ctacte = ctacte
        db.session.commit()
        flash(f'Cliente actualizado: {id_cliente}: {cliente.nombre}')
    else:     
        nombre = request.form['nombre']
        documento = request.form['documento']
        mail = request.form['mail']
        categoria = request.form['categoria']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        localidad = request.form['localidad']
        provincia = request.form['provincia']
        ctacte = request.form.get("ctacte") != None
        id_tipo_doc = request.form['tipo_doc']
        id_tipo_iva = request.form['tipo_iva']
        id_cliente = save_cliente(nombre, documento, mail, categoria, telefono, direccion, localidad, provincia, ctacte, id_tipo_doc, id_tipo_iva)
        flash(f'Cliente agregado: {id_cliente}: {nombre}')
    return redirect('/')

@bp_clientes.route('/localidades/<idprovincia>', methods=['GET'])
@check_session
def get_localidades(idprovincia):
    print(f"Fetching localidades for provincia ID: {idprovincia}")
    localidades = Localidades.query.filter_by(id_provincia=idprovincia).all()
    print(f"Localidades for provincia {idprovincia}: {[loc.localidad for loc in localidades]}")
    return jsonify(success=True, localidades=[{'id': loc.id, 'localidad': loc.localidad} for loc in localidades]) 


@bp_clientes.route('/get_cliente/<id>/<tipo_operacion>')
@check_session
def get_cliente(id, tipo_operacion):
    try:
        cliente = db.session.query(
            Clientes.id.label('id'),
            Clientes.nombre.label('nombre'),
            Clientes.documento.label('documento'),
            Clientes.email.label('email'),
            Clientes.idcategoria,
            Clientes.telefono.label('telefono'),
            Clientes.direccion.label('direccion'),
            Clientes.ctacte.label('ctacte'),
            Clientes.id_tipo_doc.label('id_tipo_doc'),
            Clientes.id_tipo_iva.label('id_tipo_iva'),
            Clientes.baja.label('baja'),
            TipoComprobantes.id.label('id_tipo_comprobante'),
            TipoComprobantes.nombre.label('tipo_comprobante'),
            Categorias.nombre.label('categoria'))\
            .join(TipoCompAplica, and_(Clientes.id_tipo_iva == TipoCompAplica.id_iva_entidad, TipoCompAplica.id_iva_owner == session['tipo_iva'], TipoCompAplica.id_tipo_oper == tipo_operacion))\
            .join(TipoComprobantes, (TipoCompAplica.id_tipo_comp == TipoComprobantes.id))\
            .outerjoin(Categorias, Clientes.idcategoria == Categorias.id)\
            .filter(Clientes.id == id).first()
    except Exception as e:
        print(e)
        cliente = None
        
    if cliente:
        if (cliente.baja == datetime(1900,1,1).date()):
            baja = False
        else:
            baja = True
        return jsonify(success=True, cliente={'id': cliente.id, 'nombre': cliente.nombre, 'idcategoria': cliente.idcategoria, 'categoria': cliente.categoria, 'telefono': cliente.telefono, 'ctacte': cliente.ctacte, 'id_tipo_comprobante': cliente.id_tipo_comprobante, 'tipo_comprobante':cliente.tipo_comprobante, 'tipo_doc':cliente.id_tipo_doc, 'tipo_iva':cliente.id_tipo_iva, 'baja': baja}) 
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
        Clientes.idcategoria,
        Clientes.telefono.label('telefono'),
        Clientes.direccion.label('direccion'),
        Clientes.ctacte.label('ctacte'),
        Clientes.id_tipo_doc.label('id_tipo_doc'),
        Clientes.id_tipo_iva.label('id_tipo_iva'),
        TipoComprobantes.id.label('id_tipo_comprobante'),
        TipoComprobantes.nombre.label('tipo_comprobante'),
        Categorias.nombre.label('categoria'))\
        .join(TipoCompAplica, and_(Clientes.id_tipo_iva == TipoCompAplica.id_iva_entidad, TipoCompAplica.id_iva_owner == session['tipo_iva'], TipoCompAplica.id_tipo_oper == tipo_operacion))\
        .join(TipoComprobantes, (TipoCompAplica.id_tipo_comp == TipoComprobantes.id))\
        .outerjoin(Categorias, Clientes.idcategoria == Categorias.id)\
        .filter(Clientes.nombre.like(f"{nombre}%")).all()
    else:
        clientes = []
    return jsonify([{'id': c.id, 'nombre': c.nombre, 'idcategoria': c.idcategoria, 'categoria': c.categoria, 'telefono': c.telefono, 'ctacte': c.ctacte, 'id_tipo_comprobante': c.id_tipo_comprobante, 'tipo_comprobante':c.tipo_comprobante, 'tipo_doc':c.id_tipo_doc, 'tipo_iva':c.id_tipo_iva} for c in clientes]) 

@bp_clientes.route('/update_cliente/<id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def update_cliente(id):
    cliente = Clientes.query.get(id)
    tipo_docs = TipoDocumento.query.all()
    tipo_ivas = TipoIva.query.all()
    if request.method == 'GET':
        return render_template('upd-cliente.html', cliente = cliente, tipo_docs=tipo_docs, tipo_ivas=tipo_ivas, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
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
@alertas_mensajes
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
        return render_template('facturas-cli.html', facturas=facturas, cliente=cliente, desde=desde_str, hasta=hasta_str, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    desde = date.today()
    hasta = date.today()
    facturas = db.session.query(Factura).join(Clientes).filter(
            Factura.idcliente == cliente.id,
            Factura.fecha >= desde,
            Factura.fecha <= hasta
        ).all()
    return render_template('facturas-cli.html', facturas=facturas, cliente=cliente, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)   

@bp_clientes.route('/abc_clientes', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def abc_clientes():
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        return redirect(url_for('clientes.abc_clientes', desde=desde, hasta=hasta))
    if request.method == 'GET':
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        if desde == None:
            desde = date.today()
        if hasta == None:    
            hasta = date.today()
        
        abc_operaciones = get_abc_operaciones(desde, hasta)
        abc_montos = get_abc_montos(desde, hasta)   
        abc_productos = get_abc_productos(desde, hasta)
        
        return render_template('abc-clientes.html', desde=desde, hasta=hasta, abc_operaciones=abc_operaciones, abc_montos=abc_montos, abc_productos=abc_productos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)