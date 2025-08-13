from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, session, g
from datetime import date
from models.proveedores import Proveedores, FacturaC, RemitoFacturas
from models.configs import TipoDocumento, TipoIva, TipoComprobantes, PlanCtas, TipoCompAplica
from models.ctacteprov import CtaCteProv
from services.bancos import BancoService
from services.proveedores import procesar_nueva_compra, procesar_nuevo_gasto, get_factura, actualizar_precios_por_compras, \
    procesar_nuevo_remito, get_remito, procesar_nueva_op, get_movs_pendientes_ctacte, get_ordenes_pago
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes
from utils.db import db
from sqlalchemy.orm import aliased
from sqlalchemy import and_

bp_proveedores = Blueprint('proveedores', __name__, template_folder='../templates/proveedores')

#------------------ proveedores --------------

@bp_proveedores.route('/proveedores/<id>', methods=['GET'])
@check_session
@alertas_mensajes
def proveedores(id):
    print(request.method)
    tipo_docs = TipoDocumento.query.all()
    tipo_ivas = TipoIva.query.all()
    proveedores = Proveedores.query.all()
    proveedor = []  
    if id != 0:
        proveedor = Proveedores.query.get(id)
    return render_template('proveedores.html', proveedor=proveedor, tipo_docs=tipo_docs, tipo_ivas=tipo_ivas, proveedores=proveedores, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_proveedores.route('/add_proveedor', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def add_proveedor():
    id = request.form['id']
    if id:
        proveedor = Proveedores.query.get(id)
        proveedor.nombre = request.form['nombre']
        proveedor.fantasia = request.form['fantasia']
        proveedor.direccion = request.form['direccion']
        proveedor.email = request.form['mail']
        proveedor.telefono = request.form['telefono']
        proveedor.documento = request.form['documento']
        proveedor.id_tipo_doc = request.form['tipoDoc']
        proveedor.id_tipo_iva = request.form['tipoIva']
        db.session.commit()
        flash('Proveedor actualizado')
    else:      
        nombre = request.form['nombre']
        fantasia = request.form['fantasia']
        direccion = request.form['direccion']
        mail = request.form['mail']
        telefono = request.form['telefono']
        documento = request.form['documento']
        tipo_doc = request.form['tipoDoc']
        tipo_iva = request.form['tipoIva']
        proveedores = Proveedores(nombre, fantasia=fantasia, email=mail, telefono=telefono, documento=documento, direccion=direccion, tipo_doc=tipo_doc, tipo_iva=tipo_iva)
        db.session.add(proveedores)
        db.session.commit()
        flash('Proveedor agregado')
    return redirect(url_for('proveedores.proveedores', id=0))

@bp_proveedores.route('/proveedor/<id>')
@check_session
def proveedor(id):
    proveedor = Proveedores.query.get(id)
    if proveedor:
        return jsonify(success=True, proveedor={"id": proveedor.id, "nombre": proveedor.nombre})
    else:
        return jsonify(success=False)

@bp_proveedores.route('/get_proveedor/<id>')
@check_session
def get_proveedor(id):
    proveedor = db.session.query(
        Proveedores.id.label('id'),
        Proveedores.nombre.label('nombre'),
        Proveedores.documento.label('documento'),
        Proveedores.email.label('email'),
        Proveedores.telefono.label('telefono'),
        Proveedores.id_tipo_doc.label('id_tipo_doc'),
        Proveedores.id_tipo_iva.label('id_tipo_iva')) \
        .filter(Proveedores.id == id).first()
    if proveedor:
        return jsonify(success=True, proveedor={'id': proveedor.id, 'nombre': proveedor.nombre, 'telefono': proveedor.telefono, 'tipo_doc':proveedor.id_tipo_doc, 'tipo_iva':proveedor.id_tipo_iva}) 
    else:
        return jsonify(success=False)

@bp_proveedores.route('/get_proveedores')
@check_session
def get_proveedores():
    nombre = request.args.get('nombre', '')
    if nombre:
        proveedores = db.session.query(
        Proveedores.id.label('id'),
        Proveedores.nombre.label('nombre'),
        Proveedores.documento.label('documento'),
        Proveedores.email.label('email'),
        Proveedores.telefono.label('telefono'),
        Proveedores.direccion.label('direccion'),
        Proveedores.id_tipo_doc.label('id_tipo_doc'),
        Proveedores.id_tipo_iva.label('id_tipo_iva'))\
        .filter(Proveedores.nombre.like(f"{nombre}%")).all()
    else:
        proveedores = []
    return jsonify([{'id': p.id, 'nombre': p.nombre, 'telefono': p.telefono, 'tipo_doc':p.id_tipo_doc, 'tipo_iva':p.id_tipo_iva} for p in proveedores]) 

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
@alertas_mensajes
def compras():
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        return redirect(url_for('proveedores.compras', desde=desde, hasta=hasta))
    if request.method == 'GET':
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        if desde == None:
            desde = date.today()
        if hasta == None:    
            hasta = date.today()
        facturas = db.session.query(FacturaC.id,
                                    FacturaC.fecha,
                                    FacturaC.nro_comprobante,
                                    FacturaC.total,
                                    TipoComprobantes.nombre.label('tipo_comprobante'),
                                    Proveedores.nombre.label('proveedor')) \
                                    .join(Proveedores, FacturaC.idproveedor == Proveedores.id) \
                                    .join(TipoComprobantes, FacturaC.idtipocomprobante == TipoComprobantes.id) \
                                    .filter(FacturaC.fecha >= desde, FacturaC.fecha <= hasta, FacturaC.idtipocomprobante != 11) \
                                    .order_by(FacturaC.fecha.desc()).all()
        return render_template('compras.html', facturas=facturas, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    
@bp_proveedores.route('/nueva_compra', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nueva_compra():
    if request.method == 'POST':
        try:
            actualizoCostos = procesar_nueva_compra(request.form, session['id_sucursal'])
            flash('Factura grabada exitosamente')
            if actualizoCostos:
                flash('Se actualizaron los costos de los artículos')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar la compra: {e}')
            return redirect(url_for('proveedores.nueva_compra'))
    planesCtas = PlanCtas.query.all()  
    tiposComp = db.session.query(TipoComprobantes.id,
                                TipoComprobantes.nombre) \
                                .join(TipoCompAplica, and_(TipoComprobantes.id == TipoCompAplica.id_tipo_comp,  TipoCompAplica.id_tipo_oper == 2)).all()  
    hoy = date.today()
    return render_template('nueva_compra.html', hoy=hoy, planesCtas=planesCtas, tiposComp=tiposComp, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_proveedores.route('/nuevo_gasto', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nuevo_gasto():
    if request.method == 'POST':
        procesar_nuevo_gasto(request.form, session['id_sucursal']) 
        flash('Gasto grabado')
        return redirect(url_for('index'))
    else:
        planesCtas = PlanCtas.query.all()
        tiposComp = db.session.query(TipoComprobantes.id,
                                TipoComprobantes.nombre) \
                                .join(TipoCompAplica, and_(TipoComprobantes.id == TipoCompAplica.id_tipo_comp,  TipoCompAplica.id_tipo_oper == 2)).all()
        return render_template('nuevo_gasto.html', planesCtas=planesCtas, tiposComp=tiposComp, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    
@bp_proveedores.route('/ver_factura_comp/<id>') 
@check_session
@alertas_mensajes
def ver_factura_comp(id):
    factura, items, pagos = get_factura(id)
    return render_template('factura-comp.html', factura=factura, items=items, pagos=pagos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
        
@bp_proveedores.route('/actualizar_precios_porcompras/<id>') 
@check_session
def actualizar_precios_porcompras(id):
    try:
        actualizar_precios_por_compras(id)
        flash('Precios actualizados')
        return redirect(url_for('proveedores.ver_factura_comp', id=id))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('proveedores.ver_factura_comp', id=id))

@bp_proveedores.route('/get_remitos/<int:idproveedor>')
@check_session
def get_remitos(idproveedor):
    if idproveedor > 0:
        remitos = db.session.query(FacturaC.id,
                                   FacturaC.fecha,
                                   FacturaC.nro_comprobante)\
                            .outerjoin(RemitoFacturas, RemitoFacturas.idremito == FacturaC.id) \
                            .filter(and_(FacturaC.idproveedor == idproveedor, FacturaC.idtipocomprobante == 11, RemitoFacturas.idremito == None)) \
                            .all()
    else:
        remitos = []
    
    return jsonify([{'id': r.id, 'fecha': r.fecha, 'nro_comprobante': r.nro_comprobante} for r in remitos]) 

        
@bp_proveedores.route('/remitosComp', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def remitosComp():
    FacturaC_Alias = aliased(FacturaC)
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        if desde == None:
            desde = date.today()
        if hasta == None:    
            hasta = date.today()
        return redirect(url_for('proveedores.remitosComp', desde=desde, hasta=hasta))
        
    if request.method == 'GET':
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        if desde == None:
            desde = date.today()
        if hasta == None:    
            hasta = date.today()
        remitos = db.session.query(FacturaC.id,
                                FacturaC.fecha,
                                FacturaC.nro_comprobante,
                                TipoComprobantes.nombre.label('tipo_comprobante'),
                                Proveedores.nombre.label('proveedor'),
                                RemitoFacturas.idfactura,
                                FacturaC_Alias.id.label('idfactura'),
                                FacturaC_Alias.fecha.label('fecha_factura'),
                                FacturaC_Alias.nro_comprobante.label('nro_comprobante_factura')) \
                                .join(Proveedores, FacturaC.idproveedor == Proveedores.id) \
                                .join(TipoComprobantes, FacturaC.idtipocomprobante == TipoComprobantes.id) \
                                .outerjoin(RemitoFacturas, RemitoFacturas.idremito == FacturaC.id) \
                                .outerjoin(FacturaC_Alias, and_(FacturaC_Alias.id == RemitoFacturas.idfactura, FacturaC_Alias.idtipocomprobante != 11)) \
                                .filter(FacturaC.fecha >= desde, FacturaC.fecha <= hasta, FacturaC.idtipocomprobante == 11) \
                                .order_by(FacturaC.fecha.desc()).all()
        
        return render_template('remitos.html', remitos=remitos, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_proveedores.route('/nuevo_remitoComp', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nuevo_remitoComp():
    if request.method == 'POST':
        try:
            procesar_nuevo_remito(request.form, session['id_sucursal'])
            flash('Remito grabado exitosamente')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar el remito: {e}')
            return redirect(url_for('proveedores.nuevo_remitoComp'))
    hoy = date.today()
    return render_template('nuevo_remitocomp.html', hoy=hoy, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
                       
@bp_proveedores.route('/ver_remito_comp/<id>') 
@check_session
@alertas_mensajes
def ver_remito_comp(id):
    remito, items = get_remito(id)
    return render_template('remito-compras.html', remito=remito, items=items, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

#--------- ordenes de pago --------------
                       
@bp_proveedores.route('/nueva_op', methods = ['GET', 'POST']) 
@check_session
@alertas_mensajes
def nueva_op():
    if request.method == 'POST':
        try:
            procesar_nueva_op(request.form, session['id_sucursal'])
            flash('Orden de pago grabado exitosamente')
            return redirect(url_for('proveedores.nueva_op'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar la orden de pago: {e}', 'error')
            return redirect(url_for('proveedores.nueva_op'))
    else:
        idproveedor = request.args.get('id', None)
    hoy = date.today()
    bancos = BancoService.obtener_todos()
    return render_template('nueva_op.html', hoy=hoy, idproveedor=idproveedor, bancos=bancos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_proveedores.route('/ordenes_pago')
@check_session
@alertas_mensajes
def ordenes_pago():
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    if desde == None:
        desde = date.today()
    if hasta == None:    
        hasta = date.today()
    ordenesPago = get_ordenes_pago(desde, hasta)
    return render_template('ordenes_pago.html', ordenesPago=ordenesPago, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_proveedores.route('/ver_op/<int:id>')
@check_session
@alertas_mensajes
def ver_op(id):
    return redirect(url_for('proveedores.ver_factura_comp', id=id))

#--------------- Cuentas Corrientes ------------------
@bp_proveedores.route('/get_movs_ctacte/<int:idproveedor>')
@check_session
def get_movs_ctacte(idproveedor):
    #Obtiene movimientos pendientes de cta. cte. de proveedores
    if idproveedor > 0:
        try:
            movs_ctacte = get_movs_pendientes_ctacte(idproveedor)
        except Exception as e:
            print(f"Error obteniendo movimientos de cta. cte.: {e}")
            raise Exception(f"Error obteniendo movimientos de cta. cte.: {e}")
          
    else:
        movs_ctacte = []
    
    return jsonify([{'id': r.id, 'fecha': r.fecha, 'tipo_comprobante': r.tipo_comprobante, 'nro_comprobante': r.nro_comprobante, 'saldo': (r.haber-r.debe-r.pagos)} for r in movs_ctacte]) 
