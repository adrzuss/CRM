from flask import Blueprint

fondos_bp = Blueprint('fondos', __name__, template_folder='../templates/fondos')

from fondos import routes
