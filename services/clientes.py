from models.clientes import Clientes
from utils.db import db

def save_cliente(nombre, documento, mail, telefono, direccion, ctacte, id_tipo_doc, id_tipo_iva):
    clientes = Clientes(nombre, documento, mail, telefono, direccion, ctacte, id_tipo_doc, id_tipo_iva)
    db.session.add(clientes)
    db.session.commit()
    return clientes.id