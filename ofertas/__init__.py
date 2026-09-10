from flask import Blueprint

ofertas_bp = Blueprint('ofertas', __name__, template_folder='../templates/ofertas')

from ofertas import routes
