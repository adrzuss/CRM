from flask import render_template, request, Blueprint
from datetime import date
from services.ventas import get_vta_hoy, get_vta_semana, ventas_por_mes, pagos_hoy, get_operaciones_hoy, get_operaciones_semana, get_ultimas_operaciones, get_10_mas_vendidos, \
                            get_op_este_mes, get_op_este_mes_anterior
from services.articulos import alerta_stocks
from services.ctactecli import get_saldo_clientes
from services.ctacteprov import get_saldo_proveedores
from utils.utils import check_session

bp_tableros = Blueprint('tableros', __name__, template_folder='../templates/tableros')

@bp_tableros.route('/tablero-inicial')
@check_session
def tablero_inicial():
    desde_sucs = request.args.get('desde_sucs')
    if desde_sucs == None:
        desde_sucs = date.today()
    hasta_sucs = request.args.get('hasta_sucs')
    if hasta_sucs == None:
        hasta_sucs = date.today()
    desde_vend = request.args.get('desde_vend')
    if desde_vend == None:
        desde_vend = date.today()
    hasta_vend = request.args.get('hasta_vend')
    if hasta_vend == None:
        hasta_vend = date.today()    
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
    return render_template('tablero.html', tituloTablero='Gerencia', desde_sucs=desde_sucs, hasta_sucs=hasta_sucs, desde_vend=desde_vend, hasta_vend=hasta_vend, vta_hoy=vta_hoy, vta_semana=vta_semana, saldo_clientes=saldo_clientes, saldo_proveedores=saldo_proveedores, meses=vta_6_meses['meses'], operaciones=vta_6_meses['operaciones'], tipoPagoss=pagosHoy['tipo_pago'], cantPagoss=pagosHoy['total_pago'], alertas=alertas)    

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
    return render_template('tablero.html', tituloTablero='Administración', desde=desde, hasta=hasta, vta_hoy=vta_hoy, vta_semana=vta_semana, saldo_clientes=saldo_clientes, saldo_proveedores=saldo_proveedores, meses=vta_6_meses['meses'], operaciones=vta_6_meses['operaciones'], tipoPagoss=pagosHoy['tipo_pago'], cantPagoss=pagosHoy['total_pago'], alertas=alertas)  

@bp_tableros.route('/tablero-basico')
@check_session
def tablero_basico():
    op_hoy = get_operaciones_hoy()
    op_semana = get_operaciones_semana()
    op_este_mes = get_op_este_mes()
    op_mes_anterior = get_op_este_mes_anterior()
    los_10_mas_vendidos = get_10_mas_vendidos()
    ultimas_op = get_ultimas_operaciones()
    
    alertas = []
    cantidad, mensaje = alerta_stocks()
    if cantidad > 0:
        alertas.append(mensaje)
    alertas.append({'titulo': 'mensaje 2', 'subtitulo': 'aca decimos que pasa2'})
    alertas.append({'titulo': 'mensaje 3', 'subtitulo': 'aca decimos que pasa3'})
    
    return render_template('tablero-basico.html', tituloTablero='Básico', op_hoy=op_hoy, op_semana=op_semana, op_este_mes=op_este_mes, detalles=los_10_mas_vendidos['det_arts'], cantidades=los_10_mas_vendidos['vta_arts'], ultimas_op=ultimas_op, alertas=alertas)