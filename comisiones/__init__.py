from flask import Blueprint

comisiones_bp = Blueprint('comisiones', __name__, template_folder='../templates/comisiones')

from comisiones import routes
