from utils.db import db
from enum import Enum
from datetime import datetime

class TipoDescuento(Enum):
    PORCENTAJE = "porcentaje"
    MONTO_FIJO = "monto_fijo"
    
class ReglaSeleccion(Enum):
    MENOR_VALOR = "menor_valor"
    MAYOR_VALOR = "mayor_valor"
    ESPECIFICO = "especifico"

class TipoCondiciones(db.Model):
    __tablename__ = 'tipo_condiciones'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)

class Oferta(db.Model):
    __tablename__ = 'ofertas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_descuento = db.Column(db.Enum(TipoDescuento), nullable=False)
    valor_descuento = db.Column(db.Numeric(10,2), nullable=False)
    cantidad_minima = db.Column(db.Numeric(10,2), nullable=False)
    multiplos = db.Column(db.Boolean, default=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    es_condicion_compra = db.Column(db.Boolean, default=False)

    def __init__(self, nombre, tipo_descuento, valor_descuento, cantidad_minima, multiplos, fecha_inicio, fecha_fin, es_condicion_compra):
        self.nombre = nombre
        self.tipo_descuento = tipo_descuento
        self.valor_descuento = valor_descuento
        self.cantidad_minima = cantidad_minima
        self.multiplos = multiplos
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.es_condicion_compra = es_condicion_compra

    def __repr__(self):
        return f'<Oferta {self.nombre}>'
    
    @property
    def tipo_descuento_display(self):
        displays = {
            TipoDescuento.PORCENTAJE: 'Porcentaje',
            TipoDescuento.MONTO_FIJO: 'Monto fijo'
        }
        return displays.get(self.tipo_descuento, self.tipo_descuento)

class OfertasVinculadas(db.Model):
    __tablename__ = 'ofertas_vinculadas'
    id = db.Column(db.Integer, primary_key=True)
    id_oferta = db.Column(db.Integer, db.ForeignKey('ofertas.id'), nullable=False)
    id_articulo_origen = db.Column(db.Integer, db.ForeignKey('articulos.id'), nullable=False)
    id_articulo_destino = db.Column(db.Integer, db.ForeignKey('articulos.id'), nullable=False)
    
    def __init__(self, id_oferta, id_articulo_origen, id_articulo_destino):
        self.id_oferta = id_oferta
        self.id_articulo_origen = id_articulo_origen
        self.id_articulo_destino = id_articulo_destino
    
class OfertasCondiciones(db.Model):
    __tablename__ = 'ofertas_condiciones'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    id_oferta = db.Column(db.Integer, db.ForeignKey('ofertas.id'), nullable=False)
    id_tipo_condicion = db.Column(db.Integer, db.ForeignKey('tipo_condiciones.id'), nullable=False)
    id_referencia = db.Column(db.Integer, nullable=False)
    
    def __init__(self, id_oferta, id_tipo_condicion, id_referencia):
        self.id_oferta = id_oferta
        self.id_tipo_condicion = id_tipo_condicion
        self.id_referencia = id_referencia

    def __repr__(self):
        return f'<OfertasCondiciones {self.id_oferta} - {self.id_tipo_condicion}>'