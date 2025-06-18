from utils.db import db

class Proveedores(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(80))
    fantasia = db.Column(db.String(80))
    email = db.Column(db.String(100))
    telefono  = db.Column(db.String(20))
    documento = db.Column(db.String(13))
    direccion = db.Column(db.String(80))
    id_tipo_doc = db.Column(db.Integer, db.ForeignKey('tipo_doc.id'))
    id_tipo_iva = db.Column(db.Integer, db.ForeignKey('tipo_iva.id'))

    def __init__(self, nombre, fantasia, email, telefono, documento, direccion, tipo_doc, tipo_iva):
        self.nombre = nombre
        self.fantasia = fantasia
        self.email = email
        self.telefono = telefono
        self.documento = documento
        self.direccion = direccion
        self.id_tipo_doc = tipo_doc
        self.id_tipo_iva = tipo_iva

class FacturaC(db.Model):
    __tablename__ = 'facturac'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idproveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    periodo = db.Column(db.Date, nullable=False)
    total = db.Column(db.Numeric(20,6), nullable=False)
    iva = db.Column(db.Numeric(20,6), nullable=False)
    exento = db.Column(db.Numeric(20,6), nullable=False)
    impint = db.Column(db.Numeric(20,6), nullable=False)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursales.id'))
    idtipocomprobante = db.Column(db.Integer, db.ForeignKey('tipo_comprobantes.id'))
    idusuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    idplancuenta = db.Column(db.Integer, db.ForeignKey('plan_ctas.id'))
    nro_comprobante = db.Column(db.String(13), nullable=False)
    usuario = db.relationship('Usuarios', backref=db.backref('facturac', lazy=True))
    proveedor = db.relationship('Proveedores', backref=db.backref('facturac', lazy=True))
    pagosfc = db.relationship('PagosFC', backref=db.backref('facturac', lazy=True))
    
    def __init__(self, idproveedor, fecha, periodo, total, nro_comprobante, iva=0, exento=0, impint=0, idsucursal=0, idtipocomprobante=0, idusuario=0, idplancuenta=0):
        self.idproveedor = idproveedor
        self.fecha = fecha
        self.periodo = periodo
        self.total = total
        self.nro_comprobante = nro_comprobante
        self.iva = iva
        self.exento = exento    
        self.impint = impint
        self.idsucursal = idsucursal
        self.idtipocomprobante = idtipocomprobante
        self.idusuario = idusuario
        self.idplancuenta = idplancuenta
        
class ItemC(db.Model):
    __tablename__ = 'itemsc'
    idfactura = db.Column(db.Integer, db.ForeignKey('facturac.id'), primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    idarticulo = db.Column(db.Integer, db.ForeignKey('articulos.id'), nullable=False)
    cantidad = db.Column(db.Numeric(20,6), nullable=False)
    precio_unitario = db.Column(db.Numeric(20,6), nullable=False)
    precio_total = db.Column(db.Numeric(20,6), nullable=False)
    iva = db.Column(db.Numeric(20,6), nullable=False)
    idalciva = db.Column(db.Integer, db.ForeignKey('alc_iva.id'), nullable=False)   
    exento = db.Column(db.Numeric(20,6), nullable=False)
    impint = db.Column(db.Numeric(20,6), nullable=False)
    articulo = db.relationship('Articulo', backref=db.backref('itemsc', lazy=True))
    factura = db.relationship('FacturaC', backref=db.backref('itemsc', lazy=True))
    
    def __init__(self, idfactura, id, idarticulo, cantidad, precio_unitario, precio_total, iva=0, idalciva=0, exento=0, impint=0):
        self.idfactura = idfactura
        self.id = id
        self.idarticulo = idarticulo
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario    
        self.precio_total = precio_total
        self.iva = iva
        self.idalciva = idalciva
        self.exento = exento
        self.impint = impint
    
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

class RemitoFacturas(db.Model):
    __tablename__ = 'remito_facturas'
    idremito = db.Column(db.Integer, db.ForeignKey('facturac.id'), primary_key=True)
    idfactura = db.Column(db.Integer, db.ForeignKey('facturac.id'), primary_key=True)
    
    
    def __init__(self, idremito, idfactura):
        self.idremito = idremito
        self.idfactura = idfactura