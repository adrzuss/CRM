from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, session
from models.configs import Configuracion, AlcIva, TipoIva, TipoDocumento, AlcIB
from models.sessions import Tareas
from models.articulos import ListasPrecios
from models.sucursales import Sucursales
from services.configs import grabar_configuracion, save_and_update_lista_precios
from utils.db import db
from utils.utils import check_session

bp_configuraciones = Blueprint('configuraciones', __name__, template_folder='../templates/configuracion')

@bp_configuraciones.route('/configuraciones')
@check_session
def configuraciones():
    configuracion = Configuracion.query.get(session['id_empresa'])
    alcIva = AlcIva.query.all()
    listas_precios = ListasPrecios.query.all()
    tipo_ivas = TipoIva.query.all()
    tipo_docs = TipoDocumento.query.all()
    tareas = Tareas.query.all()
    alcIB = AlcIB.query.all()
    return render_template('configuraciones.html', configuracion=configuracion, tipo_ivas=tipo_ivas, tipo_docs=tipo_docs, alicuotas=alcIva, listas_precios=listas_precios, tareas=tareas, ingBtos=alcIB)

"""
@bp_configuraciones.route('/alc_iva')
def alc_iva():
    alcIva = AlcIva.query.all()
    return render_template('alicuotas-iva.html', alicuotas=alcIva)
"""    

@bp_configuraciones.route('/update_config', methods=['POST'])
@check_session
def update_config():
    nombre_propietario = request.form['propietario']
    nombre_fantasia = request.form['fantasia']
    tipo_iva = request.form['tipo_iva']
    telefono = request.form['telefono']
    mail = request.form['mail']
    tipo_doc = request.form['tipo_doc']
    documento = request.form['documento']
    grabar_configuracion(nombre_propietario, nombre_fantasia, tipo_iva, tipo_doc,documento, telefono, mail)
    flash('Datos de configuracion grabados')
    return redirect('configuraciones')

@bp_configuraciones.route('/add_alc_iva', methods=['POST'])
@check_session
def add_alc_iva():
    descripcion = request.form['descripcion']
    alicuota = request.form['alicuota']
    alciva = AlcIva(descripcion, alicuota)
    db.session.add(alciva)
    db.session.commit()
    flash('Alicuota de IVA grabada')
    return redirect('configuraciones')

@bp_configuraciones.route('/add_alc_ib', methods=['POST'])
@check_session
def add_alc_ib():
    descripcion = request.form['descripcionib']
    alicuota = request.form['alicuotaib']
    alcib = AlcIB(descripcion, alicuota)
    db.session.add(alcib)
    db.session.commit()
    flash('Alicuota de Ingreso Bruto grabada')
    return redirect('configuraciones')

@bp_configuraciones.route('/add_lista_precio', methods=['POST'])
@check_session
def add_lista_precio():
    try:
        nombre_lista_precio = request.form['lista_precio']
        markup = request.form['markup']
        save_and_update_lista_precios(nombre_lista_precio, markup)
        
        flash('Lista de precios grabada')
        return redirect('configuraciones')
    except Exception as e:
        flash(f'Error grabando lista de precios: {e}', 'error')
        return redirect('configuraciones')    
    
@bp_configuraciones.route('/add_tarea', methods=['POST'])
@check_session
def add_tarea():
    try:
        nombre_tarea = request.form['tarea']
        tarea = Tareas(nombre_tarea)
        db.session.add(tarea)
        db.session.commit()
        flash('Tarea grabada')
        return redirect('configuraciones')
    except Exception as e:
        flash(f'Error grabando Tareas: {e}', 'error')
        return redirect('configuraciones')    
    
@bp_configuraciones.route('/abm_sucursales', methods=['GET', 'POST'])
@check_session
def abm_sucursales():
    if request.method == 'POST':
        id_sucursal = request.form['id_sucursal']
        nombre_sucursal = request.form['nombre']
        direccion_sucursal = request.form['direccion']
        telefono_sucursal = request.form['telefono']
        email_sucursal = request.form['email']
        if id_sucursal:
            sucursal = Sucursales.query.get(id_sucursal)
            sucursal.nombre = nombre_sucursal
            sucursal.direccion = direccion_sucursal
            sucursal.telefono = telefono_sucursal
            sucursal.email = email_sucursal
            db.session.commit()
            flash('Datos de sucursal actualizados')
        else:
            sucursal = Sucursales(nombre_sucursal, direccion_sucursal, telefono_sucursal, email_sucursal)
            db.session.add(sucursal)
            db.session.commit()
            flash('Datos de sucursal grabados')
    sucursal = None    
    sucursales = Sucursales.query.all()
    return render_template('abm-sucursales.html', sucursal=sucursal, sucursales=sucursales)

@bp_configuraciones.route('/update_sucursal/<int:id>', methods=['GET'])
@check_session
def update_sucursal(id):
    sucursal = Sucursales.query.get(id)
    sucursales = Sucursales.query.all()
    print(sucursal.id)
    return render_template('abm-sucursales.html', sucursales=sucursales, sucursal=sucursal)

@bp_configuraciones.route('/abm-sucursales/<int:id>/delete', methods=['GET', 'POST'])
@check_session
def abm_sucursales_delete(id):
    pass