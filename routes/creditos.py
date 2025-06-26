from flask import Blueprint, render_template, request, flash, redirect
from flask import g
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes

bp_creditos = Blueprint('creditos', __name__, template_folder='../templates/creditos')

@bp_creditos.route('/planes_cred')
@check_session
@alertas_mensajes
def planes_cred():
    return render_template('planes-cred.html', alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_creditos.route('/otorgamiento')
@check_session
@alertas_mensajes
def otorgamiento():
    return render_template('otorgamiento.html', alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)