from flask import Blueprint

articulos_bp = Blueprint('articulos', __name__, template_folder='../templates/articulos')

# No importamos "routes" acá arriba (como en el resto de los paquetes) porque
# articulos.models es importado muy temprano por services/configs.py (módulo
# núcleo cargado antes que Flask arranque). Si routes.py se cargara en este
# punto, arrastraría en cascada a proveedores -> bancos -> utils.msg_alertas
# -> services.ventas -> services.configs, generando un import circular real
# (services.configs todavía no habría terminado de definirse a sí mismo).
# En su lugar, index.py importa articulos.routes explícitamente justo antes
# de registrar el blueprint, cuando services.configs ya está completamente
# cargado.
