from utils.db import db
from datetime import time

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(80))
    usuario = db.Column(db.String(80))
    clave = db.Column(db.String(200))
    documento = db.Column(db.String(13))
    email = db.Column(db.String(100))
    telefono  = db.Column(db.String(20))
    direccion = db.Column(db.String(100))
    
    def __init__(self, nombre, usuario, clave, documento, email, telefono, direccion):
        self.nombre = nombre
        self.usuario = usuario
        self.clave = clave
        self.documento = documento
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        
class Tareas(db.Model):
    __tablename__ = 'tareas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tarea = db.Column(db.String(50))
    
    def __init__(self, tarea):
        self.tarea = tarea
    
class TareasUsuarios(db.Model):
    __tablename__='tareas_usuario'
    idtarea = db.Column(db.Integer, primary_key=True)
    idusuario = db.Column(db.Integer, primary_key=True)
    """
    tarea = db.relationship('Tareas', backref=db.backref('tareas_usuario', lazy=True))
    usuario = db.relationship('Usuarios', backref=db.backref('tareas_usuario', lazy=True))
    """
    
    def __init__(self, idtarea, idusuario):
        self.idtarea = idtarea
        self.idusuario = idusuario
        
class Mensajes(db.Model):
    __tablename__ = 'mensajes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idsucursal = db.Column(db.Integer)
    idusuario = db.Column(db.Integer)
    fecha = db.Column(db.Date)
    hora = db.Column(db.Time)
    tipo = db.Column(db.String(10))  # 'ALERTA' o 'MENSAJE'
    titulo = db.Column(db.String(100))
    subtitulo = db.Column(db.String(100), nullable=True)
    mensaje = db.Column(db.String(1000))
    idusr_destino = db.Column(db.Integer, nullable=True)
    idsuc_destino = db.Column(db.Integer, nullable=True)
    leido = db.Column(db.Boolean, default=False)
    
    def __init__(self, idsucursal, idusuario, fecha, hora, tipo, titulo, subtitulo, mensaje, idusr_destino=None, idsuc_destino=None, leido=False):
        self.idsucursal = idsucursal
        self.idusuario = idusuario
        self.fecha = fecha
        self.hora = hora
        self.tipo = tipo
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.mensaje = mensaje
        self.idusr_destino = idusr_destino
        self.idsuc_destino = idsuc_destino
        self.leido = leido