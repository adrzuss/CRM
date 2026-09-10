# comisiones/models.py
# Modelos SQLAlchemy para el módulo de comisiones

from utils.db import db


class ComisionesPlan(db.Model):
    """Plan de comisiones configurable con reglas y tramos."""
    __tablename__ = 'comisiones_planes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_desde = db.Column(db.Date, nullable=False)
    fecha_hasta = db.Column(db.Date)
    tipo_calculo = db.Column(db.String(30), nullable=False, default='PORCENTAJE_VENTA')
    base_calculo = db.Column(db.String(30), nullable=False, default='VENTA_TOTAL')
    modo_escalas = db.Column(db.String(30), nullable=False, default='TASA_ALCANZADA')
    observaciones = db.Column(db.Text)
    creado_por = db.Column(db.Integer)
    fecha_creacion = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    actualizado_por = db.Column(db.Integer)
    fecha_actualizacion = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relaciones
    reglas = db.relationship('ComisionesRegla', backref='plan', lazy=True, cascade='all, delete-orphan')
    tramos = db.relationship('ComisionesTramo', backref='plan', lazy=True, cascade='all, delete-orphan')
    asignaciones = db.relationship('ComisionesAsignacion', backref='plan', lazy=True, cascade='all, delete-orphan')

    def __init__(self, nombre, fecha_desde, tipo_calculo='PORCENTAJE_VENTA',
                 base_calculo='VENTA_TOTAL', modo_escalas='TASA_ALCANZADA',
                 descripcion=None, fecha_hasta=None, observaciones=None,
                 creado_por=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.tipo_calculo = tipo_calculo
        self.base_calculo = base_calculo
        self.modo_escalas = modo_escalas
        self.observaciones = observaciones
        self.creado_por = creado_por


class ComisionesRegla(db.Model):
    """Regla de comisión dentro de un plan, con criterio y prioridad."""
    __tablename__ = 'comisiones_reglas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_plan = db.Column(db.Integer, db.ForeignKey('comisiones_planes.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_regla = db.Column(db.String(20), nullable=False, default='EXCLUSIVA')
    criterio = db.Column(db.String(30), nullable=False)
    valor_criterio = db.Column(db.String(200))
    porcentaje = db.Column(db.Numeric(10, 6), nullable=False, default=0)
    importe_fijo = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    prioridad = db.Column(db.Integer, nullable=False, default=0)
    acumulable = db.Column(db.Boolean, nullable=False, default=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_desde = db.Column(db.Date, nullable=False)
    fecha_hasta = db.Column(db.Date)

    def __init__(self, id_plan, nombre, criterio, valor_criterio, fecha_desde,
                 tipo_regla='EXCLUSIVA', porcentaje=0, importe_fijo=0,
                 prioridad=0, acumulable=False, fecha_hasta=None):
        self.id_plan = id_plan
        self.nombre = nombre
        self.tipo_regla = tipo_regla
        self.criterio = criterio
        self.valor_criterio = valor_criterio
        self.porcentaje = porcentaje
        self.importe_fijo = importe_fijo
        self.prioridad = prioridad
        self.acumulable = acumulable
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta


class ComisionesTramo(db.Model):
    """Tramo de escala para comisiones escalonadas."""
    __tablename__ = 'comisiones_tramos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_plan = db.Column(db.Integer, db.ForeignKey('comisiones_planes.id'), nullable=False)
    desde = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    hasta = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    porcentaje = db.Column(db.Numeric(10, 6), nullable=False, default=0)
    importe_fijo = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    orden = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, id_plan, desde, hasta, porcentaje=0, importe_fijo=0, orden=0):
        self.id_plan = id_plan
        self.desde = desde
        self.hasta = hasta
        self.porcentaje = porcentaje
        self.importe_fijo = importe_fijo
        self.orden = orden


class ComisionesAsignacion(db.Model):
    """Asignación temporal de un plan a un vendedor."""
    __tablename__ = 'comisiones_asignaciones'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_plan = db.Column(db.Integer, db.ForeignKey('comisiones_planes.id'), nullable=False)
    fecha_desde = db.Column(db.Date, nullable=False)
    fecha_hasta = db.Column(db.Date)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, id_usuario, id_plan, fecha_desde, fecha_hasta=None, activo=True):
        self.id_usuario = id_usuario
        self.id_plan = id_plan
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.activo = activo


class ComisionesLiquidacion(db.Model):
    """Liquidación de comisiones de un período."""
    __tablename__ = 'comisiones_liquidaciones'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    periodo_desde = db.Column(db.Date, nullable=False)
    periodo_hasta = db.Column(db.Date, nullable=False)
    fecha_liquidacion = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    estado = db.Column(db.String(20), nullable=False, default='BORRADOR')
    total = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    observaciones = db.Column(db.Text)
    idusuario = db.Column(db.Integer, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    # Relaciones
    detalles = db.relationship('ComisionesDetalle', backref='liquidacion', lazy=True, cascade='all, delete-orphan')

    def __init__(self, periodo_desde, periodo_hasta, idusuario, observaciones=None):
        self.periodo_desde = periodo_desde
        self.periodo_hasta = periodo_hasta
        self.idusuario = idusuario
        self.observaciones = observaciones


class ComisionesDetalle(db.Model):
    """Detalle individual de comisión calculada para trazabilidad completa."""
    __tablename__ = 'comisiones_detalle'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_liquidacion = db.Column(db.Integer, db.ForeignKey('comisiones_liquidaciones.id'), nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_factura = db.Column(db.Integer, nullable=False)
    id_item = db.Column(db.Integer, nullable=False)
    id_regla = db.Column(db.Integer, db.ForeignKey('comisiones_reglas.id'), nullable=True)
    tipo_movimiento = db.Column(db.String(20), nullable=False, default='VENTA')
    tipo_comision = db.Column(db.String(30), nullable=False)
    base_calculo = db.Column(db.String(30), nullable=False)
    cantidad = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    costo_unitario = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    importe_venta = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    importe_costo = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    importe_margen = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    porcentaje = db.Column(db.Numeric(10, 6), nullable=False, default=0)
    importe_comision = db.Column(db.Numeric(20, 6), nullable=False, default=0)
    observaciones = db.Column(db.Text)

    # Relaciones
    regla = db.relationship('ComisionesRegla', backref='detalles', lazy=True)

    def __init__(self, id_liquidacion, id_usuario, id_factura, id_item,
                 tipo_movimiento, tipo_comision, base_calculo,
                 id_regla=None, cantidad=0, costo_unitario=0,
                 importe_venta=0, importe_costo=0, importe_margen=0,
                 porcentaje=0, importe_comision=0, observaciones=None):
        self.id_liquidacion = id_liquidacion
        self.id_usuario = id_usuario
        self.id_factura = id_factura
        self.id_item = id_item
        self.id_regla = id_regla
        self.tipo_movimiento = tipo_movimiento
        self.tipo_comision = tipo_comision
        self.base_calculo = base_calculo
        self.cantidad = cantidad
        self.costo_unitario = costo_unitario
        self.importe_venta = importe_venta
        self.importe_costo = importe_costo
        self.importe_margen = importe_margen
        self.porcentaje = porcentaje
        self.importe_comision = importe_comision
        self.observaciones = observaciones
