from utils.db import db

class Clientes(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80))
    documento = db.Column(db.String(13))
    email = db.Column(db.String(100))
    telefono  = db.Column(db.String(20))
    direccion = db.Column(db.String(100))
    ctacte = db.Column(db.Boolean(create_constraint=False))
    
    def __init__(self, nombre, documento, email, telefono, direccion, ctacte):
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.ctacte = ctacte