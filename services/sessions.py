from flask import session, jsonify
from datetime import date, datetime
from sqlalchemy import func, and_
from utils.db import db
from models.sessions import Usuarios, Tareas, TareasUsuarios

def check_user(usr_name, clave_usr):
    usuario = Usuarios.query.filter_by(usuario=usr_name, clave=clave_usr).first()
    print(f'el usuario {usuario}')
    if not usuario:
        return False
    else:
        session['user_id'] = usuario.id
        return True
        
    
def get_usuarios():
    try:
        usuarios = Usuarios.query.all()
        return usuarios, 200
    except Exception as e:
        print(f'error: {e}')
        return jsonify(success=False, error=str(e)), 404        

def get_usuario(id):
    try:
        usuario = Usuarios.query.get_or_404(id)
        return usuario, 200
    except Exception as e:
        print(f'error: {e}')
        return jsonify(success=False, error=str(e)), 404        
    
def new_user(nombre, documento, telefono, mail, direccion, usuario, clave):
    try:
        usuario = Usuarios(nombre, usuario, clave, documento, mail, telefono, direccion)
        db.session.add(usuario)
        db.session.commit()
        return jsonify(success=True, datos={"usuario": usuario.id, "nombre": usuario.nombre}), 200
    except Exception as e:
        print(f'error: {e}')
        return jsonify(success=False, error=str(e)), 404    
   
def update_usuario(id, nombre, documento, telefono, mail, direccion, usuario, clave):
    usuario = Usuarios.query.get(id)
    usuario.nombre = nombre
    usuario.documento = documento
    usuario.telefono = telefono
    usuario.mail = mail
    usuario.direccion = direccion
    usuario.usuario = usuario
    usuario.clave = clave
    db.session.commit()
    
   
#-------------- Tareas ------------------
def get_tareas():
    return Tareas.query.all()

def get_tareas_usuarios(id):
    return {tu.idtarea for tu in TareasUsuarios.query.filter_by(idusuario=id).all()}

def limpiar_tareas(id):
    TareasUsuarios.query.filter_by(idusuario=id).delete()
    
def update_tareas_usuario(id_tarea, id_usuario):
    nueva_tarea = TareasUsuarios(idtarea=id_tarea, idusuario=id_usuario)
    db.session.add(nueva_tarea)

        