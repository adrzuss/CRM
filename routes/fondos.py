from flask import Blueprint, render_template, redirect, flash, url_for, jsonify, request
from datetime import date
from sqlalchemy import func, and_
from models.ventas import Factura, PagosFV
from models.proveedores import FacturaC, PagosFC
from models.configs import PagosCobros
from utils.db import db

bp_fondos = Blueprint('fondos', __name__, template_folder='../templates/fondos')

def obtener_total_ventas_por_tipo_ingreso(desde, hasta):
    # Realizamos el JOIN entre las tablas y agrupamos por el tipo de ingreso
    resultados = db.session.query(
        PagosCobros.pagos_cobros.label('tipo_ingreso'),  # Nombre del tipo de ingreso
        func.sum(PagosFV.total).label('total_ingreso')   # Suma de los totales
        ).join(PagosFV, PagosFV.idpago == PagosCobros.id).join(Factura, Factura.id == PagosFV.idfactura).filter(Factura.fecha.between(desde, hasta)).group_by(PagosCobros.pagos_cobros).all()
    return resultados

def obtener_total_compras_por_tipo_ingreso(desde, hasta):
    # Realizamos el JOIN entre las tablas y agrupamos por el tipo de ingreso
    resultados = db.session.query(
        PagosCobros.pagos_cobros.label('tipo_ingreso'),  # Nombre del tipo de ingreso
        func.sum(PagosFC.total).label('total_ingreso')   # Suma de los totales
        ).join(PagosFC, PagosFC.idpago == PagosCobros.id).join(FacturaC, FacturaC.id == PagosFC.idfactura).filter(FacturaC.fecha.between(desde, hasta)).group_by(PagosCobros.pagos_cobros).all()
    return resultados


@bp_fondos.route('/caja', methods=['GET', 'POST'])
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
        desde = date.today()
        hasta = date.today()
        
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
        
    print(f'Ventas: {resultadosVentas}' )
    print(f'detalle: {detalles}' )
    print(f'montos: {montos}' )
    return render_template('flujo-fondos.html', desde=desde, hasta=hasta, detalles=detalles, montos=montos)