"""
Tests para las rutas de ventas del proyecto CRM.

Verifica el comportamiento de las rutas HTTP del blueprint de ventas.
Usamos unittest.mock (patch) para reemplazar consultas a la DB y servicios
por objetos simulados (MagicMock).

Estrategia de mocks:
  - check_session: se salva configurando la sesión con user_id
  - alertas_mensajes: se evita parcheando obtener_alertas y obtener_mensajes
  - Servicios (ventas_desde_hasta, get_factura, get_comprobantes_para_nc):
    se parchean para evitar llamadas a la DB real
  - render_template: se parchea para las rutas que renderizan templates
  - Para endpoints JSON, NO se parchea render_template
"""

from unittest.mock import patch, MagicMock


def _configurar_sesion(client):
    """
    Configura datos de sesión para que el decorador @check_session
    no redirija al login.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['tipo_iva'] = '1'
        sess['id_empresa'] = 1
        sess['permisos_menu'] = []


# ──────────────────────────────────────────────
# Tests para GET /ventas/ventas
# ──────────────────────────────────────────────

def test_get_ventas_con_fechas(client):
    """
    Test GET /ventas/ventas?desde=2024-01-01&hasta=2024-12-31.

    Verifica que:
      1. Responde con status 200 (OK)
      2. Se llama a ventas_desde_hasta con las fechas correspondientes
      3. Se llama a render_template con la plantilla 'ventas.html'

    Para evitar la DB, parcheamos:
      - ventas_desde_hasta → retorna lista vacía
      - obtener_alertas y obtener_mensajes → retornan datos vacíos
      - render_template → retorna string vacío
    """
    _configurar_sesion(client)

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.ventas.render_template', return_value='') as mock_render:
                with patch('routes.ventas.ventas_desde_hasta', return_value=[]) as mock_ventas:

                    response = client.get('/ventas/ventas?desde=2024-01-01&hasta=2024-12-31')

                    assert response.status_code == 200
                    # Verificar que se llamó a ventas_desde_hasta con fechas correctas
                    mock_ventas.assert_called_once_with('2024-01-01', '2024-12-31')
                    # Verificar que se llamó a render_template con la plantilla correcta
                    mock_render.assert_called_once()
                    args, kwargs = mock_render.call_args
                    assert args[0] == 'ventas.html'


# ──────────────────────────────────────────────
# Tests para GET /ventas/ver_factura_vta/<id>
# ──────────────────────────────────────────────

def test_get_ver_factura_vta(client):
    """
    Test GET /ventas/ver_factura_vta/1 con factura existente.

    Verifica que:
      1. Responde con status 200
      2. Se llama a get_factura con el id correcto
      3. Se llama a render_template con 'factura-vta.html'
      4. Los datos de factura, items y pagos se pasan al template

    Para evitar la DB, parcheamos:
      - get_factura → retorna (mock_factura, mock_items, mock_pagos)
      - obtener_alertas y obtener_mensajes → retornan datos vacíos
      - render_template → retorna string vacío
    """
    _configurar_sesion(client)

    # Mocks para los datos de la factura
    mock_factura = MagicMock()
    mock_factura.id = 1
    mock_factura.nro_comprobante = '0001-00000005'
    mock_factura.total = 12100.00

    mock_items = [MagicMock()]
    mock_items[0].id = 1
    mock_items[0].detalle = 'Artículo de prueba'

    mock_pagos = [MagicMock()]
    mock_pagos[0].total = 12100.00

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.ventas.render_template', return_value='') as mock_render:
                with patch('routes.ventas.get_factura',
                           return_value=(mock_factura, mock_items, mock_pagos)) as mock_get_factura:

                    response = client.get('/ventas/ver_factura_vta/1')

                    assert response.status_code == 200
                    mock_get_factura.assert_called_once_with('1')
                    mock_render.assert_called_once()
                    args, kwargs = mock_render.call_args
                    assert args[0] == 'factura-vta.html'
                    # Verificar que se pasaron los datos al template
                    assert kwargs.get('factura') is mock_factura
                    assert kwargs.get('items') is mock_items
                    assert kwargs.get('pagos') is mock_pagos


# ──────────────────────────────────────────────
# Tests para POST /ventas/buscar_comprobantes_nc
# ──────────────────────────────────────────────

def test_buscar_comprobantes_nc(client):
    """
    Test POST /ventas/buscar_comprobantes_nc con fecha válida.

    Verifica que:
      1. Responde con status 200
      2. Retorna JSON con success=True
      3. Incluye lista de comprobantes encontrados

    Este endpoint es JSON (no renderiza template), por lo que
    NO se parchea render_template.
    Tampoco tiene @alertas_mensajes, solo @check_session.

    Parcheamos:
      - get_comprobantes_para_nc → retorna lista con comprobantes mock
    """
    _configurar_sesion(client)

    mock_comprobantes = [
        {'id': 1, 'nro_comprobante': '0001-00000005', 'total': 12100.00},
        {'id': 2, 'nro_comprobante': '0001-00000006', 'total': 8500.00},
    ]

    with patch('routes.ventas.get_comprobantes_para_nc',
               return_value=mock_comprobantes) as mock_get_comp:

            response = client.post(
                '/ventas/buscar_comprobantes_nc',
                json={'fecha': '2024-06-15', 'nro_comprobante': ''}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert len(data['comprobantes']) == 2
            assert data['cantidad'] == 2
            # Verificar que se llamó al servicio con los parámetros correctos
            mock_get_comp.assert_called_once_with('2024-06-15', '2024-06-15', '')


def test_buscar_comprobantes_nc_sin_fecha(client):
    """
    Test POST /ventas/buscar_comprobantes_nc sin proporcionar fecha.

    Verifica que retorna 400 con mensaje de error cuando falta la fecha.
    """
    _configurar_sesion(client)

    with patch('routes.ventas.get_comprobantes_para_nc') as mock_get_comp:
        response = client.post(
            '/ventas/buscar_comprobantes_nc',
            json={'nro_comprobante': ''}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Debe proporcionar una fecha' in data['message']
        # El servicio no debe llamarse si falta la fecha
        mock_get_comp.assert_not_called()
