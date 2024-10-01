from sqlalchemy import func
from utils.utils import format_currency
from models.ctacteprov import CtaCteProv
from utils.db import db

def saldo_ctacte(idproveedor):
    # Consulta SQLAlchemy para sumar los campos "debe" y "haber"
    result = db.session.query(
        func.sum(CtaCteProv.debe).label('total_debe'),
        func.sum(CtaCteProv.haber).label('total_haber')
    ).filter(CtaCteProv.idproveedor == idproveedor).one()

    # Convertir el resultado a un diccionario
    total_debe = result.total_debe if result.total_debe else 0
    total_haber = result.total_haber if result.total_haber else 0
    # Devolver el resultado como JSON
    return {'total_debe': total_debe, 'total_haber': total_haber}

def get_saldo_proveedores():
    try:
        saldos_cta_cte = db.session.query(func.sum(CtaCteProv.debe).label('debe'), func.sum(CtaCteProv.haber).label('haber')).all()
        saldos = format_currency(saldos_cta_cte[0][0] - saldos_cta_cte[0][1])
        return saldos
    except: 
        return format_currency(0.0)