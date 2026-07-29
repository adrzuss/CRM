from models.clientes import Clientes
from utils.db import db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def save_cliente(nombre, documento, mail, categoria, telefono, direccion, localidad, provincia, ctacte, id_tipo_doc, id_tipo_iva):
    try:
        clientes = Clientes(nombre, documento, mail, categoria, telefono, direccion, localidad, provincia, ctacte, id_tipo_doc, id_tipo_iva)
        db.session.add(clientes)
        db.session.commit()
        return clientes.id
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error SQL: {e}")
        raise Exception(f"Error SQL: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        raise

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

