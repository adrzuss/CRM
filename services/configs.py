from flask import session, current_app, flash
from sqlalchemy import text, func
from utils.db import db
from models.configs import Configuracion, TipoComprobantes
from models.articulos import ListasPrecios
from utils.db import db
from models.sessions import TareasUsuarios

def grabar_configuracion(nombre_propietario, nombre_fantasia, tipo_iva, tipo_doc, docuemnto, telefono, mail):
    configuracion = Configuracion.query.get(session['id_empresa'])
    if configuracion:
        if 'owner' in session:
            session['owner'] = nombre_propietario
        if 'company' in session:
            session['company'] = nombre_fantasia   
        configuracion.nombre_propietario = nombre_propietario
        configuracion.nombre_fantasia = nombre_fantasia
        configuracion.tipo_iva = tipo_iva
        configuracion.tipo_documento = tipo_doc
        configuracion.documento = docuemnto
        configuracion.telefono = telefono
        configuracion.mail = mail
        db.session.commit()

def getOwner():
    configuracion = Configuracion.query.get(session['id_empresa'])
    return configuracion

def getTareaUsuario():
    min_id_tarea = db.session.query(func.min(TareasUsuarios.idtarea)) \
                       .filter(TareasUsuarios.idusuario == session['user_id']) \
                       .scalar()
    return min_id_tarea

def get_comprobantes():
    tipo_comprobantes = TipoComprobantes.query.all()
    return tipo_comprobantes

def save_and_update_lista_precios(nombre_lista_precio, markup):
    lista_precio = ListasPrecios(nombre_lista_precio, markup)
    db.session.add(lista_precio)
    db.session.commit()
    idlista = lista_precio.id
    try:
        # Ejecuta el procedimiento almacenado llamándolo por nombre con sus parámetros
        with current_app.app_context():
            db.session.execute(text("CALL actualizar_precios_por_lista(:idlista, :markup)"), {'idlista': idlista, 'markup': markup})
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error al ejecutar el procedimiento almacenado: {e}", 'error')
        
        
        
        