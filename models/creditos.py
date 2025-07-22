from utils.db import db
from datetime import date

# Planes de Créditos
class PlanesCreditos(db.Model):
    __tablename__ = 'planes_creditos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500), nullable=False)
    tasa_interes = db.Column(db.Float, nullable=False)
    cuotas = db.Column(db.Integer, nullable=False)
    anticipo = db.Column(db.Boolean, default=False)
    garantes = db.Column(db.SmallInteger, default=1)
    baja = db.Column(db.Date, default=False)

    def __init__(self, nombre, descripcion, tasa_interes, cuotas, anticipo=False, garantes=1, baja=date(1900, 1, 1)):
        self.nombre = nombre
        self.descripcion = descripcion
        self.tasa_interes = tasa_interes
        self.cuotas = cuotas
        self.anticipo = anticipo
        self.garantes = garantes
        self.baja = baja

"""
#Definicion de Cuotas de los Planes de Créditos        
class PlanesCuotas(db.Model):
    __tablename__ = 'planes_cuotas'

    id = db.Column(db.Integer, primary_key=True)
    idplan = db.Column(db.Integer, db.ForeignKey('planes_creditos.id'), nullable=False)
    numero_cuota = db.Column(db.Integer, nullable=False)
    recargo_cuota = db.Column(db.Numeric(20, 6), nullable=False)

    def __init__(self, idplan, numero_cuota, recargo_cuota):
        self.idplan = idplan
        self.numero_cuota = numero_cuota
        self.recargo_cuota = recargo_cuota
"""

# Estados de Créditos
class EstadosCreditos(db.Model):
    __tablename__ = 'estados_creditos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

#Categorias de clientes y planes de créditos
class CategoriasCreditos(db.Model):
    __tablename__ = 'categorias_creditos'
    idplan = db.Column(db.Integer, db.ForeignKey('planes_creditos.id'), primary_key=True)
    idcategoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), primary_key=True)
    
    def __init__(self, idplan, idcategoria):
        self.idplan = idplan    
        self.idcategoria = idcategoria
    

# Créditos
class Creditos(db.Model):
    __tablename__ = 'creditos'

    id = db.Column(db.Integer, primary_key=True)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursales.id'), nullable=False)
    idcliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    idplan = db.Column(db.Integer, db.ForeignKey('planes_creditos.id'), nullable=False)
    cuotas = db.Column(db.Integer, nullable=False)
    monto_total = db.Column(db.Numeric(20, 6), nullable=False)
    estado = db.Column(db.Integer, db.ForeignKey('estados_creditos.id'), nullable=False)
    fecha_solicitud = db.Column(db.Date, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    idfactura = db.Column(db.Integer, db.ForeignKey('facturav.id'), nullable=True)
    observaciones = db.Column(db.String(500), nullable=True) 

    def __init__(self, idsucursal, idcliente, idplan, cuotas, monto_total, estado, fecha_solicitud, fecha_inicio, fecha_fin, idfactura=None, observaciones=None):
        self.idsucursal = idsucursal
        self.idcliente = idcliente
        self.idplan = idplan
        self.cuotas = cuotas
        self.monto_total = monto_total
        self.estado = estado
        self.fecha_solicitud = fecha_solicitud
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.idfactura = idfactura
        self.observaciones = observaciones
        
#Garantes de los Créditos
class GarantesCreditos(db.Model):
    __tablename__ = 'garantes_creditos'
    idcredito = db.Column(db.Integer, db.ForeignKey('creditos.id'), primary_key=True)
    idgarante = db.Column(db.Integer, db.ForeignKey('clientes.id'), primary_key=True)
    
    def __init__(self, idcredito, idgarante):
        self.idcredito = idcredito
        self.idgarante = idgarante
        
# Documentos requeridos para Créditos        
class DocumentosCreditos(db.Model):
    __tablename__ = 'documentos_creditos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    
    def __init__(self, nombre):
        self.nombre = nombre
    
# Relación entre Documentos y Créditos
# Esta tabla relaciona los documentos requeridos con los créditos específicos    
class DocumentosParaCreditos(db.Model):
    __tablename__ = 'planes_creditos_documentos'

    iddocumento_credito = db.Column(db.Integer, db.ForeignKey('documentos_creditos.id'), primary_key=True)
    idplan_credito = db.Column(db.Integer, db.ForeignKey('planes_creditos.id'), primary_key=True)

    def __init__(self, iddocumento_credito, idplan_credito):
        self.iddocumento_credito = iddocumento_credito
        self.idplan_credito = idplan_credito

# Documentos específicos de Créditos
# Esta tabla almacena los documentos específicos asociados a cada crédito
class DocumentosDelCreditos(db.Model):
    __tablename__ = 'documentos_del_creditos'

    id = db.Column(db.Integer, primary_key=True)
    idcredito = db.Column(db.Integer, db.ForeignKey('creditos.id'), nullable=False)
    iddocumento_credito = db.Column(db.Integer, db.ForeignKey('documentos_creditos.id'), nullable=False)
    documento = db.Column(db.String(255), nullable=False)

    def __init__(self, idcredito, iddocumento_credito, documento):
        self.idcredito = idcredito
        self.iddocumento_credito = iddocumento_credito
        self.documento = documento

# Vencimientos de las cuotas de los Créditos
class VencimientosCreditos(db.Model):
    __tablename__ = 'vencimientos_creditos'

    id = db.Column(db.Integer, primary_key=True)
    idcredito = db.Column(db.Integer, db.ForeignKey('creditos.id'), nullable=False)
    numero_cuota = db.Column(db.Integer, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(20, 6), nullable=False)

    def __init__(self, idcredito,numero_cuota, fecha_vencimiento, monto):
        self.idcredito = idcredito
        self.numero_cuota = numero_cuota
        self.fecha_vencimiento = fecha_vencimiento
        self.monto = monto

# Pagos realizados en las cuotas de los Créditos
class PagosCreditos(db.Model):
    __tablename__ = 'pagos_creditos'

    id = db.Column(db.Integer, primary_key=True)
    idcredito = db.Column(db.Integer, db.ForeignKey('creditos.id'), nullable=False)
    idvencimiento = db.Column(db.Integer, db.ForeignKey('vencimientos_creditos.id'), nullable=False)
    idfactura = db.Column(db.Integer, db.ForeignKey('facturav.id'), nullable=True)
    fecha_pago = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(20, 6), nullable=False)
    punitorios = db.Column(db.Numeric(20, 6), default=0.0)

    def __init__(self, idcredito, idvencimiento, idfactura, fecha_pago, monto, punitorios=0.0):
        self.idcredito = idcredito
        self.idvencimiento = idvencimiento
        self.idfactura = idfactura
        self.fecha_pago = fecha_pago
        self.monto = monto
        self.punitorios = punitorios