from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, session, g
from datetime import date
from services.bancos import BancoService, BancoPropioService
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes
import calendar

bp_bancos = Blueprint('bancos', __name__, template_folder='../templates/bancos')

@bp_bancos.route('/bancos', methods=['GET', 'POST'])
@bp_bancos.route('/bancos/<id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def bancos(id=0):
    if request.method == 'POST':
        id = request.form['id']
        nombre = request.form['nombre']
        nroCta = request.form['nroCta']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        mail = request.form['email']
        if id:
            banco = BancoService.actualizar(id, nombre, nroCta, direccion, telefono, mail)
            flash(f'Banco actualizado: {banco.nombre}')
        else:
            banco = BancoService.crear(nombre, nroCta, direccion, telefono, mail)
            flash(f'Banco creado: {banco.nombre}')
        return redirect(url_for('bancos.bancos'))      
    bancosAll = BancoService.obtener_todos()
    if id != 0:
        banco =  BancoService.obtener_por_id(id)
        return render_template('bancos.html', banco=banco, bancos=bancosAll, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    else:
        banco = []
        return render_template('bancos.html', banco=banco, bancos=bancosAll, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
   
@bp_bancos.route('/delete_banco/<id>')
def delete_banco(id):
    banco = BancoService.eliminar(id)
    flash(f'Banco dado de baja: {banco.nombre}')
    return redirect(url_for('bancos.bancos'))


@bp_bancos.route('/listado_movs_bancos', methods=['GET'])
@check_session
@alertas_mensajes
def listado_movs_bancos():
    bancos = BancoService.obtener_todos()
    entidad = request.args.get('entidad')
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    hoy = date.today()
    anio = hoy.year
    mes = hoy.month
    if desde == None:
        desde = date(anio, mes, 1)
    if hasta == None:    
        ultDia = calendar.monthrange(anio, mes)
        hasta = date(anio, mes, ultDia[1])
    if entidad != None and desde != None and hasta != None:
        movimientos = BancoPropioService.obtener_por_banco(entidad, desde, hasta)
    else:
        movimientos = []    
    print(movimientos)    
    return render_template('listado_movs_bancos.html', desde=desde, hasta=hasta, entidad=entidad, bancos=bancos, movimientos=movimientos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)