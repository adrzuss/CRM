from utils.db import db
from datetime import date

class TipoIva(db.Model):
    __tablename__ = 'tipo_iva'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(50), nullable=False)
    id_afip = db.Column(db.Integer, nullable=False, default=0)
    
    def __init__(self, descripcion):
        self.descripcion = descripcion

class PlanesSistema(db.Model):
    __tablename__ = 'planes_sistema'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    
class OpcionesPlanSistema(db.Model):
    __tablename__ = 'opciones_plan_sistema'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_plan_sistema = db.Column(db.Integer, db.ForeignKey('planes_sistema.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    habilitada = db.Column(db.Boolean, nullable=False, default=False)

class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    id = db.Column(db.Integer, primary_key=True)
    nombre_propietario = db.Column(db.String(100), nullable=False)
    nombre_fantasia = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    localidad = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    tipo_iva = db.Column(db.Integer, nullable=False) 
    tipo_documento = db.Column(db.Integer, nullable=False)
    documento = db.Column(db.String(13), nullable=False)
    telefono = db.Column(db.String(30), nullable=False)
    mail = db.Column(db.String(100), nullable=False)
    clave = db.Column(db.String(100), nullable=False)
    vencimiento = db.Column(db.Date, nullable=False)
    licencia = db.Column(db.String(200), nullable=False)
    paso_cert = db.Column(db.String(200))
    paso_key = db.Column(db.String(200))
    dias_vto_cta_cte = db.Column(db.SmallInteger, nullable=False, default=0)
    caja_con_apertura = db.Column(db.Boolean, nullable=False, default=False)
    idplan_sistema = db.Column(db.Integer, db.ForeignKey('planes_sistema.id'), nullable=False)
    interes_mora_creditos = db.Column(db.Numeric(20,6), nullable=False, default=0)
    
    def __init__(self, nombre_propietario, nombre_fantasia, tipo_iva, tipo_documento, documento, telefono, mail, clave, vencimiento, licencia, caja_con_apertura, idplan_sistema, interes_mora_creditos):
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
        self.caja_con_apertura = caja_con_apertura
        self.idplan_sistema = idplan_sistema
        self.interes_mora_creditos = interes_mora_creditos

class Categorias(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(80))
    
    def __init__(self, nombre):
        self.nombre = nombre
class AlcIva(db.Model):
    __tablename__ = 'alc_iva'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(100), nullable=False)
    alicuota = db.Column(db.Numeric(20,6), nullable=False)
    articulos = db.relationship('Articulo', back_populates='iva')
    
    def __init__(self, descripcion, alicuota):
        self.descripcion = descripcion
        self.alicuota = alicuota

class AlcIB(db.Model):
    __tablename__ = 'alc_ib'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(100), nullable=False)
    alicuota = db.Column(db.Numeric(20,6), nullable=False)
    articulos = db.relationship('Articulo', back_populates='ingbto')
    
    def __init__(self, descripcion, alicuota):
        self.descripcion = descripcion
        self.alicuota = alicuota
        
class PagosCobros(db.Model):
    __tablename__ = 'pagos_cobros'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pagos_cobros = db.Column(db.String(50), nullable=False)
    
    def __init__(self, pagos_cobros):
        self.pagos_cobros = pagos_cobros
        
class TipoDocumento(db.Model):
    __tablename__ = 'tipo_doc'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(30))
    id_afip = db.Column(db.Integer)

    def __init__(self, nombre, id_afip):
        self.nombre = nombre    
        self.id_afip = id_afip
class TipoArticulos(db.Model):
    __tablename__ = 'tipo_articulos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(30), nullable=False)
    
    def __init__(self, nombre):
        self.nombre = nombre
    
class TipoOperacion(db.Model):
    __tablename__ = 'tipo_operacion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(30), nullable=False)
    
    def __init__(self, nombre):
        self.nombre = nombre
        
class TipoCompAplica(db.Model):
    __tablename__ = 'tipo_comp_aplica'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_iva_owner = db.Column(db.Integer, db.ForeignKey('tipo_iva.id'))
    id_iva_entidad = db.Column(db.Integer, db.ForeignKey('tipo_iva.id'))
    id_tipo_comp = db.Column(db.Integer, db.ForeignKey('tipo_comprobantes.id'))
    id_tipo_oper = db.Column(db.Integer, db.ForeignKey('tipo_operacion.id'))
        
class TipoComprobantes(db.Model):
    __tablename__ = 'tipo_comprobantes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_afip = db.Column(db.Integer)
    nombre = db.Column(db.String(50))
    letra = db.Column(db.String(5))
    discrimina_iva = db.Column(db.Boolean, nullable=False, default=False)
    
    def __init__(self, nombre, id_afip, letra, discrimina_iva=False):
        self.nombre = nombre
        self.id_afip = id_afip
        self.letra = letra
        self.discrimina_iva = discrimina_iva
        
class TipoBalances(db.Model):
    __tablename__ = 'tipo_balances'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    
    def __init__(self, nombre):
        self.nombre = nombre
    
class PuntosVenta(db.Model):
    __tablename__ = 'puntos_venta'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    punto_vta = db.Column(db.Integer, nullable=False)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursales.id'))
    ultima_fac_a = db.Column(db.Integer, nullable=False)
    ultima_fac_b = db.Column(db.Integer, nullable=False)
    ultima_tkt = db.Column(db.Integer, nullable=False)
    ultima_fac_c = db.Column(db.Integer, nullable=False)
    ultima_deb_a = db.Column(db.Integer, nullable=False)
    ultima_deb_b = db.Column(db.Integer, nullable=False)
    ultima_deb_c = db.Column(db.Integer, nullable=False)
    ultima_nc_a = db.Column(db.Integer, nullable=False)
    ultima_nc_b = db.Column(db.Integer, nullable=False)
    ultima_nc_c = db.Column(db.Integer, nullable=False)
    ultimo_rem_x = db.Column(db.Integer, nullable=False)
    ultimo_rec_x = db.Column(db.Integer, nullable=False)
    fac_electronica = db.Column(db.Boolean, nullable=False, default=False)
    pos_printer = db.Column(db.String(100), nullable=True)
    certificado_p12 = db.Column(db.String(300))
    clave_certificado = db.Column(db.String(50))
    token = db.Column(db.String(1000))
    sign = db.Column(db.String(500))
    expiration = db.Column(db.DateTime)
    sucursal = db.relationship('Sucursales', backref=db.backref('idsucursal', lazy=True))
    
    def __init__(self, punto_vta, idsucursal, ultima_fac_a = 0, ultima_fac_b = 0, ultima_fac_c = 0, ultima_deb_a = 0, ultima_deb_b = 0, ultima_deb_c = 0, ultima_nc_a = 0, ultima_nc_b = 0, ultima_nc_c = 0, ultimo_rem_x = 0, ultimo_rec_x = 0):
        self.punto_vta = punto_vta
        self.idsucursal = idsucursal
        self.ultima_fac_a = ultima_fac_a
        self.ultima_fac_b = ultima_fac_b
        self.ultima_fac_c = ultima_fac_c
        self.ultima_deb_a = ultima_deb_a
        self.ultima_deb_b = ultima_deb_b
        self.ultima_deb_c = ultima_deb_c
        self.ultima_nc_a = ultima_nc_a
        self.ultima_nc_b = ultima_nc_b
        self.ultima_nc_c = ultima_nc_c
        self.ultimo_rem_x = ultimo_rem_x
        self.ultimo_rec_x = ultimo_rec_x
        
class PlanCtas(db.Model):
    __tablename__ = 'plan_ctas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    
    def __init__(self, nombre):
        self.nombre = nombre

class Provincias(db.Model):
    __tablename__ = 'provincias'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    provincia = db.Column(db.String(100), nullable=False)
    
    def __init__(self, provincia):
        self.provincia = provincia

class Localidades(db.Model):
    __tablename__ = 'localidades'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    localidad = db.Column(db.String(100), nullable=False)
    id_provincia = db.Column(db.Integer, db.ForeignKey('provincias.id'), nullable=False)

    def __init__(self, localidad, id_provincia):
        self.localidad = localidad
        self.id_provincia = id_provincia
        
class MonedasBilletes(db.Model):
    __tablename__ = 'monedas_billetes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Numeric(20,6), nullable=False)
    baja = db.Column(db.Date, nullable=False, default=date(1900, 1, 1))

    def __init__(self, descripcion, valor, baja=date(1900, 1, 1)):
        self.descripcion = descripcion
        self.valor = valor
        self.baja = baja
        
class TipoRendiciones(db.Model):        
    __tablename__ = 'tipo_rendiciones'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    
    def __init__(self, nombre):
        self.nombre = nombre
class RendicionesCaja(db.Model):
    __tablename__ = 'rendiciones_caja'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False)
    idusuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    idpunto_vta = db.Column(db.Integer, db.ForeignKey('puntos_venta.id'), nullable=False)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursales.id'), nullable=False)
    idtipo_rendicion = db.Column(db.Integer, db.ForeignKey('tipo_rendiciones.id'), nullable=False)
    total_ventas = db.Column(db.Numeric(20,6), nullable=False, default=0)
    total_efectivo = db.Column(db.Numeric(20,6), nullable=False, default=0)

    def __init__(self, fecha, idusuario, idpunto_vta, idsucursal, idtipo_rendicion, total_ventas, total_efectivo):
        self.fecha = fecha
        self.idusuario = idusuario
        self.idpunto_vta = idpunto_vta
        self.idsucursal = idsucursal
        self.idtipo_rendicion = idtipo_rendicion
        self.total_ventas = total_ventas
        self.total_efectivo = total_efectivo
        
class ItemsRendicionesCaja(db.Model):
    __tablename__ = 'items_rendiciones_caja'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idrendicion = db.Column(db.Integer, db.ForeignKey('rendiciones_caja.id'), nullable=False)
    idmoneda_billete = db.Column(db.Integer, db.ForeignKey('monedas_billetes.id'), nullable=False)
    cantidad = db.Column(db.Numeric(20,6), nullable=False)

    def __init__(self, idrendicion, idmoneda_billete, cantidad):
        self.idrendicion = idrendicion
        self.idmoneda_billete = idmoneda_billete
        self.cantidad = cantidad
        
        