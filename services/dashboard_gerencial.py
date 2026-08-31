# -*- coding: utf-8 -*-
"""
Servicio de Dashboard Gerencial
Funciones SQL para obtener KPIs y métricas del dashboard gerencial Stage 1
"""

from flask import session
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from utils.db import db
from models.configs import Configuracion


def _formato_moneda(valor):
    """Formatea un número como moneda argentina: $ 1.250.450,50"""
    if valor is None:
        return '$ 0,00'
    # Acepta Decimal, int o float
    if isinstance(valor, Decimal):
        valor = float(valor)
    partes = f'{valor:,.2f}'.split('.')
    parte_entera = partes[0].replace(',', '.')
    parte_decimal = partes[1]
    return f'$ {parte_entera},{parte_decimal}'


def _params_base(desde, hasta, id_sucursal=None):
    """Devuelve dict de parámetros base para queries."""
    params = {'desde': desde, 'hasta': hasta}
    if id_sucursal:
        params['id_sucursal'] = id_sucursal
    return params


def _sucursal_filter(alias='f', params=None):
    """Devuelve cláusula WHERE extra para sucursal si id_sucursal está en params."""
    if params and params.get('id_sucursal'):
        return f' AND {alias}.idsucursal = :id_sucursal'
    return ''


# ─── 1.1 KPIs ───────────────────────────────────────────────────────────────
def get_kpis(desde, hasta, id_sucursal=None):
    """
    Obtiene KPIs principales: ventas totales, cobranzas, margen bruto, ticket promedio.
    Calcula variación % vs período anterior.
    Retorna dict con valores formateados y raw.
    """
    params = _params_base(desde, hasta, id_sucursal)
    suc_filter = _sucursal_filter('f', params)

    try:
        dias_periodo = (hasta - desde).days + 1
        desde_ant = desde - timedelta(days=dias_periodo)
        hasta_ant = desde - timedelta(days=1)

        # ── Ventas periodo actual ──
        sql_ventas = text(f"""
            SELECT
                COALESCE(SUM(CASE
                    WHEN top.nombre IN ('VENTA', 'DEBITO') THEN f.total
                    ELSE -f.total
                END), 0) AS total_ventas,
                COUNT(f.id) AS cantidad_op,
                COALESCE(AVG(f.total), 0) AS ticket_promedio,
                COALESCE(SUM(f.neto), 0) AS total_neto
            FROM facturav f
            JOIN clientes c ON f.idcliente = c.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                AND tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.fecha BETWEEN :desde AND :hasta
                AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
            {suc_filter}
        """)

        params_ant = {
            'desde': desde_ant,
            'hasta': hasta_ant
        }
        if id_sucursal:
            params_ant['id_sucursal'] = id_sucursal

        r_act = db.session.execute(sql_ventas, params).fetchone()
        r_ant = db.session.execute(sql_ventas, params_ant).fetchone()

        # ── Costo mercadería vendida (margen) ──
        sql_costo = text(f"""
            SELECT COALESCE(SUM(iv.cantidad * a.costo_total), 0) AS costo_total
            FROM itemsv iv
            JOIN facturav f ON iv.idfactura = f.id
            JOIN clientes c ON f.idcliente = c.id
            JOIN articulos a ON iv.idarticulo = a.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                AND tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.fecha BETWEEN :desde AND :hasta
                AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
            {suc_filter}
        """)

        costo_act = db.session.execute(sql_costo, params).fetchone()
        costo_ant = db.session.execute(sql_costo, params_ant).fetchone()

        # ── Cobranzas (pagos_fv) ──
        sql_cobranzas = text(f"""
            SELECT COALESCE(SUM(pf.total), 0) AS total_cobrado
            FROM pagos_fv pf
            JOIN facturav f ON pf.idfactura = f.id
            WHERE f.fecha BETWEEN :desde AND :hasta
            {suc_filter}
        """)

        cob_act = db.session.execute(sql_cobranzas, params).fetchone()
        cob_ant = db.session.execute(sql_cobranzas, params_ant).fetchone()

        # ── Cálculos ──
        ventas_actual = Decimal(str(r_act.total_ventas or 0))
        ventas_anterior = Decimal(str(r_ant.total_ventas or 0))
        var_ventas = round(float((ventas_actual - ventas_anterior) / ventas_anterior * 100), 1) if ventas_anterior > 0 else None

        cob_actual = Decimal(str(cob_act.total_cobrado or 0))
        cob_anterior = Decimal(str(cob_ant.total_cobrado or 0))
        var_cobranzas = round(float((cob_actual - cob_anterior) / cob_anterior * 100), 1) if cob_anterior > 0 else None

        costo_act_val = Decimal(str(costo_act.costo_total or 0))
        margen_bruto = ventas_actual - costo_act_val
        pct_margen = round(float(margen_bruto / ventas_actual * 100), 1) if ventas_actual > 0 else 0

        tkt_actual = Decimal(str(r_act.ticket_promedio or 0))
        tkt_anterior = Decimal(str(r_ant.ticket_promedio or 0))
        var_ticket = round(float((tkt_actual - tkt_anterior) / tkt_anterior * 100), 1) if tkt_anterior > 0 else None

        return {
            'ventas_totales': _formato_moneda(ventas_actual),
            'ventas_totales_raw': float(ventas_actual),
            'var_ventas': var_ventas,
            'cobranzas': _formato_moneda(cob_actual),
            'cobranzas_raw': float(cob_actual),
            'var_cobranzas': var_cobranzas,
            'margen_bruto': _formato_moneda(margen_bruto),
            'margen_bruto_raw': float(margen_bruto),
            'pct_margen': pct_margen,
            'ticket_promedio': _formato_moneda(tkt_actual),
            'ticket_promedio_raw': float(tkt_actual),
            'var_ticket': var_ticket,
        }

    except SQLAlchemyError as e:
        print(f"Error en KPIs dashboard gerencial: {e}")
        return {
            'ventas_totales': '$ 0,00',
            'ventas_totales_raw': 0,
            'var_ventas': 0,
            'cobranzas': '$ 0,00',
            'cobranzas_raw': 0,
            'var_cobranzas': 0,
            'margen_bruto': '$ 0,00',
            'margen_bruto_raw': 0,
            'pct_margen': 0,
            'ticket_promedio': '$ 0,00',
            'ticket_promedio_raw': 0,
            'var_ticket': 0,
        }


# ─── 1.2 Evolución de ventas ────────────────────────────────────────────────
def get_evolucion_ventas(desde, hasta, id_sucursal=None, comparar=False, granularidad='auto'):
    """
    Devuelve datos para gráfico línea de evolución de ventas.
    Granularidad: 'diaria', 'semanal', 'mensual' o 'auto' (según rango).
    Si comparar=True, incluye datos del período anterior para overlay.
    """
    params = _params_base(desde, hasta, id_sucursal)
    suc_filter = _sucursal_filter('f', params)

    try:
        dias_periodo = (hasta - desde).days + 1

        # Determinar granularidad automática
        if granularidad == 'auto':
            if dias_periodo <= 31:
                granularidad = 'diaria'
            elif dias_periodo <= 180:
                granularidad = 'semanal'
            else:
                granularidad = 'mensual'

        if granularidad == 'diaria':
            select_grupo = "DATE_FORMAT(f.fecha, '%d/%m') AS periodo"
            order_grupo = "f.fecha"
            group_grupo = "f.fecha"
        elif granularidad == 'semanal':
            select_grupo = "CONCAT('Sem ', WEEK(f.fecha, 1)) AS periodo"
            order_grupo = "MIN(f.fecha)"
            group_grupo = "YEAR(f.fecha), WEEK(f.fecha, 1)"
        else:
            select_grupo = "DATE_FORMAT(f.fecha, '%b %Y') AS periodo"
            order_grupo = "DATE_FORMAT(f.fecha, '%Y-%m-01')"
            group_grupo = "DATE_FORMAT(f.fecha, '%Y-%m')"

        sql = text(f"""
            SELECT
                {select_grupo},
                {order_grupo} AS fecha_orden,
                COALESCE(SUM(CASE
                    WHEN top.nombre IN ('VENTA', 'DEBITO') THEN f.total
                    ELSE -f.total
                END), 0) AS total
            FROM facturav f
            JOIN clientes c ON f.idcliente = c.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                AND tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.fecha BETWEEN :desde AND :hasta
                AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
            {suc_filter}
            GROUP BY {group_grupo}
            ORDER BY fecha_orden
        """)

        result = db.session.execute(sql, params).fetchall()

        periodos = []
        totales = []
        for row in result:
            periodos.append(row.periodo)
            totales.append(round(float(row.total), 2))

        data = {
            'periodos': periodos,
            'totales': totales,
            'granularidad': granularidad
        }

        # Período anterior para comparación
        if comparar:
            dias = (hasta - desde).days + 1
            desde_ant = desde - timedelta(days=dias)
            hasta_ant = desde - timedelta(days=1)
            params_ant = {'desde': desde_ant, 'hasta': hasta_ant}
            if id_sucursal:
                params_ant['id_sucursal'] = id_sucursal

            r_ant = db.session.execute(sql, params_ant).fetchall()
            totales_ant = [round(float(row.total), 2) for row in r_ant]
            data['totales_anteriores'] = totales_ant

        return data

    except SQLAlchemyError as e:
        print(f"Error en evolución ventas dashboard gerencial: {e}")
        return {'periodos': [], 'totales': [], 'granularidad': 'diaria'}


# ─── 1.3 Ventas por sucursal ────────────────────────────────────────────────
def get_ventas_sucursal(desde, hasta, id_sucursal=None):
    """
    Ventas agrupadas por sucursal: importe, operaciones, ticket promedio, participación %.
    """
    params = _params_base(desde, hasta, id_sucursal)
    # Para ventas por sucursal, si hay filtro de sucursal, solo mostrar esa
    suc_filter = ''
    if id_sucursal:
        suc_filter = ' AND f.idsucursal = :id_sucursal'

    try:
        sql = text(f"""
            SELECT
                s.nombre AS sucursal,
                f.idsucursal AS id_sucursal,
                COALESCE(SUM(CASE
                    WHEN top.nombre IN ('VENTA', 'DEBITO') THEN f.total
                    ELSE -f.total
                END), 0) AS ventas_totales,
                COUNT(f.id) AS operaciones,
                COALESCE(AVG(f.total), 0) AS ticket_promedio
            FROM facturav f
            JOIN sucursales s ON f.idsucursal = s.id
            JOIN clientes c ON f.idcliente = c.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                AND tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.fecha BETWEEN :desde AND :hasta
                AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
            {suc_filter}
            GROUP BY f.idsucursal, s.nombre
            ORDER BY ventas_totales DESC
        """)

        result = db.session.execute(sql, params).fetchall()

        # Total general para calcular participación
        total_ventas = sum(float(row.ventas_totales or 0) for row in result)

        sucursales = []
        for row in result:
            ventas = float(row.ventas_totales or 0)
            op = int(row.operaciones or 0)
            tkt = float(row.ticket_promedio or 0)
            pct = (ventas / total_ventas * 100) if total_ventas > 0 else 0
            sucursales.append({
                'sucursal': row.sucursal,
                'id_sucursal': row.id_sucursal,
                'ventas_totales': _formato_moneda(ventas),
                'ventas_totales_raw': ventas,
                'operaciones': op,
                'ticket_promedio': _formato_moneda(tkt),
                'participacion': round(pct, 1),
            })

        return sucursales

    except SQLAlchemyError as e:
        print(f"Error en ventas por sucursal dashboard gerencial: {e}")
        return []


# ─── 1.4 Ventas por rubro ───────────────────────────────────────────────────
def get_ventas_rubro(desde, hasta, id_sucursal=None):
    """
    Ventas agrupadas por rubro: importe, unidades, participación %.
    Artículos sin rubro se agrupan como "Sin rubro".
    """
    params = _params_base(desde, hasta, id_sucursal)
    suc_filter = _sucursal_filter('f', params)

    try:
        sql = text(f"""
            SELECT
                COALESCE(r.nombre, 'Sin rubro') AS rubro,
                COALESCE(SUM(iv.precio_total), 0) AS importe,
                COALESCE(SUM(iv.cantidad), 0) AS unidades
            FROM itemsv iv
            JOIN facturav f ON iv.idfactura = f.id
            JOIN articulos a ON iv.idarticulo = a.id
            LEFT JOIN rubros r ON a.idrubro = r.id
            JOIN clientes c ON f.idcliente = c.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                AND tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.fecha BETWEEN :desde AND :hasta
                AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
            {suc_filter}
            GROUP BY r.id, r.nombre
            ORDER BY importe DESC
        """)

        result = db.session.execute(sql, params).fetchall()

        total_importe = sum(float(row.importe or 0) for row in result)

        rubros = []
        for row in result:
            importe = float(row.importe or 0)
            unidades = float(row.unidades or 0)
            pct = (importe / total_importe * 100) if total_importe > 0 else 0
            rubros.append({
                'rubro': row.rubro,
                'importe': _formato_moneda(importe),
                'importe_raw': importe,
                'unidades': int(unidades),
                'participacion': round(pct, 1),
            })

        return {'rubros': rubros, 'total_importe': total_importe}

    except SQLAlchemyError as e:
        print(f"Error en ventas por rubro dashboard gerencial: {e}")
        return {'rubros': [], 'total_importe': 0}


# ─── 1.4 Comparación Rubro × Sucursal ────────────────────────────────────────
def get_rubro_sucursal_comparacion(desde, hasta, id_sucursal=None):
    """
    Cross-tab: rubros como filas, sucursales como columnas.
    Cada celda tiene unidades, porcentaje (participación en la sucursal),
    e indicador (up/down/neutral) comparando contra el benchmark de la sucursal.
    """
    params = _params_base(desde, hasta, id_sucursal)
    suc_filter = _sucursal_filter('f', params)

    try:
        sql = text(f"""
            SELECT
                COALESCE(r.nombre, 'Sin rubro') AS rubro,
                s.nombre AS sucursal,
                s.id AS id_sucursal,
                COALESCE(SUM(iv.cantidad), 0) AS unidades
            FROM itemsv iv
            JOIN facturav f ON iv.idfactura = f.id
            JOIN articulos a ON iv.idarticulo = a.id
            LEFT JOIN rubros r ON a.idrubro = r.id
            JOIN sucursales s ON f.idsucursal = s.id
            JOIN clientes c ON f.idcliente = c.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                AND tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.fecha BETWEEN :desde AND :hasta
                AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
            {suc_filter}
            GROUP BY r.id, r.nombre, s.id, s.nombre
            ORDER BY r.nombre, s.nombre
        """)

        rows = db.session.execute(sql, params).fetchall()

        if not rows:
            return {'rubros': [], 'sucursales': [], 'cells': {}, 'benchmarks': {}, 'grand_total': 0}

        # Collect unique rubros and sucursales (sorted alphabetically)
        rubros_set = set()
        sucursales_set = set()
        for row in rows:
            rubros_set.add(row.rubro)
            sucursales_set.add(row.sucursal)

        rubros = sorted(rubros_set)
        sucursales = sorted(sucursales_set)

        # Build per-sucursal totals
        sucursal_totals = {s: 0 for s in sucursales}
        cells_raw = {}  # rubro -> sucursal -> unidades
        for row in rows:
            r = row.rubro
            s = row.sucursal
            u = int(row.unidades or 0)
            sucursal_totals[s] += u
            if r not in cells_raw:
                cells_raw[r] = {}
            cells_raw[r][s] = u

        grand_total = sum(sucursal_totals.values())

        # Calculate benchmarks (sucursal's overall share of grand_total)
        benchmarks = {}
        for s in sucursales:
            benchmarks[s] = round((sucursal_totals[s] / grand_total * 100), 1) if grand_total > 0 else 0

        # Build rubro totals (sum of all sucursales per rubro)
        rubro_totals = {}
        for r in rubros:
            rubro_totals[r] = sum(cells_raw.get(r, {}).get(s, 0) for s in sucursales)

        # Build cells with percentage and indicator
        cells = {}
        for r in rubros:
            cells[r] = {}
            # Benchmark: rubro's % of grand total
            rubro_pct_total = round((rubro_totals[r] / grand_total * 100), 1) if grand_total > 0 else 0
            for s in sucursales:
                u = cells_raw.get(r, {}).get(s, 0)
                total_s = sucursal_totals[s]
                pct = round((u / total_s * 100), 1) if total_s > 0 else 0

                if pct > rubro_pct_total:
                    indicator = 'up'
                elif pct < rubro_pct_total:
                    indicator = 'down'
                else:
                    indicator = 'neutral'

                cells[r][s] = {
                    'unidades': u,
                    'porcentaje': pct,
                    'indicator': indicator,
                }

        return {
            'rubros': rubros,
            'sucursales': sucursales,
            'cells': cells,
            'rubro_totals': rubro_totals,
            'benchmarks': benchmarks,
            'grand_total': grand_total,
        }

    except SQLAlchemyError as e:
        print(f"Error en comparación rubro-sucursal dashboard gerencial: {e}")
        return {'rubros': [], 'sucursales': [], 'cells': {}, 'benchmarks': {}, 'grand_total': 0}


# ─── 1.5 Top productos ──────────────────────────────────────────────────────
def get_top_productos(desde, hasta, id_sucursal=None, limite=10):
    """
    Top productos por facturación con cantidad y margen estimado.
    """
    params = _params_base(desde, hasta, id_sucursal)
    params['limite'] = limite
    suc_filter = _sucursal_filter('f', params)

    try:
        sql = text(f"""
            SELECT
                a.codigo,
                a.detalle,
                COALESCE(r.nombre, 'Sin rubro') AS rubro,
                COALESCE(SUM(iv.precio_total), 0) AS facturacion,
                COALESCE(SUM(iv.cantidad), 0) AS cantidad,
                COALESCE(SUM(iv.cantidad * a.costo_total), 0) AS costo,
                COALESCE(SUM(iv.precio_total), 0) - COALESCE(SUM(iv.cantidad * a.costo_total), 0) AS margen
            FROM itemsv iv
            JOIN facturav f ON iv.idfactura = f.id
            JOIN articulos a ON iv.idarticulo = a.id
            LEFT JOIN rubros r ON a.idrubro = r.id
            JOIN clientes c ON f.idcliente = c.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                AND tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.fecha BETWEEN :desde AND :hasta
                AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
            {suc_filter}
            GROUP BY a.id, a.codigo, a.detalle, r.id, r.nombre
            ORDER BY facturacion DESC
            LIMIT :limite
        """)

        result = db.session.execute(sql, params).fetchall()

        productos = []
        for row in result:
            fac = float(row.facturacion or 0)
            cant = float(row.cantidad or 0)
            marg = float(row.margen or 0)
            productos.append({
                'codigo': row.codigo,
                'detalle': (row.detalle[:35] + '...') if row.detalle and len(row.detalle) > 35 else (row.detalle or ''),
                'rubro': row.rubro,
                'facturacion': _formato_moneda(fac),
                'facturacion_raw': fac,
                'cantidad': int(cant),
                'margen': _formato_moneda(marg),
                'margen_raw': marg,
            })

        return productos

    except SQLAlchemyError as e:
        print(f"Error en top productos dashboard gerencial: {e}")
        return []


# ─── 1.6 Top vendedores ─────────────────────────────────────────────────────
def get_top_vendedores(desde, hasta, id_sucursal=None, limite=10):
    """
    Top vendedores por ventas totales con operaciones, ticket promedio y participación.
    Se usa el campo vendedor de facturav (nombre del vendedor).
    """
    params = _params_base(desde, hasta, id_sucursal)
    params['limite'] = limite
    suc_filter = _sucursal_filter('f', params)

    try:
        sql = text(f"""
            SELECT
                COALESCE(u.nombre, 'Sin vendedor') AS vendedor,
                COALESCE(SUM(CASE
                    WHEN top.nombre IN ('VENTA', 'DEBITO') THEN f.total
                    ELSE -f.total
                END), 0) AS ventas_totales,
                COUNT(f.id) AS operaciones,
                COALESCE(AVG(f.total), 0) AS ticket_promedio
            FROM facturav f
            JOIN clientes c ON f.idcliente = c.id
            JOIN usuarios u ON f.idusuario = u.id
            JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
            JOIN tipo_comp_aplica tca ON tc.id = tca.id_tipo_comp
                AND tca.id_iva_entidad = c.id_tipo_iva
            JOIN tipo_operacion top ON tca.id_tipo_oper = top.id
            WHERE f.fecha BETWEEN :desde AND :hasta
                AND top.nombre IN ('VENTA', 'CREDITO', 'DEBITO')
            {suc_filter}
            GROUP BY u.id, u.nombre
            ORDER BY ventas_totales DESC
            LIMIT :limite
        """)

        result = db.session.execute(sql, params).fetchall()

        total_ventas = sum(float(row.ventas_totales or 0) for row in result)

        vendedores = []
        for row in result:
            ventas = float(row.ventas_totales or 0)
            op = int(row.operaciones or 0)
            tkt = float(row.ticket_promedio or 0)
            pct = (ventas / total_ventas * 100) if total_ventas > 0 else 0
            vendedores.append({
                'vendedor': row.vendedor,
                'ventas_totales': _formato_moneda(ventas),
                'ventas_totales_raw': ventas,
                'operaciones': op,
                'ticket_promedio': _formato_moneda(tkt),
                'participacion': round(pct, 1),
            })

        return vendedores

    except SQLAlchemyError as e:
        print(f"Error en top vendedores dashboard gerencial: {e}")
        return []


# ─── 2.1 Stock KPIs ─────────────────────────────────────────────────────────
def get_stock_kpis(id_sucursal=None):
    """
    Clasifica artículos en 4 categorías de stock usando 'deseable' como umbral mínimo.
    Retorna dict con conteos por categoría, total, y valor total del stock.
    """
    params = {}
    suc_filter = ''
    if id_sucursal:
        suc_filter = ' AND s.idsucursal = :id_sucursal'
        params['id_sucursal'] = id_sucursal

    try:
        sql = text(f"""
            SELECT
                SUM(CASE WHEN s.actual <= 0 THEN 1 ELSE 0 END) AS sin_stock,
                SUM(CASE WHEN s.actual > 0 AND s.deseable IS NOT NULL AND s.deseable > 0 AND s.actual < s.deseable THEN 1 ELSE 0 END) AS bajo_minimo,
                SUM(CASE WHEN (s.deseable IS NULL OR s.actual >= s.deseable) AND (s.maximo IS NULL OR s.maximo = 0 OR s.actual <= s.maximo) THEN 1 ELSE 0 END) AS saludable,
                SUM(CASE WHEN s.maximo > 0 AND s.actual > s.maximo THEN 1 ELSE 0 END) AS exceso,
                COUNT(DISTINCT s.idarticulo) AS total_articulos,
                COALESCE(SUM(CASE WHEN a.costo_total > 0 THEN s.actual * a.costo_total ELSE 0 END), 0) AS valor_total_stock
            FROM stocks s
            JOIN articulos a ON s.idarticulo = a.id
            WHERE a.baja = '1900-01-01' AND a.idtipoarticulo IN (1, 3)
            {suc_filter}
        """)

        row = db.session.execute(sql, params).fetchone()

        sin_stock = int(row.sin_stock or 0)
        bajo_minimo = int(row.bajo_minimo or 0)
        saludable = int(row.saludable or 0)
        exceso = int(row.exceso or 0)
        total_articulos = int(row.total_articulos or 0)
        valor_raw = Decimal(str(row.valor_total_stock or 0))

        return {
            'sin_stock': sin_stock,
            'bajo_minimo': bajo_minimo,
            'stock_saludable': saludable,
            'exceso': exceso,
            'total_articulos': total_articulos,
            'valor_total_stock': _formato_moneda(valor_raw),
            'valor_total_stock_raw': float(valor_raw),
        }

    except SQLAlchemyError as e:
        print(f"Error en stock KPIs dashboard gerencial: {e}")
        return {
            'sin_stock': 0,
            'bajo_minimo': 0,
            'stock_saludable': 0,
            'exceso': 0,
            'total_articulos': 0,
            'valor_total_stock': '$ 0,00',
            'valor_total_stock_raw': 0,
        }


# ─── 2.2 Stock por Sucursal ─────────────────────────────────────────────────
def get_stock_sucursal(id_sucursal=None):
    """
    Stock agrupado por sucursal: unidades totales, valor estimado, sin stock, bajo mínimo.
    Retorna lista de dicts ordenados por unidades DESC.
    """
    params = {}
    suc_filter = ''
    if id_sucursal:
        suc_filter = ' AND s.idsucursal = :id_sucursal'
        params['id_sucursal'] = id_sucursal

    try:
        sql = text(f"""
            SELECT
                s.idsucursal,
                suc.nombre AS sucursal,
                COUNT(DISTINCT s.idarticulo) AS total_articulos,
                COALESCE(SUM(s.actual), 0) AS unidades_totales,
                COALESCE(SUM(CASE WHEN s.actual <= 0 THEN 1 ELSE 0 END), 0) AS sin_stock,
                COALESCE(SUM(CASE WHEN s.actual > 0 AND s.deseable IS NOT NULL AND s.deseable > 0 AND s.actual < s.deseable THEN 1 ELSE 0 END), 0) AS bajo_minimo,
                COALESCE(SUM(CASE WHEN a.costo_total > 0 THEN s.actual * a.costo_total ELSE 0 END), 0) AS valor_estimado
            FROM stocks s
            JOIN articulos a ON s.idarticulo = a.id
            JOIN sucursales suc ON s.idsucursal = suc.id
            WHERE a.baja = '1900-01-01' AND a.idtipoarticulo IN (1, 3)
            {suc_filter}
            GROUP BY s.idsucursal, suc.nombre
            ORDER BY unidades_totales DESC
        """)

        result = db.session.execute(sql, params).fetchall()

        sucursales = []
        for row in result:
            valor_raw = Decimal(str(row.valor_estimado or 0))
            sucursales.append({
                'sucursal': row.sucursal,
                'id_sucursal': row.idsucursal,
                'total_articulos': int(row.total_articulos or 0),
                'unidades_totales': int(row.unidades_totales or 0),
                'sin_stock': int(row.sin_stock or 0),
                'bajo_minimo': int(row.bajo_minimo or 0),
                'valor_estimado': _formato_moneda(valor_raw),
                'valor_estimado_raw': float(valor_raw),
            })

        return sucursales

    except SQLAlchemyError as e:
        print(f"Error en stock por sucursal dashboard gerencial: {e}")
        return []


# ─── 2.3 Productos sin Movimiento ───────────────────────────────────────────
def get_productos_sin_movimiento(id_sucursal=None, dias=30):
    """
    Artículos con stock > 0 pero sin ventas en los últimos N días.
    Retorna dict con lista de productos, total, y flag de truncación.
    """
    params = {'dias': dias}
    suc_filter = ''
    if id_sucursal:
        suc_filter = ' AND s.idsucursal = :id_sucursal'
        params['id_sucursal'] = id_sucursal

    try:
        sql = text(f"""
            SELECT
                a.codigo,
                a.detalle,
                s.actual AS stock_actual,
                s.idsucursal,
                COALESCE(r.nombre, 'Sin rubro') AS rubro,
                MAX(f.fecha) AS ultima_venta
            FROM articulos a
            JOIN stocks s ON a.id = s.idarticulo
            LEFT JOIN itemsv iv ON iv.idarticulo = a.id
            LEFT JOIN facturav f ON iv.idfactura = f.id
                AND f.fecha >= DATE_SUB(CURDATE(), INTERVAL :dias DAY)
            LEFT JOIN rubros r ON a.idrubro = r.id
            WHERE a.baja = '1900-01-01' AND a.idtipoarticulo IN (1, 3)
                AND s.actual > 0
            {suc_filter}
            GROUP BY a.id, a.codigo, a.detalle, s.actual, s.idsucursal, r.nombre
            HAVING ultima_venta IS NULL OR ultima_venta < DATE_SUB(CURDATE(), INTERVAL :dias DAY)
            ORDER BY ultima_venta ASC
            LIMIT 100
        """)

        result = db.session.execute(sql, params).fetchall()

        productos = []
        for row in result:
            ultima_venta = row.ultima_venta
            if ultima_venta:
                # Formatear como dd/mm/yyyy
                ultima_display = ultima_venta.strftime('%d/%m/%Y')
                ultima_str = ultima_venta.strftime('%Y-%m-%d')
            else:
                ultima_display = 'Sin ventas'
                ultima_str = None

            productos.append({
                'codigo': row.codigo,
                'detalle': (row.detalle[:40] + '...') if row.detalle and len(row.detalle) > 40 else (row.detalle or ''),
                'stock_actual': int(row.stock_actual or 0),
                'rubro': row.rubro,
                'ultima_venta': ultima_str,
                'ultima_venta_display': ultima_display,
            })

        # Para saber si hay más de 100, hacemos un count separado
        sql_count = text(f"""
            SELECT COUNT(*) AS total
            FROM (
                SELECT a.id
                FROM articulos a
                JOIN stocks s ON a.id = s.idarticulo
                LEFT JOIN itemsv iv ON iv.idarticulo = a.id
                LEFT JOIN facturav f ON iv.idfactura = f.id
                    AND f.fecha >= DATE_SUB(CURDATE(), INTERVAL :dias DAY)
                WHERE a.baja = '1900-01-01' AND a.idtipoarticulo IN (1, 3)
                    AND s.actual > 0
                {suc_filter}
                GROUP BY a.id, s.actual, s.idsucursal
                HAVING MAX(f.fecha) IS NULL OR MAX(f.fecha) < DATE_SUB(CURDATE(), INTERVAL :dias DAY)
            ) AS sub
        """)
        count_row = db.session.execute(sql_count, params).fetchone()
        total_count = int(count_row.total or 0)

        return {
            'productos': productos,
            'total': total_count,
            'mostrando': len(productos),
            'tiene_mas': total_count > len(productos),
        }

    except SQLAlchemyError as e:
        print(f"Error en productos sin movimiento dashboard gerencial: {e}")
        return {
            'productos': [],
            'total': 0,
            'mostrando': 0,
            'tiene_mas': False,
        }


# ─── 3.1 Helper: días vencimiento cta_cte ───────────────────────────────────
def get_dias_vto_cta_cte():
    """
    Lee dias_vto_cta_cte de la tabla configuracion.
    Si el valor es 0, retorna 30 (default).
    """
    try:
        config = Configuracion.query.get(1)
        if config and config.dias_vto_cta_cte and config.dias_vto_cta_cte > 0:
            return int(config.dias_vto_cta_cte)
        return 30
    except Exception:
        return 30


# ─── 3.2 KPIs Cuentas por Cobrar ───────────────────────────────────────────
def get_cta_cobrar_kpis(dias_vto=None):
    """
    KPIs cuentas por cobrar (clientes):
    saldo_total, saldo_vencido, saldo_por_vencer, cantidad_deudores.
    Saldo = SUM(debe - haber) por cliente, filtrado saldo > 0.
    Vencido: MAX(fecha) < CURDATE() - dias_vto.
    """
    if dias_vto is None:
        dias_vto = get_dias_vto_cta_cte()

    try:
        sql = text("""
            SELECT
                COUNT(DISTINCT CASE WHEN sub.saldo > 0 THEN sub.idcliente END) AS cantidad_deudores,
                COALESCE(SUM(CASE WHEN sub.saldo > 0 THEN sub.saldo ELSE 0 END), 0) AS saldo_total,
                COALESCE(SUM(CASE WHEN sub.saldo > 0 AND sub.ultima_fecha < CURDATE() - INTERVAL :dias DAY THEN sub.saldo ELSE 0 END), 0) AS saldo_vencido,
                COALESCE(SUM(CASE WHEN sub.saldo > 0 AND sub.ultima_fecha >= CURDATE() - INTERVAL :dias DAY THEN sub.saldo ELSE 0 END), 0) AS saldo_por_vencer
            FROM (
                SELECT
                    idcliente,
                    SUM(debe - haber) AS saldo,
                    MAX(fecha) AS ultima_fecha
                FROM cta_cte_cli
                GROUP BY idcliente
            ) sub
        """)

        row = db.session.execute(sql, {'dias': dias_vto}).fetchone()

        saldo_total = Decimal(str(row.saldo_total or 0))
        saldo_vencido = Decimal(str(row.saldo_vencido or 0))
        saldo_por_vencer = Decimal(str(row.saldo_por_vencer or 0))
        cantidad = int(row.cantidad_deudores or 0)

        return {
            'saldo_total': _formato_moneda(saldo_total),
            'saldo_total_raw': float(saldo_total),
            'saldo_vencido': _formato_moneda(saldo_vencido),
            'saldo_vencido_raw': float(saldo_vencido),
            'saldo_por_vencer': _formato_moneda(saldo_por_vencer),
            'saldo_por_vencer_raw': float(saldo_por_vencer),
            'cantidad_deudores': cantidad,
            'dias_vto': dias_vto,
        }

    except SQLAlchemyError as e:
        print(f"Error en cta_cobrar_kpis dashboard gerencial: {e}")
        return {
            'saldo_total': '$ 0,00',
            'saldo_total_raw': 0,
            'saldo_vencido': '$ 0,00',
            'saldo_vencido_raw': 0,
            'saldo_por_vencer': '$ 0,00',
            'saldo_por_vencer_raw': 0,
            'cantidad_deudores': 0,
            'dias_vto': dias_vto,
        }


# ─── 3.3 Top Deudores ─────────────────────────────────────────────────────
def get_cta_cobrar_top(limite=10, dias_vto=None):
    """
    Top deudores: clientes con mayor saldo positivo.
    Retorna lista de dicts con nombre, documento, saldo, ultima_fecha.
    """
    if dias_vto is None:
        dias_vto = get_dias_vto_cta_cte()

    try:
        sql = text("""
            SELECT
                c.id,
                c.nombre,
                c.documento,
                COALESCE(SUM(ccc.debe - ccc.haber), 0) AS saldo,
                MAX(ccc.fecha) AS ultima_fecha
            FROM cta_cte_cli ccc
            JOIN clientes c ON ccc.idcliente = c.id
            GROUP BY c.id, c.nombre, c.documento
            HAVING saldo > 0
            ORDER BY saldo DESC
            LIMIT :limite
        """)

        result = db.session.execute(sql, {'limite': limite}).fetchall()

        deudores = []
        for row in result:
            saldo = Decimal(str(row.saldo or 0))
            ultima = row.ultima_fecha
            deudores.append({
                'nombre': row.nombre,
                'documento': row.documento or '',
                'saldo': _formato_moneda(saldo),
                'saldo_raw': float(saldo),
                'ultima_fecha': ultima.strftime('%d/%m/%Y') if ultima else 'Sin fecha',
                'es_vencido': ultima is not None and ultima < (date.today() - timedelta(days=dias_vto)),
            })

        return deudores

    except SQLAlchemyError as e:
        print(f"Error en cta_cobrar_top dashboard gerencial: {e}")
        return []


# ─── 3.4 KPIs Cuentas por Pagar ────────────────────────────────────────────
def get_cta_pagar_kpis(dias_vto=None):
    """
    KPIs cuentas por pagar (proveedores):
    saldo_total, saldo_vencido, saldo_por_vencer, cantidad_proveedores.
    Misma lógica que cta_cobrar pero con cta_cte_prov/proveedores.
    """
    if dias_vto is None:
        dias_vto = get_dias_vto_cta_cte()

    try:
        sql = text("""
            SELECT
                COUNT(DISTINCT CASE WHEN sub.saldo > 0 THEN sub.idproveedor END) AS cantidad_proveedores,
                COALESCE(SUM(CASE WHEN sub.saldo > 0 THEN sub.saldo ELSE 0 END), 0) AS saldo_total,
                COALESCE(SUM(CASE WHEN sub.saldo > 0 AND sub.ultima_fecha < CURDATE() - INTERVAL :dias DAY THEN sub.saldo ELSE 0 END), 0) AS saldo_vencido,
                COALESCE(SUM(CASE WHEN sub.saldo > 0 AND sub.ultima_fecha >= CURDATE() - INTERVAL :dias DAY THEN sub.saldo ELSE 0 END), 0) AS saldo_por_vencer
            FROM (
                SELECT
                    idproveedor,
                    SUM(debe - haber) AS saldo,
                    MAX(fecha) AS ultima_fecha
                FROM cta_cte_prov
                GROUP BY idproveedor
            ) sub
        """)

        row = db.session.execute(sql, {'dias': dias_vto}).fetchone()

        saldo_total = Decimal(str(row.saldo_total or 0))
        saldo_vencido = Decimal(str(row.saldo_vencido or 0))
        saldo_por_vencer = Decimal(str(row.saldo_por_vencer or 0))
        cantidad = int(row.cantidad_proveedores or 0)

        return {
            'saldo_total': _formato_moneda(saldo_total),
            'saldo_total_raw': float(saldo_total),
            'saldo_vencido': _formato_moneda(saldo_vencido),
            'saldo_vencido_raw': float(saldo_vencido),
            'saldo_por_vencer': _formato_moneda(saldo_por_vencer),
            'saldo_por_vencer_raw': float(saldo_por_vencer),
            'cantidad_proveedores': cantidad,
            'dias_vto': dias_vto,
        }

    except SQLAlchemyError as e:
        print(f"Error en cta_pagar_kpis dashboard gerencial: {e}")
        return {
            'saldo_total': '$ 0,00',
            'saldo_total_raw': 0,
            'saldo_vencido': '$ 0,00',
            'saldo_vencido_raw': 0,
            'saldo_por_vencer': '$ 0,00',
            'saldo_por_vencer_raw': 0,
            'cantidad_proveedores': 0,
            'dias_vto': dias_vto,
        }


# ─── 3.5 Top Proveedores ───────────────────────────────────────────────────
def get_cta_pagar_top(limite=10, dias_vto=None):
    """
    Top proveedores: proveedores con mayor saldo positivo.
    Retorna lista de dicts con nombre, fantasia, saldo, ultima_fecha.
    """
    if dias_vto is None:
        dias_vto = get_dias_vto_cta_cte()

    try:
        sql = text("""
            SELECT
                p.id,
                p.nombre,
                p.fantasia,
                COALESCE(SUM(ccc.debe - ccc.haber), 0) AS saldo,
                MAX(ccc.fecha) AS ultima_fecha
            FROM cta_cte_prov ccc
            JOIN proveedores p ON ccc.idproveedor = p.id
            GROUP BY p.id, p.nombre, p.fantasia
            HAVING saldo > 0
            ORDER BY saldo DESC
            LIMIT :limite
        """)

        result = db.session.execute(sql, {'limite': limite}).fetchall()

        proveedores = []
        for row in result:
            saldo = Decimal(str(row.saldo or 0))
            ultima = row.ultima_fecha
            proveedores.append({
                'nombre': row.fantasia if row.fantasia else row.nombre,
                'fantasia': row.fantasia or '',
                'saldo': _formato_moneda(saldo),
                'saldo_raw': float(saldo),
                'ultima_fecha': ultima.strftime('%d/%m/%Y') if ultima else 'Sin fecha',
                'es_vencido': ultima is not None and ultima < (date.today() - timedelta(days=dias_vto)),
            })

        return proveedores

    except SQLAlchemyError as e:
        print(f"Error en cta_pagar_top dashboard gerencial: {e}")
        return []


# ─── 4.1 KPIs Créditos ──────────────────────────────────────────────────────
def get_creditos_kpis(id_sucursal=None):
    """
    KPIs de cartera de créditos: total activos, vencidos, monto total, % morosidad.
    Saldo se calcula como SUM(vencimientos.monto) - SUM(pagos.monto).
    Filtra estados distintos de ANULADO/CANCELADO/RECHAZADO.
    """
    params = {}
    suc_filter = ''
    if id_sucursal:
        suc_filter = ' AND c.idsucursal = :id_sucursal'
        params['id_sucursal'] = id_sucursal

    try:
        sql = text(f"""
            SELECT
                COUNT(DISTINCT sub.idcredito) AS total_activos,
                COUNT(DISTINCT CASE WHEN sub.tiene_cuota_vencida = 1 THEN sub.idcredito END) AS creditos_vencidos,
                COALESCE(SUM(sub.saldo), 0) AS monto_total_cartera,
                COUNT(DISTINCT c.idcliente) AS cantidad_deudores
            FROM (
                SELECT
                    c.id AS idcredito,
                    SUM(vc.monto) - COALESCE(SUM(pc.total_pagado), 0) AS saldo,
                    MAX(CASE
                        WHEN vc.fecha_vencimiento < CURDATE()
                            AND (vc.monto - COALESCE(pc.total_pagado, 0)) > 0
                        THEN 1 ELSE 0
                    END) AS tiene_cuota_vencida
                FROM creditos c
                JOIN vencimientos_creditos vc ON vc.idcredito = c.id
                JOIN estados_creditos ec ON c.estado = ec.id
                LEFT JOIN (
                    SELECT idvencimiento, SUM(monto) AS total_pagado
                    FROM pagos_creditos
                    GROUP BY idvencimiento
                ) pc ON vc.id = pc.idvencimiento
                WHERE ec.nombre NOT IN ('ANULADO', 'CANCELADO', 'RECHAZADO')
                {suc_filter}
                GROUP BY c.id
                HAVING saldo > 0
            ) sub
            JOIN creditos c ON sub.idcredito = c.id
        """)

        row = db.session.execute(sql, params).fetchone()

        total_activos = int(row.total_activos or 0)
        creditos_vencidos = int(row.creditos_vencidos or 0)
        monto_raw = Decimal(str(row.monto_total_cartera or 0))
        cantidad_deudores = int(row.cantidad_deudores or 0)

        porcentaje_morosidad = round((creditos_vencidos / total_activos * 100), 1) if total_activos > 0 else 0

        return {
            'creditos_activos': total_activos,
            'creditos_vencidos': creditos_vencidos,
            'monto_total_cartera': _formato_moneda(monto_raw),
            'monto_total_cartera_raw': float(monto_raw),
            'porcentaje_morosidad': porcentaje_morosidad,
            'cantidad_deudores': cantidad_deudores,
        }

    except SQLAlchemyError as e:
        print(f"Error en creditos KPIs dashboard gerencial: {e}")
        return {
            'creditos_activos': 0,
            'creditos_vencidos': 0,
            'monto_total_cartera': '$ 0,00',
            'monto_total_cartera_raw': 0,
            'porcentaje_morosidad': 0,
            'cantidad_deudores': 0,
        }


# ─── 4.2 Top Deudores Créditos ──────────────────────────────────────────────
def get_creditos_top_deudores(limite=10, id_sucursal=None):
    """
    Top deudores por crédito: cliente, documento, cantidad de créditos activos,
    saldo total impago. Saldo = SUM(vencimientos.monto) - SUM(pagos.monto).
    """
    params = {'limite': limite}
    suc_filter = ''
    if id_sucursal:
        suc_filter = ' AND c.idsucursal = :id_sucursal'
        params['id_sucursal'] = id_sucursal

    try:
        sql = text(f"""
            SELECT
                cli.nombre,
                cli.documento,
                COUNT(DISTINCT sub.idcredito) AS cantidad_creditos,
                COALESCE(SUM(sub.saldo), 0) AS saldo_total
            FROM (
                SELECT
                    c.id AS idcredito,
                    SUM(vc.monto) - COALESCE(SUM(pc.total_pagado), 0) AS saldo
                FROM creditos c
                JOIN vencimientos_creditos vc ON vc.idcredito = c.id
                JOIN estados_creditos ec ON c.estado = ec.id
                LEFT JOIN (
                    SELECT idvencimiento, SUM(monto) AS total_pagado
                    FROM pagos_creditos
                    GROUP BY idvencimiento
                ) pc ON vc.id = pc.idvencimiento
                WHERE ec.nombre NOT IN ('ANULADO', 'CANCELADO', 'RECHAZADO')
                {suc_filter}
                GROUP BY c.id, c.idcliente
                HAVING saldo > 0
            ) sub
            JOIN creditos c ON sub.idcredito = c.id
            JOIN clientes cli ON c.idcliente = cli.id
            GROUP BY cli.id, cli.nombre, cli.documento
            ORDER BY saldo_total DESC
            LIMIT :limite
        """)

        result = db.session.execute(sql, params).fetchall()

        deudores = []
        for row in result:
            saldo = Decimal(str(row.saldo_total or 0))
            deudores.append({
                'nombre': row.nombre,
                'documento': row.documento or '',
                'cantidad_creditos': int(row.cantidad_creditos or 0),
                'saldo_total': _formato_moneda(saldo),
                'saldo_total_raw': float(saldo),
            })

        return deudores

    except SQLAlchemyError as e:
        print(f"Error en creditos top deudores dashboard gerencial: {e}")
        return []


# ─── 5.1 KPIs Bancos ────────────────────────────────────────────────────────
def get_bancos_kpis(desde, hasta, id_sucursal=None):
    """
    KPIs bancarios: saldo total consolidado, movimientos del mes,
    ingresos y egresos del período.
    Saldo es histórico (no filtrado por fechas). Movimientos/ingresos/egresos
    se filtran por el período seleccionado.
    """
    try:
        # Saldo acumulado de TODOS los movimientos (histórico)
        sql_saldo = text("""
            SELECT
                b.id,
                b.nombre,
                COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'C' THEN bp.monto ELSE 0 END), 0) AS total_creditos,
                COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'D' THEN bp.monto ELSE 0 END), 0) AS total_debitos,
                COALESCE(SUM(CASE
                    WHEN tmb.tipo_operacion = 'C' THEN bp.monto
                    ELSE -bp.monto
                END), 0) AS saldo
            FROM bancos b
            LEFT JOIN bancos_propios bp ON b.id = bp.id_banco AND bp.baja = '1900-01-01'
            LEFT JOIN tipo_mov_bancos tmb ON bp.tipo_movimiento = tmb.id
            WHERE b.baja = '1900-01-01'
            GROUP BY b.id, b.nombre
        """)

        result_saldo = db.session.execute(sql_saldo, {}).fetchall()
        saldo_total = Decimal('0')
        for row in result_saldo:
            saldo_total += Decimal(str(row.saldo or 0))

        # Movimientos del período
        sql_movimientos = text("""
            SELECT
                COUNT(*) AS movimientos_mes,
                COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'C' THEN bp.monto ELSE 0 END), 0) AS ingresos_mes,
                COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'D' THEN bp.monto ELSE 0 END), 0) AS egresos_mes
            FROM bancos_propios bp
            JOIN tipo_mov_bancos tmb ON bp.tipo_movimiento = tmb.id
            WHERE bp.fecha_emision BETWEEN :desde AND :hasta
                AND bp.baja = '1900-01-01'
        """)

        row_mov = db.session.execute(sql_movimientos, {'desde': desde, 'hasta': hasta}).fetchone()
        movimientos_mes = int(row_mov.movimientos_mes or 0)
        ingresos_mes = Decimal(str(row_mov.ingresos_mes or 0))
        egresos_mes = Decimal(str(row_mov.egresos_mes or 0))

        return {
            'saldo_total_bancos': _formato_moneda(saldo_total),
            'saldo_total_bancos_raw': float(saldo_total),
            'movimientos_mes': movimientos_mes,
            'ingresos_mes': _formato_moneda(ingresos_mes),
            'ingresos_mes_raw': float(ingresos_mes),
            'egresos_mes': _formato_moneda(egresos_mes),
            'egresos_mes_raw': float(egresos_mes),
        }

    except SQLAlchemyError as e:
        print(f"Error en bancos KPIs dashboard gerencial: {e}")
        return {
            'saldo_total_bancos': '$ 0,00',
            'saldo_total_bancos_raw': 0,
            'movimientos_mes': 0,
            'ingresos_mes': '$ 0,00',
            'ingresos_mes_raw': 0,
            'egresos_mes': '$ 0,00',
            'egresos_mes_raw': 0,
        }


# ─── 5.2 Detalle Bancos ─────────────────────────────────────────────────────
def get_bancos_detalle(id_sucursal=None):
    """
    Saldo desglosado por cada banco activo con participación porcentual.
    Saldo es histórico. Movimientos se filtran por el período.
    Retorna lista de dicts: banco, saldo, movimientos, participacion.
    """
    try:
        sql = text("""
            SELECT
                b.id,
                b.nombre,
                COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'C' THEN bp.monto ELSE 0 END), 0) AS total_creditos,
                COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'D' THEN bp.monto ELSE 0 END), 0) AS total_debitos,
                COALESCE(SUM(CASE
                    WHEN tmb.tipo_operacion = 'C' THEN bp.monto
                    ELSE -bp.monto
                END), 0) AS saldo,
                COUNT(CASE WHEN bp.id IS NOT NULL THEN 1 END) AS total_movimientos
            FROM bancos b
            LEFT JOIN bancos_propios bp ON b.id = bp.id_banco AND bp.baja = '1900-01-01'
            LEFT JOIN tipo_mov_bancos tmb ON bp.tipo_movimiento = tmb.id
            WHERE b.baja = '1900-01-01'
            GROUP BY b.id, b.nombre
            ORDER BY saldo DESC
        """)

        result = db.session.execute(sql, {}).fetchall()

        # Calcular saldo total positivo para participación
        saldo_total_positivo = Decimal('0')
        bancos_data = []
        for row in result:
            saldo = Decimal(str(row.saldo or 0))
            if saldo > 0:
                saldo_total_positivo += saldo
            bancos_data.append({
                'banco': row.nombre,
                'saldo': _formato_moneda(saldo),
                'saldo_raw': float(saldo),
                'movimientos': int(row.total_movimientos or 0),
                'participacion': 0,
            })

        # Calcular participación
        for b in bancos_data:
            if saldo_total_positivo > 0:
                b['participacion'] = round(float(Decimal(str(b['saldo_raw'])) / saldo_total_positivo * 100), 1)
            else:
                b['participacion'] = 0

        return bancos_data

    except SQLAlchemyError as e:
        print(f"Error en bancos detalle dashboard gerencial: {e}")
        return []


# ─── 5.3 KPIs Caja ─────────────────────────────────────────────────────────
def get_caja_kpis(desde, hasta, id_sucursal=None):
    """
    KPIs de caja: total efectivo rendido, total otros valores,
    cantidad de rendiciones en el período.
    Filtra por sucursal si se indica.
    """
    params = {'desde': desde, 'hasta': hasta}
    suc_filter = ''
    if id_sucursal:
        suc_filter = ' AND rc.idsucursal = :id_sucursal'
        params['id_sucursal'] = id_sucursal

    try:
        sql = text(f"""
            SELECT
                COALESCE(SUM(rc.total_efectivo), 0) AS total_efectivo,
                COALESCE(SUM(COALESCE(rc.total_otros_valores, 0)), 0) AS total_otros_valores,
                COUNT(rc.id) AS cantidad_rendiciones
            FROM rendiciones_caja rc
            WHERE rc.fecha BETWEEN :desde AND :hasta
            {suc_filter}
        """)

        row = db.session.execute(sql, params).fetchone()
        efectivo = Decimal(str(row.total_efectivo or 0))
        otros = Decimal(str(row.total_otros_valores or 0))

        return {
            'total_efectivo': _formato_moneda(efectivo),
            'total_efectivo_raw': float(efectivo),
            'total_otros_valores': _formato_moneda(otros),
            'total_otros_valores_raw': float(otros),
            'cantidad_rendiciones': int(row.cantidad_rendiciones or 0),
        }

    except SQLAlchemyError as e:
        print(f"Error en caja KPIs dashboard gerencial: {e}")
        return {
            'total_efectivo': '$ 0,00',
            'total_efectivo_raw': 0,
            'total_otros_valores': '$ 0,00',
            'total_otros_valores_raw': 0,
            'cantidad_rendiciones': 0,
        }


# ─── 5.4 Rendiciones Caja Recientes ────────────────────────────────────────
def get_caja_rendiciones_recientes(desde, hasta, id_sucursal=None, limite=10):
    """
    Últimas rendiciones de caja con usuario y sucursal.
    Filtra por período y opcionalmente por sucursal.
    Retorna lista de dicts con fecha, usuario, sucursal, montos formateados.
    """
    params = {'desde': desde, 'hasta': hasta, 'limite': limite}
    suc_filter = ''
    if id_sucursal:
        suc_filter = ' AND rc.idsucursal = :id_sucursal'
        params['id_sucursal'] = id_sucursal

    try:
        sql = text(f"""
            SELECT
                rc.fecha,
                u.nombre AS usuario,
                s.nombre AS sucursal,
                COALESCE(rc.total_ventas, 0) AS total_ventas,
                COALESCE(rc.total_efectivo, 0) AS total_efectivo,
                COALESCE(COALESCE(rc.total_otros_valores, 0), 0) AS total_otros_valores
            FROM rendiciones_caja rc
            JOIN usuarios u ON rc.idusuario = u.id
            JOIN sucursales s ON rc.idsucursal = s.id
            WHERE rc.fecha BETWEEN :desde AND :hasta
            {suc_filter}
            ORDER BY rc.fecha DESC
            LIMIT :limite
        """)

        result = db.session.execute(sql, params).fetchall()

        rendiciones = []
        for row in result:
            vent = Decimal(str(row.total_ventas or 0))
            efe = Decimal(str(row.total_efectivo or 0))
            otr = Decimal(str(row.total_otros_valores or 0))
            rendiciones.append({
                'fecha': row.fecha.strftime('%d/%m/%Y') if row.fecha else '',
                'usuario': row.usuario or '',
                'sucursal': row.sucursal or '',
                'total_ventas': _formato_moneda(vent),
                'total_ventas_raw': float(vent),
                'total_efectivo': _formato_moneda(efe),
                'total_efectivo_raw': float(efe),
                'total_otros_valores': _formato_moneda(otr),
                'total_otros_valores_raw': float(otr),
            })

        return rendiciones

    except SQLAlchemyError as e:
        print(f"Error en caja rendiciones dashboard gerencial: {e}")
        return []


# ─── 6.1 Alertas Gerenciales ────────────────────────────────────────────────
def get_alertas_gerenciales(stock_kpis, creditos_kpis, cta_cobrar_kpis, bancos_detalle):
    """
    Evalúa condiciones críticas y retorna lista de alertas.
    Cada alerta: { tipo, titulo, mensaje, severidad, icono, seccion_target, detalle_raw }
    severidad: 'danger' | 'warning' | 'info'
    Reutiliza funciones existentes — sin queries nuevas.
    """
    alertas = []

    # Stock: bajo mínimo
    if stock_kpis.get('bajo_minimo', 0) > 0:
        alertas.append({
            'tipo': 'stock_bajo',
            'titulo': 'Stock Bajo Mínimo',
            'mensaje': f"{stock_kpis['bajo_minimo']} artículos por debajo del nivel deseable",
            'severidad': 'warning',
            'icono': 'fa-box',
            'seccion_target': 'seccion-stock-kpis',
            'detalle_raw': stock_kpis['bajo_minimo']
        })

    # Stock: sin stock
    if stock_kpis.get('sin_stock', 0) > 0:
        alertas.append({
            'tipo': 'sin_stock',
            'titulo': 'Sin Stock',
            'mensaje': f"{stock_kpis['sin_stock']} artículos sin unidades disponibles",
            'severidad': 'danger',
            'icono': 'fa-times-circle',
            'seccion_target': 'seccion-stock-kpis',
            'detalle_raw': stock_kpis['sin_stock']
        })

    # Créditos vencidos
    if creditos_kpis.get('creditos_vencidos', 0) > 0:
        porcentaje = creditos_kpis.get('porcentaje_morosidad', 0)
        alertas.append({
            'tipo': 'creditos_vencidos',
            'titulo': 'Créditos Vencidos',
            'mensaje': f"{creditos_kpis['creditos_vencidos']} créditos con cuota vencida — {porcentaje}% morosidad",
            'severidad': 'danger',
            'icono': 'fa-credit-card',
            'seccion_target': 'seccion-creditos-kpis',
            'detalle_raw': creditos_kpis['creditos_vencidos']
        })

    # Cta_cte vencida
    if cta_cobrar_kpis.get('saldo_vencido_raw', 0) > 0:
        alertas.append({
            'tipo': 'cta_cte_vencida',
            'titulo': 'Cuenta Corriente Vencida',
            'mensaje': f"{cta_cobrar_kpis['saldo_vencido']} de saldo vencido a cobrar ({cta_cobrar_kpis.get('cantidad_deudores', 0)} clientes)",
            'severidad': 'danger',
            'icono': 'fa-hand-holding-dollar',
            'seccion_target': 'seccion-cta-cobrar-kpis',
            'detalle_raw': cta_cobrar_kpis['saldo_vencido_raw']
        })

    # Bancos saldo negativo — una alerta por banco
    bancos_negativos = [b for b in bancos_detalle if b.get('saldo_raw', 0) < 0]
    for b in bancos_negativos:
        alertas.append({
            'tipo': 'banco_negativo',
            'titulo': f"Saldo Negativo: {b['banco']}",
            'mensaje': f"Saldo {b['saldo']} — revisar movimientos",
            'severidad': 'danger',
            'icono': 'fa-building-columns',
            'seccion_target': 'seccion-bancos-detalle',
            'detalle_raw': b['saldo_raw']
        })

    return alertas


# ─── 1.7 Agregador ──────────────────────────────────────────────────────────
def get_datos_dashboard(desde, hasta, id_sucursal=None, comparar=False):
    """
    Función principal que agrega todos los datos del dashboard.
    Retorna un dict con todas las secciones.
    """
    stock_kpis = get_stock_kpis(id_sucursal)
    creditos_kpis = get_creditos_kpis(id_sucursal)
    cta_cobrar_kpis = get_cta_cobrar_kpis()
    bancos_detalle = get_bancos_detalle()

    return {
        'kpis': get_kpis(desde, hasta, id_sucursal),
        'evolucion': get_evolucion_ventas(desde, hasta, id_sucursal, comparar),
        'sucursales': get_ventas_sucursal(desde, hasta, id_sucursal),
        'rubros': get_ventas_rubro(desde, hasta, id_sucursal),
        'rubro_sucursal': get_rubro_sucursal_comparacion(desde, hasta, id_sucursal),
        'top_productos': get_top_productos(desde, hasta, id_sucursal, 10),
        'top_vendedores': get_top_vendedores(desde, hasta, id_sucursal, 10),
        'stock_kpis': stock_kpis,
        'stock_sucursal': get_stock_sucursal(id_sucursal),
        'productos_sin_movimiento': get_productos_sin_movimiento(id_sucursal, 30),
        'cta_cobrar_kpis': cta_cobrar_kpis,
        'cta_cobrar_top': get_cta_cobrar_top(10),
        'cta_pagar_kpis': get_cta_pagar_kpis(),
        'cta_pagar_top': get_cta_pagar_top(10),
        'creditos_kpis': creditos_kpis,
        'creditos_top_deudores': get_creditos_top_deudores(10, id_sucursal),
        'bancos_kpis': get_bancos_kpis(desde, hasta),
        'bancos_detalle': bancos_detalle,
        'caja_kpis': get_caja_kpis(desde, hasta, id_sucursal),
        'caja_rendiciones': get_caja_rendiciones_recientes(desde, hasta, id_sucursal),
        'alertas': get_alertas_gerenciales(stock_kpis, creditos_kpis, cta_cobrar_kpis, bancos_detalle),
    }
