from flask import Flask, session
from utils.config import Config
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
from flask_sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    app.register_blueprint(bp_sesiones)
    app.register_blueprint(bp_tableros)
    app.register_blueprint(bp_clientes)
    app.register_blueprint(bp_ctactecli)
    app.register_blueprint(bp_articulos)
    app.register_blueprint(bp_ventas)
    app.register_blueprint(bp_proveedores)
    app.register_blueprint(bp_ctacteprov)
    app.register_blueprint(bp_configuraciones)
    app.register_blueprint(bp_entidades)
    app.register_blueprint(bp_fondos)
    
    @app.before_request
    def make_session_permanent():
        session.permanent = True  # Hace que la sesión sea permanente (respetará PERMANENT_SESSION_LIFETIME)
        
    return app



