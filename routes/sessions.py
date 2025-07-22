from flask import Flask, Blueprint, render_template, session, request, url_for, flash, redirect, g
from services.sessions import check_user, new_user, get_usuarios, get_usuario, get_tareas, get_tareas_usuarios, limpiar_tareas, update_tareas_usuario, update_usuario
from models.sucursales import Sucursales
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes
from services.configs import get_sucursales
from services.sessions import save_msg_user, save_msg_branch, get_mensajes_mios, get_mensajes_para_mi, get_mensaje, autenticar_usuario

bp_sesiones = Blueprint('sesion', __name__, template_folder='../templates/sessions', static_folder='../static')

@bp_sesiones.route('/login', methods=['GET', 'POST'])
def login():
    sucursales = Sucursales.query.all()
    if request.method == 'POST':
        usuario = request.form['usuario'] 
        clave = request.form['clave']
        sucursal_id = request.form['sucursal']
        if autenticar_usuario(usuario, clave, sucursal_id):
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario y/o contraseña incorrecta')
            return redirect( url_for('sesion.login'))
    else:    
        return render_template('login.html', sucursales=sucursales)

# Esta ruta es para API login, es para ser usada por aplicaciones mobiles o clientes que necesiten autenticarse
@bp_sesiones.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    usuario = data.get('usuario')
    clave = data.get('clave')
    sucursal_id = data.get('sucursal')
    if autenticar_usuario(usuario, clave, sucursal_id):
        return {'success': True}, 200
    else:
        return {'success': False, 'error': 'Credenciales incorrectas'}, 401

@bp_sesiones.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
    if 'user_name' in session:
        session.pop('user_name', None)    
    session.clear()     
    return redirect(url_for('index'))

@bp_sesiones.route('/usuarios')
@check_session
@alertas_mensajes
def usuarios():
    datos, status_code = get_usuarios()
    if status_code == 200:
        return render_template('usuarios.html', usuarios=datos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    else:
        usuarios = []
        return render_template('usuarios.html', usuarios=usuarios, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_sesiones.route('/registro')
def registro():
    return render_template('register.html')

@bp_sesiones.route('/add-user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        nombre = request.form['nombre']
        documento = request.form['documento']
        telefono = request.form['telefono']
        mail = request.form['mail']
        direccion = request.form['direccion']
        usuario = request.form['usuario']
        clave = request.form['clave']
        clave2 = request.form['clave2']
        if clave == clave2:
            resultado, status_code = new_user(nombre, documento, telefono, mail, direccion, usuario, clave)
            if (status_code == 200):
                datos = resultado.get_json()
                flash(f'Datos de usuario grabados {datos["datos"]["usuario"]}')
                return redirect(url_for('sesion.usuarios'))
            else:
                flash(f'Error grabando datos de usuario: {resultado.error}', 'error')    
        else:
            flash('Las claves no coinciden', 'error')    
    
@bp_sesiones.route('/update_user/<id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def update_user(id):
    if request.method == 'GET':
        usuario, status_code = get_usuario(id)
        tareas = get_tareas()
        
        # Tareas asignadas a este usuario
        tareas_asignadas = get_tareas_usuarios(id)

        if status_code != 200:
            usuario = []    
    elif request.method == 'POST':
        nombre = request.form['nombre']
        documento = request.form['documento']
        telefono = request.form['telefono']
        mail = request.form['mail']
        direccion = request.form['direccion']
        usuario = request.form['usuario']
        clave = request.form['clave']
        
        tareas_seleccionadas = request.form.getlist('tareas')

        # Limpiar las asignaciones actuales del usuario
        limpiar_tareas(id)
        # Asignar las nuevas tareas seleccionadas
        for id_tarea in tareas_seleccionadas:
            update_tareas_usuario(id_tarea, id)
        update_usuario(id, nombre, documento, telefono, mail, direccion, usuario, clave)
        
        flash('Usuario y tareas asignadas correctamente.')
        return redirect(url_for('index'))    
    return render_template('upd-usuario.html', usuario=usuario, tareas=tareas, tareas_asignadas=tareas_asignadas, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_sesiones.route('/centro_mensajes')
@check_session
@alertas_mensajes
def centro_mensajes():
    usuarios = get_usuarios()
    sucursales = get_sucursales()
    mensajesMios = []
    mensajesMios = get_mensajes_mios(session['user_id'])[0]
    mensajesParaMi = []
    mensajesParaMi = get_mensajes_para_mi(session['user_id'], session['id_sucursal'])[0]
    return render_template('centro_mensajes.html', mensajesMios=mensajesMios, mensajesParaMi=mensajesParaMi, usuarios=usuarios[0], sucursales=sucursales, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_sesiones.route('/grabar_mensaje_usuario', methods=['POST'])
@check_session
@alertas_mensajes
def grabar_mensaje_usuario():
    if request.method == 'POST':
        titulo = request.form['tituloUsuario']
        subtitulo = request.form['subtituloUsuario']
        mensaje = request.form['mensajeUsuario']
        usuarioDestino = request.form['usuario']
        # Aquí puedes agregar la lógica para guardar el mensaje en la base de datos
        resultado = save_msg_user(titulo, subtitulo, mensaje, usuarioDestino)
        if resultado[0]['success']==True:
            flash('Mensaje enviado correctamente', 'success')
        else:
            flash(f'Error al enviar el mensaje: {resultado[0]["error"]}', 'error')
        return redirect(url_for('sesion.centro_mensajes'))

@bp_sesiones.route('/grabar_mensaje_sucursal', methods=['POST'])
@check_session
@alertas_mensajes
def grabar_mensaje_sucursal():
    if request.method == 'POST':
        titulo = request.form['tituloSucursal']
        subtitulo = request.form['subtituloSucursal']
        mensaje = request.form['mensajeSucursal']
        sucursalDestino = request.form['sucursal']
        # Aquí puedes agregar la lógica para guardar el mensaje en la base de datos
        resultado = save_msg_branch(titulo, subtitulo, mensaje, sucursalDestino)
        if resultado[0]['success']==True:
            flash('Mensaje enviado correctamente', 'success')
        else:
            flash(f'Error al enviar el mensaje: {resultado[0]["error"]}', 'error')
        return redirect(url_for('sesion.centro_mensajes'))
    
@bp_sesiones.route('/view_mensaje/<id>', methods=['GET'])
@check_session
@alertas_mensajes
def view_mensaje(id):
    mensaje, status_code = get_mensaje(id)
    if status_code == 200:
        return render_template('view_msg.html', mensaje=mensaje, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    else:
        flash(f'Error al obtener el mensaje: {mensaje}', 'error')
        return redirect(url_for('sesion.centro_mensajes'))
