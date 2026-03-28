from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, session, g, current_app
from sqlalchemy import and_
from werkzeug.utils import secure_filename
import os
import uuid
from models.configs import Configuracion, AlcIva, Categorias, TipoIva, TipoDocumento, AlcIB, PuntosVenta, PlanCtas, \
                           TipoComprobantes, TipoCompAplica, MonedasBilletes, PlanesSistema, OpcionesPlanSistema, LineasComprobantes
from models.sessions import Tareas
from models.articulos import ListasPrecios, Colores, DetallesArticulos
from models.sucursales import Sucursales
from services.configs import grabar_configuracion, save_and_update_lista_precios, grabarDatosPtoVta, validar_cuit, \
                            get_lineas_comprobantes, guardar_lineas_comprobantes
from utils.db import db
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes
from datetime import date

bp_configuraciones = Blueprint('configuraciones', __name__, template_folder='../templates/configuracion')

@bp_configuraciones.route('/configuraciones')
@check_session
@alertas_mensajes
def configuraciones():
    #configuracion = Configuracion.query.get(session['id_empresa'])
    configuracion = db.session.query(Configuracion.id,
                                     Configuracion.nombre_propietario,
                                     Configuracion.nombre_fantasia,
                                     Configuracion.tipo_iva,
                                     Configuracion.tipo_documento,
                                     Configuracion.documento,
                                     Configuracion.telefono,
                                     Configuracion.mail,
                                     Configuracion.clave,
                                     Configuracion.vencimiento,
                                     Configuracion.licencia,
                                     Configuracion.caja_con_apertura,
                                     Configuracion.idplan_sistema,
                                     Configuracion.interes_mora_creditos,
                                     Configuracion.logo,
                                     PlanesSistema.nombre.label('nombre_plan')
                                     ).join(PlanesSistema, PlanesSistema.id == Configuracion.idplan_sistema
                                     ).filter(Configuracion.id == session['id_empresa']).first()
    alcIva = AlcIva.query.all()
    listas_precios = ListasPrecios.query.all()
    tipo_ivas = TipoIva.query.all()
    tipo_docs = TipoDocumento.query.all()
    tareas = Tareas.query.all()
    alcIB = AlcIB.query.all()
    planCtas = PlanCtas.query.all()
    categorias = Categorias.query.all()
    monedasBilletes = MonedasBilletes.query.all()
    colores = Colores.query.all()
    detalles_articulos = DetallesArticulos.query.all()
    return render_template('configuraciones.html', configuracion=configuracion, tipo_ivas=tipo_ivas, tipo_docs=tipo_docs, alicuotas=alcIva, listas_precios=listas_precios, tareas=tareas, ingBtos=alcIB, planCtas=planCtas, categorias=categorias, monedasBilletes=monedasBilletes, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes, colores=colores, detalles_articulos=detalles_articulos)

@bp_configuraciones.route('/update_config', methods=['POST'])
@check_session
def update_config():
    nombre_propietario = request.form['propietario']
    nombre_fantasia = request.form['fantasia']
    tipo_iva = request.form['tipo_iva']
    telefono = request.form['telefono']
    mail = request.form['mail']
    tipo_doc = request.form['tipo_doc']
    documento = request.form['documento']
    dias_vto_cta_cte = request.form['dias_vto_cc']
    idplan_sistema = request.form.get('idplanSistema', '')
    interes_mora_creditos = request.form['interesMora']
    eliminar_logo = request.form.get('eliminar_logo', '0') == '1'
    
    # Procesar logo
    logo_filename = None
    logo_file = request.files.get('logo')
    
    idplan_sistema = PlanesSistema.query.filter_by(nombre=idplan_sistema).first().id if idplan_sistema else None
    
    if eliminar_logo:
        # Marcar para eliminar el logo actual
        logo_filename = ''
    elif logo_file and logo_file.filename:
        # Validar extensión usando configuración global
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'svg'})
        file_ext = logo_file.filename.rsplit('.', 1)[-1].lower() if '.' in logo_file.filename else ''
        
        if file_ext in allowed_extensions:
            # Crear carpeta si no existe
            logos_dir = os.path.join(current_app.root_path, 'static', 'img', 'logos')
            os.makedirs(logos_dir, exist_ok=True)
            
            # Generar nombre único
            unique_name = f"logo_{session.get('id_empresa', 'default')}_{uuid.uuid4().hex[:8]}.{file_ext}"
            logo_path = os.path.join(logos_dir, unique_name)
            
            # Eliminar logo anterior si existe
            try:
                config_actual = Configuracion.query.get(session['id_empresa'])
                if config_actual and config_actual.logo:
                    old_logo_path = os.path.join(logos_dir, config_actual.logo)
                    if os.path.exists(old_logo_path):
                        os.remove(old_logo_path)
            except Exception as e:
                print(f"Error al eliminar logo anterior: {e}")
            
            # Guardar nuevo archivo
            logo_file.save(logo_path)
            logo_filename = unique_name
        else:
            flash('Formato de imagen no válido. Use PNG, JPG, GIF o SVG.', 'warning')
    try:
        grabar_configuracion(nombre_propietario, nombre_fantasia, tipo_iva, tipo_doc, documento, telefono, mail, dias_vto_cta_cte, idplan_sistema, interes_mora_creditos, logo_filename)
        flash('Datos de configuracion grabados')
        return redirect('configuraciones')
    except Exception as e:
        flash(f'Error grabando configuración: {e}', 'error')
        return redirect('configuraciones')

@bp_configuraciones.route('/add_alc_iva', methods=['POST'])
@check_session
def add_alc_iva():
    descripcion = request.form['descripcion']
    alicuota = request.form['alicuota']
    alciva = AlcIva(descripcion, alicuota)
    db.session.add(alciva)
    db.session.commit()
    flash('Alicuota de IVA grabada')
    return redirect('configuraciones')

@bp_configuraciones.route('/add_categoria', methods=['POST'])
@check_session
def add_categoria():
    categoria = request.form['categoria']
    categoria = Categorias(nombre=categoria)
    db.session.add(categoria)
    db.session.commit()
    flash('Categoria de clientes grabada')
    return redirect('configuraciones')


@bp_configuraciones.route('/add_alc_ib', methods=['POST'])
@check_session
def add_alc_ib():
    descripcion = request.form['descripcionib']
    alicuota = request.form['alicuotaib']
    alcib = AlcIB(descripcion, alicuota)
    db.session.add(alcib)
    db.session.commit()
    flash('Alicuota de Ingreso Bruto grabada')
    return redirect('configuraciones')

@bp_configuraciones.route('/add_lista_precio', methods=['POST'])
@check_session
def add_lista_precio():
    try:
        nombre_lista_precio = request.form['lista_precio']
        markup = request.form['markup']
        save_and_update_lista_precios(nombre_lista_precio, markup)
        
        flash('Lista de precios grabada')
        return redirect('configuraciones')
    except Exception as e:
        flash(f'Error grabando lista de precios: {e}', 'error')
        return redirect('configuraciones')    
    
@bp_configuraciones.route('/add_tarea', methods=['POST'])
@check_session
def add_tarea():
    try:
        nombre_tarea = request.form['tarea']
        tarea = Tareas(nombre_tarea)
        db.session.add(tarea)
        db.session.commit()
        flash('Tarea grabada')
        return redirect('configuraciones')
    except Exception as e:
        flash(f'Error grabando Tareas: {e}', 'error')
        return redirect('configuraciones')    

@bp_configuraciones.route('/add_planCtas', methods=['POST'])
@check_session
def add_planCtas():
    try:
        nombre_planCtas = request.form['tarea']
        planCtas = PlanCtas(nombre = nombre_planCtas)
        db.session.add(planCtas)
        db.session.commit()
        flash('Plan de cuenta grabado')
        return redirect('configuraciones')
    except Exception as e:
        flash(f'Error grabando Plan ctas.: {e}', 'error')
        return redirect('configuraciones')    

@bp_configuraciones.route('/add_monedabillete', methods=['POST'])
@check_session
def add_monedabillete():
    try:
        descripcion = request.form['descripcion']
        valor = request.form['valor']
        baja = request.form['baja']
        if not baja:
            baja = date(1900, 1, 1)
        monedaBillete = MonedasBilletes(descripcion, valor, baja)
        db.session.add(monedaBillete)
        db.session.commit()
        flash('Moneda/billete grabado')
        return redirect('configuraciones')
    except Exception as e:
        flash(f'Error grabando Plan ctas.: {e}', 'error')
        return redirect('configuraciones')        
    
@bp_configuraciones.route('/abm_sucursales', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def abm_sucursales():
    if request.method == 'POST':
        id_sucursal = request.form['id_sucursal']
        nombre_sucursal = request.form['nombre']
        direccion_sucursal = request.form['direccion']
        telefono_sucursal = request.form['telefono']
        email_sucursal = request.form['email']
        if id_sucursal:
            sucursal = Sucursales.query.get(id_sucursal)
            sucursal.nombre = nombre_sucursal
            sucursal.direccion = direccion_sucursal
            sucursal.telefono = telefono_sucursal
            sucursal.email = email_sucursal
            db.session.commit()
            flash('Datos de sucursal actualizados')
        else:
            sucursal = Sucursales(nombre_sucursal, direccion_sucursal, telefono_sucursal, email_sucursal)
            db.session.add(sucursal)
            db.session.commit()
            flash('Datos de sucursal grabados')
    sucursal = None    
    sucursales = Sucursales.query.all()
    return render_template('abm-sucursales.html', sucursal=sucursal, sucursales=sucursales, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_configuraciones.route('/update_sucursal/<int:id>', methods=['GET'])
@check_session
@alertas_mensajes
def update_sucursal(id):
    sucursal = Sucursales.query.get(id)
    sucursales = Sucursales.query.all()
    return render_template('abm-sucursales.html', sucursales=sucursales, sucursal=sucursal, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_configuraciones.route('/abm-sucursales/<int:id>/delete', methods=['GET', 'POST'])
@check_session
def abm_sucursales_delete(id):
    pass

@bp_configuraciones.route('/puntos_venta/<int:id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def puntos_venta(id=0):
    if request.method == 'POST':
        idPuntoVenta = grabarDatosPtoVta(request.form)
        puntoVenta = PuntosVenta.query.get(idPuntoVenta)
        idPuntoVenta = puntoVenta.id if puntoVenta else None
    else:
        idPuntoVenta = id
        if idPuntoVenta > 0:
            puntoVenta = PuntosVenta.query.get(idPuntoVenta)
        else:
            puntoVenta = None    
    sucursales = Sucursales.query.all()    
    puntos_venta = PuntosVenta.query.all()
    return render_template('puntos-venta.html', puntos_venta=puntos_venta, puntoVenta=puntoVenta, sucursales=sucursales, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_configuraciones.route('/get_tipos_comprobantes/<id_tipo_iva>/<aplica>')
@check_session
def get_tipos_comprobantes(id_tipo_iva, aplica):
    tipos_comprobantes = db.session.query(TipoComprobantes) \
                         .join(TipoCompAplica, and_(TipoCompAplica.id_iva_owner == session['tipo_iva'], TipoCompAplica.id_tipo_oper == aplica)) \
                         .all()
    tipos_comprobantes = [{'id': tc.id, 'nombre': tc.nombre} for tc in tipos_comprobantes]
    return jsonify(success=True, tipos_comprobantes=tipos_comprobantes) 

@bp_configuraciones.route('/checkCuit/<cuit>/<tipo_doc>')
@check_session
def checkCuit(cuit, tipo_doc):
    if tipo_doc in ['2', '3']:
        cuitValido = validar_cuit(cuit)
    else:
        cuitValido = True
    return jsonify(success=True, cuitValido=cuitValido) 

@bp_configuraciones.route('/planes_opciones')
@check_session
@alertas_mensajes
def planes_opciones():
    planes = PlanesSistema.query.all()
    opciones = OpcionesPlanSistema.query.all()
    return render_template('planes-opciones.html', planes=planes, opciones=opciones, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_configuraciones.route('/add_color', methods=['POST'])
@check_session
def add_color():
    nombre = request.form['nombreColor']
    codColor = request.form['color']
    color = Colores(nombre, codColor)
    db.session.add(color)
    db.session.commit()
    flash('Color grabado')
    return redirect('configuraciones')

@bp_configuraciones.route('/add_detalle_articulo', methods=['POST'])
@check_session
def add_detalle_articulo():
    nombre = request.form['nombreDetalleArticulo']
    detalle_articulo = DetallesArticulos(nombre)
    db.session.add(detalle_articulo)
    db.session.commit()
    flash('Detalle de artículo grabado')
    return redirect('configuraciones')

# =============================================================================
# HTMX ENDPOINTS - CRUD COMPLETO PARA CONFIGURACIONES
# =============================================================================

# --- Helpers para renderizar tablas parciales ---
def render_tabla_alicuotas_iva():
    alicuotas = AlcIva.query.all()
    return render_template('partials/_tabla_alc_iva.html', alicuotas=alicuotas)

def render_tabla_alicuotas_ib():
    ingBtos = AlcIB.query.all()
    return render_template('partials/_tabla_alc_ib.html', ingBtos=ingBtos)

def render_tabla_listas_precios():
    listas_precios = ListasPrecios.query.all()
    return render_template('partials/_tabla_listas_precios.html', listas_precios=listas_precios)

def render_tabla_tareas():
    tareas = Tareas.query.all()
    return render_template('partials/_tabla_tareas.html', tareas=tareas)

def render_tabla_plan_ctas():
    planCtas = PlanCtas.query.all()
    return render_template('partials/_tabla_plan_ctas.html', planCtas=planCtas)

def render_tabla_categorias():
    categorias = Categorias.query.all()
    return render_template('partials/_tabla_categorias.html', categorias=categorias)

def render_tabla_monedas_billetes():
    monedasBilletes = MonedasBilletes.query.all()
    return render_template('partials/_tabla_monedas_billetes.html', monedasBilletes=monedasBilletes)

def render_tabla_colores():
    colores = Colores.query.all()
    return render_template('partials/_tabla_colores.html', colores=colores)

def render_tabla_detalles_articulos():
    detalles_articulos = DetallesArticulos.query.all()
    return render_template('partials/_tabla_detalles_articulos.html', detalles_articulos=detalles_articulos)

def render_tabla_tipo_ivas():
    tipo_ivas = TipoIva.query.all()
    return render_template('partials/_tabla_tipo_ivas.html', tipo_ivas=tipo_ivas)

def render_tabla_tipo_docs():
    tipo_docs = TipoDocumento.query.all()
    return render_template('partials/_tabla_tipo_docs.html', tipo_docs=tipo_docs)

# --- HTMX: Alícuotas IVA ---
@bp_configuraciones.route('/htmx/add_alc_iva', methods=['POST'])
@check_session
def htmx_add_alc_iva():
    descripcion = request.form['descripcion']
    alicuota = request.form['alicuota']
    alciva = AlcIva(descripcion, alicuota)
    db.session.add(alciva)
    db.session.commit()
    return render_tabla_alicuotas_iva()

@bp_configuraciones.route('/htmx/get_alc_iva/<int:id>', methods=['GET'])
@check_session
def get_alc_iva(id):
    item = AlcIva.query.get_or_404(id)
    return render_template('partials/_form_edit_alc_iva.html', item=item, entidad='alicuotas_iva')

@bp_configuraciones.route('/htmx/update_alc_iva/<int:id>', methods=['POST'])
@check_session
def update_alc_iva(id):
    item = AlcIva.query.get_or_404(id)
    item.descripcion = request.form['descripcion']
    item.alicuota = request.form['alicuota']
    db.session.commit()
    return render_tabla_alicuotas_iva()

# --- HTMX: Alícuotas Ingresos Brutos ---
@bp_configuraciones.route('/htmx/add_alc_ib', methods=['POST'])
@check_session
def htmx_add_alc_ib():
    descripcion = request.form['descripcion']
    alicuota = request.form['alicuota']
    alcib = AlcIB(descripcion, alicuota)
    db.session.add(alcib)
    db.session.commit()
    return render_tabla_alicuotas_ib()

@bp_configuraciones.route('/htmx/get_alc_ib/<int:id>', methods=['GET'])
@check_session
def get_alc_ib(id):
    item = AlcIB.query.get_or_404(id)
    return render_template('partials/_form_edit_alc_ib.html', item=item, entidad='alicuotas_ib')

@bp_configuraciones.route('/htmx/update_alc_ib/<int:id>', methods=['POST'])
@check_session
def update_alc_ib(id):
    item = AlcIB.query.get_or_404(id)
    item.descripcion = request.form['descripcion']
    item.alicuota = request.form['alicuota']
    db.session.commit()
    return render_tabla_alicuotas_ib()

# --- HTMX: Listas de Precios ---
@bp_configuraciones.route('/htmx/add_lista_precio', methods=['POST'])
@check_session
def htmx_add_lista_precio():
    nombre = request.form['nombre']
    markup = request.form['markup']
    save_and_update_lista_precios(nombre, markup)
    return render_tabla_listas_precios()

@bp_configuraciones.route('/htmx/get_lista_precio/<int:id>', methods=['GET'])
@check_session
def get_lista_precio(id):
    item = ListasPrecios.query.get_or_404(id)
    return render_template('partials/_form_edit_lista_precio.html', item=item, entidad='listas_precios')

@bp_configuraciones.route('/htmx/update_lista_precio/<int:id>', methods=['POST'])
@check_session
def update_lista_precio(id):
    item = ListasPrecios.query.get_or_404(id)
    item.nombre = request.form['nombre']
    item.markup = request.form['markup']
    db.session.commit()
    return render_tabla_listas_precios()

# --- HTMX: Tareas ---
@bp_configuraciones.route('/htmx/add_tarea', methods=['POST'])
@check_session
def htmx_add_tarea():
    nombre_tarea = request.form['tarea']
    tarea = Tareas(nombre_tarea)
    db.session.add(tarea)
    db.session.commit()
    return render_tabla_tareas()

@bp_configuraciones.route('/htmx/get_tarea/<int:id>', methods=['GET'])
@check_session
def get_tarea(id):
    item = Tareas.query.get_or_404(id)
    return render_template('partials/_form_edit_tarea.html', item=item, entidad='tareas')

@bp_configuraciones.route('/htmx/update_tarea/<int:id>', methods=['POST'])
@check_session
def update_tarea(id):
    item = Tareas.query.get_or_404(id)
    item.tarea = request.form['tarea']
    db.session.commit()
    return render_tabla_tareas()

# --- HTMX: Plan de Cuentas ---
@bp_configuraciones.route('/htmx/add_planCta', methods=['POST'])
@check_session
def htmx_add_planCta():
    nombre = request.form['nombre']
    planCta = PlanCtas(nombre=nombre)
    db.session.add(planCta)
    db.session.commit()
    return render_tabla_plan_ctas()

@bp_configuraciones.route('/htmx/get_planCta/<int:id>', methods=['GET'])
@check_session
def get_planCta(id):
    item = PlanCtas.query.get_or_404(id)
    return render_template('partials/_form_edit_plan_cta.html', item=item, entidad='plan_ctas')

@bp_configuraciones.route('/htmx/update_planCta/<int:id>', methods=['POST'])
@check_session
def update_planCta(id):
    item = PlanCtas.query.get_or_404(id)
    item.nombre = request.form['nombre']
    db.session.commit()
    return render_tabla_plan_ctas()

# --- HTMX: Categorías ---
@bp_configuraciones.route('/htmx/add_categoria', methods=['POST'])
@check_session
def htmx_add_categoria():
    nombre = request.form['nombre']
    categoria = Categorias(nombre=nombre)
    db.session.add(categoria)
    db.session.commit()
    return render_tabla_categorias()

@bp_configuraciones.route('/htmx/get_categoria/<int:id>', methods=['GET'])
@check_session
def get_categoria(id):
    item = Categorias.query.get_or_404(id)
    return render_template('partials/_form_edit_categoria.html', item=item, entidad='categorias')

@bp_configuraciones.route('/htmx/update_categoria/<int:id>', methods=['POST'])
@check_session
def update_categoria(id):
    item = Categorias.query.get_or_404(id)
    item.nombre = request.form['nombre']
    db.session.commit()
    return render_tabla_categorias()

# --- HTMX: Monedas y Billetes (con baja lógica) ---
@bp_configuraciones.route('/htmx/add_monedabillete', methods=['POST'])
@check_session
def htmx_add_monedabillete():
    descripcion = request.form['descripcion']
    valor = request.form['valor']
    monedaBillete = MonedasBilletes(descripcion, valor)
    db.session.add(monedaBillete)
    db.session.commit()
    return render_tabla_monedas_billetes()

@bp_configuraciones.route('/htmx/get_monedabillete/<int:id>', methods=['GET'])
@check_session
def get_monedabillete(id):
    item = MonedasBilletes.query.get_or_404(id)
    return render_template('partials/_form_edit_moneda_billete.html', item=item, entidad='monedas_billetes')

@bp_configuraciones.route('/htmx/update_monedabillete/<int:id>', methods=['POST'])
@check_session
def update_monedabillete(id):
    item = MonedasBilletes.query.get_or_404(id)
    item.descripcion = request.form['descripcion']
    item.valor = request.form['valor']
    db.session.commit()
    return render_tabla_monedas_billetes()

@bp_configuraciones.route('/htmx/delete_monedabillete/<int:id>', methods=['POST'])
@check_session
def delete_monedabillete(id):
    item = MonedasBilletes.query.get_or_404(id)
    item.baja = date.today()
    db.session.commit()
    return render_tabla_monedas_billetes()

# --- HTMX: Colores ---
@bp_configuraciones.route('/htmx/add_color', methods=['POST'])
@check_session
def htmx_add_color():
    nombre = request.form['nombre']
    codColor = request.form['color']
    color = Colores(nombre, codColor)
    db.session.add(color)
    db.session.commit()
    return render_tabla_colores()

@bp_configuraciones.route('/htmx/get_color/<int:id>', methods=['GET'])
@check_session
def get_color(id):
    item = Colores.query.get_or_404(id)
    return render_template('partials/_form_edit_color.html', item=item, entidad='colores')

@bp_configuraciones.route('/htmx/update_color/<int:id>', methods=['POST'])
@check_session
def update_color(id):
    item = Colores.query.get_or_404(id)
    item.nombre = request.form['nombre']
    item.color = request.form['color']
    db.session.commit()
    return render_tabla_colores()

# --- HTMX: Detalles de Artículos ---
@bp_configuraciones.route('/htmx/add_detalle_articulo', methods=['POST'])
@check_session
def htmx_add_detalle_articulo():
    nombre = request.form['nombre']
    detalle = DetallesArticulos(nombre)
    db.session.add(detalle)
    db.session.commit()
    return render_tabla_detalles_articulos()

@bp_configuraciones.route('/htmx/get_detalle_articulo/<int:id>', methods=['GET'])
@check_session
def get_detalle_articulo(id):
    item = DetallesArticulos.query.get_or_404(id)
    return render_template('partials/_form_edit_detalle_articulo.html', item=item, entidad='detalles_articulos')

@bp_configuraciones.route('/htmx/update_detalle_articulo/<int:id>', methods=['POST'])
@check_session
def update_detalle_articulo(id):
    item = DetallesArticulos.query.get_or_404(id)
    item.nombre = request.form['nombre']
    db.session.commit()
    return render_tabla_detalles_articulos()

# --- HTMX: Tipo IVA ---
@bp_configuraciones.route('/htmx/get_tipo_iva/<int:id>', methods=['GET'])
@check_session
def get_tipo_iva(id):
    item = TipoIva.query.get_or_404(id)
    return render_template('partials/_form_edit_tipo_iva.html', item=item, entidad='tipo_ivas')

@bp_configuraciones.route('/htmx/update_tipo_iva/<int:id>', methods=['POST'])
@check_session
def update_tipo_iva(id):
    item = TipoIva.query.get_or_404(id)
    item.descripcion = request.form['descripcion']
    item.id_afip = request.form.get('id_afip', 0)
    db.session.commit()
    return render_tabla_tipo_ivas()

# --- HTMX: Tipo Documento ---
@bp_configuraciones.route('/htmx/get_tipo_doc/<int:id>', methods=['GET'])
@check_session
def get_tipo_doc(id):
    item = TipoDocumento.query.get_or_404(id)
    return render_template('partials/_form_edit_tipo_doc.html', item=item, entidad='tipo_docs')

@bp_configuraciones.route('/htmx/update_tipo_doc/<int:id>', methods=['POST'])
@check_session
def update_tipo_doc(id):
    item = TipoDocumento.query.get_or_404(id)
    item.nombre = request.form['nombre']
    item.id_afip = request.form.get('id_afip', 0)
    db.session.commit()
    return render_tabla_tipo_docs()

# =============================================================================
# LÍNEAS DE COMPROBANTES (Cabecera y Pie de Ticket)
# =============================================================================

@bp_configuraciones.route('/lineas_comprobantes/<int:id_punto_vta>', methods=['GET'])
@check_session
def lineas_comprobantes(id_punto_vta):
    """Obtiene las líneas de comprobantes de un punto de venta"""
    lineas = get_lineas_comprobantes(id_punto_vta)
    punto_vta = PuntosVenta.query.get_or_404(id_punto_vta)
    return render_template('partials/_modal-lineas-comprobantes.html', 
                          lineas=lineas, 
                          punto_vta=punto_vta)

@bp_configuraciones.route('/lineas_comprobantes/<int:id_punto_vta>', methods=['POST'])
@check_session
def guardar_lineas(id_punto_vta):
    """Guarda las líneas de comprobantes de un punto de venta"""
    try:
        lineas_data = []
        for i in range(1, 11):
            texto = request.form.get(f'linea_{i}', '').strip()
            solo_en_ventas = request.form.get(f'solo_ventas_{i}') == 'on'
            if texto:  # Solo guardar si tiene texto
                lineas_data.append({
                    'idlinea': i,
                    'texto': texto,
                    'solo_en_ventas': solo_en_ventas
                })
        
        guardar_lineas_comprobantes(id_punto_vta, lineas_data)
        return jsonify(success=True, message='Líneas guardadas correctamente')
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@bp_configuraciones.route('/api/lineas_comprobantes/<int:id_punto_vta>', methods=['GET'])
@check_session
def api_lineas_comprobantes(id_punto_vta):
    """API JSON para obtener las líneas de comprobantes de un punto de venta"""
    lineas = get_lineas_comprobantes(id_punto_vta)
    # Convertir a formato para JS: separar cabecera y pie
    cabecera = []
    pie = []
    for i in range(1, 6):
        if lineas[i]['texto']:
            cabecera.append({
                'linea': i,
                'texto': lineas[i]['texto'],
                'solo_en_ventas': lineas[i]['solo_en_ventas']
            })
    for i in range(6, 11):
        if lineas[i]['texto']:
            pie.append({
                'linea': i,
                'texto': lineas[i]['texto'],
                'solo_en_ventas': lineas[i]['solo_en_ventas']
            })
    return jsonify(success=True, cabecera=cabecera, pie=pie)
