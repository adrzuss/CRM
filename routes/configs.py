from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, session
from models.configs import Configuracion, AlcIva, TipoIva, TipoDocumento
from models.sessions import Tareas
from models.articulos import ListasPrecios
from services.configs import grabar_configuracion
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
    return render_template('configuraciones.html', configuracion=configuracion, tipo_ivas=tipo_ivas, tipo_docs=tipo_docs, alicuotas=alcIva, listas_precios=listas_precios, tareas=tareas)

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
    tipo_iva = request.form['iva']
    telefono = request.form['telefono']
    mail = request.form['mail']
    grabar_configuracion(nombre_propietario, nombre_fantasia, tipo_iva, telefono, mail)
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

@bp_configuraciones.route('/add_lista_precio', methods=['POST'])
@check_session
def add_lista_precio():
    try:
        nombre_lista_precio = request.form['lista_precio']
        markup = request.form['markup']
        lista_precio = ListasPrecios(nombre_lista_precio, markup)
        db.session.add(lista_precio)
        db.session.commit()
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