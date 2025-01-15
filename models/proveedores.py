from utils.db import db

class Proveedores(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80))
    email = db.Column(db.String(100))
    telefono  = db.Column(db.String(20))
    documento = db.Column(db.String(13))
    id_tipo_doc = db.Column(db.Integer, db.ForeignKey('tipo_doc.id'))
    id_tipo_iva = db.Column(db.Integer, db.ForeignKey('tipo_iva.id'))
    
    def __init__(self, nombre, email, telefono, documento, tipo_doc, tipo_iva):
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.documento = documento
        self.id_tipo_doc = tipo_doc
        self.id_tipo_iva = tipo_iva

class FacturaC(db.Model):
    __tablename__ = 'facturac'
    id = db.Column(db.Integer, primary_key=True)
    idproveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    total = db.Column(db.Numeric(20,6), nullable=False)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursales.id'))
    idtipocomprobante = db.Column(db.Integer, db.ForeignKey('tipo_comprobantes.id'))
    proveedor = db.relationship('Proveedores', backref=db.backref('facturac', lazy=True))
    pagosfc = db.relationship('PagosFC', backref=db.backref('facturac', lazy=True))
    
    def __init__(self, idproveedor, fecha, total, idsucursal, idtipocomprobante):
        self.idproveedor = idproveedor
        self.fecha = fecha
        self.total = total
        self.idsucursal = idsucursal
        self.idtipocomprobante = idtipocomprobante
        
class ItemC(db.Model):
    __tablename__ = 'itemsc'
    idfactura = db.Column(db.Integer, db.ForeignKey('facturac.id'), primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    idarticulo = db.Column(db.Integer, db.ForeignKey('articulos.id'), nullable=False)
    cantidad = db.Column(db.Numeric(20,6), nullable=False)
    precio_unitario = db.Column(db.Numeric(20,6), nullable=False)
    precio_total = db.Column(db.Numeric(20,6), nullable=False)
    articulo = db.relationship('Articulo', backref=db.backref('itemsc', lazy=True))
    factura = db.relationship('FacturaC', backref=db.backref('itemsc', lazy=True))
    
    def __init__(self, idfactura, id, idarticulo, cantidad, precio_unitario, precio_total):
        self.idfactura = idfactura
        self.id = id
        self.idarticulo = idarticulo
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario    
        self.precio_total = precio_total
    
class PagosFC(db.Model):
    __tablename__ = 'pagos_fc'
    idfactura = db.Column(db.Integer, db.ForeignKey('facturac.id'), primary_key=True)
    idpago = db.Column(db.Integer, primary_key=True)
    tipo  = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Numeric(20,6), nullable=False)
    
    def __init__(self, idfactura, idpago, tipo, total):
        self.idfactura = idfactura
        self.idpago = idpago
        self.tipo = tipo
        self.total = total