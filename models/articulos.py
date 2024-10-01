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
    imagen = db.Column(db.String(255))
    iva = db.relationship('AlcIva', back_populates='articulos')
    marca = db.relationship('Marca', back_populates='articulos')
    rubro = db.relationship('Rubro', back_populates='articulos')
    precios = db.relationship('Precio', backref='articulo', lazy=True)

    def __init__(self, codigo, detalle, costo, idiva, idrubro, idmarca, imagen):
        self.codigo = codigo
        self.detalle = detalle
        self.costo = costo
        self.idiva = idiva
        self.idrubro = idrubro
        self.idmarca = idmarca
        self.imagen = imagen
        
class Stock(db.Model):
    __tablename__ = 'stocks'
    idstock = db.Column(db.Integer, primary_key=True)
    idarticulo = db.Column(db.Integer, db.ForeignKey('articulos.id'), primary_key=True)
    actual = db.Column(db.Integer, nullable=False)
    maximo = db.Column(db.Integer)
    deseable = db.Column(db.Integer)
    
    def __init__(self, idstock, idarticulo, actual, maximo, deseable):
        self.idstock = idstock
        self.idarticulo = idarticulo
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