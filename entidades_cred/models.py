from utils.db import db
from datetime import timedelta, date, datetime

class EntidadesCred(db.Model):
    __tablename__ = 'entidades'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entidad = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(200), nullable=False)
    baja = db.Column(db.Date, nullable=False)
    
    def __init__(self, entidad, telefono):
        self.entidad = entidad
        self.telefono = telefono
        self.baja = datetime(1900, 1, 1)
        
class FinanciacionEntCred(db.Model):
    __tablename__ = 'financiacion_ent'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_entidad = db.Column(db.Integer, db.ForeignKey('entidades.id'), nullable=False)
    cuotas = db.Column(db.Integer, nullable=False)
    coeficiente = db.Column(db.Numeric(20, 6), nullable=False)
    acreditacion_dias = db.Column(db.Integer, nullable=False)

    def __init__(self, id_entidad, cuotas, coeficiente, acreditacion_dias):
        self.id_entidad = id_entidad
        self.cuotas = cuotas
        self.coeficiente = coeficiente
        self.acreditacion_dias = acreditacion_dias
        
class MovEntidades(db.Model):
    __tablename__ = 'mov_entidades'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idfactura = db.Column(db.Integer, db.ForeignKey('facturav.id'), nullable=False)
    identidad = db.Column(db.Integer, db.ForeignKey('entidades.id'), nullable=False)
    cuotas = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Numeric(20, 6), nullable=False)
    intereses = db.Column(db.Numeric(20, 6), nullable=False)
    documento = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)

    def __init__(self, idfactura, identidad, cuotas, total, intereses, documento, telefono):
        self.idfactura = idfactura
        self.identidad = identidad
        self.cuotas = cuotas
        self.total = total
        self.intereses = intereses
        self.documento = documento
        self.telefono = telefono