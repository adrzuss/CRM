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