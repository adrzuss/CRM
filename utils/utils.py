from flask import session, redirect, url_for
from functools import wraps
from decimal import Decimal, InvalidOperation
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