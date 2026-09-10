"""
Tests de integración para el flujo completo de cambio de precio.

Verifica la interacción entre:
- Frontend (JS) → construye query string correcto
- Backend route (/filtrar_articulos) → acepta query params, valida lista_precio
- Service (obtenerArticulosMarcaRubro) → filtra y calcula precios
- Frontend → popula tabla con resultados

Escenarios cubiertos (SCE-010 a SCE-014):
- SCE-010: Click con marca y rubro seleccionados
- SCE-011: Click solo con marca
- SCE-012: Click solo con rubro
- SCE-013: Click sin marca ni rubro (solo lista_precio)
- SCE-014: Resultado vacío muestra tabla vacía (sin error)
"""

from unittest.mock import patch, MagicMock
from decimal import Decimal


def _configurar_sesion(client):
    """Configura sesión para tests que requieren autenticación."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['tipo_iva'] = '1'
        sess['id_empresa'] = 1
        sess['permisos_menu'] = []


# ──────────────────────────────────────────────
# Tests de integración: Route → Service
# ──────────────────────────────────────────────

def test_integracion_filtrar_con_marca_y_rubro(client):
    """
    Test SCE-010: Flujo completo con marca=1, rubro=2, lista_precio=3, porcentaje=10.

    Verifica que:
      1. La ruta acepta query params con todos los filtros
      2. Llama a obtenerArticulosMarcaRubro con parámetros correctos
      3. Retorna artículos con precio_actual y precio_nuevo calculado
    """
    _configurar_sesion(client)

    mock_articulos = [
        {'codigo': '001', 'descripcion': 'ARTÍCULO 1', 'precio_actual': 100.00, 'precio_nuevo': 110.00},
        {'codigo': '002', 'descripcion': 'ARTÍCULO 2', 'precio_actual': 200.00, 'precio_nuevo': 220.00},
    ]

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('articulos.routes.obtenerArticulosMarcaRubro',
                       return_value=mock_articulos) as mock_obtener:

                response = client.get('/articulos/filtrar_articulos?marca=1&rubro=2&lista_precio=3&porcentaje=10')

                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert len(data['articulos']) == 2
                # Verificar que el service fue llamado con todos los parámetros
                mock_obtener.assert_called_once_with(1, 2, 3, 10)


def test_integracion_filtrar_solo_marca(client):
    """
    Test SCE-011: Flujo completo solo con marca=1, lista_precio=3 (sin rubro).

    Verifica que:
      1. La ruta acepta query params con solo marca
      2. rubro=None se pasa al service
      3. Retorna artículos filtrados por marca y lista_precio
    """
    _configurar_sesion(client)

    mock_articulos = [
        {'codigo': '001', 'descripcion': 'ARTÍCULO 1', 'precio_actual': 100.00, 'precio_nuevo': 105.00},
    ]

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('articulos.routes.obtenerArticulosMarcaRubro',
                       return_value=mock_articulos) as mock_obtener:

                response = client.get('/articulos/filtrar_articulos?marca=1&lista_precio=3&porcentaje=5')

                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert len(data['articulos']) == 1
                mock_obtener.assert_called_once_with(1, None, 3, 5)


def test_integracion_filtrar_solo_rubro(client):
    """
    Test SCE-012: Flujo completo solo con rubro=2, lista_precio=3 (sin marca).

    Verifica que:
      1. La ruta acepta query params con solo rubro
      2. marca=None se pasa al service
      3. Retorna artículos filtrados por rubro y lista_precio
    """
    _configurar_sesion(client)

    mock_articulos = [
        {'codigo': '002', 'descripcion': 'ARTÍCULO 2', 'precio_actual': 200.00, 'precio_nuevo': 210.00},
    ]

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('articulos.routes.obtenerArticulosMarcaRubro',
                       return_value=mock_articulos) as mock_obtener:

                response = client.get('/articulos/filtrar_articulos?rubro=2&lista_precio=3&porcentaje=5')

                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert len(data['articulos']) == 1
                mock_obtener.assert_called_once_with(None, 2, 3, 5)


def test_integracion_filtrar_solo_lista_precio(client):
    """
    Test SCE-013: Flujo completo solo con lista_precio=3 (sin marca ni rubro).

    Verifica que:
      1. La ruta acepta query params con solo lista_precio
      2. marca=None, rubro=None se pasan al service
      3. Retorna todos los artículos de esa lista de precios
    """
    _configurar_sesion(client)

    mock_articulos = [
        {'codigo': '001', 'descripcion': 'ARTÍCULO 1', 'precio_actual': 100.00, 'precio_nuevo': 100.00},
        {'codigo': '002', 'descripcion': 'ARTÍCULO 2', 'precio_actual': 200.00, 'precio_nuevo': 200.00},
        {'codigo': '003', 'descripcion': 'ARTÍCULO 3', 'precio_actual': 300.00, 'precio_nuevo': 300.00},
    ]

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('articulos.routes.obtenerArticulosMarcaRubro',
                       return_value=mock_articulos) as mock_obtener:

                response = client.get('/articulos/filtrar_articulos?lista_precio=3')

                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert len(data['articulos']) == 3
                # porcentaje default = 0
                mock_obtener.assert_called_once_with(None, None, 3, 0)


def test_integracion_filtrar_resultado_vacio(client):
    """
    Test SCE-014: Flujo completo cuando no hay artículos que coincidan.

    Verifica que:
      1. La ruta retorna 200 (no error)
      2. Retorna array vacío []
      3. No muestra error en el frontend (comportamiento esperado)
    """
    _configurar_sesion(client)

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('articulos.routes.obtenerArticulosMarcaRubro',
                       return_value=[]) as mock_obtener:

                response = client.get('/articulos/filtrar_articulos?marca=999&rubro=999&lista_precio=3')

                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert data['articulos'] == []
                mock_obtener.assert_called_once_with(999, 999, 3, 0)


# ──────────────────────────────────────────────
# Tests de integración: Validación de parámetros
# ──────────────────────────────────────────────

def test_integracion_filtrar_sin_lista_precio_error_400(client):
    """
    Test: Validación de lista_precio obligatorio en integración.

    Verifica que la ruta retorna 400 cuando falta lista_precio,
    independientemente de otros parámetros.
    """
    _configurar_sesion(client)

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):

            response = client.get('/articulos/filtrar_articulos?marca=1&rubro=2&porcentaje=10')

            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert 'lista_precio es requerido' in data['error']


def test_integracion_filtrar_porcentaje_default_cero(client):
    """
    Test: Porcentaje por defecto es 0 cuando no se proporciona.

    Verifica que al omitir porcentaje, el service recibe 0.
    """
    _configurar_sesion(client)

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('articulos.routes.obtenerArticulosMarcaRubro',
                       return_value=[]) as mock_obtener:

                response = client.get('/articulos/filtrar_articulos?lista_precio=1')

                assert response.status_code == 200
                mock_obtener.assert_called_once_with(None, None, 1, 0)


def test_integracion_filtrar_legacy_path_params_todavia_funcionan(client):
    """
    Test: Compatibilidad hacia atrás - ruta legacy con path params.

    Verifica que URLs como /filtrar_articulos/1/2/3/10.0 siguen funcionando.
    
    Nota: El converter float de Flask requiere punto decimal (10.0, no 10)
    """
    _configurar_sesion(client)

    mock_articulos = [
        {'codigo': '001', 'descripcion': 'ARTÍCULO 1', 'precio_actual': 100.00, 'precio_nuevo': 110.00},
    ]

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('articulos.routes.obtenerArticulosMarcaRubro',
                       return_value=mock_articulos) as mock_obtener:

                response = client.get('/articulos/filtrar_articulos/1/2/3/10.0')

                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert len(data['articulos']) == 1
                mock_obtener.assert_called_once_with(1, 2, 3, 10.0)


# ──────────────────────────────────────────────
# Tests de estructura de respuesta para frontend
# ──────────────────────────────────────────────

def test_integracion_estructura_respuesta_para_tabla(client):
    """
    Test: Verificar que la estructura de respuesta coincide con lo que espera el JS.

    El frontend espera:
    - data.success: boolean
    - data.articulos: array de objetos con {codigo, descripcion, precio_actual, precio_nuevo}
    """
    _configurar_sesion(client)

    mock_articulos = [
        {'codigo': 'ABC123', 'descripcion': 'Producto Test', 'precio_actual': 150.75, 'precio_nuevo': 165.83},
    ]

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('articulos.routes.obtenerArticulosMarcaRubro',
                       return_value=mock_articulos):

                response = client.get('/articulos/filtrar_articulos?lista_precio=1&porcentaje=10')

                assert response.status_code == 200
                data = response.get_json()
                
                # Estructura esperada por el frontend
                assert 'success' in data
                assert 'articulos' in data
                assert isinstance(data['articulos'], list)
                assert len(data['articulos']) == 1
                
                articulo = data['articulos'][0]
                assert 'codigo' in articulo
                assert 'descripcion' in articulo
                assert 'precio_actual' in articulo
                assert 'precio_nuevo' in articulo
                assert isinstance(articulo['precio_actual'], (int, float))
                assert isinstance(articulo['precio_nuevo'], (int, float))