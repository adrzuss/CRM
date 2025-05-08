from utils.db import db
from datetime import date

class Clientes(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(80))
    documento = db.Column(db.String(13))
    email = db.Column(db.String(100))
    telefono  = db.Column(db.String(20))
    direccion = db.Column(db.String(100))
    ctacte = db.Column(db.Boolean(create_constraint=False))
    baja = db.Column(db.Date, nullable=False)
    id_tipo_doc = db.Column(db.Integer, db.ForeignKey('tipo_doc.id'))
    id_tipo_iva = db.Column(db.Integer, db.ForeignKey('tipo_iva.id'))
    """
    tipo_doc = db.relationship('TipoDocumento', back_populates='clientes')
    tipo_iva = db.relationship('TipoIva', back_populates='clientes')
    """
    
    def __init__(self, nombre, documento, email, telefono, direccion, ctacte, id_tipo_doc, id_tipo_iva):
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.ctacte = ctacte
        self.id_tipo_doc = id_tipo_doc
        self.id_tipo_iva = id_tipo_iva
        self.baja = date(1900, 1, 1)