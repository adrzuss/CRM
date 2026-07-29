"""
Tests para las funciones auxiliares (utils) del proyecto CRM.

Estas funciones son puramente lógicas (no tocan base de datos),
por lo que NO necesitan mocks. Solo importamos las funciones
y probamos distintos valores de entrada.

Funciones testeadas:
  - convertir_decimal(): convierte strings a Decimal
  - format_currency(): formatea montos como moneda
  - precio(): calcula IVA, neto, exento y precio final
"""

from decimal import Decimal
import pytest

from utils.utils import convertir_decimal, format_currency, precio


# ──────────────────────────────────────────────
# Tests para convertir_decimal
# ──────────────────────────────────────────────

def test_convertir_decimal_con_punto():
    """
    Verifica que "1234.56" (punto como separador decimal)
    se convierta correctamente a Decimal('1234.56').
    """
    resultado = convertir_decimal("1234.56")
    assert resultado == Decimal("1234.56")


def test_convertir_decimal_con_coma():
    """
    Verifica que "1234,56" (coma como separador decimal,
    formato usado en Argentina) se convierta correctamente.
    """
    resultado = convertir_decimal("1234,56")
    assert resultado == Decimal("1234.56")


def test_convertir_decimal_con_none():
    """
    Verifica que pasar None lance ValueError porque
    no se puede convertir un valor vacío a Decimal.
    """
    with pytest.raises(ValueError, match="El valor no puede estar vacío"):
        convertir_decimal(None)


def test_convertir_decimal_con_string_invalido():
    """
    Verifica que pasar "abc" (texto no numérico)
    lance ValueError porque no es un formato decimal válido.
    """
    with pytest.raises(ValueError, match="no es válido como decimal"):
        convertir_decimal("abc")


def test_convertir_decimal_con_string_vacio():
    """
    Verifica que pasar un string vacío lance ValueError
    (la función considera falsy un string vacío).
    """
    with pytest.raises(ValueError, match="El valor no puede estar vacío"):
        convertir_decimal("")


# ──────────────────────────────────────────────
# Tests para format_currency
# ──────────────────────────────────────────────

def test_format_currency_positivo():
    """
    Verifica que 1000 se formatee como "$1,000.00".
    """
    resultado = format_currency(1000)
    # El formato puede variar según el locale.
    # Aceptamos "$1,000.00" (con separador de miles) o "$1000.00"
    assert resultado in ("$1,000.00", "$1000.00")


def test_format_currency_cero():
    """
    Verifica que 0 se formatee como "$0.00".
    """
    resultado = format_currency(0)
    assert resultado == "$0.00"


def test_format_currency_negativo():
    """
    Verifica que -500 se formatee como "$-500.00".
    """
    resultado = format_currency(-500)
    assert resultado == "$-500.00"


def test_format_currency_none():
    """
    Verifica que pasar None lance TypeError.

    La función format_currency usa '{:,.2f}'.format(amount),
    y Python no permite formatear None como float.
    Este test documenta que la función NO maneja None.
    """
    with pytest.raises(TypeError):
        format_currency(None)


# ──────────────────────────────────────────────
# Tests para precio (cálculo de IVA, neto, exento)
# ──────────────────────────────────────────────

def test_precio_alicuota_21():
    """
    Calcula precio con IVA 21%, sin exento, sin bonificación,
    sin recargo, sin impuestos internos.

    Si PFinal=121 y IVA=21%, entonces:
      - Neto = 121 / (1 + 0.21) = 100
      - IVA  = 100 * 21 / 100 = 21
      - PFinal = 100 + 21 = 121
    """
    resultado = precio(
        PFinal=Decimal("121"),
        ImpInt=Decimal("0"),
        Exento=Decimal("0"),
        PrcBonif=Decimal("0"),
        Recargo=Decimal("0"),
        CoefIva=Decimal("21"),
        CoefIB=Decimal("0")
    )

    assert resultado['Neto'] == Decimal("100")
    assert resultado['Iva'] == Decimal("21")
    assert resultado['PFinal'] == Decimal("121")
    assert resultado['Exento'] == Decimal("0")
    assert resultado['Descuento'] == Decimal("0")
    # Recargo solo se agrega al dict cuando Recargo > 0 (es 0 en este caso)
    assert resultado.get('Recargo', Decimal('0')) == Decimal('0')


def test_precio_alicuota_10_5():
    """
    Calcula precio con IVA 10.5% (alícuota reducida).

    Si PFinal=110.5 y IVA=10.5%, entonces:
      - Neto = 110.5 / (1 + 0.105) = 100
      - IVA  = 100 * 10.5 / 100 = 10.5
      - PFinal = 100 + 10.5 = 110.5
    """
    resultado = precio(
        PFinal=Decimal("110.50"),
        ImpInt=Decimal("0"),
        Exento=Decimal("0"),
        PrcBonif=Decimal("0"),
        Recargo=Decimal("0"),
        CoefIva=Decimal("10.5"),
        CoefIB=Decimal("0")
    )

    assert resultado['Neto'] == Decimal("100")
    assert resultado['Iva'] == Decimal("10.5")
    assert resultado['PFinal'] == Decimal("110.5")


def test_precio_alicuota_0():
    """
    Calcula precio con IVA 0% (exento total).

    Si PFinal=100 y no hay IVA, entonces:
      - Neto = 100 / 1 = 100
      - IVA = 0
      - PFinal = 100
    """
    resultado = precio(
        PFinal=Decimal("100"),
        ImpInt=Decimal("0"),
        Exento=Decimal("0"),
        PrcBonif=Decimal("0"),
        Recargo=Decimal("0"),
        CoefIva=Decimal("0"),
        CoefIB=Decimal("0")
    )

    assert resultado['Neto'] == Decimal("100")
    assert resultado['Iva'] == Decimal("0")
    assert resultado['PFinal'] == Decimal("100")


def test_precio_con_exento_parcial():
    """
    Calcula precio con exento parcial del 50%.
    Cuando hay exento, la alícuota de IVA se reduce:
      AlicuotaIva = CoefIva - (CoefIva * Exento / 100)

    Con CoefIva=21 y Exento=50:
      - AlicuotaIva = 21 - (21 * 50 / 100) = 21 - 10.5 = 10.5
      - Neto = 110.5 / (1 + 0.105) = 100
      - Exento = 110.5 * 50 / 100 = 55.25
      - IVA = 100 * 10.5 / 100 = 10.5
      - PFinal = 100 + 10.5 + 0 = 110.5
    """
    resultado = precio(
        PFinal=Decimal("110.50"),
        ImpInt=Decimal("0"),
        Exento=Decimal("50"),
        PrcBonif=Decimal("0"),
        Recargo=Decimal("0"),
        CoefIva=Decimal("21"),
        CoefIB=Decimal("0")
    )

    assert resultado['Neto'] == Decimal("100")
    assert resultado['Iva'] == Decimal("10.5")
    assert resultado['Exento'] == Decimal("55.25")
    assert resultado['PFinal'] == Decimal("110.5")


def test_precio_con_bonificacion():
    """
    Calcula precio con bonificación del 10%.

    PFinal=108.90, Bonif=10%:
      - Neto base = 108.90 / 1.21 = 90
      - Descuento = 90 * 10 / 100 = 9
      - Neto final = 90 - 9 = 81
      - IVA = 81 * 21 / 100 = 17.01
      - PFinal = 81 + 17.01 = 98.01
      - Descuento = (121 - (81 + 17.01 + 0))... 
    """
    resultado = precio(
        PFinal=Decimal("108.90"),
        ImpInt=Decimal("0"),
        Exento=Decimal("0"),
        PrcBonif=Decimal("10"),
        Recargo=Decimal("0"),
        CoefIva=Decimal("21"),
        CoefIB=Decimal("0")
    )

    # Neto base = 108.90 / 1.21 = 90
    # Descuento = 90 * 0.10 = 9
    # Neto final = 81
    # IVA = 81 * 0.21 = 17.01
    # PFinal = 81 + 17.01 = 98.01
    # El Descuento reportado es la diferencia: 108.90 - (81 + 17.01 + 0) = 10.89
    assert resultado['Neto'] == Decimal("81")
    assert resultado['Iva'] == Decimal("17.01")
    assert resultado['Descuento'] == Decimal("10.89")
    assert resultado['PFinal'] == Decimal("98.01")
