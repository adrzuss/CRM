from flask import Blueprint

bp_sesiones = Blueprint('sesion', __name__, template_folder='../templates/sessions', static_folder='../static')

# No importamos "routes" acá arriba. sessions.models/services son importados
# muy temprano por módulos núcleo (configs, utils.msg_alertas). Si routes.py
# se cargara en este punto, arrastraría en cascada de vuelta a configs/articulos
# generando un import circular real (ver el mismo problema resuelto en
# articulos/__init__.py). index.py importa sessions.routes explícitamente
# justo antes de registrar el blueprint.
