from utils.db import db
from datetime import timedelta  

class Sucursales(db.Model):
    __tablename__ = 'sucursales'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    alta = db.Column(db.DateTime, nullable=False, default=db.func.now())
    baja = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Sucursales %r>' % self.nombre
    
    def __init__(self, nombre, direccion, telefono, email):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email  
        self.baja = timedelta(0)