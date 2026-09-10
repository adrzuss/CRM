from flask import Blueprint

bp_configuraciones = Blueprint('configuraciones', __name__, template_folder='../templates/configuracion')

# No importamos "routes" acá arriba (mismo motivo que en sessions/__init__.py
# y articulos/__init__.py): configs.models/services son importados muy
# temprano por utils/utils.py y por index.py (getOwner/getTareaUsuario), antes
# de que exista el árbol completo de blueprints. index.py importa
# configs.routes explícitamente justo antes de registrar el blueprint.
