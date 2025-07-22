from flask import g
from functools import wraps
from services.articulos import alerta_stocks_faltante, alerta_stocks_limite, alerta_precios_nuevos, remitos_mercaderia
from services.ctactecli import ctacte_vencida
from services.sessions import alerta_mensajes_usuario, alerta_mensajes_sucursal, alerta_mensajes_creditos_nuevos, \
                              alerta_mensajes_creditos_pendientes, alerta_mensajes_creditos_rechazados, \
                              alerta_mensajes_creditos_aprobados

def obtener_alertas():
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
        cantidad, mensaje = alerta_mensajes_usuario()
        if cantidad > 0:
            cantidadMensajes += 1
            mensajes.append(mensaje)
        cantidad, mensaje = alerta_mensajes_sucursal()
        if cantidad > 0:
            cantidadMensajes += 1
            mensajes.append(mensaje)
        #mensajes de créditos    
        cantidad, mensaje = alerta_mensajes_creditos_nuevos()
        if cantidad > 0:
            cantidadMensajes += 1
            mensajes.append(mensaje)    
        cantidad, mensaje = alerta_mensajes_creditos_pendientes()
        if cantidad > 0:
            cantidadMensajes += 1
            mensajes.append(mensaje)        
        cantidad, mensaje = alerta_mensajes_creditos_rechazados()
        if cantidad > 0:
            cantidadMensajes += 1
            mensajes.append(mensaje)        
        cantidad, mensaje = alerta_mensajes_creditos_aprobados()
        if cantidad > 0:
            cantidadMensajes += 1
            mensajes.append(mensaje)        
    except Exception as e:  
        print(f"Error al obtener mensajes: {str(e)}")
        cantidad = 1
        cantidadMensajes = 1        
        mensajes.append({'titulo': 'Error obteniendo mensajes', 'subtitulo': f'{str(e)}', 'tipo': 'peligro', 'url': ''})
    return mensajes, cantidadMensajes 

def alertas_mensajes(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.alertas, g.cantidadAlertas = obtener_alertas()
        g.mensajes, g.cantidadMensajes = obtener_mensajes()
        return func(*args, **kwargs)
    return wrapper
