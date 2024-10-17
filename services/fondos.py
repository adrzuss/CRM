from sqlalchemy import func, and_
from models.ventas import Factura, PagosFV
from models.proveedores import FacturaC, PagosFC
from models.configs import PagosCobros
from utils.db import db

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
