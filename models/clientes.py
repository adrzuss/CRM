from utils.db import db
from datetime import date

class Clientes(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(80), nullable=False)
    documento = db.Column(db.String(13), nullable=False)
    email = db.Column(db.String(100))
    telefono  = db.Column(db.String(20))
    direccion = db.Column(db.String(100), nullable=False)
    idlocalidad = db.Column(db.Integer, db.ForeignKey('localidades.id'), nullable=False)
    idprovincia = db.Column(db.Integer, db.ForeignKey('provincias.id'), nullable=False)
    ctacte = db.Column(db.Boolean, nullable=False, default=False)
    idcategoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    id_tipo_doc = db.Column(db.Integer, db.ForeignKey('tipo_doc.id'), nullable=False)
    id_tipo_iva = db.Column(db.Integer, db.ForeignKey('tipo_iva.id'), nullable=False)
    baja = db.Column(db.Date, nullable=False)
    
    def __init__(self, nombre, documento, email, categoria, telefono, direccion, idlocalidad, idprovincia, ctacte, id_tipo_doc, id_tipo_iva):
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.idcategoria = categoria
        self.telefono = telefono
        self.direccion = direccion
        self.idlocalidad = idlocalidad
        self.idprovincia = idprovincia
        self.ctacte = ctacte
        self.id_tipo_doc = id_tipo_doc
        self.id_tipo_iva = id_tipo_iva
        self.baja = date(1900, 1, 1)
    """
    tipo_doc = db.relationship('TipoDocumento', back_populates='clientes')
    tipo_iva = db.relationship('TipoIva', back_populates='clientes')
    """
    
    def __init__(self, nombre, documento, email, categoria, telefono, direccion, localidad, provincia, ctacte, id_tipo_doc, id_tipo_iva):
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.idcategoria = categoria
        self.telefono = telefono
        self.direccion = direccion
        self.localidad = localidad
        self.provincia = provincia
        self.ctacte = ctacte
        self.id_tipo_doc = id_tipo_doc
        self.id_tipo_iva = id_tipo_iva
        self.baja = date(1900, 1, 1)