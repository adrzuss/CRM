from flask import Blueprint, render_template, request, g
from datetime import date, datetime
from sqlalchemy import func, and_
from services.ventas import get_vta_desde_hasta
from models.sessions import Usuarios
from services.fondos import obtener_total_ventas_por_tipo_ingreso, obtener_total_compras_por_tipo_ingreso, get_ventas_compras, get_detalle_gastos
from utils.db import db
from utils.utils import check_session, alertas_mensajes

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
    return render_template('caja.html', fecha=fecha, resultadosVentas=resultadosVentas, resultadosCompras=resultadosCompras, totalVenta=totalVenta, totalCompra=totalCompra, usuarios=usuarios, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

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
        print('detalleGastos', detalleGastos)
    return render_template('flujo-fondos.html', desde=desde, hasta=hasta, detalles=detalles, montos=montos, valoresVtasCompras=ventasCompras['valores'], detalleVtasCompras=ventasCompras['detalle'], detalleGastosLeyendas=detalleGastos['detalle'], detalleGastosValores=detalleGastos['valores'], alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)