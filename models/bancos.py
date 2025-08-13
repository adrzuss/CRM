from utils.db import db
from datetime import date

class Banco(db.Model):
    __tablename__ = 'bancos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    nro_cta = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    baja = db.Column(db.Date, nullable=False)
    
    def __init__(self, nombre, nro_cta, direccion, telefono, email):
        self.nombre = nombre
        self.nro_cta = nro_cta
        self.direccion = direccion
        self.telefono = telefono
        self.email = email  
        self.baja = date(1900, 1, 1)

class TipoMovBancos(db.Model):
    __tablename__ = 'tipo_mov_bancos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    tipo_operacion = db.Column(db.String(1), nullable=False)
    
    def __init__(self, nombre, descripcion, tipo_operacion):
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo_operacion = tipo_operacion
    
    def __init__(self, nombre, descripcion, tipo_operacion):
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo_operacion = tipo_operacion
        
class BancoPropio(db.Model):
    __tablename__ = 'bancos_propios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_emision = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    tipo_movimiento = db.Column(db.Integer, db.ForeignKey('tipo_mov_bancos.id'), nullable=False)
    nro_movimiento = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Numeric(20,6), nullable=False)
    id_banco = db.Column(db.Integer, db.ForeignKey('bancos.id'), nullable=False)
    baja = db.Column(db.Date, nullable=False)
    
    def __init__(self, fecha_emision, fecha_vencimiento, tipo_movimiento, nro_movimiento, monto, id_banco):
        self.fecha_emision = fecha_emision
        self.fecha_vencimiento = fecha_vencimiento
        self.tipo_movimiento = tipo_movimiento
        self.nro_movimiento = nro_movimiento
        self.monto = monto
        self.id_banco = id_banco    
        self.baja = date(1900, 1, 1)
       
class BancoPropioProveedor(db.Model):
    __tablename__ = 'banco_propio_proveedor'
    id_banco_propio = db.Column(db.Integer, db.ForeignKey('bancos_propios.id'), primary_key=True)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id'), primary_key=True)
    
    def __init__(self, id_banco_propio, id_proveedor):
        self.id_banco_propio = id_banco_propio
        self.id_proveedor = id_proveedor
    
    
    