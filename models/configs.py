from utils.db import db

class TipoIva(db.Model):
    __tablename__ = 'tipo_iva'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(50), nullable=False)
    
    def __init__(self, descripcion):
        self.descripcion = descripcion

class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    id = db.Column(db.Integer, primary_key=True)
    nombre_propietario = db.Column(db.String(100), nullable=False)
    nombre_fantasia = db.Column(db.String(100), nullable=False)
    tipo_iva = db.Column(db.Integer, nullable=False) 
    tipo_documento = db.Column(db.Integer, nullable=False)
    documento = db.Column(db.String(13), nullable=False)
    telefono = db.Column(db.String(30), nullable=False)
    mail = db.Column(db.String(100), nullable=False)
    clave = db.Column(db.String(100), nullable=False)
    vencimiento = db.Column(db.Date, nullable=False)
    licencia = db.Column(db.String(200), nullable=False)
    
    def __init__(self, nombre_propietario, nombre_fantasia, tipo_iva, tipo_documento, documento, telefono, mail, clave, vencimiento, licencia):
        self.nombre_propietario = nombre_propietario
        self.nombre_fantasia = nombre_fantasia
        self.tipo_iva = tipo_iva
        self.tipo_documento = tipo_documento
        self.documento = documento
        self.telefono = telefono
        self.mail = mail
        self.clave = clave
        self.vencimiento = vencimiento
        self.licencia = licencia

class AlcIva(db.Model):
    __tablename__ = 'alc_iva'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100), nullable=False)
    alicuota = db.Column(db.Float, nullable=False)
    articulos = db.relationship('Articulo', back_populates='iva')
    
    def __init__(self, descripcion, alicuota):
        self.descripcion = descripcion
        self.alicuota = alicuota
        
class PagosCobros(db.Model):
    __tablename__ = 'pagos_cobros'
    id = db.Column(db.Integer, primary_key=True)
    pagos_cobros = db.Column(db.String(50), nullable=False)
    
    def __init__(self, pagos_cobros):
        self.pagos_cobros = pagos_cobros
        
class TipoDocumento(db.Model):
    __tablename__ = 'tipo_doc'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30))
    id_afip = db.Column(db.Integer)

    def __init__(self, nombre, id_afip):
        self.nombre = nombre    
        self.id_afip = id_afip
class TipoArticulos(db.Model):
    __tablename__ = 'tipo_articulos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False)
    
    def __init__(self, nombre):
        self.nombre = nombre
    
class TipoOperacion(db.Model):
    __tablename__ = 'tipo_operacion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False)
    
    def __init__(self, nombre):
        self.nombre = nombre
        
class TipoCompAplica(db.Model):
    __tablename__ = 'tipo_comp_aplica'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False)
    
    def __init__(self, nombre):
        self.nombre = nombre
class TipoComprobantes(db.Model):
    __tablename__ = 'tipo_comprobantes'
    id = db.Column(db.Integer, primary_key=True)
    id_tipo_iva_owner = db.Column(db.Integer, db.ForeignKey('tipo_iva.id'))
    id_tipo_iva = db.Column(db.Integer, db.ForeignKey('tipo_iva.id'))
    id_afip = db.Column(db.Integer)
    nombre = db.Column(db.String(50))
    id_tipo_operacion = db.Column(db.Integer, db.ForeignKey('tipo_operacion.id'))   
    id_tipo_comp_aplica = db.Column(db.Integer, db.ForeignKey('tipo_comp_aplica.id'))
    
    def __init__(self, nombre, id_tipo_iva_owner, id_tipo_iva, id_afip, id_tipo_operacion, id_tipo_comp_aplica):
        self.id_tipo_iva_owner = id_tipo_iva_owner
        self.id_tipo_iva = id_tipo_iva
        self.id_afip = id_afip
        self.nombre = nombre
        self.id_tipo_operacion = id_tipo_operacion
        self.id_tipo_comp_aplica = id_tipo_comp_aplica
        
class TipoBalances(db.Model):
    __tablename__ = 'tipo_balances'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    
    def __init__(self, nombre):
        self.nombre = nombre