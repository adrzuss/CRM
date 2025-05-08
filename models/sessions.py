from utils.db import db

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