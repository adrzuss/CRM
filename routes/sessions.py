from flask import Flask, Blueprint, render_template, session, request, url_for, flash, redirect, g
from services.sessions import check_user, new_user, get_usuarios, get_usuario, get_tareas, get_tareas_usuarios, limpiar_tareas, update_tareas_usuario, update_usuario
from models.sucursales import Sucursales
from utils.utils import alertas_mensajes, check_session

bp_sesiones = Blueprint('sesion', __name__, template_folder='../templates/sessions', static_folder='../static')

@bp_sesiones.route('/login', methods=['GET', 'POST'])
def login():
    sucursales = Sucursales.query.all()
    if request.method == 'POST':
        usuario = request.form['usuario'] 
        clave = request.form['clave']
        usuario_ok = check_user(usuario, clave)
        if usuario_ok == True:
            session['id_sucursal'] = int(request.form['sucursal'])
            sucursal = Sucursales.query.get(session['id_sucursal'])
            session['nombre_sucursal'] = sucursal.nombre
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario y/o contraseña incorrecta')
            return redirect( url_for('sesion.login'))
    else:    
        return render_template('login.html', sucursales=sucursales)

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
        return render_template('usuarios.html', usuarios=datos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)
    else:
        usuarios = []
        return render_template('usuarios.html', usuarios=usuarios, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

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
    return render_template('upd-usuario.html', usuario=usuario, tareas=tareas, tareas_asignadas=tareas_asignadas, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)