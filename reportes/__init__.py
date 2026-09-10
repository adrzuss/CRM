from flask import Blueprint

reportes_bp = Blueprint('reportes', __name__, template_folder='../templates/reportes')

from reportes import routes
