from flask import render_template, request, Blueprint
from flask import g, jsonify, session
from datetime import date, timedelta, datetime
from services.ventas import get_vta_hoy, get_vta_semana, ventas_por_mes, pagos_hoy, get_operaciones_hoy, get_operaciones_semana, get_ultimas_operaciones, get_10_mas_vendidos, \
                            get_op_este_mes, get_op_este_mes_anterior, get_vta_sucursales_data, get_vta_vendedores_data, get_vta_rubros
from services.reportes import get_datos_reporte_gerencial, get_sucursales_lista
from services.articulos import get_stocks_negativos, get_stocks_faltantes
from services.ctactecli import get_saldo_clientes
from services.ctacteprov import get_saldo_proveedores
from services.creditos import get_datos_creditos
from services.dashboard_gerencial import (
    get_datos_dashboard,
    get_kpis,
    get_evolucion_ventas,
    get_ventas_sucursal,
    get_ventas_rubro,
    get_rubro_sucursal_comparacion,
    get_top_productos,
    get_top_vendedores,
    get_stock_kpis,
    get_stock_sucursal,
    get_productos_sin_movimiento,
    get_cta_cobrar_kpis,
    get_cta_cobrar_top,
    get_cta_pagar_kpis,
    get_cta_pagar_top,
    get_creditos_kpis,
    get_creditos_top_deudores,
    get_bancos_kpis,
    get_bancos_detalle,
    get_caja_kpis,
    get_caja_rendiciones_recientes,
    get_alertas_gerenciales,
)
from utils.utils import check_session, format_currency
from utils.msg_alertas import alertas_mensajes

bp_tableros = Blueprint('tableros', __name__, template_folder='../templates/tableros')


# ─── Helpers Dashboard Gerencial ──────────────────────────────────────────────

def _parsear_filtros():
    """Parsea los parámetros de filtro desde el request."""
    desde_str = request.args.get('desde')
    hasta_str = request.args.get('hasta')
    id_sucursal_str = request.args.get('id_sucursal')
    comparar_str = request.args.get('comparar', '0')

    # Fechas: default últimos 30 días, max 90
    if desde_str:
        try:
            desde = datetime.strptime(desde_str, '%Y-%m-%d').date()
        except ValueError:
            desde = date.today() - timedelta(days=30)
    else:
        desde = date.today() - timedelta(days=30)

    if hasta_str:
        try:
            hasta = datetime.strptime(hasta_str, '%Y-%m-%d').date()
        except ValueError:
            hasta = date.today()
    else:
        hasta = date.today()

    # Limitar a 90 días máximo
    if (hasta - desde).days > 90:
        desde = hasta - timedelta(days=90)

    # Sucursal
    id_sucursal = None
    if id_sucursal_str and id_sucursal_str.isdigit() and int(id_sucursal_str) > 0:
        id_sucursal = int(id_sucursal_str)

    comparar = comparar_str == '1'

    return desde, hasta, id_sucursal, comparar


def _api_respuesta(funcion, *args, **kwargs):
    """Wrapper para endpoints JSON con manejo de errores."""
    try:
        resultado = funcion(*args, **kwargs)
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ─── Rutas Tableros (originales) ─────────────────────────────────────────────

@bp_tableros.route('/tablero-inicial')
@check_session
@alertas_mensajes
def tablero_inicial():
    # fechas hoy y 6 meses atrás
    fecha_hoy = date.today()
    fecha_inicio = fecha_hoy - timedelta(days=180)
    
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
    saldo_clientes_actual, saldo_clientes_vencido = get_saldo_clientes()
    saldo_proveedores = get_saldo_proveedores()
    pagosHoy = pagos_hoy()
    vta_rubros = get_vta_rubros(fecha_inicio, fecha_hoy)
    ventasSucursales = get_vta_sucursales_data(desde_sucs, hasta_sucs)
    ventasVendedores = get_vta_vendedores_data(desde_vend, hasta_vend)
    datos_creditos = get_datos_creditos()
    return render_template('tablero.html', tituloTablero='Gerencia', desde_sucs=desde_sucs, hasta_sucs=hasta_sucs, desde_vend=desde_vend, \
                           hasta_vend=hasta_vend, vta_hoy=vta_hoy, vta_semana=vta_semana, saldo_clientes_actual=format_currency(saldo_clientes_actual), \
                           saldo_clientes_vencido=format_currency(saldo_clientes_vencido), saldo_proveedores=saldo_proveedores, \
                           meses=vta_6_meses['meses'], operaciones=vta_6_meses['operaciones'], tipoPagoss=pagosHoy['tipo_pago'], \
                           cantPagoss=pagosHoy['total_pago'], rubros=vta_rubros['rubros'], vtaRubros=vta_rubros['vtaRubros'], cantRubros=vta_rubros['cantRubros'], \
                            ventasSucursales=ventasSucursales, ventasVendedores=ventasVendedores, datos_creditos=datos_creditos)


@bp_tableros.route('/tablero-gerencial')
@check_session
@alertas_mensajes
def tablero_gerencial():
    # Obtener parámetros de fecha del request
    
    desde_str = request.args.get('desde')
    hasta_str = request.args.get('hasta')
    
    # Si no hay fechas, usar último mes como default
    if desde_str:
        try:
            desde = datetime.strptime(desde_str, '%Y-%m-%d').date()
        except ValueError:
            desde = date.today() - timedelta(days=30)
    else:
        desde = date.today() - timedelta(days=30)
    
    if hasta_str:
        try:
            hasta = datetime.strptime(hasta_str, '%Y-%m-%d').date()
        except ValueError:
            hasta = date.today()
    else:
        hasta = date.today()
    
    # Obtener datos del reporte
    data = get_datos_reporte_gerencial(desde, hasta)
    
    return render_template('reportes/reporte-gerencial.html',
                           desde=desde.strftime('%Y-%m-%d'),
                           hasta=hasta.strftime('%Y-%m-%d'),
                           data=data)    

@bp_tableros.route('/tablero-administrativo')
@check_session
@alertas_mensajes
def tablero_administrativo():
    desde = request.args.get('desde_sucs')
    if desde == None:
        desde = date.today()
    hasta = request.args.get('hasta_sucs')
    if hasta == None:
        hasta= date.today()
    
    vta_hoy = get_vta_hoy()
    vta_semana = get_vta_semana()
    vta_6_meses = ventas_por_mes()
    saldo_clientes = get_saldo_clientes()
    saldo_proveedores = get_saldo_proveedores()
    pagosHoy = pagos_hoy()
    return render_template('tablero.html', tituloTablero='Administración', desde=desde, hasta=hasta, vta_hoy=vta_hoy, vta_semana=vta_semana, saldo_clientes=saldo_clientes, saldo_proveedores=saldo_proveedores, meses=vta_6_meses['meses'], operaciones=vta_6_meses['operaciones'], tipoPagoss=pagosHoy['tipo_pago'], cantPagoss=pagosHoy['total_pago'], alertas=g.alertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)  

@bp_tableros.route('/tablero-basico')
@check_session
@alertas_mensajes
def tablero_basico():
    op_hoy = get_operaciones_hoy()
    op_semana = get_operaciones_semana()
    op_este_mes = get_op_este_mes()
    op_mes_anterior = get_op_este_mes_anterior()
    los_10_mas_vendidos = get_10_mas_vendidos()
    ultimas_op = get_ultimas_operaciones()
    stock_negativos = get_stocks_negativos()
    stock_faltantes = get_stocks_faltantes()
    return render_template('tablero-basico.html', tituloTablero='Básico', op_hoy=op_hoy, op_semana=op_semana, op_este_mes=op_este_mes, detalles=los_10_mas_vendidos['det_arts'], cantidades=los_10_mas_vendidos['vta_arts'], ultimas_op=ultimas_op, stock_negativos=stock_negativos, stock_faltantes=stock_faltantes)

@bp_tableros.route('/plan-vencido')
@check_session
@alertas_mensajes
def plan_vencido():
    return render_template('plan-vencido.html')


# ─── Dashboard Gerencial — Ruta principal ─────────────────────────────────────

@bp_tableros.route('/dashboard-gerencial')
@check_session
@alertas_mensajes
def dashboard_gerencial():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()

    data = get_datos_dashboard(desde, hasta, id_sucursal, comparar)
    sucursales = get_sucursales_lista()
    return render_template(
        'dashboard-gerencial.html',
        data=data,
        sucursales=sucursales,
        desde=desde.strftime('%Y-%m-%d'),
        hasta=hasta.strftime('%Y-%m-%d'),
        id_sucursal=id_sucursal or '',
        comparar=comparar,
    )


# ─── Dashboard Gerencial — API endpoints HTMX ────────────────────────────────

@bp_tableros.route('/api/dashboard-gerencial/kpis')
@check_session
def api_kpis():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_kpis, desde, hasta, id_sucursal)


@bp_tableros.route('/api/dashboard-gerencial/evolucion')
@check_session
def api_evolucion():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    granularidad = request.args.get('granularidad', 'auto')
    return _api_respuesta(get_evolucion_ventas, desde, hasta, id_sucursal, comparar, granularidad)


@bp_tableros.route('/api/dashboard-gerencial/sucursales')
@check_session
def api_sucursales():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_ventas_sucursal, desde, hasta, id_sucursal)


@bp_tableros.route('/api/dashboard-gerencial/rubros')
@check_session
def api_rubros():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_ventas_rubro, desde, hasta, id_sucursal)


@bp_tableros.route('/api/dashboard-gerencial/rubro-sucursal')
@check_session
def api_rubro_sucursal():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_rubro_sucursal_comparacion, desde, hasta, id_sucursal)


@bp_tableros.route('/api/dashboard-gerencial/top-productos')
@check_session
def api_top_productos():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_top_productos, desde, hasta, id_sucursal, 10)


@bp_tableros.route('/api/dashboard-gerencial/top-vendedores')
@check_session
def api_top_vendedores():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_top_vendedores, desde, hasta, id_sucursal, 10)


# ─── API endpoints Stock (Etapa 2) ─────────────────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/stock-kpis')
@check_session
def api_stock_kpis():
    id_sucursal_str = request.args.get('id_sucursal')
    id_sucursal = int(id_sucursal_str) if id_sucursal_str and id_sucursal_str.isdigit() and int(id_sucursal_str) > 0 else None
    return _api_respuesta(get_stock_kpis, id_sucursal)


@bp_tableros.route('/api/dashboard-gerencial/stock-sucursales')
@check_session
def api_stock_sucursales():
    id_sucursal_str = request.args.get('id_sucursal')
    id_sucursal = int(id_sucursal_str) if id_sucursal_str and id_sucursal_str.isdigit() and int(id_sucursal_str) > 0 else None
    return _api_respuesta(get_stock_sucursal, id_sucursal)


@bp_tableros.route('/api/dashboard-gerencial/stock-sin-movimiento')
@check_session
def api_stock_sin_movimiento():
    id_sucursal_str = request.args.get('id_sucursal')
    id_sucursal = int(id_sucursal_str) if id_sucursal_str and id_sucursal_str.isdigit() and int(id_sucursal_str) > 0 else None
    dias_str = request.args.get('dias', '30')
    try:
        dias = int(dias_str)
        if dias not in (30, 60, 90):
            dias = 30
    except (ValueError, TypeError):
        dias = 30
    return _api_respuesta(get_productos_sin_movimiento, id_sucursal, dias)


# ─── API endpoints Cuentas por Cobrar / Pagar (Etapa 3) ────────────────────
@bp_tableros.route('/api/dashboard-gerencial/cta-cobrar-kpis')
@check_session
def api_cta_cobrar_kpis():
    dias_vto_str = request.args.get('dias_vto')
    dias_vto = None
    if dias_vto_str and dias_vto_str.isdigit():
        dias_vto = int(dias_vto_str)
    return _api_respuesta(get_cta_cobrar_kpis, dias_vto)


@bp_tableros.route('/api/dashboard-gerencial/cta-cobrar-top')
@check_session
def api_cta_cobrar_top():
    limite_str = request.args.get('limite', '10')
    dias_vto_str = request.args.get('dias_vto')
    try:
        limite = int(limite_str)
    except (ValueError, TypeError):
        limite = 10
    dias_vto = None
    if dias_vto_str and dias_vto_str.isdigit():
        dias_vto = int(dias_vto_str)
    return _api_respuesta(get_cta_cobrar_top, limite, dias_vto)


@bp_tableros.route('/api/dashboard-gerencial/cta-pagar-kpis')
@check_session
def api_cta_pagar_kpis():
    dias_vto_str = request.args.get('dias_vto')
    dias_vto = None
    if dias_vto_str and dias_vto_str.isdigit():
        dias_vto = int(dias_vto_str)
    return _api_respuesta(get_cta_pagar_kpis, dias_vto)


@bp_tableros.route('/api/dashboard-gerencial/cta-pagar-top')
@check_session
def api_cta_pagar_top():
    limite_str = request.args.get('limite', '10')
    dias_vto_str = request.args.get('dias_vto')
    try:
        limite = int(limite_str)
    except (ValueError, TypeError):
        limite = 10
    dias_vto = None
    if dias_vto_str and dias_vto_str.isdigit():
        dias_vto = int(dias_vto_str)
    return _api_respuesta(get_cta_pagar_top, limite, dias_vto)


# ─── API endpoints Créditos (Etapa 4) ──────────────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/creditos-kpis')
@check_session
def api_creditos_kpis():
    id_sucursal_str = request.args.get('id_sucursal')
    id_sucursal = int(id_sucursal_str) if id_sucursal_str and id_sucursal_str.isdigit() and int(id_sucursal_str) > 0 else None
    return _api_respuesta(get_creditos_kpis, id_sucursal)


@bp_tableros.route('/api/dashboard-gerencial/creditos-top')
@check_session
def api_creditos_top():
    limite_str = request.args.get('limite', '10')
    id_sucursal_str = request.args.get('id_sucursal')
    try:
        limite = int(limite_str)
    except (ValueError, TypeError):
        limite = 10
    id_sucursal = int(id_sucursal_str) if id_sucursal_str and id_sucursal_str.isdigit() and int(id_sucursal_str) > 0 else None
    return _api_respuesta(get_creditos_top_deudores, limite, id_sucursal)


# ─── API endpoints Bancos (Etapa 5) ────────────────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/bancos-kpis')
@check_session
def api_bancos_kpis():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_bancos_kpis, desde, hasta)


@bp_tableros.route('/api/dashboard-gerencial/bancos-detalle')
@check_session
def api_bancos_detalle():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_bancos_detalle)


# ─── API endpoints Caja (Etapa 5) ──────────────────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/caja-kpis')
@check_session
def api_caja_kpis():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_caja_kpis, desde, hasta, id_sucursal)


@bp_tableros.route('/api/dashboard-gerencial/caja-rendiciones')
@check_session
def api_caja_rendiciones():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    limite_str = request.args.get('limite', '10')
    try:
        limite = int(limite_str)
    except (ValueError, TypeError):
        limite = 10
    return _api_respuesta(get_caja_rendiciones_recientes, desde, hasta, id_sucursal, limite)


# ─── API endpoint Alertas Gerenciales (Etapa 6) ────────────────────────────
@bp_tableros.route('/api/dashboard-gerencial/alertas')
@check_session
def api_alertas():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    stock_kpis = get_stock_kpis(id_sucursal)
    creditos_kpis = get_creditos_kpis(id_sucursal)
    cta_cobrar_kpis = get_cta_cobrar_kpis()
    bancos_detalle = get_bancos_detalle()
    alertas = get_alertas_gerenciales(stock_kpis, creditos_kpis, cta_cobrar_kpis, bancos_detalle)
    return jsonify({'success': True, 'data': alertas})
