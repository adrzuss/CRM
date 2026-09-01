# -*- coding: utf-8 -*-
"""
Blueprint y rutas para el Dashboard Gerencial Stage 1.
Ruta principal: GET /dashboard-gerencial
API endpoints para HTMX: /api/dashboard-gerencial/{seccion}
"""

from flask import Blueprint, render_template, request, jsonify, session
from datetime import date, timedelta, datetime

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
from services.reportes import get_sucursales_lista
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes

bp_dashboard_gerencial = Blueprint(
    'dashboard_gerencial',
    __name__,
    template_folder='../templates'
)


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


# ─── Ruta principal ──────────────────────────────────────────────────────────
@bp_dashboard_gerencial.route('/dashboard-gerencial')
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


# ─── API endpoints para HTMX ────────────────────────────────────────────────
def _api_respuesta(funcion, *args, **kwargs):
    """Wrapper para endpoints JSON con manejo de errores."""
    try:
        resultado = funcion(*args, **kwargs)
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/kpis')
@check_session
def api_kpis():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_kpis, desde, hasta, id_sucursal)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/evolucion')
@check_session
def api_evolucion():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    granularidad = request.args.get('granularidad', 'auto')
    return _api_respuesta(get_evolucion_ventas, desde, hasta, id_sucursal, comparar, granularidad)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/sucursales')
@check_session
def api_sucursales():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_ventas_sucursal, desde, hasta, id_sucursal)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/rubros')
@check_session
def api_rubros():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_ventas_rubro, desde, hasta, id_sucursal)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/rubro-sucursal')
@check_session
def api_rubro_sucursal():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_rubro_sucursal_comparacion, desde, hasta, id_sucursal)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/top-productos')
@check_session
def api_top_productos():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_top_productos, desde, hasta, id_sucursal, 10)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/top-vendedores')
@check_session
def api_top_vendedores():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_top_vendedores, desde, hasta, id_sucursal, 10)


# ─── API endpoints Stock (Etapa 2) ─────────────────────────────────────────
@bp_dashboard_gerencial.route('/api/dashboard-gerencial/stock-kpis')
@check_session
def api_stock_kpis():
    id_sucursal_str = request.args.get('id_sucursal')
    id_sucursal = int(id_sucursal_str) if id_sucursal_str and id_sucursal_str.isdigit() and int(id_sucursal_str) > 0 else None
    return _api_respuesta(get_stock_kpis, id_sucursal)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/stock-sucursales')
@check_session
def api_stock_sucursales():
    id_sucursal_str = request.args.get('id_sucursal')
    id_sucursal = int(id_sucursal_str) if id_sucursal_str and id_sucursal_str.isdigit() and int(id_sucursal_str) > 0 else None
    return _api_respuesta(get_stock_sucursal, id_sucursal)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/stock-sin-movimiento')
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
@bp_dashboard_gerencial.route('/api/dashboard-gerencial/cta-cobrar-kpis')
@check_session
def api_cta_cobrar_kpis():
    dias_vto_str = request.args.get('dias_vto')
    dias_vto = None
    if dias_vto_str and dias_vto_str.isdigit():
        dias_vto = int(dias_vto_str)
    return _api_respuesta(get_cta_cobrar_kpis, dias_vto)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/cta-cobrar-top')
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


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/cta-pagar-kpis')
@check_session
def api_cta_pagar_kpis():
    dias_vto_str = request.args.get('dias_vto')
    dias_vto = None
    if dias_vto_str and dias_vto_str.isdigit():
        dias_vto = int(dias_vto_str)
    return _api_respuesta(get_cta_pagar_kpis, dias_vto)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/cta-pagar-top')
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
@bp_dashboard_gerencial.route('/api/dashboard-gerencial/creditos-kpis')
@check_session
def api_creditos_kpis():
    id_sucursal_str = request.args.get('id_sucursal')
    id_sucursal = int(id_sucursal_str) if id_sucursal_str and id_sucursal_str.isdigit() and int(id_sucursal_str) > 0 else None
    return _api_respuesta(get_creditos_kpis, id_sucursal)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/creditos-top')
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
@bp_dashboard_gerencial.route('/api/dashboard-gerencial/bancos-kpis')
@check_session
def api_bancos_kpis():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_bancos_kpis, desde, hasta)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/bancos-detalle')
@check_session
def api_bancos_detalle():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_bancos_detalle)


# ─── API endpoints Caja (Etapa 5) ──────────────────────────────────────────
@bp_dashboard_gerencial.route('/api/dashboard-gerencial/caja-kpis')
@check_session
def api_caja_kpis():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    return _api_respuesta(get_caja_kpis, desde, hasta, id_sucursal)


@bp_dashboard_gerencial.route('/api/dashboard-gerencial/caja-rendiciones')
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
@bp_dashboard_gerencial.route('/api/dashboard-gerencial/alertas')
@check_session
def api_alertas():
    desde, hasta, id_sucursal, comparar = _parsear_filtros()
    stock_kpis = get_stock_kpis(id_sucursal)
    creditos_kpis = get_creditos_kpis(id_sucursal)
    cta_cobrar_kpis = get_cta_cobrar_kpis()
    bancos_detalle = get_bancos_detalle()
    alertas = get_alertas_gerenciales(stock_kpis, creditos_kpis, cta_cobrar_kpis, bancos_detalle)
    return jsonify({'success': True, 'data': alertas})
