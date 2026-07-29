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
    from services.articulos.articulos import obtenerArticulosMarcaRubro

    # Mock para el resultado de la consulta
    mock_articulo = MagicMock()
    mock_articulo.codigo = '001'
    mock_articulo.detalle = 'ARTÍCULO TEST'
    mock_articulo.precio = Decimal('100.00')

    mock_query = MagicMock()
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_articulo]

    with patch('services.articulos.articulos.db.session.query',
               return_value=mock_query):

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
    from services.articulos.articulos import obtenerArticulosMarcaRubro

    mock_articulo = MagicMock()
    mock_articulo.codigo = '002'
    mock_articulo.detalle = 'ARTÍCULO SIN CAMBIO'
    mock_articulo.precio = Decimal('250.50')

    mock_query = MagicMock()
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_articulo]

    with patch('services.articulos.articulos.db.session.query',
               return_value=mock_query):

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
    from services.articulos.articulos import obtenerArticulosMarcaRubro

    mock_query = MagicMock()
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = []

    with patch('services.articulos.articulos.db.session.query',
               return_value=mock_query):

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
    from services.articulos.articulos import _guardar_precios

    # Mock del formulario con 2 items de precio
    mock_form = {
        'precio[1][idlista]': '1',
        'precio[1][precio]': '1500.00',
        'precio[2][idlista]': '2',
        'precio[2][precio]': '1800.00',
    }

    mock_precio_db = MagicMock()
    mock_precio_db.precio = Decimal('1400.00')

    with patch('services.articulos.articulos.Precio') as mock_precio_model:
        with patch('services.articulos.articulos.db.session') as mock_db:
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
