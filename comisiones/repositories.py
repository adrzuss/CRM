# comisiones/repositories.py
# Consultas a base de datos para el módulo de comisiones
# Todas las funciones retornan listas de RowProxy (accesibles por nombre de columna)

from utils.db import db
from sqlalchemy import text


def get_plan_activo(usuario_id, fecha):
    """Obtiene el plan activo para un vendedor en una fecha determinada.
    Retorna una fila con: id, nombre, descripcion, tipo_calculo, base_calculo,
    modo_escalas, fecha_desde, fecha_hasta, o None si no hay plan.
    """
    resultado = db.session.execute(
        text("""
            SELECT p.id, p.nombre, p.descripcion, p.tipo_calculo, p.base_calculo,
                   p.modo_escalas, p.fecha_desde, p.fecha_hasta
            FROM comisiones_planes p
            JOIN comisiones_asignaciones a ON p.id = a.id_plan
            WHERE a.id_usuario = :usuario_id
              AND a.activo = 1
              AND p.activo = 1
              AND :fecha BETWEEN a.fecha_desde AND COALESCE(a.fecha_hasta, '9999-12-31')
              AND :fecha BETWEEN p.fecha_desde AND COALESCE(p.fecha_hasta, '9999-12-31')
            LIMIT 1
        """),
        {'usuario_id': usuario_id, 'fecha': fecha}
    ).fetchone()
    return dict(resultado._mapping) if resultado else None


def get_reglas_plan(plan_id):
    """Obtiene todas las reglas activas de un plan, ordenadas por prioridad descendente.
    Retorna lista de filas con: id, nombre, tipo_regla, criterio, valor_criterio,
    porcentaje, importe_fijo, prioridad, acumulable.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, nombre, tipo_regla, criterio, valor_criterio,
                   porcentaje, importe_fijo, prioridad, acumulable
            FROM comisiones_reglas
            WHERE id_plan = :plan_id
              AND activo = 1
            ORDER BY prioridad DESC
        """),
        {'plan_id': plan_id}
    ).fetchall()
    return [dict(r._mapping) for r in resultado]


def get_tramos_plan(plan_id):
    """Obtiene todos los tramos de un plan, ordenados por orden ascendente.
    Retorna lista de filas con: id, desde, hasta, porcentaje, importe_fijo, orden.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, desde, hasta, porcentaje, importe_fijo, orden
            FROM comisiones_tramos
            WHERE id_plan = :plan_id
            ORDER BY orden ASC
        """),
        {'plan_id': plan_id}
    ).fetchall()
    return [dict(r._mapping) for r in resultado]


def get_ventas_periodo(desde, hasta, usuario_id=None):
    """Obtiene todas las ventas (facturas) de un período.
    Si se pasa usuario_id, filtra por vendedor.
    Retorna lista de filas con: id, fecha, idcliente, idusuario, total, idtipocomprobante.
    """
    sql = """
        SELECT id, fecha, idcliente, idusuario, total, idtipocomprobante
        FROM facturav
        WHERE fecha BETWEEN :desde AND :hasta
    """
    params = {'desde': desde, 'hasta': hasta}

    if usuario_id is not None:
        sql += " AND idusuario = :usuario_id"
        params['usuario_id'] = usuario_id

    resultado = db.session.execute(text(sql), params).fetchall()
    return [dict(r._mapping) for r in resultado]


def get_items_periodo(desde, hasta, usuario_id=None):
    """Obtiene todos los ítems de ventas de un período, con datos del vendedor,
    cliente y tipo de operación (VENTA/CREDITO/DEBITO).
    Si se pasa usuario_id, filtra por vendedor.
    Retorna lista de filas con: idfactura, id_item, idarticulo, cantidad,
    precio_total, bonificacion, costo_unitario, idusuario, idcliente, fecha,
    tipo_operacion, idtipocomprobante.
    """
    sql = """
        SELECT
            iv.idfactura,
            iv.id AS id_item,
            iv.idarticulo,
            iv.cantidad,
            iv.precio_total,
            iv.bonificacion,
            iv.costo_unitario,
            f.idusuario,
            f.idcliente,
            f.fecha,
            f.idtipocomprobante,
            COALESCE(top.nombre, 'VENTA') AS tipo_operacion
        FROM itemsv iv
        JOIN facturav f ON iv.idfactura = f.id
        LEFT JOIN clientes c ON f.idcliente = c.id
        LEFT JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
        LEFT JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
            AND tca.id_iva_entidad = c.id_tipo_iva
        LEFT JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
        WHERE f.fecha BETWEEN :desde AND :hasta
    """
    params = {'desde': desde, 'hasta': hasta}

    if usuario_id is not None:
        sql += " AND f.idusuario = :usuario_id"
        params['usuario_id'] = usuario_id

    resultado = db.session.execute(text(sql), params).fetchall()
    return [dict(r._mapping) for r in resultado]


def get_detalles_existentes(liquidacion_id):
    """Obtiene los detalles existentes de una liquidación (para verificación de idempotencia).
    Retorna lista de filas con: id, id_factura, id_item, id_regla.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, id_factura, id_item, id_regla
            FROM comisiones_detalle
            WHERE id_liquidacion = :liquidacion_id
        """),
        {'liquidacion_id': liquidacion_id}
    ).fetchall()
    return [dict(r._mapping) for r in resultado]


def get_asignacion(usuario_id, fecha):
    """Obtiene la asignación activa de un vendedor en una fecha determinada.
    Retorna una fila con: id, id_usuario, id_plan, fecha_desde, fecha_hasta, o None.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, id_usuario, id_plan, fecha_desde, fecha_hasta
            FROM comisiones_asignaciones
            WHERE id_usuario = :usuario_id
              AND activo = 1
              AND :fecha BETWEEN fecha_desde AND COALESCE(fecha_hasta, '9999-12-31')
            LIMIT 1
        """),
        {'usuario_id': usuario_id, 'fecha': fecha}
    ).fetchone()
    return dict(resultado._mapping) if resultado else None


def get_usuario(usuario_id):
    """Obtiene la información de un usuario.
    Retorna una fila con: id, usuario (o nombre), o None.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, usuario
            FROM usuarios
            WHERE id = :usuario_id
        """),
        {'usuario_id': usuario_id}
    ).fetchone()
    return dict(resultado._mapping) if resultado else None


def get_articulo(articulo_id):
    """Obtiene la información de un artículo con su rubro, marca y tipo.
    Retorna una fila con: id, codigo, detalle, idrubro, rubro, idmarca, marca,
    idtipoarticulo, o None.
    """
    resultado = db.session.execute(
        text("""
            SELECT a.id, a.codigo, a.detalle,
                   a.idrubro, r.nombre AS rubro,
                   a.idmarca, m.nombre AS marca,
                   a.idtipoarticulo
            FROM articulos a
            LEFT JOIN rubros r ON a.idrubro = r.id
            LEFT JOIN marcas m ON a.idmarca = m.id
            WHERE a.id = :articulo_id
        """),
        {'articulo_id': articulo_id}
    ).fetchone()
    return dict(resultado._mapping) if resultado else None


def get_cliente(cliente_id):
    """Obtiene la información de un cliente.
    Retorna una fila con: id, nombre, documento, id_tipo_iva, o None.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, nombre, documento, id_tipo_iva
            FROM clientes
            WHERE id = :cliente_id
        """),
        {'cliente_id': cliente_id}
    ).fetchone()
    return dict(resultado._mapping) if resultado else None


def get_tipo_operacion_nombre(factura_id):
    """Obtiene el tipo de operación (VENTA/CREDITO/DEBITO) de una factura.
    Retorna 'VENTA' por defecto si no se puede resolver.
    """
    resultado = db.session.execute(
        text("""
            SELECT COALESCE(top.nombre, 'VENTA') AS tipo_operacion
            FROM facturav f
            JOIN clientes c ON f.idcliente = c.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                AND tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.id = :factura_id
        """),
        {'factura_id': factura_id}
    ).fetchone()
    return resultado[0] if resultado else 'VENTA'


# ================================================================
# Funciones de escritura para liquidaciones
# ================================================================

def crear_liquidacion(periodo_desde, periodo_hasta, usuario_id,
                      observaciones=None, estado='BORRADOR'):
    """Crea el encabezado de una liquidación y retorna su ID."""
    resultado = db.session.execute(
        text("""
            INSERT INTO comisiones_liquidaciones
                (periodo_desde, periodo_hasta, estado, total, observaciones, idusuario)
            VALUES
                (:periodo_desde, :periodo_hasta, :estado, 0, :observaciones, :idusuario)
        """),
        {
            'periodo_desde': periodo_desde,
            'periodo_hasta': periodo_hasta,
            'estado': estado,
            'observaciones': observaciones,
            'idusuario': usuario_id,
        }
    )
    # Obtener el ID insertado
    liquidacion_id = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
    return {'id': liquidacion_id}


def insertar_detalle(id_liquidacion, id_usuario, id_factura, id_item,
                     tipo_movimiento, tipo_comision, base_calculo,
                     id_regla=None, cantidad=0, costo_unitario=0,
                     importe_venta=0, importe_costo=0, importe_margen=0,
                     porcentaje=0, importe_comision=0, observaciones=None):
    """Inserta un registro de detalle de comisión."""
    db.session.execute(
        text("""
            INSERT INTO comisiones_detalle
                (id_liquidacion, id_usuario, id_factura, id_item, id_regla,
                 tipo_movimiento, tipo_comision, base_calculo,
                 cantidad, costo_unitario, importe_venta, importe_costo,
                 importe_margen, porcentaje, importe_comision, observaciones)
            VALUES
                (:id_liquidacion, :id_usuario, :id_factura, :id_item, :id_regla,
                 :tipo_movimiento, :tipo_comision, :base_calculo,
                 :cantidad, :costo_unitario, :importe_venta, :importe_costo,
                 :importe_margen, :porcentaje, :importe_comision, :observaciones)
        """),
        {
            'id_liquidacion': id_liquidacion,
            'id_usuario': id_usuario,
            'id_factura': id_factura,
            'id_item': id_item,
            'id_regla': id_regla,
            'tipo_movimiento': tipo_movimiento,
            'tipo_comision': tipo_comision,
            'base_calculo': base_calculo,
            'cantidad': cantidad,
            'costo_unitario': costo_unitario,
            'importe_venta': importe_venta,
            'importe_costo': importe_costo,
            'importe_margen': importe_margen,
            'porcentaje': porcentaje,
            'importe_comision': importe_comision,
            'observaciones': observaciones,
        }
    )


def actualizar_total_liquidacion(liquidacion_id, total):
    """Actualiza el total de una liquidación."""
    db.session.execute(
        text("""
            UPDATE comisiones_liquidaciones
            SET total = :total
            WHERE id = :id
        """),
        {'id': liquidacion_id, 'total': total}
    )


def actualizar_estado_liquidacion(liquidacion_id, estado, observaciones=None):
    """Actualiza el estado y opcionalmente las observaciones de una liquidación."""
    if observaciones is not None:
        db.session.execute(
            text("""
                UPDATE comisiones_liquidaciones
                SET estado = :estado, observaciones = :observaciones
                WHERE id = :id
            """),
            {'id': liquidacion_id, 'estado': estado, 'observaciones': observaciones}
        )
    else:
        db.session.execute(
            text("""
                UPDATE comisiones_liquidaciones
                SET estado = :estado
                WHERE id = :id
            """),
            {'id': liquidacion_id, 'estado': estado}
        )


def get_liquidacion(liquidacion_id):
    """Obtiene una liquidación por su ID.
    Retorna dict con: id, periodo_desde, periodo_hasta, fecha_liquidacion,
    estado, total, observaciones, idusuario, fecha_creacion.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, periodo_desde, periodo_hasta, fecha_liquidacion,
                   estado, total, observaciones, idusuario, fecha_creacion
            FROM comisiones_liquidaciones
            WHERE id = :id
        """),
        {'id': liquidacion_id}
    ).fetchone()
    return dict(resultado._mapping) if resultado else None


def get_liquidaciones(filtro=None):
    """Obtiene liquidaciones con filtros opcionales.
    Filtros soportados: estado, desde, hasta, usuario_id.
    Retorna lista de dicts.
    """
    filtro = filtro or {}
    sql = """
        SELECT id, periodo_desde, periodo_hasta, fecha_liquidacion,
               estado, total, observaciones, idusuario, fecha_creacion
        FROM comisiones_liquidaciones
        WHERE 1=1
    """
    params = {}

    if filtro.get('estado'):
        sql += " AND estado = :estado"
        params['estado'] = filtro['estado']

    if filtro.get('desde'):
        sql += " AND periodo_desde >= :desde"
        params['desde'] = filtro['desde']

    if filtro.get('hasta'):
        sql += " AND periodo_hasta <= :hasta"
        params['hasta'] = filtro['hasta']

    if filtro.get('usuario_id'):
        sql += " AND idusuario = :usuario_id"
        params['usuario_id'] = filtro['usuario_id']

    sql += " ORDER BY fecha_creacion DESC"

    resultado = db.session.execute(text(sql), params).fetchall()
    return [dict(r._mapping) for r in resultado]


def get_detalles_completos(liquidacion_id):
    """Obtiene el detalle completo de una liquidación con nombres resueltos.
    Retorna lista de dicts.
    """
    resultado = db.session.execute(
        text("""
            SELECT d.id, d.id_liquidacion, d.id_usuario, d.id_factura, d.id_item,
                   d.id_regla, d.tipo_movimiento, d.tipo_comision, d.base_calculo,
                   d.cantidad, d.costo_unitario, d.importe_venta, d.importe_costo,
                   d.importe_margen, d.porcentaje, d.importe_comision, d.observaciones,
                   r.nombre AS nombre_regla,
                   u.usuario AS nombre_usuario
            FROM comisiones_detalle d
            LEFT JOIN comisiones_reglas r ON d.id_regla = r.id
            LEFT JOIN usuarios u ON d.id_usuario = u.id
            WHERE d.id_liquidacion = :liquidacion_id
            ORDER BY d.id_usuario, d.id_factura, d.id_item
        """),
        {'liquidacion_id': liquidacion_id}
    ).fetchall()
    return [dict(r._mapping) for r in resultado]


def contar_liquidaciones_por_periodo(desde, hasta):
    """Cuenta liquidaciones que se superponen con un período dado.
    Excluye liquidaciones ANULADAS.
    Retorna cantidad de liquidaciones encontradas.
    """
    resultado = db.session.execute(
        text("""
            SELECT COUNT(*) AS cantidad
            FROM comisiones_liquidaciones
            WHERE estado != 'ANULADA'
              AND NOT (periodo_hasta < :desde OR periodo_desde > :hasta)
        """),
        {'desde': desde, 'hasta': hasta}
    ).fetchone()
    return resultado[0] if resultado else 0


# ================================================================
# CRUD para planes
# ================================================================

def get_planes(incluir_inactivos=False):
    """Obtiene todos los planes de comisiones.
    Retorna lista de dicts.
    """
    sql = """
        SELECT id, nombre, descripcion, activo, fecha_desde, fecha_hasta,
               tipo_calculo, base_calculo, modo_escalas, observaciones,
               fecha_creacion, fecha_actualizacion
        FROM comisiones_planes
    """
    if not incluir_inactivos:
        sql += " WHERE activo = 1"
    sql += " ORDER BY nombre"
    
    resultado = db.session.execute(text(sql)).fetchall()
    return [dict(r._mapping) for r in resultado]


def get_plan(plan_id):
    """Obtiene un plan por su ID.
    Retorna dict o None.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, nombre, descripcion, activo, fecha_desde, fecha_hasta,
                   tipo_calculo, base_calculo, modo_escalas, observaciones,
                   fecha_creacion, fecha_actualizacion
            FROM comisiones_planes
            WHERE id = :id
        """),
        {'id': plan_id}
    ).fetchone()
    return dict(resultado._mapping) if resultado else None


def crear_plan(nombre, tipo_calculo, base_calculo, modo_escalas,
               fecha_desde, fecha_hasta=None, descripcion=None,
               observaciones=None, creado_por=None):
    """Crea un nuevo plan de comisiones.
    Retorna el ID del plan creado.
    """
    resultado = db.session.execute(
        text("""
            INSERT INTO comisiones_planes
                (nombre, tipo_calculo, base_calculo, modo_escalas,
                 fecha_desde, fecha_hasta, descripcion, observaciones, creado_por)
            VALUES
                (:nombre, :tipo_calculo, :base_calculo, :modo_escalas,
                 :fecha_desde, :fecha_hasta, :descripcion, :observaciones, :creado_por)
        """),
        {
            'nombre': nombre,
            'tipo_calculo': tipo_calculo,
            'base_calculo': base_calculo,
            'modo_escalas': modo_escalas,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'descripcion': descripcion,
            'observaciones': observaciones,
            'creado_por': creado_por,
        }
    )
    plan_id = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
    return plan_id


def actualizar_plan(plan_id, **kwargs):
    """Actualiza un plan de comisiones.
    Acepta cualquier campo como keyword argument.
    """
    if not kwargs:
        return
    
    set_clauses = []
    params = {'id': plan_id}
    for campo, valor in kwargs.items():
        set_clauses.append(f"{campo} = :{campo}")
        params[campo] = valor
    
    sql = f"""
        UPDATE comisiones_planes
        SET {', '.join(set_clauses)}
        WHERE id = :id
    """
    db.session.execute(text(sql), params)


def toggle_plan(plan_id):
    """Activa/desactiva un plan.
    Retorna el nuevo estado.
    """
    resultado = db.session.execute(
        text("SELECT activo FROM comisiones_planes WHERE id = :id"),
        {'id': plan_id}
    ).fetchone()
    
    if not resultado:
        return None
    
    nuevo_estado = not resultado[0]
    db.session.execute(
        text("UPDATE comisiones_planes SET activo = :activo WHERE id = :id"),
        {'activo': nuevo_estado, 'id': plan_id}
    )
    return nuevo_estado


def duplicar_plan(plan_id, nuevo_nombre, creado_por=None):
    """Duplica un plan con todas sus reglas y tramos.
    Retorna el ID del nuevo plan.
    """
    # Obtener plan original
    plan_original = get_plan(plan_id)
    if not plan_original:
        return None
    
    # Crear nuevo plan
    nuevo_plan_id = crear_plan(
        nombre=nuevo_nombre,
        tipo_calculo=plan_original['tipo_calculo'],
        base_calculo=plan_original['base_calculo'],
        modo_escalas=plan_original['modo_escalas'],
        fecha_desde=plan_original['fecha_desde'],
        fecha_hasta=plan_original['fecha_hasta'],
        descripcion=plan_original['descripcion'],
        observaciones=plan_original['observaciones'],
        creado_por=creado_por,
    )
    
    # Copiar reglas
    reglas = get_reglas_plan(plan_id)
    for regla in reglas:
        db.session.execute(
            text("""
                INSERT INTO comisiones_reglas
                    (id_plan, nombre, tipo_regla, criterio, valor_criterio,
                     porcentaje, importe_fijo, prioridad, acumulable, activo,
                     fecha_desde, fecha_hasta)
                VALUES
                    (:id_plan, :nombre, :tipo_regla, :criterio, :valor_criterio,
                     :porcentaje, :importe_fijo, :prioridad, :acumulable, 1,
                     :fecha_desde, :fecha_hasta)
            """),
            {
                'id_plan': nuevo_plan_id,
                'nombre': regla['nombre'],
                'tipo_regla': regla['tipo_regla'],
                'criterio': regla['criterio'],
                'valor_criterio': regla['valor_criterio'],
                'porcentaje': regla['porcentaje'],
                'importe_fijo': regla['importe_fijo'],
                'prioridad': regla['prioridad'],
                'acumulable': regla['acumulable'],
                'fecha_desde': plan_original['fecha_desde'],
                'fecha_hasta': plan_original['fecha_hasta'],
            }
        )
    
    # Copiar tramos
    tramos = get_tramos_plan(plan_id)
    for tramo in tramos:
        db.session.execute(
            text("""
                INSERT INTO comisiones_tramos
                    (id_plan, desde, hasta, porcentaje, importe_fijo, orden)
                VALUES
                    (:id_plan, :desde, :hasta, :porcentaje, :importe_fijo, :orden)
            """),
            {
                'id_plan': nuevo_plan_id,
                'desde': tramo['desde'],
                'hasta': tramo['hasta'],
                'porcentaje': tramo['porcentaje'],
                'importe_fijo': tramo['importe_fijo'],
                'orden': tramo['orden'],
            }
        )
    
    return nuevo_plan_id


# ================================================================
# CRUD para reglas
# ================================================================

def get_regla(regla_id):
    """Obtiene una regla por su ID.
    Retorna dict o None.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, id_plan, nombre, tipo_regla, criterio, valor_criterio,
                   porcentaje, importe_fijo, prioridad, acumulable, activo,
                   fecha_desde, fecha_hasta
            FROM comisiones_reglas
            WHERE id = :id
        """),
        {'id': regla_id}
    ).fetchone()
    return dict(resultado._mapping) if resultado else None


def crear_regla(id_plan, nombre, criterio, valor_criterio, fecha_desde,
                tipo_regla='EXCLUSIVA', porcentaje=0, importe_fijo=0,
                prioridad=0, acumulable=False, fecha_hasta=None):
    """Crea una nueva regla de comisión.
    Retorna el ID de la regla creada.
    """
    resultado = db.session.execute(
        text("""
            INSERT INTO comisiones_reglas
                (id_plan, nombre, tipo_regla, criterio, valor_criterio,
                 porcentaje, importe_fijo, prioridad, acumulable, activo,
                 fecha_desde, fecha_hasta)
            VALUES
                (:id_plan, :nombre, :tipo_regla, :criterio, :valor_criterio,
                 :porcentaje, :importe_fijo, :prioridad, :acumulable, 1,
                 :fecha_desde, :fecha_hasta)
        """),
        {
            'id_plan': id_plan,
            'nombre': nombre,
            'tipo_regla': tipo_regla,
            'criterio': criterio,
            'valor_criterio': valor_criterio,
            'porcentaje': porcentaje,
            'importe_fijo': importe_fijo,
            'prioridad': prioridad,
            'acumulable': acumulable,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    )
    regla_id = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
    return regla_id


def actualizar_regla(regla_id, **kwargs):
    """Actualiza una regla de comisión.
    Acepta cualquier campo como keyword argument.
    """
    if not kwargs:
        return
    
    set_clauses = []
    params = {'id': regla_id}
    for campo, valor in kwargs.items():
        set_clauses.append(f"{campo} = :{campo}")
        params[campo] = valor
    
    sql = f"""
        UPDATE comisiones_reglas
        SET {', '.join(set_clauses)}
        WHERE id = :id
    """
    db.session.execute(text(sql), params)


def eliminar_regla(regla_id):
    """Elimina una regla de comisión (soft delete - desactiva)."""
    db.session.execute(
        text("UPDATE comisiones_reglas SET activo = 0 WHERE id = :id"),
        {'id': regla_id}
    )


# ================================================================
# CRUD para tramos
# ================================================================

def get_tramo(tramo_id):
    """Obtiene un tramo por su ID.
    Retorna dict o None.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, id_plan, desde, hasta, porcentaje, importe_fijo, orden
            FROM comisiones_tramos
            WHERE id = :id
        """),
        {'id': tramo_id}
    ).fetchone()
    return dict(resultado._mapping) if resultado else None


def crear_tramo(id_plan, desde, hasta, porcentaje=0, importe_fijo=0, orden=0):
    """Crea un nuevo tramo de escala.
    Retorna el ID del tramo creado.
    """
    resultado = db.session.execute(
        text("""
            INSERT INTO comisiones_tramos
                (id_plan, desde, hasta, porcentaje, importe_fijo, orden)
            VALUES
                (:id_plan, :desde, :hasta, :porcentaje, :importe_fijo, :orden)
        """),
        {
            'id_plan': id_plan,
            'desde': desde,
            'hasta': hasta,
            'porcentaje': porcentaje,
            'importe_fijo': importe_fijo,
            'orden': orden,
        }
    )
    tramo_id = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
    return tramo_id


def actualizar_tramo(tramo_id, **kwargs):
    """Actualiza un tramo de escala.
    Acepta cualquier campo como keyword argument.
    """
    if not kwargs:
        return
    
    set_clauses = []
    params = {'id': tramo_id}
    for campo, valor in kwargs.items():
        set_clauses.append(f"{campo} = :{campo}")
        params[campo] = valor
    
    sql = f"""
        UPDATE comisiones_tramos
        SET {', '.join(set_clauses)}
        WHERE id = :id
    """
    db.session.execute(text(sql), params)


def eliminar_tramo(tramo_id):
    """Elimina un tramo de escala."""
    db.session.execute(
        text("DELETE FROM comisiones_tramos WHERE id = :id"),
        {'id': tramo_id}
    )


# ================================================================
# CRUD para asignaciones
# ================================================================

def get_asignaciones(filtro=None):
    """Obtiene asignaciones con filtros opcionales.
    Retorna lista de dicts.
    """
    filtro = filtro or {}
    sql = """
        SELECT a.id, a.id_usuario, a.id_plan, a.fecha_desde, a.fecha_hasta,
               a.activo, u.usuario AS nombre_usuario, p.nombre AS nombre_plan
        FROM comisiones_asignaciones a
        LEFT JOIN usuarios u ON a.id_usuario = u.id
        LEFT JOIN comisiones_planes p ON a.id_plan = p.id
        WHERE 1=1
    """
    params = {}
    
    if filtro.get('usuario_id'):
        sql += " AND a.id_usuario = :usuario_id"
        params['usuario_id'] = filtro['usuario_id']
    
    if filtro.get('plan_id'):
        sql += " AND a.id_plan = :plan_id"
        params['plan_id'] = filtro['plan_id']
    
    if filtro.get('activo') is not None:
        sql += " AND a.activo = :activo"
        params['activo'] = filtro['activo']
    
    sql += " ORDER BY a.fecha_desde DESC"
    
    resultado = db.session.execute(text(sql), params).fetchall()
    return [dict(r._mapping) for r in resultado]


def get_asignacion_por_id(asignacion_id):
    """Obtiene una asignación por su ID.
    Retorna dict o None.
    """
    resultado = db.session.execute(
        text("""
            SELECT a.id, a.id_usuario, a.id_plan, a.fecha_desde, a.fecha_hasta,
                   a.activo, u.usuario AS nombre_usuario, p.nombre AS nombre_plan
            FROM comisiones_asignaciones a
            LEFT JOIN usuarios u ON a.id_usuario = u.id
            LEFT JOIN comisiones_planes p ON a.id_plan = p.id
            WHERE a.id = :id
        """),
        {'id': asignacion_id}
    ).fetchone()
    return dict(resultado._mapping) if resultado else None


def crear_asignacion(id_usuario, id_plan, fecha_desde, fecha_hasta=None, activo=True):
    """Crea una nueva asignación.
    Retorna el ID de la asignación creada.
    """
    resultado = db.session.execute(
        text("""
            INSERT INTO comisiones_asignaciones
                (id_usuario, id_plan, fecha_desde, fecha_hasta, activo)
            VALUES
                (:id_usuario, :id_plan, :fecha_desde, :fecha_hasta, :activo)
        """),
        {
            'id_usuario': id_usuario,
            'id_plan': id_plan,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'activo': activo,
        }
    )
    asignacion_id = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
    return asignacion_id


def actualizar_asignacion(asignacion_id, **kwargs):
    """Actualiza una asignación.
    Acepta cualquier campo como keyword argument.
    """
    if not kwargs:
        return
    
    set_clauses = []
    params = {'id': asignacion_id}
    for campo, valor in kwargs.items():
        set_clauses.append(f"{campo} = :{campo}")
        params[campo] = valor
    
    sql = f"""
        UPDATE comisiones_asignaciones
        SET {', '.join(set_clauses)}
        WHERE id = :id
    """
    db.session.execute(text(sql), params)


def eliminar_asignacion(asignacion_id):
    """Elimina una asignación (soft delete - desactiva)."""
    db.session.execute(
        text("UPDATE comisiones_asignaciones SET activo = 0 WHERE id = :id"),
        {'id': asignacion_id}
    )


def get_vendedores():
    """Obtiene todos los vendedores (usuarios).
    Retorna lista de dicts.
    """
    resultado = db.session.execute(
        text("""
            SELECT id, usuario
            FROM usuarios
            ORDER BY usuario
        """)
    ).fetchall()
    return [dict(r._mapping) for r in resultado]
