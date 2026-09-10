# comisiones/routes.py
# Rutas Flask del módulo de comisiones
# Blueprint: comisiones_bp

from flask import render_template, request, jsonify, redirect, url_for, flash, session, g
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from comisiones import comisiones_bp
from comisiones import repositories as repo
from comisiones.services import ComisionesService
from comisiones.constants import (
    TipoComision, BaseCalculo, ModoEscalas,
    EstadoLiquidacion, TipoMovimiento, TipoRegla
)
from comisiones.validators import (
    validar_superposicion_liquidacion,
    validar_detalles_no_vacios,
    validar_estado_liquidacion_transicion,
    validar_superposicion_asignaciones
)
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes
from utils.db import db

service = ComisionesService()


# ================================================================
# Dashboard
# ================================================================

@comisiones_bp.route('/comisiones/')
@check_session
@alertas_mensajes
def dashboard():
    """Dashboard principal del módulo de comisiones."""
    # Resumen de planes activos
    planes = repo.get_planes(incluir_inactivos=False)
    planes_activos = len(planes)
    
    # Liquidaciones pendientes (BORRADOR o CALCULADA)
    liquidaciones_pendientes = repo.get_liquidaciones({'estado': 'BORRADOR'})
    liquidaciones_calculadas = repo.get_liquidaciones({'estado': 'CALCULADA'})
    total_pendientes = len(liquidaciones_pendientes) + len(liquidaciones_calculadas)
    
    # Total comisiones del mes actual
    hoy = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1)
    fin_mes = date(hoy.year, hoy.month + 1, 1) if hoy.month < 12 else date(hoy.year + 1, 1, 1)
    
    liquidaciones_mes = repo.get_liquidaciones({
        'desde': inicio_mes,
        'hasta': fin_mes
    })
    total_comisiones_mes = sum(
        float(liq.get('total', 0)) for liq in liquidaciones_mes
        if liq.get('estado') != 'ANULADA'
    )
    
    return render_template('comisiones/index.html',
        planes_activos=planes_activos,
        total_pendientes=total_pendientes,
        total_comisiones_mes=total_comisiones_mes,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


# ================================================================
# Planes
# ================================================================

@comisiones_bp.route('/comisiones/planes')
@check_session
@alertas_mensajes
def listar_planes():
    """Lista todos los planes de comisiones."""
    incluir_inactivos = request.args.get('todos', '0') == '1'
    planes = repo.get_planes(incluir_inactivos=incluir_inactivos)
    
    return render_template('comisiones/planes.html',
        planes=planes,
        incluir_inactivos=incluir_inactivos,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/planes/nuevo', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nuevo_plan():
    """Formulario y creación de nuevo plan."""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            tipo_calculo = request.form['tipo_calculo']
            base_calculo = request.form['base_calculo']
            modo_escalas = request.form['modo_escalas']
            fecha_desde = datetime.strptime(request.form['fecha_desde'], '%Y-%m-%d').date()
            fecha_hasta_str = request.form.get('fecha_hasta', '')
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date() if fecha_hasta_str else None
            descripcion = request.form.get('descripcion', '')
            observaciones = request.form.get('observaciones', '')
            
            plan_id = repo.crear_plan(
                nombre=nombre,
                tipo_calculo=tipo_calculo,
                base_calculo=base_calculo,
                modo_escalas=modo_escalas,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                descripcion=descripcion,
                observaciones=observaciones,
                creado_por=session.get('user_id')
            )
            
            db.session.commit()
            flash('Plan creado exitosamente', 'success')
            return redirect(url_for('comisiones.ver_plan', id=plan_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear plan: {str(e)}', 'error')
            return redirect(url_for('comisiones.nuevo_plan'))
    
    return render_template('comisiones/plan_form.html',
        plan=None,
        tipos_calculo=TipoComision,
        bases_calculo=BaseCalculo,
        modos_escalas=ModoEscalas,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/planes/<int:id>')
@check_session
@alertas_mensajes
def ver_plan(id):
    """Vista detallada de un plan con sus reglas y tramos."""
    plan = repo.get_plan(id)
    if not plan:
        flash('Plan no encontrado', 'error')
        return redirect(url_for('comisiones.listar_planes'))
    
    reglas = repo.get_reglas_plan(id)
    tramos = repo.get_tramos_plan(id)
    
    return render_template('comisiones/plan_form.html',
        plan=plan,
        reglas=reglas,
        tramos=tramos,
        tipos_calculo=TipoComision,
        bases_calculo=BaseCalculo,
        modos_escalas=ModoEscalas,
        tipos_regla=TipoRegla,
        solo_lectura=True,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/planes/<int:id>/editar', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def editar_plan(id):
    """Formulario y actualización de plan existente."""
    plan = repo.get_plan(id)
    if not plan:
        flash('Plan no encontrado', 'error')
        return redirect(url_for('comisiones.listar_planes'))
    
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            tipo_calculo = request.form['tipo_calculo']
            base_calculo = request.form['base_calculo']
            modo_escalas = request.form['modo_escalas']
            fecha_desde = datetime.strptime(request.form['fecha_desde'], '%Y-%m-%d').date()
            fecha_hasta_str = request.form.get('fecha_hasta', '')
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date() if fecha_hasta_str else None
            descripcion = request.form.get('descripcion', '')
            observaciones = request.form.get('observaciones', '')
            
            repo.actualizar_plan(
                plan_id=id,
                nombre=nombre,
                tipo_calculo=tipo_calculo,
                base_calculo=base_calculo,
                modo_escalas=modo_escalas,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                descripcion=descripcion,
                observaciones=observaciones,
                actualizado_por=session.get('user_id')
            )
            
            db.session.commit()
            flash('Plan actualizado exitosamente', 'success')
            return redirect(url_for('comisiones.ver_plan', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar plan: {str(e)}', 'error')
            return redirect(url_for('comisiones.editar_plan', id=id))
    
    reglas = repo.get_reglas_plan(id)
    tramos = repo.get_tramos_plan(id)
    
    return render_template('comisiones/plan_form.html',
        plan=plan,
        reglas=reglas,
        tramos=tramos,
        tipos_calculo=TipoComision,
        bases_calculo=BaseCalculo,
        modos_escalas=ModoEscalas,
        tipos_regla=TipoRegla,
        solo_lectura=False,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/planes/<int:id>/duplicar', methods=['POST'])
@check_session
@alertas_mensajes
def duplicar_plan(id):
    """Duplica un plan existente con todas sus reglas y tramos."""
    try:
        nuevo_nombre = request.form.get('nuevo_nombre', '')
        if not nuevo_nombre:
            flash('Debe ingresar un nombre para el nuevo plan', 'error')
            return redirect(url_for('comisiones.ver_plan', id=id))
        
        nuevo_plan_id = repo.duplicar_plan(
            plan_id=id,
            nuevo_nombre=nuevo_nombre,
            creado_por=session.get('user_id')
        )
        
        if nuevo_plan_id:
            db.session.commit()
            flash(f'Plan duplicado exitosamente como "{nuevo_nombre}"', 'success')
            return redirect(url_for('comisiones.ver_plan', id=nuevo_plan_id))
        else:
            flash('Error al duplicar plan', 'error')
            return redirect(url_for('comisiones.ver_plan', id=id))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error al duplicar plan: {str(e)}', 'error')
        return redirect(url_for('comisiones.ver_plan', id=id))


@comisiones_bp.route('/comisiones/planes/<int:id>/toggle', methods=['POST'])
@check_session
@alertas_mensajes
def toggle_plan(id):
    """Activa/desactiva un plan."""
    try:
        nuevo_estado = repo.toggle_plan(id)
        if nuevo_estado is not None:
            db.session.commit()
            estado_texto = "activado" if nuevo_estado else "desactivado"
            flash(f'Plan {estado_texto} exitosamente', 'success')
        else:
            flash('Plan no encontrado', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar estado del plan: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.listar_planes'))


# ================================================================
# Reglas
# ================================================================

@comisiones_bp.route('/comisiones/planes/<int:id_plan>/reglas')
@check_session
@alertas_mensajes
def listar_reglas(id_plan):
    """Lista las reglas de un plan."""
    plan = repo.get_plan(id_plan)
    if not plan:
        flash('Plan no encontrado', 'error')
        return redirect(url_for('comisiones.listar_planes'))
    
    reglas = repo.get_reglas_plan(id_plan)
    
    return render_template('comisiones/reglas.html',
        plan=plan,
        reglas=reglas,
        tipos_regla=TipoRegla,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/planes/<int:id_plan>/reglas/nueva', methods=['POST'])
@check_session
@alertas_mensajes
def nueva_regla(id_plan):
    """Crea una nueva regla para un plan."""
    try:
        nombre = request.form['nombre']
        tipo_regla = request.form['tipo_regla']
        criterio = request.form['criterio']
        valor_criterio = request.form['valor_criterio']
        porcentaje = Decimal(request.form.get('porcentaje', '0'))
        importe_fijo = Decimal(request.form.get('importe_fijo', '0'))
        prioridad = int(request.form.get('prioridad', '0'))
        acumulable = request.form.get('acumulable') == '1'
        
        plan = repo.get_plan(id_plan)
        fecha_desde = plan['fecha_desde'] if plan else date.today()
        fecha_hasta = plan['fecha_hasta'] if plan else None
        
        regla_id = repo.crear_regla(
            id_plan=id_plan,
            nombre=nombre,
            criterio=criterio,
            valor_criterio=valor_criterio,
            fecha_desde=fecha_desde,
            tipo_regla=tipo_regla,
            porcentaje=porcentaje,
            importe_fijo=importe_fijo,
            prioridad=prioridad,
            acumulable=acumulable,
            fecha_hasta=fecha_hasta
        )
        
        db.session.commit()
        flash('Regla creada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear regla: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.listar_reglas', id_plan=id_plan))


@comisiones_bp.route('/comisiones/reglas/<int:id>/editar', methods=['POST'])
@check_session
@alertas_mensajes
def editar_regla(id):
    """Actualiza una regla existente."""
    try:
        regla = repo.get_regla(id)
        if not regla:
            flash('Regla no encontrada', 'error')
            return redirect(url_for('comisiones.listar_planes'))
        
        nombre = request.form['nombre']
        tipo_regla = request.form['tipo_regla']
        criterio = request.form['criterio']
        valor_criterio = request.form['valor_criterio']
        porcentaje = Decimal(request.form.get('porcentaje', '0'))
        importe_fijo = Decimal(request.form.get('importe_fijo', '0'))
        prioridad = int(request.form.get('prioridad', '0'))
        acumulable = request.form.get('acumulable') == '1'
        
        repo.actualizar_regla(
            regla_id=id,
            nombre=nombre,
            tipo_regla=tipo_regla,
            criterio=criterio,
            valor_criterio=valor_criterio,
            porcentaje=porcentaje,
            importe_fijo=importe_fijo,
            prioridad=prioridad,
            acumulable=acumulable
        )
        
        db.session.commit()
        flash('Regla actualizada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar regla: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.listar_reglas', id_plan=regla['id_plan']))


@comisiones_bp.route('/comisiones/reglas/<int:id>/eliminar', methods=['POST'])
@check_session
@alertas_mensajes
def eliminar_regla(id):
    """Elimina (desactiva) una regla."""
    try:
        regla = repo.get_regla(id)
        if not regla:
            flash('Regla no encontrada', 'error')
            return redirect(url_for('comisiones.listar_planes'))
        
        repo.eliminar_regla(id)
        db.session.commit()
        flash('Regla eliminada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar regla: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.listar_reglas', id_plan=regla['id_plan']))


# ================================================================
# Tramos
# ================================================================

@comisiones_bp.route('/comisiones/planes/<int:id_plan>/tramos')
@check_session
@alertas_mensajes
def listar_tramos(id_plan):
    """Lista los tramos de un plan."""
    plan = repo.get_plan(id_plan)
    if not plan:
        flash('Plan no encontrado', 'error')
        return redirect(url_for('comisiones.listar_planes'))
    
    tramos = repo.get_tramos_plan(id_plan)
    
    return render_template('comisiones/tramos.html',
        plan=plan,
        tramos=tramos,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/planes/<int:id_plan>/tramos/nuevo', methods=['POST'])
@check_session
@alertas_mensajes
def nuevo_tramo(id_plan):
    """Crea un nuevo tramo para un plan."""
    try:
        desde = Decimal(request.form.get('desde', '0'))
        hasta = Decimal(request.form.get('hasta', '0'))
        porcentaje = Decimal(request.form.get('porcentaje', '0'))
        importe_fijo = Decimal(request.form.get('importe_fijo', '0'))
        orden = int(request.form.get('orden', '0'))
        
        tramo_id = repo.crear_tramo(
            id_plan=id_plan,
            desde=desde,
            hasta=hasta,
            porcentaje=porcentaje,
            importe_fijo=importe_fijo,
            orden=orden
        )
        
        db.session.commit()
        flash('Tramo creado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear tramo: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.listar_tramos', id_plan=id_plan))


@comisiones_bp.route('/comisiones/tramos/<int:id>/editar', methods=['POST'])
@check_session
@alertas_mensajes
def editar_tramo(id):
    """Actualiza un tramo existente."""
    try:
        tramo = repo.get_tramo(id)
        if not tramo:
            flash('Tramo no encontrado', 'error')
            return redirect(url_for('comisiones.listar_planes'))
        
        desde = Decimal(request.form.get('desde', '0'))
        hasta = Decimal(request.form.get('hasta', '0'))
        porcentaje = Decimal(request.form.get('porcentaje', '0'))
        importe_fijo = Decimal(request.form.get('importe_fijo', '0'))
        orden = int(request.form.get('orden', '0'))
        
        repo.actualizar_tramo(
            tramo_id=id,
            desde=desde,
            hasta=hasta,
            porcentaje=porcentaje,
            importe_fijo=importe_fijo,
            orden=orden
        )
        
        db.session.commit()
        flash('Tramo actualizado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar tramo: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.listar_tramos', id_plan=tramo['id_plan']))


@comisiones_bp.route('/comisiones/tramos/<int:id>/eliminar', methods=['POST'])
@check_session
@alertas_mensajes
def eliminar_tramo(id):
    """Elimina un tramo."""
    try:
        tramo = repo.get_tramo(id)
        if not tramo:
            flash('Tramo no encontrado', 'error')
            return redirect(url_for('comisiones.listar_planes'))
        
        repo.eliminar_tramo(id)
        db.session.commit()
        flash('Tramo eliminado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar tramo: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.listar_tramos', id_plan=tramo['id_plan']))


# ================================================================
# Asignaciones
# ================================================================

@comisiones_bp.route('/comisiones/asignaciones')
@check_session
@alertas_mensajes
def listar_asignaciones():
    """Lista todas las asignaciones de vendedores a planes."""
    filtro = {}
    if request.args.get('usuario_id'):
        filtro['usuario_id'] = int(request.args.get('usuario_id'))
    if request.args.get('plan_id'):
        filtro['plan_id'] = int(request.args.get('plan_id'))
    if request.args.get('activo'):
        filtro['activo'] = request.args.get('activo') == '1'
    
    asignaciones = repo.get_asignaciones(filtro)
    planes = repo.get_planes()
    vendedores = repo.get_vendedores()
    
    return render_template('comisiones/asignaciones.html',
        asignaciones=asignaciones,
        planes=planes,
        vendedores=vendedores,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/asignaciones/nueva', methods=['POST'])
@check_session
@alertas_mensajes
def nueva_asignacion():
    """Crea una nueva asignación."""
    try:
        id_usuario = int(request.form['id_usuario'])
        id_plan = int(request.form['id_plan'])
        fecha_desde = datetime.strptime(request.form['fecha_desde'], '%Y-%m-%d').date()
        fecha_hasta_str = request.form.get('fecha_hasta', '')
        fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date() if fecha_hasta_str else None
        
        # Validar superposición
        validar_superposicion_asignaciones(id_usuario, fecha_desde, fecha_hasta)
        
        asignacion_id = repo.crear_asignacion(
            id_usuario=id_usuario,
            id_plan=id_plan,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        
        db.session.commit()
        flash('Asignación creada exitosamente', 'success')
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear asignación: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.listar_asignaciones'))


@comisiones_bp.route('/comisiones/asignaciones/<int:id>/editar', methods=['POST'])
@check_session
@alertas_mensajes
def editar_asignacion(id):
    """Actualiza una asignación existente."""
    try:
        asignacion = repo.get_asignacion_por_id(id)
        if not asignacion:
            flash('Asignación no encontrada', 'error')
            return redirect(url_for('comisiones.listar_asignaciones'))
        
        id_usuario = int(request.form['id_usuario'])
        id_plan = int(request.form['id_plan'])
        fecha_desde = datetime.strptime(request.form['fecha_desde'], '%Y-%m-%d').date()
        fecha_hasta_str = request.form.get('fecha_hasta', '')
        fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date() if fecha_hasta_str else None
        
        # Validar superposición (excluyendo la actual)
        validar_superposicion_asignaciones(id_usuario, fecha_desde, fecha_hasta, exclude_id=id)
        
        repo.actualizar_asignacion(
            asignacion_id=id,
            id_usuario=id_usuario,
            id_plan=id_plan,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        
        db.session.commit()
        flash('Asignación actualizada exitosamente', 'success')
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar asignación: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.listar_asignaciones'))


@comisiones_bp.route('/comisiones/asignaciones/<int:id>/eliminar', methods=['POST'])
@check_session
@alertas_mensajes
def eliminar_asignacion(id):
    """Elimina (desactiva) una asignación."""
    try:
        repo.eliminar_asignacion(id)
        db.session.commit()
        flash('Asignación eliminada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar asignación: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.listar_asignaciones'))


# ================================================================
# Cálculo de comisiones
# ================================================================

@comisiones_bp.route('/comisiones/calcular')
@check_session
@alertas_mensajes
def calcular_form():
    """Formulario para calcular comisiones de un período."""
    vendedores = repo.get_vendedores()
    
    return render_template('comisiones/calcular.html',
        vendedores=vendedores,
        resultado=None,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/calcular/preview', methods=['POST'])
@check_session
@alertas_mensajes
def calcular_preview():
    """Previsualiza el cálculo de comisiones sin guardarlo."""
    try:
        desde = datetime.strptime(request.form['desde'], '%Y-%m-%d').date()
        hasta = datetime.strptime(request.form['hasta'], '%Y-%m-%d').date()
        usuario_id = request.form.get('usuario_id')
        if usuario_id:
            usuario_id = int(usuario_id)
        else:
            usuario_id = None
        
        resultado = service.calcular_periodo(desde, hasta, usuario_id)
        
        vendedores = repo.get_vendedores()
        
        return render_template('comisiones/calcular.html',
            vendedores=vendedores,
            resultado=resultado,
            desde=desde,
            hasta=hasta,
            usuario_id=usuario_id,
            alertas=g.alertas,
            cantidadAlertas=g.cantidadAlertas,
            mensajes=g.mensajes,
            cantidadMensajes=g.cantidadMensajes
        )
        
    except Exception as e:
        flash(f'Error al calcular comisiones: {str(e)}', 'error')
        return redirect(url_for('comisiones.calcular_form'))


@comisiones_bp.route('/comisiones/calcular/confirmar', methods=['POST'])
@check_session
@alertas_mensajes
def calcular_confirmar():
    """Confirma el cálculo y crea la liquidación."""
    try:
        desde = datetime.strptime(request.form['desde'], '%Y-%m-%d').date()
        hasta = datetime.strptime(request.form['hasta'], '%Y-%m-%d').date()
        usuario_id = request.form.get('usuario_id')
        if usuario_id:
            usuario_id = int(usuario_id)
        else:
            usuario_id = None
        
        # Recalcular para obtener los detalles
        resultado = service.calcular_periodo(desde, hasta, usuario_id)
        
        if not resultado['detalles']:
            flash('No se calcularon comisiones para el período indicado', 'error')
            return redirect(url_for('comisiones.calcular_form'))
        
        # Crear liquidación
        resultado_creacion = service.crear_liquidacion(
            periodo_desde=desde,
            periodo_hasta=hasta,
            detalles_calculo=resultado['detalles'],
            usuario_id=session.get('user_id'),
            observaciones=request.form.get('observaciones', '')
        )
        
        if resultado_creacion.get('success'):
            flash(f"Liquidación creada exitosamente (ID: {resultado_creacion['liquidacion_id']})", 'success')
            return redirect(url_for('comisiones.ver_liquidacion', id=resultado_creacion['liquidacion_id']))
        else:
            flash('Error al crear liquidación', 'error')
            
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al confirmar cálculo: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.calcular_form'))


# ================================================================
# Liquidaciones
# ================================================================

@comisiones_bp.route('/comisiones/liquidaciones')
@check_session
@alertas_mensajes
def listar_liquidaciones():
    """Lista todas las liquidaciones."""
    filtro = {}
    if request.args.get('estado'):
        filtro['estado'] = request.args.get('estado')
    if request.args.get('desde'):
        filtro['desde'] = datetime.strptime(request.args.get('desde'), '%Y-%m-%d').date()
    if request.args.get('hasta'):
        filtro['hasta'] = datetime.strptime(request.args.get('hasta'), '%Y-%m-%d').date()
    
    liquidaciones = service.get_liquidaciones(filtro)
    
    return render_template('comisiones/liquidaciones.html',
        liquidaciones=liquidaciones,
        filtro=filtro,
        estados=EstadoLiquidacion,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/liquidaciones/<int:id>')
@check_session
@alertas_mensajes
def ver_liquidacion(id):
    """Vista detallada de una liquidación."""
    datos = service.get_detalle_liquidacion(id)
    if not datos:
        flash('Liquidación no encontrada', 'error')
        return redirect(url_for('comisiones.listar_liquidaciones'))
    
    return render_template('comisiones/liquidacion_detalle.html',
        liquidacion=datos['liquidacion'],
        detalles=datos['detalles'],
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/liquidaciones/<int:id>/confirmar', methods=['POST'])
@check_session
@alertas_mensajes
def confirmar_liquidacion(id):
    """Confirma una liquidación (la congela)."""
    try:
        resultado = service.confirmar_liquidacion(
            liquidacion_id=id,
            usuario_id=session.get('user_id')
        )
        
        if resultado.get('success'):
            flash('Liquidación confirmada exitosamente', 'success')
        else:
            flash('Error al confirmar liquidación', 'error')
            
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al confirmar liquidación: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.ver_liquidacion', id=id))


@comisiones_bp.route('/comisiones/liquidaciones/<int:id>/anular', methods=['POST'])
@check_session
@alertas_mensajes
def anular_liquidacion(id):
    """Anula una liquidación."""
    try:
        motivo = request.form.get('motivo', '')
        if not motivo:
            flash('Debe ingresar un motivo de anulación', 'error')
            return redirect(url_for('comisiones.ver_liquidacion', id=id))
        
        resultado = service.anular_liquidacion(
            liquidacion_id=id,
            motivo=motivo,
            usuario_id=session.get('user_id')
        )
        
        if resultado.get('success'):
            flash('Liquidación anulada exitosamente', 'success')
        else:
            flash('Error al anular liquidación', 'error')
            
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al anular liquidación: {str(e)}', 'error')
    
    return redirect(url_for('comisiones.ver_liquidacion', id=id))


# ================================================================
# Reportes
# ================================================================

@comisiones_bp.route('/comisiones/reportes')
@check_session
@alertas_mensajes
def reportes():
    """Dashboard de reportes de comisiones."""
    return render_template('comisiones/reportes.html',
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/reportes/vendedor', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def reporte_vendedor():
    """Reporte de comisiones por vendedor."""
    vendedores = repo.get_vendedores()
    datos = None
    
    if request.method == 'POST':
        try:
            usuario_id = int(request.form['usuario_id'])
            desde = datetime.strptime(request.form['desde'], '%Y-%m-%d').date()
            hasta = datetime.strptime(request.form['hasta'], '%Y-%m-%d').date()
            
            # Obtener liquidaciones del período
            liquidaciones = service.get_liquidaciones({
                'desde': desde,
                'hasta': hasta,
                'usuario_id': usuario_id
            })
            
            # Obtener detalles
            todos_detalles = []
            for liq in liquidaciones:
                datos_liq = service.get_detalle_liquidacion(liq['id'])
                if datos_liq:
                    for det in datos_liq['detalles']:
                        if det['id_usuario'] == usuario_id:
                            todos_detalles.append(det)
            
            total = sum(float(d.get('importe_comision', 0)) for d in todos_detalles)
            
            datos = {
                'detalles': todos_detalles,
                'total': total,
                'usuario_id': usuario_id,
                'desde': desde,
                'hasta': hasta
            }
            
        except Exception as e:
            flash(f'Error al generar reporte: {str(e)}', 'error')
    
    return render_template('comisiones/reporte_vendedor.html',
        vendedores=vendedores,
        datos=datos,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/reportes/periodo', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def reporte_periodo():
    """Reporte de comisiones por período."""
    datos = None
    
    if request.method == 'POST':
        try:
            desde = datetime.strptime(request.form['desde'], '%Y-%m-%d').date()
            hasta = datetime.strptime(request.form['hasta'], '%Y-%m-%d').date()
            
            # Obtener liquidaciones del período
            liquidaciones = service.get_liquidaciones({
                'desde': desde,
                'hasta': hasta
            })
            
            # Agrupar por vendedor
            por_vendedor = {}
            for liq in liquidaciones:
                datos_liq = service.get_detalle_liquidacion(liq['id'])
                if datos_liq:
                    for det in datos_liq['detalles']:
                        vid = det['id_usuario']
                        if vid not in por_vendedor:
                            por_vendedor[vid] = {
                                'nombre': det.get('nombre_usuario', f'Vendedor {vid}'),
                                'total': 0,
                                'cantidad': 0
                            }
                        por_vendedor[vid]['total'] += float(det.get('importe_comision', 0))
                        por_vendedor[vid]['cantidad'] += 1
            
            total_general = sum(v['total'] for v in por_vendedor.values())
            
            datos = {
                'por_vendedor': por_vendedor,
                'total_general': total_general,
                'desde': desde,
                'hasta': hasta
            }
            
        except Exception as e:
            flash(f'Error al generar reporte: {str(e)}', 'error')
    
    return render_template('comisiones/reporte_periodo.html',
        datos=datos,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@comisiones_bp.route('/comisiones/reportes/articulo', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def reporte_articulo():
    """Reporte de comisiones por artículo."""
    datos = None
    
    if request.method == 'POST':
        try:
            desde = datetime.strptime(request.form['desde'], '%Y-%m-%d').date()
            hasta = datetime.strptime(request.form['hasta'], '%Y-%m-%d').date()
            
            # Obtener liquidaciones del período
            liquidaciones = service.get_liquidaciones({
                'desde': desde,
                'hasta': hasta
            })
            
            # Obtener detalles con información de artículos
            por_articulo = {}
            for liq in liquidaciones:
                datos_liq = service.get_detalle_liquidacion(liq['id'])
                if datos_liq:
                    for det in datos_liq['detalles']:
                        # Obtener información del artículo
                        articulo = repo.get_articulo(det.get('id_item'))
                        art_nombre = articulo['detalle'] if articulo else f'Artículo {det.get("id_item")}'
                        art_id = det.get('id_item')
                        
                        if art_id not in por_articulo:
                            por_articulo[art_id] = {
                                'nombre': art_nombre,
                                'total': 0,
                                'cantidad': 0
                            }
                        por_articulo[art_id]['total'] += float(det.get('importe_comision', 0))
                        por_articulo[art_id]['cantidad'] += 1
            
            total_general = sum(a['total'] for a in por_articulo.values())
            
            datos = {
                'por_articulo': por_articulo,
                'total_general': total_general,
                'desde': desde,
                'hasta': hasta
            }
            
        except Exception as e:
            flash(f'Error al generar reporte: {str(e)}', 'error')
    
    return render_template('comisiones/reporte_articulo.html',
        datos=datos,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )
