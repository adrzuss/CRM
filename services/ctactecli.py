from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError
from models.ctactecli import CtaCteCli
from utils.db import db
from services.ventas import procesar_recibo_cta_cte
from decimal import Decimal

def procesar_movimiento_cta_cte(form):
    idcliente = form['idcliente']
    fecha = form['fecha']
    importe = form['importe']
    debe_haber = form.get('debe_haber')
    try:
        if debe_haber == 'debe':
            debe = importe
            haber = Decimal(0)
        else:
            debe = Decimal(0)
            haber = importe
        ctactecli = CtaCteCli(idcliente, fecha, debe, haber)
        db.session.add(ctactecli)
        db.session.flush()
        if debe_haber == 'haber': #Si el haber es mayor a cero, se genera un recibo
            recibo = procesar_recibo_cta_cte(form, ctactecli)
            ctactecli.idcomp = recibo.id
        db.session.commit()
        return ctactecli
    except SQLAlchemyError as e:
        db.session.rollback()
        ctactecli = []
        print(f"Error grabando mov. cta. cte cliente: {e}")
        raise Exception(f"Error grabando mov. cta. cte cliente: {e}")
    except Exception as e:
        db.session.rollback()
        ctactecli = []
        print(f"Error grabando mov. cta. cte cliente: {e}")
        raise Exception(f"Error grabando mov. cta. cte cliente: {e}")
    

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
    cantidad = db.session.execute(text("CALL get_clientes_cc_vencidas(:empresa)"), {'empresa': 1}).scalar()
    if cantidad > 0:            
        return cantidad, {'titulo': 'Ctas ctes vencidas', 'subtitulo': f'Hay {cantidad} de clientes con ctas. ctes. vencidas', 'tipo': 'peligro', 'entidad': 'sistema', 'url': 'ctactecli.lst_cc_cli_vencidas'}
    else:
        return cantidad, {}
   
def get_lst_vencidas():
    try:
        vencidas = db.session.execute(text("CALL lst_clientes_cc_vencidas(:empresa)"), {'empresa': 1}).fetchall()
        return vencidas
    except:
        return []
    
