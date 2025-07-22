from flask import session, jsonify
from datetime import date, datetime
from sqlalchemy import func, and_, text
from utils.db import db
from models.sucursales import Sucursales
from models.sessions import Usuarios, Tareas, TareasUsuarios

def autenticar_usuario(usuario, clave, sucursal_id):
    usuario_ok = check_user(usuario, clave)
    if usuario_ok:
        session['id_sucursal'] = int(sucursal_id)
        sucursal = Sucursales.query.get(session['id_sucursal'])
        session['nombre_sucursal'] = sucursal.nombre
        return True
    else:
        return False

def check_user(usr_name, clave_usr):
    usuario = Usuarios.query.filter_by(usuario=usr_name, clave=clave_usr).first()
    if not usuario:
        return False
    else:
        session['user_id'] = usuario.id
        session['user_name'] = usuario.nombre
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
    user = Usuarios.query.get(id)
    user.nombre = nombre
    user.documento = documento
    user.telefono = telefono
    user.email = mail
    user.direccion = direccion
    user.usuario = usuario
    user.clave = clave
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

#-------------- Mensajes ------------------

def get_mensaje(id):
    try:
        from models.sessions import Mensajes
        mensajes = Mensajes.query.get(id)
        if not mensajes:
            return jsonify(success=False, error='Mensaje no encontrado'), 404
        else:
            return mensajes, 200
    except Exception as e:
        print(f'error: {e}')
        return jsonify(success=False, error=str(e)), 404

def save_msg_user(titulo, subtitulo, mensaje, usuarioDestino):
    try:
        from models.sessions import Mensajes
        from datetime import datetime
        
        nuevo_mensaje = Mensajes(
            idsucursal=session['id_sucursal'],
            idusuario=session['user_id'],
            fecha=datetime.now().date(),
            hora=datetime.now().time(),
            tipo='MENSAJE',
            titulo=titulo,
            subtitulo=subtitulo,
            mensaje=mensaje,
            idusr_destino=usuarioDestino
        )
        db.session.add(nuevo_mensaje)
        db.session.commit()
        return {'success':True, 'message':'Mensaje guardado correctamente'}, 200
    except Exception as e:
        print(f'error: {e}')
        return {'success':False, 'error':str(e)}, 404

def save_msg_branch(titulo, subtitulo, mensaje, sucursalDestino):
    try:
        from models.sessions import Mensajes
        from datetime import datetime
        laHora = datetime.now().time().replace(microsecond=0).strftime('%H:%M:%S')
        print(f'laHora: {laHora}')
        nuevo_mensaje = Mensajes(
            idsucursal=session['id_sucursal'],
            idusuario=session['user_id'],
            fecha=datetime.now().date(),
            hora=laHora,
            tipo='MENSAJE',
            titulo=titulo,
            subtitulo=subtitulo,
            mensaje=mensaje,
            idsuc_destino=sucursalDestino
        )
        db.session.add(nuevo_mensaje)
        db.session.commit()
        return {'success':True, 'message':'Mensaje guardado correctamente'}, 200
    except Exception as e:
        print(f'error: {e}')
        return {'success':False, 'error':str(e)}, 404
    
def get_mensajes_mios(id_usuario):
    try:
        from models.sessions import Mensajes
        mensajes = db.session.execute(text("CALL get_mensajes_mios(:idusuario)"), {'idusuario': id_usuario}).fetchall()
        return mensajes, 200
    except Exception as e:
        print(f'error: {e}')
        return jsonify(success=False, error=str(e)), 404    
    
def get_mensajes_para_mi(id_usuario, id_sucursal):
    try:
        from models.sessions import Mensajes
        mensajes = db.session.execute(text("CALL get_mensajes_para_mi(:idusuario, :idsucursal)"), {'idusuario': id_usuario, 'idsucursal': id_sucursal}).fetchall()
        return mensajes, 200
    except Exception as e:
        print(f'error: {e}')
        return jsonify(success=False, error=str(e)), 404    
    
def alerta_mensajes_usuario():
    cantidad = db.session.execute(text("CALL get_cantidad_mensajes_para_mi(:idusuario)"), {'idusuario': session['user_id']}).scalar()
    if cantidad > 0:            
        return cantidad, {'titulo': 'Mensajes de usuario', 'subtitulo': f'Hay {cantidad} mensajes de usuario', 'tipo': 'peligro', 'entidad': 'usuario', 'url': ''}
    else:
        return cantidad, {}
    
def alerta_mensajes_sucursal():
    cantidad = db.session.execute(text("CALL get_cantidad_mensajes_esta_sucursal(:idsucursal)"), {'idsucursal': session['id_sucursal']}).scalar()
    if cantidad > 0:            
        return cantidad, {'titulo': 'Mensajes de sucursal', 'subtitulo': f'Hay {cantidad} mensajes de sucursal', 'tipo': 'peligro', 'entidad': 'sucursal', 'url': ''}
    else:
        return cantidad, {}

def alerta_mensajes_creditos_nuevos():
    cantidad = db.session.execute(text("CALL get_cantidad_mensajes_creditos_nuevos()")).scalar()
    if cantidad > 0:            
        mensaje = f'Hay {cantidad} solicitudes de créditos nuevos' if cantidad > 1 else f'Hay {cantidad} solicitud de crédito nuevo'
        return cantidad, {'titulo': 'Mensajes de créditos nuevos', 'subtitulo': mensaje , 'tipo': 'bien', 'entidad': 'credito', 'url': 'creditos.lst_nuevos'}
    else:
        return cantidad, {}
    
def alerta_mensajes_creditos_pendientes():
    cantidad = db.session.execute(text("CALL get_cantidad_mensajes_creditos_pendientes(:idsucursal)"), {'idsucursal': session['id_sucursal']}).scalar()
    if cantidad > 0:            
        mensaje = f'Hay {cantidad} créditos pendientes de aprobación' if cantidad > 1 else f'Hay {cantidad} crédito pendiente de aprobación'
        return cantidad, {'titulo': 'Mensajes de créditos pendientes', 'subtitulo': mensaje, 'tipo': 'peligro', 'entidad': 'credito', 'url': 'creditos.lst_pendientes'}
    else:
        return cantidad, {}

def alerta_mensajes_creditos_rechazados():
    cantidad = db.session.execute(text("CALL get_cantidad_mensajes_creditos_rechazados(:idsucursal)"), {'idsucursal': session['id_sucursal']}).scalar()
    if cantidad > 0:            
        mensaje = f'Hay {cantidad} créditos rechazados' if cantidad > 1 else f'Hay {cantidad} crédito rechazado'
        return cantidad, {'titulo': 'Mensajes de créditos rechazados', 'subtitulo': mensaje, 'tipo': 'peligro', 'entidad': 'credito', 'url': 'creditos.lst_rechazados'}
    else:
        return cantidad, {}
    
def alerta_mensajes_creditos_aprobados():
    cantidad = db.session.execute(text("CALL get_cantidad_mensajes_creditos_aprobados(:idsucursal)"), {'idsucursal': session['id_sucursal']}).scalar()
    if cantidad > 0:            
        mensaje = f'Hay {cantidad} créditos aprobados' if cantidad > 1 else f'Hay {cantidad} crédito aprobado'
        return cantidad, {'titulo': 'Mensajes de créditos aprobados', 'subtitulo': mensaje, 'tipo': 'exito', 'entidad': 'credito', 'url': 'creditos.lst_aprobados'}
    else:
        return cantidad, {}