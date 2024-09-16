from flask import session
from models.configs import Configuracion
from utils.db import db

def grabar_configuracion(nombre_propietario, nombre_fantasia, tipo_iva, telefono, mail):
    configuracion = Configuracion.query.get(session['user_id'])
    if configuracion:
        configuracion.nombre_propietario = nombre_propietario
        configuracion.nombre_fantasia = nombre_fantasia
        configuracion.tipo_iva = tipo_iva
        configuracion.telefono = telefono
        configuracion.mail = mail
        db.session.commit()

def get_owner():
    #session['user_id']
    configuracion = Configuracion.query.get(1)
    print(f'El propietario: {configuracion.nombre_propietario}')
    return configuracion.nombre_propietario