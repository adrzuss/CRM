import logging
from flask import Flask, session, redirect, url_for, render_template
from sqlalchemy.exc import OperationalError
from services.configs import getOwner, getTareaUsuario
from utils.db import db
from utils.utils import check_session
from utils.config import Config
from models.articulos import PedirEnVentas
from routes.sessions import bp_sesiones
from routes.tableros import bp_tableros
from routes.clientes import bp_clientes
from routes.ctactecli import bp_ctactecli
from routes.articulos import bp_articulos
from routes.ventas import bp_ventas
from routes.proveedores import bp_proveedores
from routes.ctacteprov import bp_ctacteprov
from routes.configs import bp_configuraciones
from routes.entidades_cred import bp_entidades
from routes.fondos import bp_fondos
from routes.creditos import bp_creditos
from routes.bancos import bp_bancos
from routes.ofertas import bp_ofertas

def create_app():
    app = Flask(__name__, static_folder=Config.STATIC_FOLDER, template_folder=Config.TEMPLATES_FOLDER)
    
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"), # Guarda los logs en un archivo
                        logging.StreamHandler()          # Muestra los logs en la consola (útil para systemd/journalctl)
                    ])
    
    app.config.from_object(Config)
    
    app.register_blueprint(bp_sesiones, url_prefix= '/sesions')
    app.register_blueprint(bp_tableros, url_prefix='/')
    app.register_blueprint(bp_clientes, url_prefix='/clientes')
    app.register_blueprint(bp_ctactecli, url_prefix='/ctactecli')
    app.register_blueprint(bp_articulos, url_prefix='/articulos')
    app.register_blueprint(bp_ventas, url_prefix='/ventas')
    app.register_blueprint(bp_proveedores, url_prefix='/proveedores')
    app.register_blueprint(bp_ctacteprov, url_prefix='/ctacteprov')
    app.register_blueprint(bp_configuraciones, url_prefix='/configuracion')
    app.register_blueprint(bp_entidades, url_prefix='/entidades')
    app.register_blueprint(bp_fondos, url_prefix='/fondos')
    app.register_blueprint(bp_creditos, url_prefix='/creditos')
    app.register_blueprint(bp_bancos, url_prefix='/bancos')
    app.register_blueprint(bp_ofertas, url_prefix='/ofertas')
    
    @app.before_request
    def make_session_permanent():
        session.permanent = True  # Hace que la sesión sea permanente (respetará PERMANENT_SESSION_LIFETIME)
        if not ('id_empresa' in session):
            session['id_empresa'] = 1
    return app

try:
    app = create_app()
    
except Exception as e:
    print("No se pudo iniciar la aplicación 1:", str(e))

try:
    with app.app_context():
        db.init_app(app)
        db.create_all()   
except OperationalError:
    @app.route('/')
    def error_db():
        return render_template("error.html", error=f"No se pudo iniciar la aplicación. Error de conexión a la base de datos. {OperationalError}")
except Exception as e:
    @app.route('/')
    def error_extra():
        return render_template("error.html", error=f"No se pudo iniciar la aplicación. {str(e)}")   
else:
    @app.route('/')
    @check_session
    def index():
        configuracion = getOwner()
        session['owner'] = configuracion.nombre_propietario
        session['company'] = configuracion.nombre_fantasia
        session['tipo_iva'] = configuracion.tipo_iva
        tareaUsuario = getTareaUsuario()
        match tareaUsuario:
            case 1:
                return redirect(url_for('tableros.tablero_inicial'))
            case 2:
                return redirect(url_for('tableros.tablero_administrativo'))
            case _:
                return redirect(url_for('tableros.tablero_basico'))
                

@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='img/favicon.png')

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
    return render_template("404.html", error=f"Página no encontrada: {e}"), 404

# Manejador para error 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", error=f"Error interno del servidor: {e}"), 500

# Manejador para errores de base de datos
@app.errorhandler(OperationalError)
def database_error(e):
    return render_template("error.html", tipoError="bd", error=f"No se pudo conectar a la base de datos: {e}"), 500

if __name__ == "__main__":
    app.run(debug=True)