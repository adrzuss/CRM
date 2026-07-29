import time
from flask import g, session
from functools import wraps
from services.articulos import alerta_stocks_faltante, alerta_stocks_limite, alerta_precios_nuevos, remitos_mercaderia
from services.ctactecli import ctacte_vencida
from services.sessions import alerta_mensajes_usuario, alerta_mensajes_sucursal, alerta_mensajes_creditos_nuevos, \
                              alerta_mensajes_creditos_pendientes, alerta_mensajes_creditos_rechazados, \
                              alerta_mensajes_creditos_aprobados
from services.creditos import alerta_creditos_atrasados                              

# Cache en memoria por usuario+sucursal para evitar N queries por request
_cache = {}
CACHE_TTL = 60  # segundos entre recargas de alertas

def _cache_key(prefix=''):
    return f"{prefix}{session.get('user_id', 0)}_{session.get('id_sucursal', 0)}"

def obtener_alertas():
    ahora = time.time()
    key = _cache_key('a_')
    cached = _cache.get(key)
    if cached and ahora - cached['ts'] < CACHE_TTL:
        return cached['data']
    
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
        
        cantidad, mensaje = alerta_creditos_atrasados()
        if cantidad > 0:
            cantidadAlertas += 1
            alertas.append(mensaje)
            
    except Exception as e:  
        print(f"Error al obtener alertas: {str(e)}")
        cantidad = 1
        cantidadAlertas = 1        
        alertas.append({'titulo': 'Error obteniendo alertas', 'subtitulo': f'{str(e)}', 'tipo': 'peligro', 'url': ''})
    
    _cache[key] = {'ts': ahora, 'data': (alertas, cantidadAlertas)}
    return alertas, cantidadAlertas

def obtener_mensajes():
    ahora = time.time()
    key = _cache_key('m_')
    cached = _cache.get(key)
    if cached and ahora - cached['ts'] < CACHE_TTL:
        return cached['data']
    
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
    
    _cache[key] = {'ts': ahora, 'data': (mensajes, cantidadMensajes)}
    return mensajes, cantidadMensajes 

def alertas_mensajes(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.alertas, g.cantidadAlertas = obtener_alertas()
        g.mensajes, g.cantidadMensajes = obtener_mensajes()
        return func(*args, **kwargs)
    return wrapper
