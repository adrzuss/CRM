from flask import Blueprint

ctacteprov_bp = Blueprint('ctacteprov', __name__, template_folder='../templates/ctacteprov')

from ctacteprov import routes
