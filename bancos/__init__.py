from flask import Blueprint

bancos_bp = Blueprint('bancos', __name__, template_folder='../templates/bancos')

from bancos import routes
