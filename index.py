import logging
import secrets
from flask import Flask, session, redirect, url_for, render_template, flash, g
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import OperationalError
from services.configs import getOwner, getTareaUsuario
from services.sessions import get_permisos_usuario, tiene_permiso
from utils.db import db
from flask_migrate import Migrate, upgrade
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
from routes.reportes import bp_reportes

migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder=Config.STATIC_FOLDER, template_folder=Config.TEMPLATES_FOLDER)
    
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"), # Guarda los logs en un archivo
                        logging.StreamHandler()          # Muestra los logs en la consola (útil para systemd/journalctl)
                    ])
    
    app.config.from_object(Config)
    CSRFProtect(app)
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(bp_sesiones, url_prefix= '/sesiones')
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
    app.register_blueprint(bp_reportes, url_prefix='/reportes')
    
    @app.before_request
    def make_session_permanent():
        session.permanent = True  # Hace que la sesión sea permanente (respetará PERMANENT_SESSION_LIFETIME)
        if not ('id_empresa' in session):
            session['id_empresa'] = 1
        g.nonce = secrets.token_hex(16)  # Nonce para CSP en scripts inline
    
    @app.context_processor
    def inject_permisos_menu():
        """Inyecta los permisos de menú en todas las plantillas."""
        permisos_menu = set()
        plan_vencido = False
        
        if 'user_id' in session:
            # Verificar si el plan está vencido
            if 'dias_vencimiento' in session and session['dias_vencimiento'] is not None:
                plan_vencido = session['dias_vencimiento'] <= -30
            
            # Obtener permisos solo si el plan no está vencido
            if not plan_vencido:
                if 'permisos_menu' not in session:
                    session['permisos_menu'] = list(get_permisos_usuario(session['user_id']))
                permisos_menu = set(session.get('permisos_menu', []))
        
        def tiene_permiso_menu(codigo):
            """Función helper para verificar permisos en las plantillas."""
            if plan_vencido:
                return False
            return tiene_permiso(codigo, permisos_menu)
        
        return {
            'permisos_menu': permisos_menu,
            'tiene_permiso': tiene_permiso_menu,
            'plan_vencido': plan_vencido
        }

    @app.context_processor
    def inject_alertas():
        """Inyecta alertas y mensajes en todas las plantillas.
        
        Usa getattr con defaults para rutas que no usan @alertas_mensajes
        (login, logout, etc.) donde g.alertas no está definido.
        """
        return dict(
            alertas=getattr(g, 'alertas', []),
            cantidadAlertas=getattr(g, 'cantidadAlertas', 0),
            mensajes=getattr(g, 'mensajes', []),
            cantidadMensajes=getattr(g, 'cantidadMensajes', 0)
        )
    
    @app.after_request
    def add_security_headers(response):
        """Agrega headers de seguridad HTTP a todas las respuestas."""
        nonce = getattr(g, 'nonce', '')
        
        # Headers básicos de seguridad
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '0'  # Deprecated, pero BACA
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS solo si la cookie de sesión usa Secure (producción con HTTPS)
        if Config.SESSION_COOKIE_SECURE:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content-Security-Policy
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net https://unpkg.com; "
            f"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            f"font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            f"img-src 'self' data:; "
            f"connect-src 'self'; "
            f"frame-ancestors 'none'; "
            f"form-action 'self'"
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response
            
    return app

try:
    app = create_app()
    
except Exception as e:
    print("No se pudo iniciar la aplicación 1:", str(e))

try:
    with app.app_context():
        upgrade()   
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
        configuracion, plan_sistema, dias_vencimiento = getOwner()
        session['owner'] = configuracion.nombre_propietario
        session['company'] = configuracion.nombre_fantasia
        session['tipo_iva'] = configuracion.tipo_iva
        session['plan'] = plan_sistema
        session['plan_vencimiento'] = configuracion.vencimiento.strftime('%d/%m/%Y') if configuracion.vencimiento else 'N/A'
        session['dias_vencimiento'] = dias_vencimiento
        if dias_vencimiento <= -30:
            tareaUsuario = 99
            flash("Tu plan ha vencido hace más de 30 días. Por favor, contacta al soporte para renovar tu suscripción.", "danger")
        else:    
            tareaUsuario = getTareaUsuario()
        match tareaUsuario:
            case 1:
                return redirect(url_for('tableros.tablero_inicial'))
            case 2:
                #return redirect(url_for('tableros.tablero_administrativo'))
                return redirect(url_for('tableros.tablero_inicial'))
            case 99:
                return redirect(url_for('tableros.plan_vencido'))
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