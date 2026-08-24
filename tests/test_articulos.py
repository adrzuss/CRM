"""
Tests para las rutas de artículos del proyecto CRM.

Verifica el comportamiento de las rutas HTTP del blueprint de artículos.
Usamos unittest.mock (patch) para reemplazar consultas a la DB y servicios
por objetos simulados (MagicMock).

Estrategia de mocks:
  - check_session: se salva configurando la sesión con user_id
  - alertas_mensajes: se evita parcheando obtener_alertas y obtener_mensajes
  - Modelos (Marca, Rubro, etc.): se parchean .query para retornar datos de prueba
  - Servicios (get_listado_articulos): se parchean para evitar DB real
  - render_template: se parchea para rutas que renderizan templates
  - Para endpoints JSON, NO se parchea render_template
  - db.session.query: se parchea con un MagicMock encadenable para rutas complejas
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
# Tests para GET /articulos/articulos
# ──────────────────────────────────────────────

def test_get_articulos_listado(client):
    """
    Test GET /articulos/articulos - listado principal de artículos.

    Verifica que:
      1. Responde con status 200
      2. Se consultan marcas y rubros ordenados por nombre
      3. Se llama a render_template con 'articulos.html'

    Parcheamos:
      - Marca.query → retorna marcas mock
      - Rubro.query → retorna rubros mock
      - obtener_alertas y obtener_mensajes → retornan datos vacíos
      - render_template → retorna string vacío
    """
    _configurar_sesion(client)

    mock_marca = MagicMock()
    mock_marca.id = 1
    mock_marca.nombre = 'Marca Test'

    mock_rubro = MagicMock()
    mock_rubro.id = 1
    mock_rubro.nombre = 'Rubro Test'

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.articulos.render_template', return_value='') as mock_render:
                with patch('models.articulos.Marca.query') as mock_marca_query:
                    mock_marca_query.order_by.return_value.all.return_value = [mock_marca]

                    with patch('models.articulos.Rubro.query') as mock_rubro_query:
                        mock_rubro_query.order_by.return_value.all.return_value = [mock_rubro]

                        response = client.get('/articulos/articulos')

                        assert response.status_code == 200
                        # Verificar render_template
                        mock_render.assert_called_once()
                        args, kwargs = mock_render.call_args
                        assert args[0] == 'articulos.html'
                        # Verificar que se pasaron marcas y rubros
                        assert kwargs.get('marcas') == [mock_marca]
                        assert kwargs.get('rubros') == [mock_rubro]


# ──────────────────────────────────────────────
# Tests para GET /articulos/api/articulos (DataTables)
# ──────────────────────────────────────────────

def test_api_articulos_datatables(client):
    """
    Test GET /articulos/api/articulos con parámetros de DataTables.

    Verifica que:
      1. Responde con status 200
      2. Retorna JSON con formato DataTables (draw, recordsTotal, data)
      3. Se llama a get_listado_articulos con los parámetros correctos

    NO se parchea render_template porque es un endpoint JSON.
    """
    _configurar_sesion(client)

    mock_data = [
        {'id': 1, 'codigo': '001', 'detalle': 'Artículo 1', 'costo': 100},
        {'id': 2, 'codigo': '002', 'detalle': 'Artículo 2', 'costo': 200},
    ]

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.articulos.get_listado_articulos',
                       return_value=(1, 2, 2, mock_data)) as mock_get_listado:

                    response = client.get('/articulos/api/articulos?draw=1&start=0&length=10')

                    assert response.status_code == 200
                    data = response.get_json()
                    assert data['draw'] == 1
                    assert data['recordsTotal'] == 2
                    assert data['recordsFiltered'] == 2
                    assert len(data['data']) == 2
                    # Verificar que el servicio fue llamado con los parámetros correctos
                    mock_get_listado.assert_called_once()
                    args, kwargs = mock_get_listado.call_args
                    # args: (idmarca, idrubro, verBaja, draw, search_value, start, length, order_column, order_dir)
                    assert args[3] == 1  # draw


def test_api_articulos_sin_resultados(client):
    """
    Test GET /articulos/api/articulos cuando no hay artículos.

    Verifica que retorna JSON con lista vacía cuando no hay resultados.
    """
    _configurar_sesion(client)

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.articulos.get_listado_articulos',
                       return_value=(1, 0, 0, [])):

                    response = client.get('/articulos/api/articulos?draw=1&start=0&length=10')

                    assert response.status_code == 200
                    data = response.get_json()
                    assert data['draw'] == 1
                    assert data['recordsTotal'] == 0
                    assert len(data['data']) == 0


# ──────────────────────────────────────────────
# Tests para GET /articulos/update_articulo/<id>
# ──────────────────────────────────────────────

def test_get_update_articulo_existente(client):
    """
    Test GET /articulos/update_articulo/1 con artículo existente.

    Esta ruta renderiza 'upd-articulos.html' con datos completos del artículo
    incluyendo marcas, rubros, IVA, IB, listas de precios, stocks, colores y
    detalles. Es la ruta más compleja del módulo artículos.

    Verifica que:
      1. Responde con status 200
      2. Se llama a render_template con 'upd-articulos.html'
      3. Se pasa el artículo encontrado al template

    Parcheamos a nivel de modelos y db.session.query para evitar
    cualquier consulta a la base de datos real.
    """
    _configurar_sesion(client)

    # Mock para el artículo
    mock_articulo = MagicMock()
    mock_articulo.id = 1
    mock_articulo.codigo = '001'
    mock_articulo.detalle = 'ARTÍCULO DE PRUEBA'
    mock_articulo.costo = 100
    mock_articulo.costo_total = 100
    mock_articulo.exento = 0
    mock_articulo.impint = 0
    mock_articulo.idiva = 1
    mock_articulo.idib = 1
    mock_articulo.idrubro = 1
    mock_articulo.idmarca = 1
    mock_articulo.idtipoarticulo = 1
    mock_articulo.es_compuesto = False
    mock_articulo.pedir_en_ventas = 'SI'
    mock_articulo.con_colores = False
    mock_articulo.con_talles = False

    # Mock encadenable para db.session.query
    mock_db_query = MagicMock()
    mock_db_query.outerjoin.return_value = mock_db_query
    mock_db_query.join.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.filter_by.return_value = mock_db_query
    mock_db_query.order_by.return_value = mock_db_query
    mock_db_query.all.return_value = []
    mock_db_query.first.return_value = None

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.articulos.render_template', return_value='') as mock_render:
                with patch('models.articulos.Marca.query') as mock_marca:
                    mock_marca.order_by.return_value.all.return_value = []

                    with patch('models.configs.AlcIva.query') as mock_iva:
                        mock_iva.all.return_value = []

                        with patch('models.configs.AlcIB.query') as mock_ib:
                            mock_ib.all.return_value = []

                            with patch('models.articulos.Rubro.query') as mock_rubro:
                                mock_rubro.order_by.return_value.all.return_value = []

                                with patch('models.configs.TipoArticulos.query') as mock_tipo:
                                    mock_tipo.all.return_value = []

                                    with patch('models.articulos.Colores.query') as mock_col:
                                        mock_col.all.return_value = []

                                        with patch('models.articulos.DetallesArticulos.query') as mock_det:
                                            mock_det.all.return_value = []

                                            with patch('utils.db.db.session.query',
                                                      return_value=mock_db_query):
                                              with patch('utils.db.db.session.get',
                                                        return_value=mock_articulo):

                                                            response = client.get(
                                                                '/articulos/update_articulo/1'
                                                            )

                                                            assert response.status_code == 200
                                                            mock_render.assert_called_once()
                                                            args, kwargs = mock_render.call_args
                                                            assert args[0] == 'upd-articulos.html'
                                                            # Verificar que se pasó el artículo
                                                            assert kwargs.get('articulo') is mock_articulo


def test_get_update_articulo_nuevo(client):
    """
    Test GET /articulos/update_articulo/0 para crear artículo nuevo.

    Cuando id=0, la ruta debe pasar articulo=[] (vacío) al template,
    junto con las listas de precios (vacíos).

    Verifica que:
      1. Responde con status 200
      2. Se pasa articulo=[] (lista vacía para artículo nuevo)
    """
    _configurar_sesion(client)

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.articulos.render_template', return_value='') as mock_render:
                with patch('models.articulos.Marca.query') as mock_marca:
                    mock_marca.order_by.return_value.all.return_value = []

                    with patch('models.configs.AlcIva.query') as mock_iva:
                        mock_iva.all.return_value = []

                        with patch('models.configs.AlcIB.query') as mock_ib:
                            mock_ib.all.return_value = []

                            with patch('models.articulos.Rubro.query') as mock_rubro:
                                mock_rubro.order_by.return_value.all.return_value = []

                                with patch('models.configs.TipoArticulos.query') as mock_tipo:
                                    mock_tipo.all.return_value = []

                                    with patch('models.articulos.ListasPrecios.query') as mock_lp:
                                        mock_lp.all.return_value = []

                                        with patch('models.articulos.Colores.query') as mock_col:
                                            mock_col.all.return_value = []

                                            with patch('models.articulos.DetallesArticulos.query') as mock_det:
                                                mock_det.all.return_value = []

                                                response = client.get(
                                                    '/articulos/update_articulo/0'
                                                )

                                                assert response.status_code == 200
                                                mock_render.assert_called_once()
                                                args, kwargs = mock_render.call_args
                                                assert args[0] == 'upd-articulos.html'
                                                # Para artículo nuevo, id=0 → articulo=[]
                                                assert kwargs.get('articulo') == []


# ──────────────────────────────────────────────
# Tests para GET /articulos/api/<id>/colores-detalles
# ──────────────────────────────────────────────

def test_get_articulo_colores_detalles(client):
    """
    Test GET /articulos/api/1/colores-detalles con artículo existente.

    Verifica que:
      1. Responde con status 200
      2. Retorna JSON con success=True
      3. Incluye colores, detalles y datos del artículo

    Este endpoint verifica sesión manualmente (user_id en session)
    y NO usa @check_session ni @alertas_mensajes.

    Parcheamos db.session.query para simular la consulta del artículo,
    colores y detalles.
    """
    _configurar_sesion(client)

    # Mock para el artículo
    mock_articulo_q = MagicMock()
    mock_articulo_q.id = 1
    mock_articulo_q.codigo = '001'
    mock_articulo_q.detalle = 'Artículo de prueba'

    # Mock para colores
    mock_color = MagicMock()
    mock_color.id = 1
    mock_color.nombre = 'Rojo'
    mock_color.color = '#FF0000'

    # Mock para detalles
    mock_detalle = MagicMock()
    mock_detalle.id = 1
    mock_detalle.nombre = 'Talle M'

    # Mock encadenable para db.session.query
    mock_db_query = MagicMock()

    def mock_query_side_effect(*args, **kwargs):
        """Retorna distintos mocks según la consulta."""
        # Para cada llamada a db.session.query, devolvemos un nuevo MagicMock
        # con la cadena completa configurada
        m = MagicMock()
        m.filter_by.return_value.first.side_effect = [
            mock_articulo_q,  # primera llamada: articulo
            None, None,       # siguientes llamadas
        ]
        m.join.return_value = m
        m.filter.return_value = m
        m.all.side_effect = [
            [mock_color],    # colores
            [mock_detalle],  # detalles
        ]
        return m

    with patch('utils.db.db.session.query') as mock_sq:
        # Configurar el mock para que filter_by().first() retorne el artículo mock
        first_query = MagicMock()
        first_query.filter_by.return_value.first.return_value = mock_articulo_q

        join_query = MagicMock()
        join_query.join.return_value = join_query
        join_query.filter.return_value = join_query

        # Configurar 3 llamadas: articulo, colores, detalles
        mock_sq.side_effect = [
            first_query,         # 1ra llamada: artículo
            join_query,          # 2da llamada: colores
            join_query,          # 3ra llamada: detalles
        ]

        # Configurar .all() para cada join_query
        join_query.all.side_effect = [
            [mock_color],    # colores
            [mock_detalle],  # detalles
        ]

        response = client.get('/articulos/api/1/colores-detalles')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['colores']) == 1
        assert data['colores'][0]['nombre'] == 'Rojo'
        assert len(data['detalles']) == 1
        assert data['detalles'][0]['nombre'] == 'Talle M'
        assert data['articulo']['id'] == 1
        assert data['articulo']['codigo'] == '001'


def test_get_articulo_colores_detalles_no_encontrado(client):
    """
    Test GET /articulos/api/999/colores-detalles con artículo inexistente.

    Verifica que retorna 404 cuando el artículo no existe.
    """
    _configurar_sesion(client)

    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = None

    with patch('utils.db.db.session.query', return_value=mock_query):
        response = client.get('/articulos/api/999/colores-detalles')

        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'Artículo no encontrado' in data['message']


# ──────────────────────────────────────────────
# Tests para GET /articulos/api/lst_stock_sucursales (DataTables)
# ──────────────────────────────────────────────

def test_api_lst_stock_sucursales_sin_parametros(client):
    """
    Test GET /articulos/api/lst_stock_sucursales sin query string.

    Verifica que:
      1. Responde con status 200 (nunca 500)
      2. Retorna JSON con formato DataTables (draw=1 default, recordsTotal=0, data=[])
      3. No se invoca obtener_stock_sucursales (el guard de filtro vacío corta antes)

    NO se parchea render_template porque es un endpoint JSON.
    """
    _configurar_sesion(client)

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.articulos.obtener_stock_sucursales') as mock_service:

                    response = client.get('/articulos/api/lst_stock_sucursales')

                    assert response.status_code == 200
                    data = response.get_json()
                    assert data['draw'] == 1
                    assert data['recordsTotal'] == 0
                    assert data['recordsFiltered'] == 0
                    assert data['data'] == []
                    # El guard retorna antes de ejecutar el service
                    mock_service.assert_not_called()


def test_api_lst_stock_sucursales_sin_order_column(client):
    """
    Test GET /articulos/api/lst_stock_sucursales con filtros y sin order[0][column].

    Verifica que:
      1. Responde con status 200
      2. Retorna JSON con formato DataTables (draw echo)
      3. El service se llama con order_column=0 (default del handler)

    NO se parchea render_template porque es un endpoint JSON.
    """
    _configurar_sesion(client)

    mock_data = [
        {'id': 1, 'codigo': '001', 'detalle': 'Artículo 1'},
        {'id': 2, 'codigo': '002', 'detalle': 'Artículo 2'},
    ]

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)):
        with patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
            with patch('routes.articulos.obtener_stock_sucursales',
                       return_value=(1, 2, 2, mock_data, ['id', 'codigo', 'detalle'])) as mock_service:

                    response = client.get('/articulos/api/lst_stock_sucursales?idmarca=1&idrubro=1&draw=1')

                    assert response.status_code == 200
                    data = response.get_json()
                    assert data['draw'] == 1
                    assert data['recordsTotal'] == 2
                    assert data['recordsFiltered'] == 2
                    assert len(data['data']) == 2
                    # Verificar que el service fue llamado con order_column=0 (default)
                    mock_service.assert_called_once()
                    args, kwargs = mock_service.call_args
                    # args: (idmarca, idrubro, draw, search_value, start, length, order_column, order_dir)
                    assert args[0] == 1  # idmarca
                    assert args[1] == 1  # idrubro
                    assert args[2] == 1  # draw
                    assert args[6] == 0  # order_column default
