from flask import Blueprint

bp_ventas = Blueprint('ventas', __name__, template_folder='../templates/ventas')

# Lazy-routes: ventas.models es importado por clientes.routes (cluster con ciclo),
# así que no importamos routes acá arriba. index.py hace import ventas.routes
# explícitamente antes de registrar el blueprint.
