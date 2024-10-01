from flask import session, redirect, url_for
from app import create_app
from services.configs import get_owner
from routes.sessions import login
from utils.db import db

app = create_app()

with app.app_context():
    db.init_app(app)
    db.create_all()   

@app.route('/')
def index():
    if ('user_id' in session):
        configuracion = get_owner()
        session['owner'] = configuracion.nombre_propietario
        session['company'] = configuracion.nombre_fantasia
        return redirect(url_for('tableros.tablero_inicial'))
    else:
        return redirect(url_for('sesion.login'))    

if __name__ == "__main__":
    app.run(debug=True)