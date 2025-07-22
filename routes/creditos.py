from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask import g
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes
from models.entidades_cred import EntidadesCred
from services.creditos import get_planes_creditos, procesar_plan_credito, get_documentos_creditos, \
                              procesar_documento_creditos, get_estados_creditos, procesar_estado_creditos, \
                              get_docs_por_plan, asignar_documento_para_plan, limpiar_documentos_para_plan, \
                              generar_cronograma_frances, get_requisitos, generar_credito_cliente, \
                              get_cats_por_plan, limpiar_categorias_para_plan, asignar_categoria_para_plan, \
                              get_planes_creditos_categoria, get_creditos_by_estado, get_credito_by_id,\
                              buscar_documento_descarga, grabar_cuotas, actualizar_credito,get_credito_by_idcliente, \
                              vencimientos_cuotas_creditos, get_cuotas_pendientes, generarRecibo
from datetime import date, timedelta


bp_creditos = Blueprint('creditos', __name__, template_folder='../templates/creditos')

@bp_creditos.route('/config_cred')
@check_session
@alertas_mensajes
def config_cred():
    planes_creditos = get_planes_creditos()
    documentos_de_creditos = get_documentos_creditos()
    estados = get_estados_creditos()
    documentos_por_plan = get_docs_por_plan()
    return render_template('config-cred.html', planes_creditos=planes_creditos, documentos_de_creditos=documentos_de_creditos, estados=estados, documentos_por_plan=documentos_por_plan, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_creditos.route('/get_documentos_por_plan/<id>')
@check_session
def get_documentos_por_plan(id):
    documentos_por_plan = get_docs_por_plan(id)
    documentos = [{'idDoc': d.id, 'documento': d.nombre, 'idDocCred': d.iddocumento_credito, 'idPlanCred': d.idplan_credito} for d in documentos_por_plan]
    return jsonify(documentos=documentos)

@bp_creditos.route('/get_categorias_por_plan/<id>')
@check_session
def get_categorias_por_plan(id):
    categorias_por_plan = get_cats_por_plan(id)
    categorias = [{'id': c.id, 'nombre': c.nombre, 'idplan': c.idplan, 'idcat': c.idcategoria} for c in categorias_por_plan]
    return jsonify(categorias=categorias)

@bp_creditos.route('/add_documento_para_creditos', methods=['POST'])
@check_session
def add_documento_para_creditos():
    documentos = request.form.getlist('documentos')
    idplan_credito = request.form.get('idplandoc')
    limpiar_documentos_para_plan(idplan_credito)
    for doc in documentos:
        asignar_documento_para_plan(doc, idplan_credito)
    return redirect(url_for('creditos.config_cred'))

@bp_creditos.route('/add_categorias_para_creditos', methods=['POST'])
@check_session
def add_categorias_para_creditos():
    categorias = request.form.getlist('categorias')
    idplan_credito = request.form.get('idplancategoria')
    limpiar_categorias_para_plan(idplan_credito)
    for cat in categorias:
        asignar_categoria_para_plan(cat, idplan_credito)
    return redirect(url_for('creditos.config_cred'))


@bp_creditos.route('/add_plan_credito', methods=['POST'])
@check_session
@alertas_mensajes
def add_plan_credito():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    tasa_interes = request.form['tasa_interes']
    cuotas = request.form['cuotas']
    anticipo = request.form.get('anticipo', False)
    baja = date(1900, 1, 1)
    plan = procesar_plan_credito(nombre, descripcion, tasa_interes, cuotas, anticipo, baja)
    if plan:
        flash(f'Plan de crédito grabado: {plan.descripcion}')
        return redirect(url_for('creditos.config_cred'))
    else:
        flash(f'Error grabando plan de crédito: ', 'error')
        return redirect(url_for('creditos.config_cred'))
    
@bp_creditos.route('/add_documento_creditos', methods=['POST'])
@check_session
@alertas_mensajes
def add_documento_creditos():
    nombre = request.form['nombre_documento']
    documentos = procesar_documento_creditos(nombre)
    if documentos:
        flash(f'Documentos de crédito grabado: {documentos.nombre}')
        return redirect(url_for('creditos.config_cred'))
    else:
        flash('Error grabando documentos de crédito', 'error')
        return redirect(url_for('creditos.config_cred'))

@bp_creditos.route('/planes_para_cliente/<categoria>')
@check_session
def planes_para_cliente(categoria):
    planes = get_planes_creditos_categoria(categoria)
    planes = [{'id': p.id, 'nombre': p.nombre, 'tasa_interes': p.tasa_interes, 'cuotas': p.cuotas, 'anticipo': p.anticipo, 'garantes': p.garantes} for p in planes]
    return jsonify(success=True, planes=planes)

@bp_creditos.route('/add_estado_creditos', methods=['POST'])
@check_session
@alertas_mensajes
def add_estado_creditos():
    nombre = request.form['nombre_documento']
    descripcion = request.form['descripcion']
    estado = procesar_estado_creditos(nombre, descripcion)
    if estado:
        flash(f'Estado de crédito grabado: {estado.nombre}')
        return redirect(url_for('creditos.config_cred'))
    else:
        flash('Error grabando estado de crédito', 'error')
        return redirect(url_for('creditos.config_cred'))

@bp_creditos.route('/simulador_cred')
@check_session
@alertas_mensajes
def simulador_cred():
    planes = get_planes_creditos()
    datos_planes = [{'id': p.id, 'nombre': p.nombre, 'tasa_interes': p.tasa_interes, 'cuotas': p.cuotas, 'anticipo': p.anticipo} for p in planes]
    idPlanSeleccionado = request.args.get('idPlan', None)
    if idPlanSeleccionado:
        cuotas = request.args.get('cuotas', None)
        tasa_interes = request.args.get('tasa_interes', None)    
        monto_total = request.args.get('monto_total', None)
        anticipo = request.args.get('anticipo', None)
        if cuotas and tasa_interes and monto_total:
            monto_total = float(monto_total)
            cuotas = int(cuotas)
            tasa_interes = float(tasa_interes) / 100 #dividimos la tasa mensual en 100 para expresarlo como porcentage
            anticipo = anticipo == "True"
            cronograma, cuota = generar_cronograma_frances(monto_total, tasa_interes, cuotas)
            requisitos = get_requisitos(idPlanSeleccionado)
            return render_template('simulador-creditos.html', datos_planes=datos_planes, cronograma=cronograma, cuota=cuota, requisitos=requisitos, monto_total=monto_total, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    return render_template('simulador-creditos.html', datos_planes=datos_planes, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_creditos.route('/generar_cuotas')
@check_session
def generar_cuotas():
    cuotas = request.args.get('cuotas', None)
    tasa_interes = request.args.get('tasa_interes', None)    
    monto_total = request.args.get('monto_total', None)
    cuotas = int(cuotas)
    tasa_interes = float(tasa_interes) / 100
    monto_total = float(monto_total)
    cronograma, cuota = generar_cronograma_frances(monto_total, tasa_interes, cuotas)
    return jsonify(cronograma=cronograma, cuota=cuota)

    

@bp_creditos.route('/otorgamiento')
@check_session
@alertas_mensajes
def otorgamiento():
    cliente = []
    credito = []
    fecha_solicitud = date.today()
    return render_template('otorgamiento.html', cliente=cliente, credito=credito, fecha_solicitud=fecha_solicitud, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_creditos.route('/ver_credito/<id_credito>')
@check_session
@alertas_mensajes
def ver_credito(id_credito):
    # Aquí podrías cargar los datos del crédito específico utilizando el ID
    credito, garantes, documentos, cuotas_generadas = get_credito_by_id(id_credito)
    if not credito:
        flash('Crédito no encontrado', 'error')
        return redirect(url_for('creditos.otorgamiento'))
    planesCategorias = get_planes_creditos_categoria(credito.idcategoria)
    print(f"los documentos del crédito son: {documentos}")
    return render_template('ver-credito.html', credito=credito, garantes=garantes, documentos=documentos, cuotas_generadas=cuotas_generadas, planesCategorias=planesCategorias, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_creditos.route('/generar_credito', methods=['POST'])
@check_session
@alertas_mensajes
def generar_credito():
    
    formulario = request.form
    archivos = request.files
    
    idcredito, mensaje = generar_credito_cliente(formulario, archivos)
    if not idcredito:
        flash(f'Error al generar el crédito: {mensaje}', 'error')
        return redirect(url_for('creditos.otorgamiento'))
    flash(f'El crédito ha sido generado con éxito: {idcredito}', 'success')
    return redirect(url_for('creditos.otorgamiento'))
    
@bp_creditos.route('/procesar_estado_credito', methods=['POST'])
@check_session
@alertas_mensajes
def procesar_estado_credito():
        
    idcredito = request.form.get('idcredito')
    estado = request.form.get('estado')
    idplan = request.form.get('idplan')
    monto_total = request.form.get('monto_total')
    tasa_interes = request.form.get('tasa_interes')
    cuotas = request.form.get('cuotas')
    observaciones = request.form.get('observaciones')
    if estado == '3':  # Aprobado
        cronograma, cuota = generar_cronograma_frances(float(monto_total), float(tasa_interes)/100, int(cuotas))
        cuotarGeneradas = grabar_cuotas(idcredito, idplan, cronograma)
        if not cuotarGeneradas:
            flash('Error al grabar las cuotas del crédito', 'error')
            return redirect(url_for('creditos.ver_credito', id_credito=idcredito))
    creditoActualizado = actualizar_credito(idcredito, estado, monto_total, tasa_interes, cuotas, observaciones)
    if not creditoActualizado:
        flash('Error al actualizar el crédito', 'error')
        return redirect(url_for('creditos.ver_credito', id_credito=idcredito))
    else:
        flash('Crédito actualizado con éxito', 'success')
    
    return redirect(url_for('creditos.ver_credito', id_credito=idcredito))

@bp_creditos.route('/lst_creditos')
@check_session
@alertas_mensajes
def lst_creditos():
    try:
        desde = request.args.get('desde', date.today())
        hasta = request.args.get('hasta', date.today())
        # Obtener los datos de los créditos nuevos
        nuevos = get_creditos_by_estado(desde, hasta, 1,2,3,4,5,6,7)
        # Pasar los resultados a la plantilla
        titulo = 'Créditos registrados'
        return render_template('lst-estados-creditos.html', accion='creditos.lst_creditos', titulo=titulo, desde=desde, hasta=hasta, creditos=nuevos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None

@bp_creditos.route('/lst_nuevos')
@check_session
@alertas_mensajes
def lst_nuevos():
    try:
        desde = request.args.get('desde', date.today())
        hasta = request.args.get('hasta', date.today())
        # Obtener los datos de los créditos nuevos
        nuevos = get_creditos_by_estado(desde, hasta, 1)
        # Pasar los resultados a la plantilla
        titulo = 'Créditos Nuevos'
        return render_template('lst-estados-creditos.html', accion='creditos.lst_nuevos', titulo=titulo, desde=desde, hasta=hasta, creditos=nuevos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None


@bp_creditos.route('/lst_pendientes')
@check_session
@alertas_mensajes
def lst_pendientes():
    try:
        desde = request.args.get('desde', date.today())
        hasta = request.args.get('hasta', date.today())
        # Obtener los datos de los créditos nuevos
        nuevos = get_creditos_by_estado(desde, hasta, 2, 7)
        # Pasar los resultados a la plantilla
        titulo = 'Créditos Pendientes de Aprobación o con pedido de actualización de datos'
        return render_template('lst-estados-creditos.html', accion='creditos.lst_pendientes', titulo=titulo, desde=desde, hasta=hasta, creditos=nuevos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None

@bp_creditos.route('/lst_rechazados')
@check_session
@alertas_mensajes
def lst_rechazados():
    try:
        desde = request.args.get('desde', date.today()-timedelta(days=15))
        hasta = request.args.get('hasta', date.today())
        # Obtener los datos de los créditos nuevos
        nuevos = get_creditos_by_estado(desde, hasta, 4)
        # Pasar los resultados a la plantilla
        titulo = 'Créditos Rechazados'
        return render_template('lst-estados-creditos.html', accion='creditos.lst_rechazados', titulo=titulo, desde=desde, hasta=hasta, creditos=nuevos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None
    
@bp_creditos.route('/lst_aprobados')
@check_session
@alertas_mensajes
def lst_aprobados():
    try:
        desde = request.args.get('desde', date.today()-timedelta(days=15))
        hasta = request.args.get('hasta', date.today())
        # Obtener los datos de los créditos nuevos
        nuevos = get_creditos_by_estado(desde, hasta, 3)
        # Pasar los resultados a la plantilla
        titulo = 'Créditos Aprobados'
        return render_template('lst-estados-creditos.html', accion='creditos.lst_aprobados', titulo=titulo, desde=desde, hasta=hasta, creditos=nuevos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None

@bp_creditos.route('/descargar_documento/<idcredito>/<iddocumento>')
@check_session
def descargar_documento(idcredito, iddocumento):
    # For windows you need to use drive name [ex: F:/Example.pdf]
    path = buscar_documento_descarga(idcredito, iddocumento)
    
    return send_file(path, as_attachment=True)

@bp_creditos.route('/hay_credito/<idcliente>')
@check_session
def hay_credito(idcliente):
    # Lógica para verificar si hay crédito para el cliente
    try:
        credito = get_credito_by_idcliente(idcliente)
        if credito:
            return jsonify(success=True, credito={'idcredito': credito.id, 'estado': credito.estado, 'monto_credito': credito.monto_total, 'cuotas': credito.cuotas})
        else:
            return jsonify(success=False, credito={'idcredito': 0, 'estado': 0, 'monto_credito': 0, 'cuotas': 0})
    except Exception as e:
        print(f"Error al verificar crédito del cliente: {e}")
        return jsonify(success=False, mensaje='Error al verificar crédito del cliente.')    

@bp_creditos.route('/vencimientos_cuotas', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def vencimientos_cuotas():
    if request.method == 'GET':
        hoy = date.today()
        desde = request.args.get('desde', hoy.replace(day=1))  # Por defecto, desde el primer día del mes actual
        hasta = request.args.get('hasta', hoy)
        cuotas = vencimientos_cuotas_creditos(desde, hasta)
        return render_template('lst-vencimiento-cuotas.html', cuotas=cuotas, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        return redirect(url_for('creditos.vencimientos_cuotas', desde=desde, hasta=hasta))   
    
@bp_creditos.route('/seleccionar_cuota', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def seleccionar_cuota():
    print("Entrando a seleccionar cuota")
    if request.method == 'GET':
        # Lógica para mostrar el formulario de cobranza
        entidades = EntidadesCred.query.all()
        print("Seleccion de cuotas por GET")
        return render_template('seleccion-cuotas-pago.html', entidades=entidades, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
        
    if request.method == 'POST':
        # Lógica para procesar el formulario de cobranza    
        print("Seleccion de cuotas por POST")
        return redirect(url_for('creditos.seleccionar_cuota'))
    
@bp_creditos.route('/cuotas_pendientes/<idcliente>')
@check_session
def cuotas_pendientes(idcliente):
    try:
        cuotasPendientes = get_cuotas_pendientes(idcliente)
        return jsonify(success=True, cuotas = [{'id': cuota[0], 'monto_total': cuota[1], 'numero_cuota': cuota[2], 'fecha_vencimiento': cuota[3], 'monto': cuota[5], 'dias_mora': 0 if cuota[4] <= 0 else cuota[4]} for cuota in cuotasPendientes])
    except Exception as e:
        print(f"Error al obtener las cuotas pendientes: {e}")
        return jsonify(success=False, mensaje=f'Error al obtener las cuotas pendientes: {e}')    
    
@bp_creditos.route('/cobrar_cuotas', methods=['POST'])
@check_session
@alertas_mensajes
def cobrar_cuotas():
    print("Entrando a cobrar cuotas")
    if request.method == 'POST':
        data = request.get_json()
        cuotas = data.get('cuotas', [])
        idCliente = data.get('idCliente', None)
        totalCuotas = data.get('totalCuotas', 0)
        efectivo = data.get('efectivo', 0)
        tarjeta = data.get('tarjeta', 0)
        entidad = data.get('entidad', 0)

        resultado = generarRecibo(idCliente, cuotas, totalCuotas, efectivo, tarjeta, entidad)
        
        if not resultado['success']:
            print(f"Error al cobrar cuotas: {resultado['mensaje']}")
            flash(f"Error al cobrar cuotas: {resultado['mensaje']}", 'error')
        else:    
            print("Cuotas cobradas exitosamente")    
            flash('Cuotas cobradas exitosamente.')
    return jsonify(success=False, mensaje='Método no permitido.')