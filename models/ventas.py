from utils.db import db
from models.clientes import Clientes
from models.sucursales import Sucursales

class Factura(db.Model):
    __tablename__ = 'facturav'
    id = db.Column(db.Integer, primary_key=True)
    idcliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    idlista = db.Column(db.Integer, db.ForeignKey('listas_precio.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    total = db.Column(db.Float, nullable=False)
    idtipocomprobante = db.Column(db.Integer, db.ForeignKey('tipo_comprobantes.id'))
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursales.id'))
    cliente = db.relationship('Clientes', backref=db.backref('facturav', lazy=True))
    lista = db.relationship('ListasPrecios', backref=db.backref('listas_precio', lazy=True))
    tipocomprobante = db.relationship('TipoComprobantes', backref=db.backref('tipo_comprobantes', lazy=True))
    sucursal = db.relationship('Sucursales', backref=db.backref('sucursales', lazy=True))
    cliente = db.relationship('Clientes', backref=db.backref('facturav', lazy=True))
    lista = db.relationship('ListasPrecios', backref=db.backref('listas_precio', lazy=True))
    tipocomprobante = db.relationship('TipoComprobantes', backref=db.backref('tipo_comprobantes', lazy=True))
    
    def __init__(self, idcliente, idlista, fecha, id_tipo_comprobante, idsucursal, total=0):
        self.idcliente = idcliente
        self.idlista = idlista
        self.fecha = fecha
        self.total = total
        self.idtipocomprobante = id_tipo_comprobante
        self.idsucursal = idsucursal

class Item(db.Model):
    __tablename__ = 'itemsv'
    idfactura = db.Column(db.Integer, db.ForeignKey('facturav.id'), primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    idarticulo = db.Column(db.Integer, db.ForeignKey('articulos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    precio_total = db.Column(db.Float, nullable=False)
    articulo = db.relationship('Articulo', backref=db.backref('items', lazy=True))
    factura = db.relationship('Factura', backref=db.backref('items', lazy=True))

class PagosFV(db.Model):
    __tablename__ = 'pagos_fv'
    idfactura = db.Column(db.Integer, db.ForeignKey('facturav.id'), primary_key=True)
    idpago = db.Column(db.Integer, primary_key=True)
    tipo  = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    def __init__(self, idfactura, idpago, tipo, total):
        self.idfactura = idfactura
        self.idpago = idpago
        self.tipo = tipo
        self.total = total