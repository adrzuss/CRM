from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, session, g
from sqlalchemy import and_
from models.configs import Configuracion, AlcIva, Categorias, TipoIva, TipoDocumento, AlcIB, PuntosVenta, PlanCtas, \
                           TipoComprobantes, TipoCompAplica, MonedasBilletes, PlanesSistema, OpcionesPlanSistema
from models.sessions import Tareas
from models.articulos import ListasPrecios
from models.sucursales import Sucursales
from services.configs import grabar_configuracion, save_and_update_lista_precios, grabarDatosPtoVta, validar_cuit
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
    return render_template('configuraciones.html', configuracion=configuracion, tipo_ivas=tipo_ivas, tipo_docs=tipo_docs, alicuotas=alcIva, listas_precios=listas_precios, tareas=tareas, ingBtos=alcIB, planCtas=planCtas, categorias=categorias, monedasBilletes=monedasBilletes, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

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
    idplan_sistema = request.form['idplanSistema']
    interes_mora_creditos = request.form['interesMora']
    grabar_configuracion(nombre_propietario, nombre_fantasia, tipo_iva, tipo_doc,documento, telefono, mail, dias_vto_cta_cte, idplan_sistema, interes_mora_creditos)
    flash('Datos de configuracion grabados')
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
        puntoVenta = grabarDatosPtoVta(request.form)
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