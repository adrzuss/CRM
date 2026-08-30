import math


def aplicar_redondeo(precio_base, multiplo=100, tipo='cercano', restar=0):
    """
    Aplica redondeo comercial a un precio según el múltiplo deseado.
    Ejemplo: precio=4327, multiplo=100, tipo='arriba' -> 4400
    """
    if multiplo <= 0:
        return round(precio_base, 2)

    if tipo == 'arriba':
        precio_redondeado = math.ceil(precio_base / multiplo) * multiplo
    elif tipo == 'abajo':
        precio_redondeado = math.floor(precio_base / multiplo) * multiplo
    else:  # 'cercano'
        precio_redondeado = round(precio_base / multiplo) * multiplo

    if restar > 0 and precio_redondeado >= restar:
        precio_redondeado -= restar
    print(f"Precio base: {precio_base}, Múltiplo: {multiplo}, Tipo: {tipo}, Restar: {restar} => Precio redondeado: {precio_redondeado}")
    return precio_redondeado


def calcular_precio_comercial(precio_lista_anterior, porcentaje_aumento, reglas_db):
    """
    Calcula precio teórico y aplica redondeo según regla aplicable.
    reglas_db: lista de diccionarios con keys: desde_precio, hasta_precio, multiplo, tipo_redondeo, restar_unidades
    """
    precio_teorico = precio_lista_anterior * (1 + (porcentaje_aumento / 100))

    regla_aplicable = None
    
    for regla in reglas_db:
        if regla['desde_precio'] <= precio_teorico <= regla['hasta_precio']:
            regla_aplicable = regla
            break

    if not regla_aplicable:
        return round(precio_teorico, 2)

    return precio_teorico, aplicar_redondeo(
        precio_teorico,
        multiplo=regla_aplicable['multiplo'],
        tipo=regla_aplicable['tipo_redondeo'],
        restar=regla_aplicable.get('restar_unidades', 0)
    )
