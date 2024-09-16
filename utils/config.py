from flask import current_app
from datetime import timedelta
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost/crm'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IDSTOCK = 1  # El valor de idstock
    UPLOAD_FOLDER = 'static/img/articulos'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Tamaño máximo de archivo de 16MB
    # Duración de la sesión (30 minutos)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = True  # Para HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Protege de ataques XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protege de ataques CSRF

    

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
