from flask import render_template, Blueprint
from services.ventas import get_vta_hoy, get_vta_semana, ventas_por_mes, pagos_hoy, get_operaciones_hoy, get_operaciones_semana, operaciones_por_mes
from services.articulos import alerta_stocks
from services.ctactecli import get_saldo_clientes
from services.ctacteprov import get_saldo_proveedores
from utils.utils import check_session

bp_tableros = Blueprint('tableros', __name__, template_folder='../templates/tableros')

@bp_tableros.route('/tablero-inicial')
@check_session
def tablero_inicial():
    vta_hoy = get_vta_hoy()
    vta_semana = get_vta_semana()
    vta_6_meses = ventas_por_mes()
    saldo_clientes = get_saldo_clientes()
    saldo_proveedores = get_saldo_proveedores()
    pagosHoy = pagos_hoy()
    alertas = []
    cantidad, mensaje = alerta_stocks()
    if cantidad > 0:
        alertas.append(mensaje)
    alertas.append({'titulo': 'mensaje 2', 'subtitulo': 'aca decimos que pasa2'})
    alertas.append({'titulo': 'mensaje 3', 'subtitulo': 'aca decimos que pasa3'})
    return render_template('tablero.html', tituloTablero='Gerencia', vta_hoy=vta_hoy, vta_semana=vta_semana, saldo_clientes=saldo_clientes, saldo_proveedores=saldo_proveedores, meses=vta_6_meses['meses'], operaciones=vta_6_meses['operaciones'], tipoPagoss=pagosHoy['tipo_pago'], cantPagoss=pagosHoy['total_pago'], alertas=alertas)

@bp_tableros.route('/tablero-administrativo')
@check_session
def tablero_administrativo():
    vta_hoy = get_vta_hoy()
    vta_semana = get_vta_semana()
    vta_6_meses = ventas_por_mes()
    saldo_clientes = get_saldo_clientes()
    saldo_proveedores = get_saldo_proveedores()
    pagosHoy = pagos_hoy()
    alertas = []
    cantidad, mensaje = alerta_stocks()
    if cantidad > 0:
        alertas.append(mensaje)
    alertas.append({'titulo': 'mensaje 2', 'subtitulo': 'aca decimos que pasa2'})
    alertas.append({'titulo': 'mensaje 3', 'subtitulo': 'aca decimos que pasa3'})
    return render_template('tablero.html', tituloTablero='Administración', vta_hoy=vta_hoy, vta_semana=vta_semana, saldo_clientes=saldo_clientes, saldo_proveedores=saldo_proveedores, meses=vta_6_meses['meses'], operaciones=vta_6_meses['operaciones'], tipoPagoss=pagosHoy['tipo_pago'], cantPagoss=pagosHoy['total_pago'], alertas=alertas)

@bp_tableros.route('/tablero-basico')
@check_session
def tablero_basico():
    op_hoy = get_operaciones_hoy()
    op_semana = get_operaciones_semana()
    op_6_meses = operaciones_por_mes()
    #saldo_clientes = get_saldo_clientes()
    #saldo_proveedores = get_saldo_proveedores()
    #pagosHoy = pagos_hoy()
    alertas = []
    cantidad, mensaje = alerta_stocks()
    if cantidad > 0:
            alertas.append(mensaje)
    alertas.append({'titulo': 'mensaje 2', 'subtitulo': 'aca decimos que pasa2'})
    alertas.append({'titulo': 'mensaje 3', 'subtitulo': 'aca decimos que pasa3'})
    return render_template('tablero-basico.html', tituloTablero='Básico', vta_hoy=vta_hoy, vta_semana=vta_semana, saldo_clientes=saldo_clientes, saldo_proveedores=saldo_proveedores, meses=vta_6_meses['meses'], operaciones=vta_6_meses['operaciones'], tipoPagoss=pagosHoy['tipo_pago'], cantPagoss=pagosHoy['total_pago'], alertas=alertas)