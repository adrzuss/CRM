"""
Configuración central de pytest para el proyecto CRM.

Este archivo define las fixtures (recursos reutilizables) que comparten
todos los tests del proyecto. Al estar en conftest.py, pytest las
encuentra automáticamente sin necesidad de importarlas.

Las fixtures principales son:
  - app: crea la aplicación Flask en modo testing
  - client: crea un cliente HTTP para hacer requests de prueba
"""

import pytest
from index import create_app


@pytest.fixture
def app():
    """
    Crea una instancia de la aplicación Flask configurada para testing.

    create_app() es la fábrica de aplicación definida en index.py.
    Luego de crearla, sobreescribimos algunas configuraciones para
    que los tests no necesiten una base de datos MySQL real ni
    validación CSRF.

    Configuraciones que cambiamos:
      - TESTING=True: deshabilita el catch de errores (se propagan)
      - WTF_CSRF_ENABLED=False: desactiva la validación CSRF
      - SQLALCHEMY_DATABASE_URI: usa SQLite en memoria para no
        depender de MySQL
    """
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })

    return app


@pytest.fixture
def client(app):
    """
    Crea un cliente HTTP de prueba asociado a la app.

    El cliente permite hacer requests GET, POST, etc. sin necesidad
    de ejecutar un servidor real. Se usa así:
        response = client.get('/clientes/clientes/1')
        assert response.status_code == 200

    Utiliza la fixture 'app' definida arriba.
    """
    return app.test_client()
