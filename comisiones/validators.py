# comisiones/validators.py
# Validaciones de reglas de negocio para el módulo de comisiones

from comisiones.constants import EstadoLiquidacion, TRANSICIONES_LIQUIDACION


def validar_estado_liquidacion(liquidacion, estado_requerido):
    """Valida que una liquidación esté en el estado requerido.

    Args:
        liquidacion: dict con campo 'estado'
        estado_requerido: str — estado esperado

    Raises:
        ValueError: si la liquidación no está en el estado requerido.
    """
    estado_actual = liquidacion.get('estado', '')
    if estado_actual != estado_requerido:
        raise ValueError(
            f"La liquidación debe estar en estado '{estado_requerido}', "
            f"pero está en '{estado_actual}'"
        )


def validar_estado_liquidacion_transicion(liquidacion, estado_destino):
    """Valida que una liquidación pueda transicionar al estado destino.

    Args:
        liquidacion: dict con campo 'estado'
        estado_destino: EstadoLiquidacion — estado al que se quiere transicionar

    Raises:
        ValueError: si la transición no es permitida.
    """
    estado_actual_str = liquidacion.get('estado', '')
    try:
        estado_actual = EstadoLiquidacion(estado_actual_str)
    except ValueError:
        raise ValueError(
            f"Estado de liquidación desconocido: '{estado_actual_str}'"
        )

    transiciones_permitidas = TRANSICIONES_LIQUIDACION.get(estado_actual, [])
    if estado_destino not in transiciones_permitidas:
        raise ValueError(
            f"No se puede transicionar de '{estado_actual_str}' "
            f"a '{estado_destino.value}'. "
            f"Transiciones permitidas: "
            f"{[t.value for t in transiciones_permitidas]}"
        )


def validar_superposicion_liquidacion(desde, hasta, exclude_id=None):
    """Valida que no exista una liquidación que se superponga con el período dado.

    Args:
        desde: date — inicio del período
        hasta: date — fin del período
        exclude_id: int or None — ID de liquidación a excluir (para edición)

    Raises:
        ValueError: si hay superposición con otra liquidación activa.
    """
    from comisiones import repositories as repo

    cantidad = repo.contar_liquidaciones_por_periodo(desde, hasta)
    if cantidad > 0:
        raise ValueError(
            f"Ya existe una liquidación para el período {desde} al {hasta}. "
            f"No se permite superposición de períodos."
        )


def validar_plan_activo(plan):
    """Valida que un plan esté activo y vigente.

    Args:
        plan: dict con campos 'activo', 'fecha_desde', 'fecha_hasta'

    Raises:
        ValueError: si el plan no está activo o no está vigente.
    """
    if not plan:
        raise ValueError("No se encontró un plan de comisiones")

    if not plan.get('activo'):
        raise ValueError(
            f"El plan '{plan.get('nombre', '')}' no está activo"
        )

    from datetime import date
    hoy = date.today()
    fecha_desde = plan.get('fecha_desde')
    fecha_hasta = plan.get('fecha_hasta')

    if fecha_desde and hoy < fecha_desde:
        raise ValueError(
            f"El plan '{plan.get('nombre', '')}' aún no está vigente "
            f"(desde: {fecha_desde})"
        )

    if fecha_hasta and hoy > fecha_hasta:
        raise ValueError(
            f"El plan '{plan.get('nombre', '')}' ya no está vigente "
            f"(hasta: {fecha_hasta})"
        )


def validar_detalles_no_vacios(detalles):
    """Valida que la lista de detalles no esté vacía.

    Args:
        detalles: lista de dicts de detalles calculados

    Raises:
        ValueError: si la lista está vacía.
    """
    if not detalles or len(detalles) == 0:
        raise ValueError(
            "No se calcularon comisiones para el período indicado. "
            "Verifique que existan ventas y que los vendedores tengan "
            "un plan de comisiones asignado."
        )


def validar_no_confirmada(liquidacion):
    """Valida que una liquidación NO esté confirmada (para poder editarla).

    Args:
        liquidacion: dict con campo 'estado'

    Raises:
        ValueError: si la liquidación está confirmada.
    """
    estado = liquidacion.get('estado', '')
    if estado in (EstadoLiquidacion.CONFIRMADA.value,
                  EstadoLiquidacion.PAGADA.value):
        raise ValueError(
            f"No se puede modificar una liquidación en estado '{estado}'. "
            f"Solo se permiten modificaciones en estados BORRADOR o CALCULADA."
        )


def validar_superposicion_asignaciones(usuario_id, fecha_desde, fecha_hasta,
                                       exclude_id=None):
    """Valida que no existan asignaciones superpuestas para un vendedor.

    Args:
        usuario_id: int
        fecha_desde: date
        fecha_hasta: date or None
        exclude_id: int or None — ID de asignación a excluir

    Raises:
        ValueError: si hay superposición.
    """
    from utils.db import db
    from sqlalchemy import text

    sql = """
        SELECT COUNT(*) AS cantidad
        FROM comisiones_asignaciones
        WHERE id_usuario = :usuario_id
          AND activo = 1
          AND NOT (fecha_hasta < :fecha_desde OR fecha_desde > :fecha_hasta)
    """
    params = {
        'usuario_id': usuario_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta or '9999-12-31',
    }

    if exclude_id is not None:
        sql += " AND id != :exclude_id"
        params['exclude_id'] = exclude_id

    resultado = db.session.execute(text(sql), params).fetchone()
    cantidad = resultado[0] if resultado else 0

    if cantidad > 0:
        raise ValueError(
            f"El vendedor {usuario_id} ya tiene una asignación activa "
            f"que se superpone con el período {fecha_desde} al {fecha_hasta}. "
            f"No se permiten asignaciones superpuestas."
        )
