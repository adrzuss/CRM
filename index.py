from flask import session, redirect, url_for
from app import create_app
from services.configs import get_owner
from utils.db import db
from utils.utils import check_session

app = create_app()

with app.app_context():
    db.init_app(app)
    db.create_all()   

@app.route('/')
@check_session
def index():
    configuracion = get_owner()
    session['owner'] = configuracion.nombre_propietario
    session['company'] = configuracion.nombre_fantasia
    session['tipo_iva'] = configuracion.tipo_iva
    return redirect(url_for('tableros.tablero_inicial'))

if __name__ == "__main__":
    app.run(debug=True)