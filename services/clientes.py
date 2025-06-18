from models.clientes import Clientes
from utils.db import db
from sqlalchemy import text

def save_cliente(nombre, documento, mail, telefono, direccion, ctacte, id_tipo_doc, id_tipo_iva):
    clientes = Clientes(nombre, documento, mail, telefono, direccion, ctacte, id_tipo_doc, id_tipo_iva)
    db.session.add(clientes)
    db.session.commit()
    return clientes.id

def get_abc_operaciones(desde, hasta):
    abc_operaciones = db.session.execute(text("CALL abc_cliente_operaciones(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
    return abc_operaciones
    
def get_abc_montos(desde, hasta):
    abc_montos = db.session.execute(text("CALL abc_cliente_totales(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
    return abc_montos
    
def get_abc_productos(desde, hasta):
    abc_productos = db.session.execute(text("CALL abc_cliente_productos(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
    return abc_productos

