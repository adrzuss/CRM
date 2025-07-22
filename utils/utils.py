from flask import session, redirect, url_for

from functools import wraps
from decimal import Decimal, InvalidOperation
from models.configs import AlcIva
import locale

# Set the locale to default 'C' locale
locale.setlocale(locale.LC_ALL, '')
# Define a function to the format the currency string
def format_currency(amount):
    return '${:,.2f}'.format(amount)

def check_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('sesion.login'))  # Redirigir al login si no hay sesión activa
        return func(*args, **kwargs)
    return wrapper

def convertir_decimal(valor):
    if not valor:
        raise ValueError("El valor no puede estar vacío")

    # Intentar con "." como separador decimal
    try:
        return Decimal(valor.replace(",", "."))
    except InvalidOperation:
        pass

    # Intentar con "," como separador decimal
    try:
        return Decimal(valor.replace(".", ","))
    except InvalidOperation:
        pass

    raise ValueError(f"El valor '{valor}' no es válido como decimal")

def precio(PFinal, ImpInt, Exento, PrcBonif, Recargo, CoefIva, CoefIB):
    Resultado = {}
    AlicuotaIva = CoefIva - ((CoefIva * Exento) / 100)
    PN = (PFinal - ImpInt)/(1+(AlicuotaIva / 100))
    if (PrcBonif > 0):
        Descuento = ((PN * PrcBonif) / 100)
    else:
        Descuento = Decimal(0)
    PN = PN - Descuento
    if (Recargo > 0):
        MtoRecargo = ((PN * Recargo) / 100)
    else:
        MtoRecargo = Decimal(0)
    PN = PN + MtoRecargo

    AuxExento = PFinal * Exento / 100
    Iva = PN * AlicuotaIva / 100

    Resultado['Neto'] = Decimal(PN)
    Resultado['Iva'] = Decimal(Iva)
    Resultado['Exento'] = Decimal(AuxExento)
    Resultado['PFinal'] = Decimal(PN + Iva + ImpInt)
    if (Descuento > 0):
        Resultado['Descuento'] = Decimal(PFinal - (PN + Iva + ImpInt))
    else:
        Resultado['Descuento'] = Decimal(0)
    if (Recargo > 0):
        Resultado['Recargo'] = Decimal(PFinal - (PN + Iva + ImpInt))
    Resultado['ImpInt'] = Decimal(ImpInt)
    if (CoefIB > 0):
        Resultado['IngBto'] = Decimal(((PN + ImpInt)*CoefIB)/100)
    else:
        Resultado['IngBto'] = Decimal(0)
    return Resultado

def precio_VP(costo, impInt, exento, idIva):
    impuestosInternos = costo * impInt / 100
    baseImponible = costo + impuestosInternos
    baseImponible = baseImponible * (1 - exento / 100)
    alcIva = AlcIva.query.get(idIva)
    iva = baseImponible * alcIva.alicuota / 100
    costoTotal = costo + iva + impuestosInternos
    return costoTotal    