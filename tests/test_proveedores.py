"""
Tests para las rutas de proveedores del proyecto CRM.

Verifica el comportamiento de las rutas HTTP del blueprint de proveedores.
Usamos unittest.mock (patch) para reemplazar consultas a la DB por objetos
simulados (MagicMock).

Estrategia de mocks:
  - check_session: se salva configurando la sesión con user_id
  - alertas_mensajes: se evita parcheando obtener_alertas y obtener_mensajes
  - Modelos (Proveedores, TipoDocumento, TipoIva, etc.): se parchea .query
    para retornar datos de prueba sin tocar la DB
  - Servicios (get_factura): se parchean para evitar DB real
  - render_template: se parchea para las rutas que renderizan templates
  - db.session.query: se parchea con un MagicMock encadenable para consultas
    con joins (compras)
"""

from unittest.mock import patch, MagicMock
from datetime import date


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
# Tests para GET /proveedores/proveedores/<id>
# ──────────────────────────────────────────────

def test_get_proveedores_existente(client):
    """
    Test GET /proveedores/proveedores/1 con proveedor existente.

    Verifica que:
      1. Responde con status 200 (OK)
      2. Se llama a render_template con 'proveedores.html'
      3. Se pasa el proveedor encontrado al template

    Para evitar la DB, parcheamos:
      - TipoDocumento.query → lista vacía
      - TipoIva.query → lista vacía
      - Proveedores.query → .all() con lista y .get() con proveedor mock
      - obtener_alertas y obtener_mensajes → retornan datos vacíos
      - render_template → retorna string vacío
    """
    _configurar_sesion(client)

    mock_proveedor = MagicMock()
    mock_proveedor.id = 1
    mock_proveedor.nombre = 'Proveedor Test'
    mock_proveedor.documento = '30-12345678-9'

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.proveedores.render_template', return_value='') as mock_render:
                with patch('models.configs.TipoDocumento.query') as mock_td:
                    mock_td.all.return_value = []

                    with patch('models.configs.TipoIva.query') as mock_ti:
                        mock_ti.all.return_value = []

                        with patch('models.proveedores.Proveedores.query') as mock_prov:
                            mock_prov.all.return_value = [mock_proveedor]

                            with patch('utils.db.db.session.get', return_value=mock_proveedor):

                                response = client.get('/proveedores/proveedores/1')

                                assert response.status_code == 200
                                mock_render.assert_called_once()
                                args, kwargs = mock_render.call_args
                                assert args[0] == 'proveedores.html'
                                # Verificar que se pasó el proveedor
                                assert kwargs.get('proveedor') is mock_proveedor


def test_get_proveedores_cero(client):
    """
    Test GET /proveedores/proveedores/0 sin proveedor seleccionado.

    Cuando id=0 (nuevo proveedor), la ruta debe pasar proveedor=[]
    al template en lugar de buscar por ID.

    Verifica que:
      1. Responde con status 200
      2. Se pasa proveedor=[] (lista vacía)
      3. NO se llama a Proveedores.query.get() (solo .all())
    """
    _configurar_sesion(client)

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.proveedores.render_template', return_value='') as mock_render:
                with patch('models.configs.TipoDocumento.query') as mock_td:
                    mock_td.all.return_value = []

                    with patch('models.configs.TipoIva.query') as mock_ti:
                        mock_ti.all.return_value = []

                        with patch('models.proveedores.Proveedores.query') as mock_prov:
                            mock_prov.all.return_value = []

                            # Con la corrección int(id) != 0, id='0' → int('0')=0,
                            # por lo que NO se entra al if y proveedor=[].
                            # .get() NO debe ser llamado.
                            mock_prov.get.return_value = None

                            response = client.get('/proveedores/proveedores/0')

                            assert response.status_code == 200
                            mock_render.assert_called_once()
                            args, kwargs = mock_render.call_args
                            assert args[0] == 'proveedores.html'
                            # id=0: no entra al if, proveedor queda como []
                            assert kwargs.get('proveedor') == []
                            # .get() NO se llamó porque int('0') == 0
                            mock_prov.get.assert_not_called()


# ──────────────────────────────────────────────
# Tests para GET /proveedores/compras
# ──────────────────────────────────────────────

def test_get_compras_con_fechas(client):
    """
    Test GET /proveedores/compras?desde=2024-01-01&hasta=2024-12-31.

    Verifica que:
      1. Responde con status 200
      2. Se llama a render_template con 'compras.html'
      3. Se pasan facturas, desde y hasta al template

    La ruta hace una consulta con joins entre FacturaC, Proveedores y
    TipoComprobantes. Parcheamos db.session.query para simular esta
    consulta sin tocar la base de datos.
    """
    _configurar_sesion(client)

    # Mock para una factura de compra
    mock_factura = MagicMock()
    mock_factura.id = 1
    mock_factura.fecha = date(2024, 6, 15)
    mock_factura.nro_comprobante = '0001-00000005'
    mock_factura.total = 50000.00
    mock_factura.tipo_comprobante = 'Factura A'
    mock_factura.proveedor = 'Proveedor Test'

    # Mock encadenable para db.session.query
    mock_db_query = MagicMock()
    mock_db_query.join.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.order_by.return_value = mock_db_query
    mock_db_query.all.return_value = [mock_factura]

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.proveedores.render_template', return_value='') as mock_render:
                with patch('utils.db.db.session.query',
                           return_value=mock_db_query):

                        response = client.get(
                            '/proveedores/compras?desde=2024-01-01&hasta=2024-12-31'
                        )

                        assert response.status_code == 200
                        mock_render.assert_called_once()
                        args, kwargs = mock_render.call_args
                        assert args[0] == 'compras.html'
                        # Verificar que se pasaron los datos
                        assert kwargs.get('facturas') == [mock_factura]
                        assert kwargs.get('desde') == '2024-01-01'
                        assert kwargs.get('hasta') == '2024-12-31'


def test_get_compras_sin_fechas(client):
    """
    Test GET /proveedores/compras sin parámetros de fecha.

    Cuando no se pasan desde/hasta, la ruta debe usar date.today()
    como valor por defecto.

    Verifica que responde 200 y renderiza el template.
    """
    _configurar_sesion(client)

    mock_db_query = MagicMock()
    mock_db_query.join.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.order_by.return_value = mock_db_query
    mock_db_query.all.return_value = []

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.proveedores.render_template', return_value='') as mock_render:
                with patch('utils.db.db.session.query',
                           return_value=mock_db_query):

                        response = client.get('/proveedores/compras')

                        assert response.status_code == 200
                        mock_render.assert_called_once()
                        args, kwargs = mock_render.call_args
                        assert args[0] == 'compras.html'


# ──────────────────────────────────────────────
# Tests para GET /proveedores/ver_factura_comp/<id>
# ──────────────────────────────────────────────

def test_get_ver_factura_comp(client):
    """
    Test GET /proveedores/ver_factura_comp/1 con factura existente.

    Verifica que:
      1. Responde con status 200
      2. Se llama a get_factura con el id correcto
      3. Se llama a render_template con 'factura-comp.html'
      4. Los datos de factura, items y pagos se pasan al template

    Parcheamos:
      - get_factura (de services.proveedores) → retorna datos mock
      - obtener_alertas y obtener_mensajes → retornan datos vacíos
      - render_template → retorna string vacío
    """
    _configurar_sesion(client)

    mock_factura = MagicMock()
    mock_factura.id = 1
    mock_factura.nro_comprobante = '0001-00000005'
    mock_factura.total = 50000.00
    mock_factura.proveedor_nombre = 'Proveedor Test'

    mock_items = [MagicMock()]
    mock_items[0].id = 1
    mock_items[0].detalle = 'Artículo de compra'

    mock_pagos = [MagicMock()]
    mock_pagos[0].total = 50000.00

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.proveedores.render_template', return_value='') as mock_render:
                with patch('routes.proveedores.get_factura',
                           return_value=(mock_factura, mock_items, mock_pagos)) as mock_get_factura:

                        response = client.get('/proveedores/ver_factura_comp/1')

                        assert response.status_code == 200
                        mock_get_factura.assert_called_once_with('1')
                        mock_render.assert_called_once()
                        args, kwargs = mock_render.call_args
                        assert args[0] == 'factura-comp.html'
                        # Verificar que se pasaron los datos al template
                        assert kwargs.get('factura') is mock_factura
                        assert kwargs.get('items') is mock_items
                        assert kwargs.get('pagos') is mock_pagos
