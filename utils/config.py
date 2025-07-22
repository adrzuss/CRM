from flask import current_app
from dotenv import load_dotenv
from datetime import timedelta
import os
from pathlib import Path


resultado = load_dotenv(override=True)
#print("Intentando cargar .env desde:", Path('.env').resolve())
#print("¿Existe el archivo?", os.path.exists('.env'))


#print('El paso: ', os.getenv('SQLALCHEMY_DATABASE_URI'))
#print('Resultado: ', resultado)

class Config:
    # Debo configurar estas variables con el directorio donde se encuentra la app
    #APPLICATION_ROOT = '/demo_erp'
    #SESSION_COOKIE_PATH = '/demo_erp'
    SECRET_KEY = os.getenv('MY_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    COMPANY_FOLDER = os.getenv('COMPANY_FOLDER', '')  # Carpeta de la empresa
    IDSTOCK = 1  # El valor de idstock
    LOGO_PATH = os.getenv('LOGO_PATH')
    UPLOAD_FOLDER = 'static/img/articulos'
    UPLOAD_FOLDER_CREDITOS = 'static/img/creditos'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    FE_FILES_FOLDER = 'cert_fe'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Tamaño máximo de archivo de 16MB
    # Duración de la sesión (30 minutos)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = True  # Para HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Protege de ataques XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protege de ataques CSRF
    INVOICES_FOLDER = os.getenv('INVOICES_FOLDER')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

