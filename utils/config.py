from flask import current_app
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()
class Config:
    SECRET_KEY = os.getenv('MY_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IDSTOCK = 1  # El valor de idstock
    LOGO_PATH = os.getenv('LOGO_PATH')
    UPLOAD_FOLDER = 'static/img/articulos'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Tamaño máximo de archivo de 16MB
    # Duración de la sesión (30 minutos)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = True  # Para HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Protege de ataques XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protege de ataques CSRF
    INVOICES_FOLDER = os.getenv('INVOICES_FOLDER')

    

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

