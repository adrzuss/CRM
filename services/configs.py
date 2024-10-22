from flask import session
from models.configs import Configuracion, TipoComprobantes
from utils.db import db

def grabar_configuracion(nombre_propietario, nombre_fantasia, tipo_iva, telefono, mail):
    configuracion = Configuracion.query.get(session['id_empresa'])
    if configuracion:
        if 'owner' in session:
            session['owner'] = nombre_propietario
        if 'company' in session:
            session['company'] = nombre_fantasia   
        configuracion.nombre_propietario = nombre_propietario
        configuracion.nombre_fantasia = nombre_fantasia
        configuracion.tipo_iva = tipo_iva
        configuracion.telefono = telefono
        configuracion.mail = mail
        db.session.commit()

def get_owner():
    configuracion = Configuracion.query.get(session['id_empresa'])
    print(f'El propietario: {configuracion.nombre_propietario}')
    return configuracion

def get_comprobantes():
    tipo_comprobantes = TipoComprobantes.query.all()
    return tipo_comprobantes