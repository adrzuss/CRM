"""
Tests para el módulo de redondeo de precios.

Verifica las funciones puras de redondeo comercial:
  - aplicar_redondeo: arriba, abajo, cercano, restar, edge cases
  - calcular_precio_comercial: regla encontrada, sin regla, múltiples reglas
"""

from unittest.mock import patch, MagicMock
from decimal import Decimal


# ──────────────────────────────────────────────
# Tests para aplicar_redondeo
# ──────────────────────────────────────────────

def test_aplicar_redondeo_arriba():
    """SCE-001: redondeo hacia arriba al múltiplo más cercano."""
    from articulos.services.redondeo import aplicar_redondeo

    assert aplicar_redondeo(4327, multiplo=100, tipo='arriba') == 4400
    assert aplicar_redondeo(1501, multiplo=1000, tipo='arriba') == 2000
    assert aplicar_redondeo(100, multiplo=100, tipo='arriba') == 100  # ya es múltiplo exacto


def test_aplicar_redondeo_abajo():
    """SCE-002: redondeo hacia abajo al múltiplo más cercano."""
    from articulos.services.redondeo import aplicar_redondeo

    assert aplicar_redondeo(4327, multiplo=100, tipo='abajo') == 4300
    assert aplicar_redondeo(1999, multiplo=1000, tipo='abajo') == 1000
    assert aplicar_redondeo(100, multiplo=100, tipo='abajo') == 100  # ya es múltiplo exacto


def test_aplicar_redondeo_cercano():
    """SCE-003: redondeo al múltiplo más cercano."""
    from articulos.services.redondeo import aplicar_redondeo

    assert aplicar_redondeo(4327, multiplo=100, tipo='cercano') == 4300  # 4327/100=43.27 -> round=43 -> 4300
    assert aplicar_redondeo(4350, multiplo=100, tipo='cercano') == 4400  # 4350/100=43.5 -> round=44 -> 4400
    assert aplicar_redondeo(4349, multiplo=100, tipo='cercano') == 4300  # 4349/100=43.49 -> round=43 -> 4300


def test_aplicar_redondeo_con_restar():
    """SCE-004: redondeo con resta de unidades."""
    from articulos.services.redondeo import aplicar_redondeo

    assert aplicar_redondeo(4327, multiplo=100, tipo='arriba', restar=1) == 4399
    assert aplicar_redondeo(4327, multiplo=100, tipo='arriba', restar=50) == 4350
    assert aplicar_redondeo(100, multiplo=100, tipo='arriba', restar=100) == 0  # 100 - 100 = 0
    assert aplicar_redondeo(50, multiplo=100, tipo='arriba', restar=200) == 100  # no resta si resultado < restar


def test_aplicar_redondeo_multiplo_cero():
    """Edge case: multiplo <= 0 retorna precio redondeado a 2 decimales."""
    from articulos.services.redondeo import aplicar_redondeo

    assert aplicar_redondeo(4327.567, multiplo=0, tipo='arriba') == 4327.57
    assert aplicar_redondeo(100.1, multiplo=-10, tipo='abajo') == 100.1


def test_aplicar_redondeo_precio_exacto_multiplo():
    """Edge case: precio es exactamente múltiplo, no cambia."""
    from articulos.services.redondeo import aplicar_redondeo

    assert aplicar_redondeo(4300, multiplo=100, tipo='arriba') == 4300
    assert aplicar_redondeo(4300, multiplo=100, tipo='abajo') == 4300
    assert aplicar_redondeo(4300, multiplo=100, tipo='cercano') == 4300


def test_aplicar_redondeo_restar_cero():
    """Edge case: restar=0 no modifica el resultado."""
    from articulos.services.redondeo import aplicar_redondeo

    assert aplicar_redondeo(4327, multiplo=100, tipo='arriba', restar=0) == 4400


# ──────────────────────────────────────────────
# Tests para calcular_precio_comercial
# ──────────────────────────────────────────────

def test_calcular_precio_comercial_regla_encontrada():
    """Regla encontrada: aplica redondeo según la regla del rango."""
    from articulos.services.redondeo import calcular_precio_comercial

    reglas = [{
        'desde_precio': 1000,
        'hasta_precio': 10000,
        'multiplo': 100,
        'tipo_redondeo': 'arriba',
        'restar_unidades': 0
    }]

    # precio_lista=4000, aumento=10% -> 4400 -> redondeo arriba al múltiplo 100 -> 4400 (ya es múltiplo)
    resultado = calcular_precio_comercial(4000, 10, reglas)
    assert resultado == 4400

    # precio_lista=4000, aumento=5% -> 4200 -> arriba al 100 -> 4200 (ya es múltiplo)
    resultado = calcular_precio_comercial(4000, 5, reglas)
    assert resultado == 4200

    # precio_lista=4000, aumento=8% -> 4320 -> arriba al 100 -> 4400
    resultado = calcular_precio_comercial(4000, 8, reglas)
    assert resultado == 4400


def test_calcular_precio_comercial_sin_regla():
    """Sin regla aplicable: retorna precio con 2 decimales, sin redondeo comercial."""
    from articulos.services.redondeo import calcular_precio_comercial

    resultado = calcular_precio_comercial(4000, 10, [])
    assert resultado == round(4000 * 1.1, 2)  # 4400.0

    # Precio que no cae en ningún rango
    reglas = [{
        'desde_precio': 5000,
        'hasta_precio': 10000,
        'multiplo': 100,
        'tipo_redondeo': 'arriba',
        'restar_unidades': 0
    }]
    resultado = calcular_precio_comercial(1000, 10, reglas)
    assert resultado == round(1000 * 1.1, 2)  # 1100.0, fuera de rango 5000-10000


def test_calcular_precio_comercial_multiples_reglas():
    """Múltiples reglas: selecciona la primera que coincida por rango."""
    from articulos.services.redondeo import calcular_precio_comercial

    reglas = [
        {
            'desde_precio': 0,
            'hasta_precio': 2000,
            'multiplo': 10,
            'tipo_redondeo': 'cercano',
            'restar_unidades': 0
        },
        {
            'desde_precio': 2000,
            'hasta_precio': 10000,
            'multiplo': 100,
            'tipo_redondeo': 'arriba',
            'restar_unidades': 0
        },
    ]

    # precio=1000, aumento=5% -> 1050, cae en rango 0-2000 -> cercano al 10 -> 1050 (ya es múltiplo de 10)
    resultado = calcular_precio_comercial(1000, 5, reglas)
    assert resultado == 1050

    # precio=4000, aumento=10% -> 4400, cae en rango 2000-10000 -> arriba al 100 -> 4400
    resultado = calcular_precio_comercial(4000, 10, reglas)
    assert resultado == 4400

    # precio=4000, aumento=8% -> 4320, cae en rango 2000-10000 -> arriba al 100 -> 4400
    resultado = calcular_precio_comercial(4000, 8, reglas)
    assert resultado == 4400


def test_calcular_precio_comercial_con_restar():
    """Regla con restar_unidades: aplica resta después del redondeo."""
    from articulos.services.redondeo import calcular_precio_comercial

    reglas = [{
        'desde_precio': 1000,
        'hasta_precio': 10000,
        'multiplo': 100,
        'tipo_redondeo': 'arriba',
        'restar_unidades': 1
    }]

    # precio=4000, aumento=8% -> 4320 -> arriba al 100 = 4400 -> restar 1 = 4399
    resultado = calcular_precio_comercial(4000, 8, reglas)
    assert resultado == 4399


# ──────────────────────────────────────────────
# Tests de integración: obtenerArticulosMarcaRubro con reglas
# ──────────────────────────────────────────────

def test_obtener_articulos_con_redondeo_activo():
    """
    Integración: obtenerArticulosMarcaRubro aplica redondeo cuando hay reglas activas.
    Mockea ReglaRedondeo.query y db.session.query para verificar que
    el precio_nuevo usa calcular_precio_comercial en vez del cálculo directo.
    """
    from articulos.services.articulos import obtenerArticulosMarcaRubro

    mock_articulo = MagicMock()
    mock_articulo.codigo = '001'
    mock_articulo.detalle = 'ARTÍCULO TEST'
    mock_articulo.precio = Decimal('4000.00')

    mock_query = MagicMock()
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_articulo]

    mock_regla = MagicMock()
    mock_regla.desde_precio = Decimal('1000')
    mock_regla.hasta_precio = Decimal('10000')
    mock_regla.multiplo = 100
    mock_regla.tipo_redondeo = 'arriba'
    mock_regla.restar_unidades = 0

    with patch('articulos.services.articulos.db.session.query',
               return_value=mock_query):
        with patch('articulos.services.articulos.ReglaRedondeo') as mock_model:
            mock_model.query.filter_by.return_value.all.return_value = [mock_regla]

            resultado = obtenerArticulosMarcaRubro(
                marca=1, rubro=1, lista_precio=1, porcentaje=8
            )

            assert len(resultado) == 1
            # 4000 * 1.08 = 4320 -> arriba al 100 = 4400
            assert resultado[0]['precio_nuevo'] == Decimal('4400')


def test_obtener_articulos_sin_reglas_mantiene_calculo_original():
    """
    Integración: sin reglas activas, el cálculo es precio * (1 + porcentaje/100).
    Verifica backward compatibility.
    """
    from articulos.services.articulos import obtenerArticulosMarcaRubro

    mock_articulo = MagicMock()
    mock_articulo.codigo = '002'
    mock_articulo.detalle = 'ARTÍCULO SIN REGLA'
    mock_articulo.precio = Decimal('100.00')

    mock_query = MagicMock()
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_articulo]

    with patch('articulos.services.articulos.db.session.query',
               return_value=mock_query):
        with patch('articulos.services.articulos.ReglaRedondeo') as mock_model:
            mock_model.query.filter_by.return_value.all.return_value = []

            resultado = obtenerArticulosMarcaRubro(
                marca=1, rubro=1, lista_precio=1, porcentaje=10
            )

            assert len(resultado) == 1
            # Sin reglas: 100 * 1.10 = 110.0 (passthrough con round 2 decimales)
            assert resultado[0]['precio_nuevo'] == Decimal('110')
