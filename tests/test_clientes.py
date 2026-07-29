"""
Tests para las rutas de clientes del proyecto CRM.

Estos tests verifican el comportamiento de las rutas HTTP del blueprint
de clientes. Como NO queremos depender de una base de datos MySQL real,
usamos unittest.mock (patch) para reemplazar las consultas a la DB
por objetos simulados (MagicMock).

Estrategia de mocks:
  - check_session: se salva configurando la sesión con user_id
  - alertas_mensajes: se evita parcheando obtener_alertas y obtener_mensajes
  - Modelos (Clientes, TipoDocumento, etc.): se parchea .query.get, .query.all
    y .query.filter_by para retornar datos de prueba sin tocar la DB
  - render_template: se parchea para las rutas que renderizan templates,
    porque los templates requieren muchas variables de sesión y endpoints
    que no existen en la app de test
"""

from unittest.mock import patch, MagicMock


def _configurar_sesion(client):
    """
    Configura datos de sesión para que el decorador @check_session
    no redirija al login.

    En un cliente de prueba, la sesión se modifica usando
    client.session_transaction() como context manager.

    También pre-setamos permisos_menu vacío para evitar que el
    context processor inject_permisos_menu llame a get_permisos_usuario()
    (que haría una consulta a la base de datos real).
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['tipo_iva'] = '1'
        sess['id_empresa'] = 1
        sess['permisos_menu'] = []  # Evita llamada a DB en inject_permisos_menu


# ──────────────────────────────────────────────
# Tests para GET /clientes/clientes/<id>
# ──────────────────────────────────────────────

# NOTA: estas rutas renderizan templates (clientes.html), que a su vez
# extienden base.html e incluyen partials con muchas variables de sesión
# (company, owner, user_name, etc.) y llamadas a url_for de endpoints
# que no existen en la app de test. Para evitar errores de template,
# parcheamos render_template para que devuelva un string vacío.
# Esto nos permite verificar que la ruta se ejecuta correctamente
# (status 200) sin depender de templates reales.


def test_get_cliente_existente(client):
    """
    Test GET /clientes/clientes/1 con un cliente existente.

    Verifica que:
      1. La ruta responde con status 200 (OK)
      2. Se llama a render_template con los datos del cliente

    Para evitar la DB, parcheamos:
      - Clientes.query.get → retorna un MagicMock con id=1
      - Clientes.query.all → retorna una lista con ese cliente
      - Los demás modelos (TipoDocumento, TipoIva, etc.) retornan listas vacías
      - obtener_alertas y obtener_mensajes → retornan datos vacíos
      - render_template → retorna string vacío (evita renderizar templates reales)
    """
    _configurar_sesion(client)

    # Creamos un mock que simula un cliente obtenido de la DB
    mock_cliente = MagicMock()
    mock_cliente.id = 1
    mock_cliente.nombre = "Cliente Ejemplo"
    mock_cliente.idprovincia = 1

    # Lista de parches. Cada uno reemplaza una consulta a la DB
    # con valores controlados que NO necesitan conexión MySQL.
    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.clientes.render_template', return_value='') as mock_render:
                with patch('models.clientes.Clientes.query') as mock_clientes_query:
                    mock_clientes_query.get.return_value = mock_cliente
                    mock_clientes_query.all.return_value = [mock_cliente]

                    with patch('models.configs.TipoDocumento.query') as mock_td:
                        mock_td.all.return_value = []

                        with patch('models.configs.TipoIva.query') as mock_ti:
                            mock_ti.all.return_value = []

                            with patch('models.configs.Categorias.query') as mock_cat:
                                mock_cat.all.return_value = []

                                with patch('models.configs.Provincias.query') as mock_prov:
                                    mock_prov.all.return_value = []

                                    with patch('models.configs.Localidades.query') as mock_loc:
                                        # filter_by retorna un objeto que tiene .all()
                                        mock_loc.filter_by.return_value.all.return_value = []

                                        response = client.get('/clientes/clientes/1')

                                        assert response.status_code == 200
                                        # Verificamos que se llamó a render_template
                                        # con la plantilla correcta
                                        mock_render.assert_called_once()
                                        args, kwargs = mock_render.call_args
                                        assert args[0] == 'clientes.html'


def test_get_cliente_inexistente(client):
    """
    Test GET /clientes/clientes/999 con un cliente que no existe.

    Cuando Clientes.query.get(id) retorna None, la ruta debe
    renderizar la página igual pero con la variable cliente=None
    y sin localidades.

    Verifica que responde 200 incluso cuando no se encuentra el cliente.
    """
    _configurar_sesion(client)

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.clientes.render_template', return_value='') as mock_render:
                with patch('models.clientes.Clientes.query') as mock_clientes_query:
                    # get() retorna None → cliente no encontrado
                    mock_clientes_query.get.return_value = None
                    mock_clientes_query.all.return_value = []

                    with patch('models.configs.TipoDocumento.query') as mock_td:
                        mock_td.all.return_value = []

                        with patch('models.configs.TipoIva.query') as mock_ti:
                            mock_ti.all.return_value = []

                            with patch('models.configs.Categorias.query') as mock_cat:
                                mock_cat.all.return_value = []

                                with patch('models.configs.Provincias.query') as mock_prov:
                                    mock_prov.all.return_value = []

                                    with patch('models.configs.Localidades.query') as mock_loc:
                                        mock_loc.filter_by.return_value.all.return_value = []

                                        response = client.get('/clientes/clientes/999')

                                        assert response.status_code == 200
                                        mock_render.assert_called_once()
                                        args, kwargs = mock_render.call_args
                                        # Verificamos que se pasó cliente=None
                                        assert kwargs.get('cliente') is None


# ──────────────────────────────────────────────
# Tests para GET /clientes/localidades/<idprovincia>
# ──────────────────────────────────────────────

# NOTA: Estas rutas retornan JSON (no renderizan templates), por lo que
# no necesitan parchear render_template.


def test_get_localidades(client):
    """
    Test GET /clientes/localidades/1.

    Verifica que:
      1. Responde con status 200
      2. Retorna JSON con success=True
      3. Incluye las localidades de la provincia solicitada

    Localidades.query.filter_by(id_provincia=...) se mockea
    para retornar localidades de prueba.
    """
    _configurar_sesion(client)

    # Creamos mocks para simular localidades
    mock_localidad1 = MagicMock()
    mock_localidad1.id = 1
    mock_localidad1.localidad = "Localidad Test 1"

    mock_localidad2 = MagicMock()
    mock_localidad2.id = 2
    mock_localidad2.localidad = "Localidad Test 2"

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('models.configs.Localidades.query') as mock_loc_query:
                mock_loc_query.filter_by.return_value.all.return_value = [
                    mock_localidad1, mock_localidad2
                ]

                response = client.get('/clientes/localidades/1')

                assert response.status_code == 200

                # Verificamos que la respuesta sea JSON con los datos esperados
                data = response.get_json()
                assert data['success'] is True
                assert len(data['localidades']) == 2


def test_get_localidades_sin_resultados(client):
    """
    Test GET /clientes/localidades/999 cuando no hay localidades
    para la provincia indicada.

    Verifica que retorna JSON con localidades vacío.
    """
    _configurar_sesion(client)

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('models.configs.Localidades.query') as mock_loc_query:
                mock_loc_query.filter_by.return_value.all.return_value = []

                response = client.get('/clientes/localidades/999')

                assert response.status_code == 200

                data = response.get_json()
                assert data['success'] is True
                assert len(data['localidades']) == 0


# ──────────────────────────────────────────────
# Tests para POST /clientes/new_cliente y CSRF
# ──────────────────────────────────────────────

def test_new_cliente_sin_csrf_token(client, app):
    """
    Test que verifica que POST a /clientes/new_cliente SIN token CSRF
    retorna 400 cuando la protección CSRF está habilitada.

    En la configuración normal de test (conftest.py) el CSRF está
    deshabilitado (WTF_CSRF_ENABLED=False). Para este test,
    lo habilitamos temporalmente para simular el comportamiento
    de producción.

    Cuando CSRF está activo y no se envía el token, Flask-WTF
    lanza CSRFError (hereda de BadRequest → HTTP 400).
    """
    # Habilitamos CSRF para este test específico
    app.config['WTF_CSRF_ENABLED'] = True

    with app.test_client() as csrf_client:
        # Enviamos POST sin token CSRF
        response = csrf_client.post('/clientes/new_cliente', data={})
        assert response.status_code == 400
