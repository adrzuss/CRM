"""
Tests para los servicios de artículos del proyecto CRM.

Verifica funciones del módulo services/articulos con mocking de DB.
La mayoría de las funciones en services/articulos dependen de db.session,
por lo que testeamos aquellas que tienen lógica de negocio significativa
más allá de simples consultas.

Funciones testeadas:
  - obtenerArticulosMarcaRubro: cálculo de precios nuevos con porcentaje
  - _guardar_precios: procesamiento de formulario de precios

Estrategia de mocks:
  - db.session.query: se parchea para simular consultas
  - Modelos (Articulo, Precio, etc.): se parchean según corresponda
"""

from unittest.mock import patch, MagicMock
from decimal import Decimal


# ──────────────────────────────────────────────
# Tests para obtenerArticulosMarcaRubro
# ──────────────────────────────────────────────

def test_obtener_articulos_marca_rubro_con_porcentaje():
    """
    Test obtenerArticulosMarcaRubro con marca y rubro específicos.

    Verifica que:
      - Se calcula precio_nuevo = precio_actual * (1 + porcentaje / 100)
      - Con porcentaje=10, precio_actual=100 → precio_nuevo=110
      - Los resultados se ordenan correctamente

    Se parchea db.session.query y sus encadenamientos para simular
    resultados de la DB sin conexión real.
    """
    from articulos.services.articulos import obtenerArticulosMarcaRubro

    # Mock para el resultado de la consulta
    mock_articulo = MagicMock()
    mock_articulo.codigo = '001'
    mock_articulo.detalle = 'ARTÍCULO TEST'
    mock_articulo.precio = Decimal('100.00')

    mock_query = MagicMock()
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_articulo]

    with patch('articulos.services.articulos.db.session.query',
               return_value=mock_query):
        with patch('articulos.services.articulos.ReglaRedondeo') as mock_regla:
            mock_regla.query.filter_by.return_value.all.return_value = []

            resultado = obtenerArticulosMarcaRubro(
                marca=1, rubro=1, lista_precio=1, porcentaje=10
            )

            assert len(resultado) == 1
            assert resultado[0]['codigo'] == '001'
            assert resultado[0]['descripcion'] == 'ARTÍCULO TEST'
            assert resultado[0]['precio_actual'] == Decimal('100.00')
            # 100 * (1 + 10/100) = 110
            assert resultado[0]['precio_nuevo'] == Decimal('110.00')


def test_obtener_articulos_marca_rubro_porcentaje_cero():
    """
    Test obtenerArticulosMarcaRubro con porcentaje=0 (sin cambio de precio).

    Verifica que precio_nuevo == precio_actual cuando el porcentaje es 0.
    """
    from articulos.services.articulos import obtenerArticulosMarcaRubro

    mock_articulo = MagicMock()
    mock_articulo.codigo = '002'
    mock_articulo.detalle = 'ARTÍCULO SIN CAMBIO'
    mock_articulo.precio = Decimal('250.50')

    mock_query = MagicMock()
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_articulo]

    with patch('articulos.services.articulos.db.session.query',
               return_value=mock_query):
        with patch('articulos.services.articulos.ReglaRedondeo') as mock_regla:
            mock_regla.query.filter_by.return_value.all.return_value = []

            resultado = obtenerArticulosMarcaRubro(
                marca=0, rubro=0, lista_precio=1, porcentaje=0
            )

            assert len(resultado) == 1
            # 250.50 * (1 + 0/100) = 250.50
            assert resultado[0]['precio_nuevo'] == Decimal('250.50')
            assert resultado[0]['precio_actual'] == resultado[0]['precio_nuevo']


def test_obtener_articulos_marca_rubro_sin_resultados():
    """
    Test obtenerArticulosMarcaRubro cuando no hay artículos
    que coincidan con los filtros.

    Verifica que retorna lista vacía.
    """
    from articulos.services.articulos import obtenerArticulosMarcaRubro

    mock_query = MagicMock()
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = []

    with patch('articulos.services.articulos.db.session.query',
               return_value=mock_query):
        with patch('articulos.services.articulos.ReglaRedondeo') as mock_regla:
            mock_regla.query.filter_by.return_value.all.return_value = []

            resultado = obtenerArticulosMarcaRubro(
                marca=99, rubro=99, lista_precio=1, porcentaje=10
            )

            assert resultado == []


# ──────────────────────────────────────────────
# Tests para _guardar_precios
# ──────────────────────────────────────────────

def test_guardar_precios_procesa_items_del_formulario():
    """
    Test _guardar_precios verifica que procesa correctamente
    los items de precio del formulario.

    Verifica:
      - Cuenta la cantidad de items con 'precio[i][precio]'
      - Itera sobre cada item llamando a Precio.query.get

    Se parchea Precio y db.session para evitar DB real.
    """
    from articulos.services.articulos import _guardar_precios

    # Mock del formulario con 2 items de precio
    mock_form = {
        'precio[1][idlista]': '1',
        'precio[1][precio]': '1500.00',
        'precio[2][idlista]': '2',
        'precio[2][precio]': '1800.00',
    }

    mock_precio_db = MagicMock()
    mock_precio_db.precio = Decimal('1400.00')

    with patch('articulos.services.articulos.Precio') as mock_precio_model:
        with patch('articulos.services.articulos.db.session') as mock_db:
            mock_db.add.return_value = None

            # Simular que el primer precio existe, el segundo no
            mock_db.get.side_effect = [
                mock_precio_db,   # precio[1] existe → se actualiza
                None,             # precio[2] no existe → se crea
            ]

            _guardar_precios(mock_form, id_original=1, idarticulo=1)

                # Verificar que se llamó a db.session.get para cada item
            assert mock_db.get.call_count == 2
            # Verificar que el precio existente se actualizó con el valor string
            # del formulario (el string se asigna directamente desde el form)
            assert mock_precio_db.precio == '1500.00'
            # Verificar que se creó un nuevo precio (segundo item)
            assert mock_precio_model.call_count == 1


# ──────────────────────────────────────────────
# Tests para procesar_cambio_precio (validación de items vacíos)
# ──────────────────────────────────────────────

def test_procesar_cambio_precio_con_items_validos():
    """
    Test SCE-007: procesar_cambio_precio con items válidos procesa correctamente.

    Verifica que:
      1. Crea un registro CambioPrecios
      2. Procesa cada item creando CambioPreciosItem
      3. Actualiza los precios en la tabla Precio
      4. Hace commit de la transacción
    """
    from articulos.services.precios import procesar_cambio_precio

    # Mock del formulario con 1 item
    mock_form = {
        'fecha': '2024-01-15',
        'lista_precio': '1',
        'items[0][codigo]': '001',
        'items[0][precio_actual]': '100.00',
        'items[0][precio_nuevo]': '110.00',
    }

    # Crear un objeto simple para el artículo (no MagicMock) para que .id sea un int real
    class MockArticulo:
        id = 1
    
    mock_articulo = MockArticulo()

    mock_cambio_precio = MagicMock()
    mock_cambio_precio.id = 10

    with patch('articulos.services.precios.session', {'user_id': 1, 'id_sucursal': 1}):
        with patch('articulos.services.precios.CambioPrecios', return_value=mock_cambio_precio) as mock_cp:
            with patch('articulos.services.precios.db.session') as mock_db:
                with patch('articulos.services.precios.CambioPreciosItem') as mock_cpi:
                    with patch('articulos.services.precios.actualizarPrecio') as mock_actualizar:
                        # Configurar mock para db.session.query(Articulo).filter_by(...).first()
                        mock_query = MagicMock()
                        mock_query.filter_by.return_value.first.return_value = mock_articulo
                        mock_db.query.return_value = mock_query
                        mock_db.flush.return_value = None
                        mock_db.commit.return_value = None

                        procesar_cambio_precio(mock_form)

                        # Verificar que se creó el cambio de precios
                        mock_cp.assert_called_once_with('2024-01-15', 1, 1, '1')
                        mock_db.add.assert_any_call(mock_cambio_precio)
                        mock_db.flush.assert_called_once()
                        # Verificar que se llamó a db.session.query con Articulo
                        mock_db.query.assert_called()
                        # Verificar que se creó el item
                        mock_cpi.assert_called_once()
                        # Verificar que se actualizó el precio (articulo.id = 1)
                        mock_actualizar.assert_called_once_with('1', 1, '110.00')
                        mock_db.commit.assert_called_once()


def test_procesar_cambio_precio_sin_items_lanza_error():
    """
    Test SCE-008: procesar_cambio_precio sin items lanza error y no modifica DB.

    Verifica que:
      1. Lanza Exception con mensaje indicando que se requieren items
      2. No se llama a db.session.commit
      3. Se hace rollback de la transacción
    """
    from articulos.services.precios import procesar_cambio_precio

    # Mock del formulario SIN items (solo headers)
    mock_form = {
        'fecha': '2024-01-15',
        'lista_precio': '1',
    }

    with patch('articulos.services.precios.session', {'user_id': 1, 'id_sucursal': 1}):
        with patch('articulos.services.precios.db.session') as mock_db:
            mock_db.rollback.return_value = None

            try:
                procesar_cambio_precio(mock_form)
                assert False, "Debería haber lanzado una excepción"
            except Exception as e:
                assert 'sin items' in str(e).lower() or 'items' in str(e).lower()

            # Verificar que NO se hizo commit, pero SÍ rollback
            mock_db.commit.assert_not_called()
            mock_db.rollback.assert_called()


def test_procesar_cambio_precio_items_agregados_manualmente():
    """
    Test SCE-009: procesar_cambio_precio con items agregados manualmente (no por filtro).

    Verifica que la validación de items pasa cuando el usuario agrega
    filas manualmente en la tabla (simula formulario con items).
    """
    from articulos.services.precios import procesar_cambio_precio

    # Mock del formulario con 2 items agregados manualmente
    mock_form = {
        'fecha': '2024-01-15',
        'lista_precio': '1',
        'items[0][codigo]': '001',
        'items[0][precio_actual]': '100.00',
        'items[0][precio_nuevo]': '110.00',
        'items[1][codigo]': '002',
        'items[1][precio_actual]': '200.00',
        'items[1][precio_nuevo]': '220.00',
    }

    mock_articulo_1 = MagicMock()
    mock_articulo_1.id = 1
    mock_articulo_2 = MagicMock()
    mock_articulo_2.id = 2

    mock_cambio_precio = MagicMock()
    mock_cambio_precio.id = 10

    with patch('articulos.services.precios.session', {'user_id': 1, 'id_sucursal': 1}):
        with patch('articulos.services.precios.CambioPrecios', return_value=mock_cambio_precio) as mock_cp:
            with patch('articulos.services.precios.db.session') as mock_db:
                with patch('articulos.services.precios.Articulo') as mock_articulo_model:
                    with patch('articulos.services.precios.CambioPreciosItem') as mock_cpi:
                        with patch('articulos.services.precios.actualizarPrecio') as mock_actualizar:
                            # Configurar mocks para devolver artículos diferentes según el código
                            def mock_filter_by(**kwargs):
                                m = MagicMock()
                                if kwargs.get('codigo') == '001':
                                    m.first.return_value = mock_articulo_1
                                elif kwargs.get('codigo') == '002':
                                    m.first.return_value = mock_articulo_2
                                else:
                                    m.first.return_value = None
                                return m
                            
                            mock_articulo_model.query.filter_by.side_effect = mock_filter_by
                            mock_db.flush.return_value = None
                            mock_db.commit.return_value = None

                            procesar_cambio_precio(mock_form)

                            # Verificar que se procesaron ambos items
                            assert mock_cpi.call_count == 2
                            assert mock_actualizar.call_count == 2
                            mock_db.commit.assert_called_once()
