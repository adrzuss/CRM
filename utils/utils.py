from flask import session, redirect, url_for, current_app
from flask import g
from functools import wraps
from decimal import Decimal, InvalidOperation
import locale
from services.articulos import alerta_stocks_faltante, alerta_stocks_limite, alerta_precios_nuevos, remitos_mercaderia
from services.ctactecli import ctacte_vencida

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

def obtener_alertas_y_mensajes():
    try:
        alertas = []
        cantidadAlertas = 0
        cantidad, mensaje = alerta_stocks_faltante()
        if cantidad > 0:
            cantidadAlertas += 1
            alertas.append(mensaje)
        cantidad, mensaje = alerta_stocks_limite()
        if cantidad > 0:
            cantidadAlertas += 1
            alertas.append(mensaje)
        cantidad, mensaje = alerta_precios_nuevos()
        
        if cantidad > 0:
            cantidadAlertas += 1
            alertas.append(mensaje)
    except Exception as e:  
        print(f"Error al obtener alertas: {str(e)}")
        cantidad = 1
        cantidadAlertas = 1        
        alertas.append({'titulo': 'Error obteniendo alertas', 'subtitulo': f'{str(e)}', 'tipo': 'peligro', 'url': ''})
    return alertas, cantidadAlertas

def obtener_mensajes():
    try:
        mensajes = []
        cantidadMensajes = 0
        cantidad, mensaje = remitos_mercaderia()
        if cantidad > 0:
            cantidadMensajes += 1
            mensajes.append(mensaje)
        cantidad, mensaje = ctacte_vencida()
        if cantidad > 0:
            cantidadMensajes += 1
            mensajes.append(mensaje)
        
    except Exception as e:  
        print(f"Error al obtener mensajes: {str(e)}")
        cantidad = 1
        cantidadAlertas = 1        
        mensajes.append({'titulo': 'Error obteniendo mensajes', 'subtitulo': f'{str(e)}', 'tipo': 'peligro', 'url': ''})
    return mensajes, cantidadAlertas 

def alertas_mensajes(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.alertas, g.cantidadAlertas = obtener_alertas_y_mensajes()
        g.mensajes, g.cantidadMensajes = obtener_mensajes()
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
