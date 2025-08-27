from flask import Blueprint, render_template, request, redirect, flash, url_for, g, jsonify
from models.entidades_cred import EntidadesCred
from models.ventas import Factura, PagosFV
from models.clientes import Clientes
from models.sucursales import Sucursales
from services.entidades_cred import getFinanciamiento, grabarAlicuotas, calcular_coeficiente
from utils.db import db
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes
from datetime import datetime

bp_entidades = Blueprint('entidades', __name__, template_folder='../templates/entidades')

@bp_entidades.route('/entidades/<id>', methods=['GET', 'POST'])
@bp_entidades.route('/entidades', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def entidades(id=0):
    entidades = EntidadesCred.query.all()
    if id != 0:
        entidad = EntidadesCred.query.get(id)
        if entidad:
            if request.method == 'POST':
                entidad.entidad = request.form['entidad']
                entidad.telefono = request.form['telefono']
                try:
                    db.session.commit()
                    flash('Entidad crediticia actualizada')
                    return redirect(url_for('entidades.entidades'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error actualizando entidad crediticia: {e}')
                    return redirect(url_for('entidades.entidades'))
    else:    
        entidad = []
    return render_template('entidades-cred.html', entidades=entidades, entidad=entidad, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_entidades.route('/add_entidad', methods = ['POST','GET'])
@check_session
@alertas_mensajes
def add_entidad():
    if request.method == 'POST':
        id = request.form['id']
        entidad = request.form['entidad']
        telefono = request.form['telefono']
        try:
            if id != 0:
                entidad = EntidadesCred.query.get(id)
                entidad.entidad = request.form['entidad']
                entidad.telefono = request.form['telefono']
            else:
                entidad = EntidadesCred(entidad, telefono)
                db.session.add(entidad)
            db.session.commit()
            flash('Entidad crediticia grabada')
            return redirect(url_for('entidades.entidades'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error grabado entidad crediticia: {e}')
            return redirect(url_for('entidades.entidades'))
    
    if request.method == 'GET':
        return render_template('entidades-cred.html', alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    
@bp_entidades.route('/listado_movimientos', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def listado_movimientos():
    entidades = EntidadesCred.query.all()
    if request.method == 'GET':
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        if not desde:
            desde = datetime.now().strftime('%Y-%m-%d')
        if not hasta:
            hasta = datetime.now().strftime('%Y-%m-%d')
        entidad_id = request.args.get('idEntidad')
        if entidad_id != None:
            print(f'Entidades Cred: {entidad_id}')
            movimientos = db.session.query(Factura.id, 
                                        Factura.idcliente,
                                        Factura.nro_comprobante,
                                        Factura.fecha, 
                                        Factura.total, 
                                        Sucursales.nombre.label('sucursal'),
                                        Clientes.nombre.label('cliente'),
                                        PagosFV.total.label('pago_total'), 
                                        EntidadesCred.entidad) \
                                    .join(PagosFV, Factura.id == PagosFV.idfactura) \
                                    .join(EntidadesCred, PagosFV.entidad == EntidadesCred.id) \
                                    .join(Clientes, Factura.idcliente == Clientes.id) \
                                    .join(Sucursales, Factura.idsucursal == Sucursales.id) \
                                    .filter(Factura.fecha >= desde,
                                            Factura.fecha <= hasta,
                                            EntidadesCred.id == entidad_id).all()
        else:
            print(f'Sin Entidades Cred')
            movimientos = []
        return render_template('listado-movimientos.html', desde=desde, hasta=hasta, entidades=entidades, movimientos=movimientos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    else:
        movimientos = []
        desde = request.form.get('desde', '')
        hasta = request.form.get('hasta', '')
        idEntidad = request.form.get('entidad', '')
        return redirect(url_for('entidades.listado_movimientos', desde=desde, hasta=hasta, idEntidad=idEntidad))

@bp_entidades.route('/alicuotas/<int:id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def alicuotas(id):
    if request.method == 'POST':
        resultado =grabarAlicuotas(id, request.form)
        if resultado:
            flash('Alícuotas grabadas correctamente')
        return redirect(url_for('entidades.alicuotas', id=id))
    else:
        entidad, financiamiento = getFinanciamiento(id)
        return render_template('fin-ent-cred.html', entidad=entidad, financiamiento=financiamiento, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
        
@bp_entidades.route('/coeficiente_cuotas/<int:tarjeta>/<int:cuotas>', methods=['GET'])
def coeficiente_cuotas(tarjeta, cuotas):
    if request.method == 'GET':
        return jsonify({'coeficiente': calcular_coeficiente(tarjeta, cuotas)})
