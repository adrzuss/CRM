from flask import session, current_app, flash
from sqlalchemy import text, func
from models.configs import Configuracion, TipoComprobantes, PuntosVenta, LineasComprobantes
from models.articulos import ListasPrecios
from utils.db import db
from models.sessions import TareasUsuarios
from models.sucursales import Sucursales

def grabar_configuracion(nombre_propietario, nombre_fantasia, tipo_iva, tipo_doc, docuemnto, telefono, mail, dias_vto_cta_cte, idplan_sistema, interes_mora_creditos, logo=None):
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
        configuracion.idplan_sistema = idplan_sistema
        configuracion.interes_mora_creditos = interes_mora_creditos
        
        # Actualizar logo si se proporciona (None = no cambiar, '' = eliminar, 'filename' = nuevo logo)
        if logo is not None:
            configuracion.logo = logo if logo else None
        
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
    idPuntoVenta = form.get('id_puntoventa', '')
    punto_venta = form['puntoVenta']
    idsucursal = form['idsucursal']
    tipoIva = session.get('tipo_iva', None)
    if tipoIva == 1:
        ultima_fac_a = form.get('ultima_fac_a', 0) or 0
        ultima_nc_a = form.get('ultima_nc_a', 0) or 0
        ultima_deb_a = form.get('ultima_deb_a', 0) or 0
        ultima_fac_b = form.get('ultima_fac_b', 0) or 0
        ultima_nc_b = form.get('ultima_nc_b', 0) or 0
        ultima_deb_b = form.get('ultima_deb_b', 0) or 0
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
        ultima_fac_c = form.get('ultima_fac_c', 0) or 0
        ultima_nc_c = form.get('ultima_nc_c', 0) or 0
        ultima_deb_c = form.get('ultima_deb_c', 0) or 0
    ultimo_rem_x = form.get('ultimo_rem_x', 0) or 0
    ultimo_rec_x = form.get('ultimo_rec_x', 0) or 0
    pos_printer = '1' if form.get('pos_printer') else ''
    fac_electronica = 1 if form.get('fac_electronica') else 0
    certificado_p12 = form.get('certificado', '')
    clave_certificado = form.get('clave_cert', '')
    
    print('------------------------------------------------------------------------------------------')
    print(f'Impresora pos: {pos_printer} - Fac. Electrónica: {fac_electronica}')
    
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
            puntoVenta.pos_printer = pos_printer
            puntoVenta.fac_electronica = fac_electronica
            puntoVenta.certificado_p12 = certificado_p12
            puntoVenta.clave_certificado = clave_certificado
            db.session.commit()
            flash(f'Punto de venta actualizado: {puntoVenta.punto_vta}')
        else:
            puntoVenta = PuntosVenta(punto_venta, idsucursal, ultima_fac_a, ultima_fac_b, ultima_fac_c, ultima_deb_a, ultima_deb_b, ultima_deb_c, ultima_nc_a, ultima_nc_b, ultima_nc_c, ultimo_rem_x, ultimo_rec_x)
            puntoVenta.pos_printer = pos_printer
            puntoVenta.fac_electronica = fac_electronica
            puntoVenta.certificado_p12 = certificado_p12
            puntoVenta.clave_certificado = clave_certificado
            db.session.add(puntoVenta)
            db.session.commit()
            idPuntoVenta = puntoVenta.id
            flash(f'Punto de venta grabado: {puntoVenta.punto_vta}')
        return idPuntoVenta    
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

def getDatosSucEmpresa():
    empresa = Configuracion.query.get(session['id_empresa'])
    sucursal = Sucursales.query.get(session['id_sucursal'])
    return {
        'nombre': empresa.nombre_fantasia + ' - ' + sucursal.nombre,
        'direccion': sucursal.direccion,
        'telefono': sucursal.telefono,
        'cuit': empresa.documento if empresa else ''
    }
    
def getPosPrinter(idPuntoVenta):
    puntoVenta = PuntosVenta.query.get(idPuntoVenta)
    posPrinter = puntoVenta.pos_printer if puntoVenta else None
    facElectronica = puntoVenta.fac_electronica if puntoVenta else None
    return posPrinter, facElectronica

# =============================================================================
# LÍNEAS DE COMPROBANTES (Cabecera y Pie de Ticket)
# =============================================================================

def get_lineas_comprobantes(id_punto_vta):
    """Obtiene las líneas de comprobantes de un punto de venta
    Retorna un diccionario con las 10 líneas (vacías si no existen)
    """
    try:
        lineas_db = LineasComprobantes.query.filter_by(idpuntovta=id_punto_vta).all()
        
        # Crear diccionario con las 10 líneas (vacías por defecto)
        lineas = {}
        for i in range(1, 11):
            lineas[i] = {'texto': '', 'solo_en_ventas': False}
        
        # Llenar con datos de la BD
        for linea in lineas_db:
            lineas[linea.idlinea] = {
                'texto': linea.texto,
                'solo_en_ventas': linea.solo_en_ventas
            }
        
        return lineas
    except Exception as e:
        print(f"Error al obtener líneas de comprobantes: {e}")
        return {i: {'texto': '', 'solo_en_ventas': False} for i in range(1, 11)}

def guardar_lineas_comprobantes(id_punto_vta, lineas_data):
    """Guarda las líneas de comprobantes de un punto de venta
    Elimina las líneas existentes y guarda solo las que tienen texto
    """
    try:
        # Eliminar líneas existentes
        LineasComprobantes.query.filter_by(idpuntovta=id_punto_vta).delete()
        
        # Insertar nuevas líneas (solo las que tienen texto)
        for linea in lineas_data:
            nueva_linea = LineasComprobantes(
                idpuntovta=id_punto_vta,
                idlinea=linea['idlinea'],
                texto=linea['texto'],
                solo_en_ventas=linea['solo_en_ventas']
            )
            db.session.add(nueva_linea)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e
