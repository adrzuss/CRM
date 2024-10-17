from flask import Blueprint, render_template, redirect, flash, url_for, jsonify, request
from datetime import date, datetime
from sqlalchemy import func, and_
from models.ventas import Factura, PagosFV
from services.ventas import get_vta_desde_hasta
from models.proveedores import FacturaC, PagosFC
from models.configs import PagosCobros
from services.fondos import obtener_total_ventas_por_tipo_ingreso, obtener_total_compras_por_tipo_ingreso
from utils.db import db
from utils.utils import check_session

bp_fondos = Blueprint('fondos', __name__, template_folder='../templates/fondos')

@bp_fondos.route('/caja', methods=['GET', 'POST'])
@check_session
def caja():
    if request.method == 'GET':
        resultadosVentas = []
        resultadosCompras = []
        fecha = date.today()
        totalVenta = 0
        totalCompra = 0
    if request.method == 'POST':
        fecha = request.form['fecha']
        resultadosVentas = obtener_total_ventas_por_tipo_ingreso(fecha, fecha)
        totalVenta = 0
        for registro in resultadosVentas:
            totalVenta = totalVenta + registro[1]
        resultadosCompras = obtener_total_compras_por_tipo_ingreso(fecha, fecha)
        totalCompra = 0
        for registro in  resultadosCompras:
            totalCompra = totalCompra + registro[1]
        
    return render_template('caja.html', fecha=fecha, resultadosVentas=resultadosVentas, resultadosCompras=resultadosCompras, totalVenta=totalVenta, totalCompra=totalCompra)

@bp_fondos.route('/flujoFondos', methods=['GET', 'POST'])
def flujo_fondos():
    resultadosVentas = []
    resultadosCompras = []
    detalles = []
    montos = []
    totalVenta = 0
    totalCompra = 0
    
    if request.method == 'GET':
        desde = request.args.get('desde', datetime.now().strftime('%Y-%m-01'))  # Por defecto, inicio de mes
        hasta = request.args.get('hasta', datetime.now().strftime('%Y-%m-%d'))   # Por defecto, hoy
        
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        resultadosVentas = obtener_total_ventas_por_tipo_ingreso(desde, hasta)
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
        print(ventas_desde_hasta)    
    
    return render_template('flujo-fondos.html', desde=desde, hasta=hasta, detalles=detalles, montos=montos)