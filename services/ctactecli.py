from sqlalchemy import func, text
from models.ctactecli import CtaCteCli
from utils.db import db

def saldo_ctacte(idcliente):
    # Consulta SQLAlchemy para sumar los campos "debe" y "haber"
    result = db.session.query(
        func.sum(CtaCteCli.debe).label('total_debe'),
        func.sum(CtaCteCli.haber).label('total_haber')
    ).filter(CtaCteCli.idcliente == idcliente).one()

    # Convertir el resultado a un diccionario
    total_debe = result.total_debe if result.total_debe else 0
    total_haber = result.total_haber if result.total_haber else 0
    # Devolver el resultado como JSON
    return {'total_debe': total_debe, 'total_haber': total_haber}

def get_saldo_clientes():
    try:
        saldos_cta_cte = db.session.execute(text("CALL get_saldos_cc_cli(:empresa)"), {'empresa': 1}).fetchall()
        saldoActual = float(saldos_cta_cte[0][0])
        saldoVencido = float(saldos_cta_cte[0][1])
        return saldoActual, saldoVencido
    except:
        return 0.0, 0.0
    
def ctacte_vencida():
    cantidad = db.session.execute(text("CALL get_clientes_cc_vencidas(:empresa)"), {'empresa': 1}).fetchall()
    if cantidad > 0:            
        return cantidad, {'titulo': 'Ctas ctes vencidas', 'subtitulo': f'Hay {cantidad} de clientes con ctas. ctes. vencidas', 'tipo': 'peligro', 'url': 'articulos.stock_faltantes'}
    else:
        return cantidad, {}