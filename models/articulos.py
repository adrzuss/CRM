from utils.db import db

class Articulo(db.Model):
    __tablename__ = 'articulos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False)
    detalle = db.Column(db.String(200), nullable=False)
    costo = db.Column(db.Float, nullable=False)
    idiva = db.Column(db.Integer, db.ForeignKey('alc_iva.id'))
    idmarca = db.Column(db.Integer, db.ForeignKey('marcas.id'))
    idrubro = db.Column(db.Integer, db.ForeignKey('rubros.id'))
    idtipoarticulo = db.Column(db.Integer, db.ForeignKey('tipo_articulos.id'))
    imagen = db.Column(db.String(255))
    es_compuesto = db.Column(db.Boolean, nullable=False)
    iva = db.relationship('AlcIva', back_populates='articulos')
    marca = db.relationship('Marca', back_populates='articulos')
    rubro = db.relationship('Rubro', back_populates='articulos')
    precios = db.relationship('Precio', backref='articulo', lazy=True)
    #tipoarticulo = db.relationship('TipoArticulos', back_populates='articulos', lazy=True)
    #stock = db.relationship('Stock', back_populates='idarticulo')
    
    def __init__(self, codigo, detalle, costo, idiva, idmarca, idrubro, idtipoarticulo, imagen, es_compuesto):
        self.codigo = codigo
        self.detalle = detalle
        self.costo = costo
        self.idiva = idiva
        self.idmarca = idmarca
        self.idrubro = idrubro
        self.idtipoarticulo = idtipoarticulo
        self.imagen = imagen
        self.es_compuesto = es_compuesto

class ArticuloCompuesto(db.Model):    
    __tablename__ = 'art_compuesto'
    idarticulo = db.Column(db.Integer, db.ForeignKey('articulos.id'), primary_key=True)
    idart_comp = db.Column(db.Integer, db.ForeignKey('articulos.id'), primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    
    def __init__(self, idarticulo, idart_comp, cantidad):
        self.idarticulo = idarticulo
        self.idart_comp = idart_comp
        self.cantidad = cantidad
        
class Stock(db.Model):
    __tablename__ = 'stocks'
    idstock = db.Column(db.Integer, primary_key=True)
    idarticulo = db.Column(db.Integer, db.ForeignKey('articulos.id'), primary_key=True)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursales.id'), primary_key=True)
    actual = db.Column(db.Integer, nullable=False)
    maximo = db.Column(db.Integer)
    deseable = db.Column(db.Integer)
    
    def __init__(self, idstock, idarticulo, idsucursal, actual, maximo, deseable):
        self.idstock = idstock
        self.idarticulo = idarticulo
        self.idsucursal = idsucursal
        self.actual = actual
        self.maximo = maximo
        self.deseable = deseable

class Precio(db.Model):
    __tablename__ = 'precios'
    idlista = db.Column(db.Integer, db.ForeignKey('listas_precio.id'), primary_key=True)
    idarticulo = db.Column(db.Integer, db.ForeignKey('articulos.id'), primary_key=True)
    precio = db.Column(db.Float, nullable=False)
    
    def __init__(self, idlista, idarticulo, precio):
        self.idlista = idlista
        self.idarticulo = idarticulo
        self.precio = precio

class Marca(db.Model):
    __tablename__ = 'marcas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    articulos = db.relationship('Articulo', back_populates='marca')
    
    def __init__(self, nombre):
        self.nombre = nombre

class Rubro(db.Model):
    __tablename__ = 'rubros'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    articulos = db.relationship('Articulo', back_populates='rubro')
    
    def __init__(self, nombre):
        self.nombre = nombre
        
class ListasPrecios(db.Model):
    __tablename__ = 'listas_precio'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    markup = db.Column(db.Float, nullable=False)
    
    def __init__(self, nombre, markup):
        self.nombre = nombre        
        self.markup = markup
        
class Balance(db.Model):
    __tablename__ = 'balance'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    idtipo_balance = db.Column(db.Integer, db.ForeignKey('tipo_balances.id'))
    idusuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    tipo_balance = db.relationship('TipoBalances', backref=db.backref('balance', lazy=True))
    usuario = db.relationship('Usuarios', backref=db.backref('balance', lazy=True))
    items = db.relationship('ItemBalance', backref=db.backref('balance', lazy=True))
    
    def __init__(self, idUsuario, fecha, tipo_balance=0):
        self.idusuario = idUsuario
        self.fecha = fecha
        self.idtipo_balance = tipo_balance
        
class ItemBalance(db.Model):
    __tablename__ = 'item_balance'
    id = db.Column(db.Integer, primary_key=True)
    idbalance = db.Column(db.Integer, db.ForeignKey('balance.id'))
    idarticulo = db.Column(db.Integer, db.ForeignKey('articulos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    precio_total = db.Column(db.Float, nullable=False)
    
    def _init__(self, idbalance, idarticulo, cantidad, precio_unitario, precio_total):
        self.idbalance = idbalance
        self.idarticulo = idarticulo
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.precio_total = precio_total