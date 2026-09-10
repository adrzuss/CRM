from flask import Blueprint

proveedores_bp = Blueprint('proveedores', __name__, template_folder='../templates/proveedores')

from proveedores import routes
