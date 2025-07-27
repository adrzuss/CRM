from flask import session, current_app, flash
from sqlalchemy import text, func
from models.configs import Configuracion, TipoComprobantes, PuntosVenta
from models.articulos import ListasPrecios
from utils.db import db
from models.sessions import TareasUsuarios
from models.sucursales import Sucursales

def grabar_configuracion(nombre_propietario, nombre_fantasia, tipo_iva, tipo_doc, docuemnto, telefono, mail, dias_vto_cta_cte):
    configuracion = Configuracion.query.get(session['id_empresa'])
    if configuracion:
        if 'owner' in session:
            session['owner'] = nombre_propietario
        if 'company' in session:
            session['company'] = nombre_fantasia   
        configuracion.nombre_propietario = nombre_propietario
        configuracion.nombre_fantasia = nombre_fantasia
        configuracion.tipo_iva = tipo_iva
        configuracion.tipo_documento = tipo_doc
        configuracion.documento = docuemnto
        configuracion.telefono = telefono
        configuracion.mail = mail
        configuracion.dias_vto_cta_cte = dias_vto_cta_cte
        db.session.commit()

def getOwner():
    configuracion = Configuracion.query.get(session['id_empresa'])
    return configuracion

def getTareaUsuario():
    min_id_tarea = db.session.query(func.min(TareasUsuarios.idtarea)) \
                       .filter(TareasUsuarios.idusuario == session['user_id']) \
                       .scalar()
    return min_id_tarea

def get_comprobantes():
    tipo_comprobantes = TipoComprobantes.query.all()
    return tipo_comprobantes

def getPuntosVta():
    puntos_vta = PuntosVenta.query.all()
    return puntos_vta

def getSucursales():
    sucursales = Sucursales.query.all()
    return sucursales


def save_and_update_lista_precios(nombre_lista_precio, markup):
    lista_precio = ListasPrecios(nombre_lista_precio, markup)
    db.session.add(lista_precio)
    db.session.commit()
    idlista = lista_precio.id
    try:
        # Ejecuta el procedimiento almacenado llamándolo por nombre con sus parámetros
        with current_app.app_context():
            db.session.execute(text("CALL actualizar_precios_por_lista(:idlista, :markup)"), {'idlista': idlista, 'markup': markup})
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error al ejecutar el procedimiento almacenado: {e}", 'error')
        
        
        
def grabarDatosPtoVta(form):
    idPuntoVenta = form['id_puntoventa']
    punto_venta = form['puntoVenta']
    idsucursal = form['idsucursal']
    tipoIva = session.get('tipo_iva', None)
    if tipoIva == 1:
        ultima_fac_a = form['ultima_fac_a']
        ultima_nc_a = form['ultima_nc_a']
        ultima_deb_a = form['ultima_deb_a']
        ultima_fac_b = form['ultima_fac_b']
        ultima_nc_b = form['ultima_nc_b']
        ultima_deb_b = form['ultima_deb_b']
        ultima_fac_c = 0
        ultima_nc_c = 0
        ultima_deb_c = 0
    else:
        ultima_fac_a = 0
        ultima_nc_a = 0
        ultima_deb_a = 0
        ultima_fac_b = 0
        ultima_nc_b = 0
        ultima_deb_b = 0
        ultima_fac_c = form['ultima_fac_c']
        ultima_nc_c = form['ultima_nc_c']
        ultima_deb_c = form['ultima_deb_c']
    ultimo_rem_x = form['ultimo_rem_x']
    ultimo_rec_x = form['ultimo_rec_x']
    try:    
        if idPuntoVenta:
            puntoVenta = PuntosVenta.query.get(idPuntoVenta)
            puntoVenta.punto_vta = punto_venta
            puntoVenta.idsucursal = idsucursal
            puntoVenta.ultima_fac_a = ultima_fac_a
            puntoVenta.ultima_fac_b = ultima_fac_b
            puntoVenta.ultima_fac_c = ultima_fac_c
            puntoVenta.ultima_deb_a = ultima_deb_a
            puntoVenta.ultima_deb_b = ultima_deb_b
            puntoVenta.ultima_deb_c = ultima_deb_c
            puntoVenta.ultima_nc_a = ultima_nc_a
            puntoVenta.ultima_nc_b = ultima_nc_b
            puntoVenta.ultima_nc_c = ultima_nc_c
            puntoVenta.ultimo_rem_x = ultimo_rem_x
            puntoVenta.ultimo_rec_x = ultimo_rec_x
            db.session.commit()
            flash(f'Punto de venta actualizado: {puntoVenta.punto_vta}')
        else:
            puntoVenta = PuntosVenta(punto_venta, idsucursal, ultima_fac_a, ultima_fac_b, ultima_fac_c, ultima_deb_a, ultima_deb_b, ultima_deb_c, ultima_nc_a, ultima_nc_b, ultima_nc_c, ultimo_rem_x, ultimo_rec_x)
            db.session.add(puntoVenta)
            db.session.commit()
            flash(f'Punto de venta grabado: {puntoVenta.punto_vta}')
        return puntoVenta    
    except Exception as e:
        print(e)
        flash(f'Error grabando datos de Punto de venta: {e}', 'error')        
        return None

def discrimina_iva(id_tipo_comprobante):
    tipo_comprobante = TipoComprobantes.query.get(id_tipo_comprobante)
    return tipo_comprobante.discrimina_iva

def discrimina_iva_afip(id_tipo_comprobante):
    tipo_comprobante = db.session.query(TipoComprobantes).filter_by(id_afip=id_tipo_comprobante).first()
    return tipo_comprobante.discrimina_iva

def validar_cuit(cuit: str) -> bool:
    """
    Valida un número de CUIT argentino.
    :param cuit: CUIT como string, puede incluir guiones o no.
    :return: True si el CUIT es válido, False si no lo es.
    """
    # Eliminar guiones si existen
    cuit = cuit.replace("-", "")
    
    if len(cuit) != 11 or not cuit.isdigit():
        return False

    # Pesos según el algoritmo de AFIP
    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(digito) * peso for digito, peso in zip(cuit[:10], pesos))
    verificador = 11 - (suma % 11)

    if verificador == 11:
        verificador = 0
    elif verificador == 10:
        verificador = 9  # Según norma AFIP

    return verificador == int(cuit[10])

def get_sucursales():
    sucursales = Sucursales.query.all()
    return sucursales