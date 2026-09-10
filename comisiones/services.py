# comisiones/services.py
# Lógica de negocio del módulo de comisiones
# Orquesta repositories + calculator para procesar liquidaciones

from decimal import Decimal
from collections import defaultdict

from utils.db import db
from sqlalchemy.exc import SQLAlchemyError

from comisiones import repositories as repo
from comisiones.calculator import CalculadorComisiones
from comisiones.constants import EstadoLiquidacion


class ComisionesService:
    """Servicio principal del módulo de comisiones.
    Orquesta las consultas (repositories) y el cálculo (calculator)
    para generar liquidaciones de comisiones.
    """

    def __init__(self):
        self.calculador = CalculadorComisiones()

    # ----------------------------------------------------------------
    # Cálculo de período (preview)
    # ----------------------------------------------------------------

    def calcular_periodo(self, desde, hasta, usuario_id=None):
        """Calcula comisiones para un período sin guardar nada (preview).

        Args:
            desde: date — inicio del período
            hasta: date — fin del período
            usuario_id: int or None — filtrar por vendedor específico

        Returns:
            dict con:
                - detalles: lista de dicts de comisiones calculadas
                - total: Decimal con el total de comisiones
                - resumen_por_vendedor: dict[idusuario] -> total
        """
        # 1. Obtener todos los ítems del período
        items_raw = repo.get_items_periodo(desde, hasta, usuario_id)
        
        if not items_raw:
            return {'detalles': [], 'total': Decimal(0), 'resumen_por_vendedor': {}}

        # 2. Pre-cargar artículos únicos (batch)
        articulos_ids = set()
        for item in items_raw:
            articulos_ids.add(item['idarticulo'])

        articulos_cache = {}
        for art_id in articulos_ids:
            art = repo.get_articulo(art_id)
            if art:
                articulos_cache[art_id] = art

        # 3. Agrupar ítems por vendedor
        ventas_por_vendedor = defaultdict(list)
        for item in items_raw:
            ventas_por_vendedor[item['idusuario']].append(item)

        # 4. Para cada vendedor, calcular comisiones
        todos_los_detalles = []

        for vendedor_id, items_vendedor in ventas_por_vendedor.items():
            # Obtener la fecha de una venta para buscar el plan
            fecha_referencia = items_vendedor[0]['fecha']
            
            # Obtener plan activo
            plan = repo.get_plan_activo(vendedor_id, fecha_referencia)
            if not plan:
                continue

            # Obtener reglas y tramos
            reglas = repo.get_reglas_plan(plan['id'])
            tramos = repo.get_tramos_plan(plan['id'])

            # Armar contexto
            contexto = {
                'plan': {
                    'id': plan['id'],
                    'nombre': plan['nombre'],
                    'tipo_calculo': plan['tipo_calculo'],
                    'base_calculo': plan['base_calculo'],
                    'modo_escalas': plan['modo_escalas'],
                },
                'reglas': [
                    {
                        'id': r['id'],
                        'nombre': r['nombre'],
                        'tipo_regla': r['tipo_regla'],
                        'criterio': r['criterio'],
                        'valor_criterio': r['valor_criterio'],
                        'porcentaje': Decimal(str(r['porcentaje'])),
                        'importe_fijo': Decimal(str(r['importe_fijo'])),
                        'prioridad': r['prioridad'],
                        'acumulable': r['acumulable'],
                    }
                    for r in reglas
                ],
                'tramos': [
                    {
                        'id': t['id'],
                        'desde': Decimal(str(t['desde'])),
                        'hasta': Decimal(str(t['hasta'])),
                        'porcentaje': Decimal(str(t['porcentaje'])),
                        'importe_fijo': Decimal(str(t['importe_fijo'])),
                        'orden': t['orden'],
                    }
                    for t in tramos
                ],
            }

            # Agrupar ítems por factura
            items_por_factura = defaultdict(list)
            for item in items_vendedor:
                items_por_factura[item['idfactura']].append(item)

            # Calcular por factura
            for factura_id, items_factura in items_por_factura.items():
                # Enriquecer ítems con datos del artículo
                items_enriquecidos = []
                for item in items_factura:
                    art = articulos_cache.get(item['idarticulo'])
                    item_dict = {
                        'idfactura': item['idfactura'],
                        'id_item': item['id_item'],
                        'idarticulo': item['idarticulo'],
                        'cantidad': Decimal(str(item['cantidad'])),
                        'precio_total': Decimal(str(item['precio_total'])),
                        'bonificacion': Decimal(str(item['bonificacion'])),
                        'costo_unitario': Decimal(str(item['costo_unitario'])),
                        'idusuario': item['idusuario'],
                        'idcliente': item['idcliente'],
                        'fecha': item['fecha'],
                        'tipo_operacion': item['tipo_operacion'],
                        'idtipocomprobante': item['idtipocomprobante'],
                        # Atributos del artículo para matching de reglas
                        'rubro_id': str(art['idrubro']) if art else None,
                        'marca_id': str(art['idmarca']) if art else None,
                        'rubro_nombre': art['rubro'] if art else None,
                        'marca_nombre': art['marca'] if art else None,
                    }
                    items_enriquecidos.append(item_dict)

                venta = {
                    'id': factura_id,
                    'fecha': items_factura[0]['fecha'],
                    'idusuario': vendedor_id,
                    'idcliente': items_factura[0]['idcliente'],
                    'total': sum(
                        Decimal(str(it['precio_total'])) for it in items_factura
                    ),
                    'tipo_operacion': items_factura[0]['tipo_operacion'],
                }

                detalles_venta = self.calculador.calcular_venta(
                    venta, items_enriquecidos, contexto
                )
                todos_los_detalles.extend(detalles_venta)

        # 5. Calcular totales
        total = sum(
            Decimal(str(d['importe_comision'])) for d in todos_los_detalles
        )

        resumen_por_vendedor = defaultdict(Decimal)
        for d in todos_los_detalles:
            resumen_por_vendedor[d['idusuario']] += Decimal(str(d['importe_comision']))

        return {
            'detalles': todos_los_detalles,
            'total': total,
            'resumen_por_vendedor': dict(resumen_por_vendedor),
        }

    # ----------------------------------------------------------------
    # Liquidación
    # ----------------------------------------------------------------

    def crear_liquidacion(self, periodo_desde, periodo_hasta, detalles_calculo,
                          usuario_id, observaciones=None):
        """Crea una liquidación BORRADOR a partir de detalles calculados.

        Args:
            periodo_desde: date
            periodo_hasta: date
            detalles_calculo: lista de dicts del preview (resultado de calcular_periodo)
            usuario_id: int — usuario que crea la liquidación
            observaciones: str or None

        Returns:
            dict con la liquidación creada o error.

        Raises:
            ValueError: si hay superposición de períodos o datos inválidos.
        """
        from comisiones.validators import (
            validar_superposicion_liquidacion,
            validar_detalles_no_vacios,
        )

        # Validar
        validar_detalles_no_vacios(detalles_calculo)
        validar_superposicion_liquidacion(periodo_desde, periodo_hasta)

        try:
            # Crear encabezado
            liquidacion = repo.crear_liquidacion(
                periodo_desde=periodo_desde,
                periodo_hasta=periodo_hasta,
                usuario_id=usuario_id,
                observaciones=observaciones,
                estado=EstadoLiquidacion.CALCULADA.value,
            )

            # Insertar detalles
            total = Decimal(0)
            for det in detalles_calculo:
                importe = Decimal(str(det['importe_comision']))
                total += importe

                repo.insertar_detalle(
                    id_liquidacion=liquidacion['id'],
                    id_usuario=det.get('idusuario'),
                    id_factura=det.get('idfactura'),
                    id_item=det.get('id_item'),
                    id_regla=det.get('id_regla'),
                    tipo_movimiento=det.get('tipo_movimiento', 'VENTA'),
                    tipo_comision=det.get('tipo_comision', 'PORCENTAJE_VENTA'),
                    base_calculo=det.get('base_calculo', 'VENTA_TOTAL'),
                    cantidad=det.get('cantidad', 0),
                    costo_unitario=det.get('costo_unitario', 0),
                    importe_venta=det.get('importe_venta', 0),
                    importe_costo=det.get('importe_costo', 0),
                    importe_margen=det.get('importe_margen', 0),
                    porcentaje=det.get('porcentaje', 0),
                    importe_comision=importe,
                    observaciones=det.get('observaciones'),
                )

            # Actualizar total
            repo.actualizar_total_liquidacion(liquidacion['id'], total)

            db.session.commit()

            return {
                'success': True,
                'message': 'Liquidación creada exitosamente',
                'liquidacion_id': liquidacion['id'],
                'total': total,
            }

        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error SQL creando liquidación: {e}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error creando liquidación: {e}")

    def confirmar_liquidacion(self, liquidacion_id, usuario_id):
        """Confirma una liquidación (la congela, queda inmutable).

        Args:
            liquidacion_id: int
            usuario_id: int — usuario que confirma

        Returns:
            dict con resultado de la operación.

        Raises:
            ValueError: si la liquidación no está en estado CONFIRMABLE.
        """
        from comisiones.validators import validar_estado_liquidacion_transicion

        liquidacion = repo.get_liquidacion(liquidacion_id)
        if not liquidacion:
            raise ValueError(f"Liquidación {liquidacion_id} no encontrada")

        validar_estado_liquidacion_transicion(
            liquidacion, EstadoLiquidacion.CONFIRMADA
        )

        try:
            repo.actualizar_estado_liquidacion(
                liquidacion_id, EstadoLiquidacion.CONFIRMADA.value
            )
            db.session.commit()

            return {
                'success': True,
                'message': 'Liquidación confirmada exitosamente',
            }

        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error SQL confirmando liquidación: {e}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error confirmando liquidación: {e}")

    def anular_liquidacion(self, liquidacion_id, motivo, usuario_id):
        """Anula una liquidación.

        Args:
            liquidacion_id: int
            motivo: str — motivo de la anulación
            usuario_id: int — usuario que anula

        Returns:
            dict con resultado de la operación.

        Raises:
            ValueError: si la liquidación no puede anularse.
        """
        from comisiones.validators import validar_estado_liquidacion_transicion

        liquidacion = repo.get_liquidacion(liquidacion_id)
        if not liquidacion:
            raise ValueError(f"Liquidación {liquidacion_id} no encontrada")

        validar_estado_liquidacion_transicion(
            liquidacion, EstadoLiquidacion.ANULADA
        )

        try:
            obs_actual = liquidacion.get('observaciones', '') or ''
            nueva_obs = f"{obs_actual}\nAnulada: {motivo}".strip()

            repo.actualizar_estado_liquidacion(
                liquidacion_id, EstadoLiquidacion.ANULADA.value,
                observaciones=nueva_obs
            )
            db.session.commit()

            return {
                'success': True,
                'message': 'Liquidación anulada exitosamente',
            }

        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error SQL anulando liquidación: {e}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error anulando liquidación: {e}")

    # ----------------------------------------------------------------
    # Consultas
    # ----------------------------------------------------------------

    def get_liquidaciones(self, filtro=None):
        """Obtiene liquidaciones con filtros opcionales.

        Args:
            filtro: dict con filtros opcionales:
                - estado: str
                - desde: date
                - hasta: date
                - usuario_id: int

        Returns:
            Lista de dicts con las liquidaciones.
        """
        return repo.get_liquidaciones(filtro or {})

    def get_detalle_liquidacion(self, liquidacion_id):
        """Obtiene el detalle completo de una liquidación.

        Args:
            liquidacion_id: int

        Returns:
            dict con la liquidación y sus detalles.
        """
        liquidacion = repo.get_liquidacion(liquidacion_id)
        if not liquidacion:
            return None

        detalles = repo.get_detalles_completos(liquidacion_id)

        return {
            'liquidacion': liquidacion,
            'detalles': detalles,
        }

    def get_liquidacion(self, liquidacion_id):
        """Obtiene una liquidación por ID."""
        return repo.get_liquidacion(liquidacion_id)
