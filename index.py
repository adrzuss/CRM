from flask import session, redirect, url_for, render_template
from app import create_app
from sqlalchemy.exc import OperationalError
from services.configs import get_owner
from utils.db import db
from utils.utils import check_session

try:
    app = create_app()
except:
    print("No se pudo iniciar la aplicación 1")

try:
    with app.app_context():
        db.init_app(app)
        db.create_all()   
except OperationalError:
    @app.route('/')
    def error_db():
        return render_template("error.html", error="No se pudo iniciar la aplicación. Error de conexión a la base de datos.")
else:
    @app.route('/')
    @check_session
    def index():
        configuracion = get_owner()
        session['owner'] = configuracion.nombre_propietario
        session['company'] = configuracion.nombre_fantasia
        session['tipo_iva'] = configuracion.tipo_iva
        return redirect(url_for('tableros.tablero_inicial'))

# Ruta para forzar un error 404
@app.route('/404')
def trigger_404():
    # Simular un 404
    return render_template("404.html")

# Ruta para forzar un error 500
@app.route('/500')
def trigger_500():
    #raise Exception("Simulación de error interno del servidor")
    return render_template("500.html")

# Ruta para forzar un error de base de datos
@app.route('/db_error')
def trigger_db_error():
    raise OperationalError("Simulando error de base de datos", {}, None)

# Manejador para error 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", error="Página no encontrada"), 404

# Manejador para error 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", error="Error interno del servidor"), 500

# Manejador para errores de base de datos
@app.errorhandler(OperationalError)
def database_error(e):
    return render_template("error.html", tipoError="bd", error="No se pudo conectar a la base de datos"), 500

if __name__ == "__main__":
    app.run(debug=True)