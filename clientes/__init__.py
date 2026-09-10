from flask import Blueprint

bp_clientes = Blueprint('clientes', __name__, template_folder='../templates/clientes')

# No importamos "routes" acá arriba: clientes.models/services son referenciados
# desde ventas (cluster con ciclo real clientes<->ventas), así que aplicamos el
# mismo patrón lazy-routes usado en articulos/configs/sessions para evitar un
# import circular. index.py importa clientes.routes explícitamente antes de
# registrar el blueprint.
