from sqlalchemy import func, and_
from utils.utils import format_currency
from models.entidades_cred import EntidadesCred, FinanciacionEntCred
from utils.db import db
from decimal import Decimal

def getFinanciamiento(id):
    entidad = EntidadesCred.query.get(id)
    if not entidad:
        return None, None
    financiamiento = db.session.query(FinanciacionEntCred).filter(FinanciacionEntCred.id_entidad == id).all()
    return entidad, financiamiento

def grabarAlicuotaEntCred(id, cuotas, alicuota, dias):
    try:
        finCuotas = db.session.query(FinanciacionEntCred).filter(FinanciacionEntCred.id_entidad==id, FinanciacionEntCred.cuotas==cuotas).first()
        if finCuotas:
            finCuotas.coeficiente = Decimal(alicuota)
            finCuotas.acreditacion_dias = dias
        else:    
            alc=Decimal(alicuota)
            finCuotas = FinanciacionEntCred(id_entidad=id, cuotas=cuotas, coeficiente=alc, acreditacion_dias=dias)
            db.session.add(finCuotas)
    except Exception as e:
        print(f'Error grabando alícuotas: {e}')
        return False
    return True

def grabarAlicuotas(id, form):
    try:
        FinanciacionEntCred.query.filter(FinanciacionEntCred.id_entidad==id).delete()
        db.session.flush()
        for key, value in form.items():
            if key.startswith('items') and key.endswith('[cuota]'):
                index = key.split('[')[1].split(']')[0]
                cuota = value
                alicuota = form[f'items[{index}][alicuota]']
                dias = form[f'items[{index}][dias]']
                resultado = grabarAlicuotaEntCred(id, cuota, alicuota, dias)
                if resultado == False:
                    raise
        db.session.commit()        
        return True
    except Exception as e:
        db.session.rollback()
        return False
    
def calcular_coeficiente(tarjeta, cuotas):
    print(f"Calculando coeficiente para {tarjeta}, en {cuotas} cuotas")
    coeficiente = db.session.query(FinanciacionEntCred.coeficiente).filter(and_(FinanciacionEntCred.id_entidad==tarjeta, FinanciacionEntCred.cuotas==cuotas)).scalar()
    print(f"Coeficiente: {coeficiente}")
    if coeficiente is None:
        return 1.0
    return coeficiente
    