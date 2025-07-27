from flask import Blueprint, render_template, request, g, redirect, url_for, flash
from datetime import date, datetime
from sqlalchemy import func, and_
from services.ventas import get_vta_desde_hasta
from models.sessions import Usuarios
from services.fondos import obtener_total_ventas_por_tipo_ingreso, obtener_total_compras_por_tipo_ingreso, get_ventas_compras, \
                            get_detalle_gastos, get_saldo_ctas_ctes_cli, get_saldo_ctas_ctes_prov, get_estado_resultado, \
                            getTiposRendiciones, getRendicion, getMonedasBilletes, procesarRendicion, getRendiciones
from services.sessions import get_usuarios
from services.configs import getPuntosVta, getSucursales    
from utils.db import db
from utils.utils import check_session, format_currency
from utils.msg_alertas import alertas_mensajes

bp_fondos = Blueprint('fondos', __name__, template_folder='../templates/fondos')

@bp_fondos.route('/caja', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def caja():
    if request.method == 'GET':
        resultadosVentas = []
        resultadosCompras = []
        fecha = date.today()
        totalVenta = 0
        totalCompra = 0
    if request.method == 'POST':
        fecha = request.form['fecha']
        usuario = request.form['usuario']
        resultadosVentas = obtener_total_ventas_por_tipo_ingreso(fecha, fecha, usuario)
        totalVenta = 0
        for registro in resultadosVentas:
            totalVenta = totalVenta + registro[1]
        resultadosCompras = obtener_total_compras_por_tipo_ingreso(fecha, fecha, usuario)
        totalCompra = 0
        for registro in  resultadosCompras:
            totalCompra = totalCompra + registro[1]
    usuarios = Usuarios.query.all()        
    return render_template('caja.html', fecha=fecha, resultadosVentas=resultadosVentas, resultadosCompras=resultadosCompras, totalVenta=totalVenta, totalCompra=totalCompra, usuarios=usuarios, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_fondos.route('/flujoFondos', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def flujo_fondos():
    resultadosVentas = []
    resultadosCompras = []
    detalles = []
    montos = []
    detalleGastos = {'valores': [0,0], 'detalle': ['ventas', 'compras']}
    ventasCompras = {'valores': [0,0], 'detalle': ['ventas', 'compras']}
    totalVenta = 0
    totalCompra = 0
    
    detallesCtasCtes = []
    valoresCtasCtes = []
    
    estadoResultado = []
    
    if request.method == 'GET':
        desde = request.args.get('desde', datetime.now().strftime('%Y-%m-01'))  # Por defecto, inicio de mes
        hasta = request.args.get('hasta', datetime.now().strftime('%Y-%m-%d'))   # Por defecto, hoy
        
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        resultadosVentas = obtener_total_ventas_por_tipo_ingreso(desde, hasta, 0)# usuario=0 todos los usuarios
        for registro in resultadosVentas:
            detalles.append('Vtas. ' + registro[0])
            montos.append(registro[1])
            totalVenta = totalVenta + registro[1]
        resultadosCompras = obtener_total_compras_por_tipo_ingreso(desde, hasta)
        for registro in  resultadosCompras:
            detalles.append('Comp. ' + registro[0])
            montos.append(-registro[1])
            totalCompra = totalCompra + registro[1]
        ventas_desde_hasta = get_vta_desde_hasta(desde, hasta)
        ventasCompras = get_ventas_compras(desde, hasta)
        detalleGastos = get_detalle_gastos(desde, hasta)
        saldoCtasCtesCliActual, saldoCtasCtesCliVencido = get_saldo_ctas_ctes_cli()
        saldoCtasCtesProvActual, saldoCtasCtesProvVencido = get_saldo_ctas_ctes_prov()
        
        detallesCtasCtes = ['Ctas. ctes. clientes', 'Ctas. ctes. clientes vencidas', 'Ctas. ctes. proveedores', 'Ctas. ctes. proveedores vencidas']
        valoresCtasCtes = [saldoCtasCtesCliActual, saldoCtasCtesCliVencido, saldoCtasCtesProvActual, saldoCtasCtesProvVencido]

        detalleVentas, detalleCompras = get_estado_resultado(desde, hasta)
        estadoResultado = []
        estadoResultado.append(['Ventas', format_currency(detalleVentas[0][0]), 'Venta'])
        estadoResultado.append(['Iva', format_currency(detalleVentas[0][1]), 'Impuesto'])
        estadoResultado.append(['Exento', format_currency(detalleVentas[0][2]), 'Impuesto'])
        estadoResultado.append(['Imp. Internos', format_currency(detalleVentas[0][3]), 'Impuesto'])
        estadoResultado.append(['Ing. Brutos', format_currency(detalleVentas[0][4]), 'Impuesto'])
        estadoResultado.append(['Costo de mercadería vendida', format_currency(detalleVentas[0][5]), 'Costo de mercadería vendida'])
        
        for compras in detalleCompras:
            estadoResultado.append([compras[1], format_currency(compras[0]), 'Compra/Gasto'])
        
    return render_template('flujo-fondos.html', desde=desde, hasta=hasta, detalles=detalles, montos=montos, valoresVtasCompras=ventasCompras['valores'], detalleVtasCompras=ventasCompras['detalle'], detalleGastosLeyendas=detalleGastos['detalle'], detalleGastosValores=detalleGastos['valores'], detallesCtasCtes=detallesCtasCtes, valoresCtasCtes=valoresCtasCtes, estadoResultado=estadoResultado, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)


@bp_fondos.route('/rendicionCaja/<idRendicion>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def rendicionCaja(idRendicion):
    if request.method == 'POST':
        try:
            idRendicion, mensaje = procesarRendicion(request.form)
            if idRendicion>0:
                flash('Rendición grabada', 'success')
                return redirect(url_for('fondos.rendicionCaja', idRendicion=idRendicion))
            else:
                raise Exception(f'Error grabando rendición: {mensaje}')
        except Exception as e:
            flash(f'Error grabando rendición: {e}', 'error')
            return redirect(url_for('fondos.rendicionCaja', idRendicion=idRendicion))
    else:
        tipos_rendicion = getTiposRendiciones()
        monedas_billetes = getMonedasBilletes()
        sucursales = getSucursales()
        puntosVta = getPuntosVta()
        usuarios, resultado = get_usuarios()
        rendicion, valoresRendidos = getRendicion(idRendicion) 
        
    totalRendido = 0
    return render_template('rend-cajas.html', totalRendido=totalRendido, tipos_rendicion=tipos_rendicion, puntosVta=puntosVta, \
                           usuarios=usuarios, rendicion=rendicion, valoresRendidos=valoresRendidos, monedas_billetes=monedas_billetes, \
                           sucursales=sucursales, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, \
                           cantidadMensajes=g.cantidadMensajes)


@bp_fondos.route('/lst_rendiciones', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def lst_rendiciones():
    if request.method == 'GET':
        desde = request.args.get('desde', date.today())
        hasta = request.args.get('hasta', date.today())
        rendiciones = getRendiciones(desde, hasta)
    else:
        return redirect(url_for('fondos.lst_rendiciones'))
    return render_template('lst-rendiciones.html', rendiciones=rendiciones, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)