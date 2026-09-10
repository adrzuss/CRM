# comisiones/calculator.py
# Motor de cálculo de comisiones — puro, sin dependencias de DB
# Recibe datos como dicts/Decimal, retorna resultados como dicts

from decimal import Decimal, ROUND_HALF_UP


class CalculadorComisiones:
    """Motor de cálculo de comisiones.
    No depende de la base de datos. Recibe datos a través de contexto
    y retorna resultados como listas de dicts.
    """

    def __init__(self):
        self.contexto = {}

    # ----------------------------------------------------------------
    # API principal
    # ----------------------------------------------------------------

    def calcular_venta(self, venta, items, contexto):
        """Calcula comisiones para una venta (factura) completa.

        Args:
            venta: dict con {id, fecha, idusuario, idcliente, total, tipo_operacion}
            items: lista de dicts con datos de cada ítem enriquecidos con atributos
                   del artículo (rubro, marca, etc.)
            contexto: dict con {plan, reglas, tramos, articulos_cache}

        Returns:
            Lista de dicts, uno por ítem procesado:
            {idfactura, id_item, idusuario, idcliente, tipo_movimiento,
             id_regla, tipo_comision, base_calculo, cantidad, costo_unitario,
             importe_venta, importe_costo, importe_margen, porcentaje,
             importe_comision, observaciones}
        """
        resultados = []
        plan = contexto.get('plan')
        if not plan:
            return resultados

        tipo_operacion = venta.get('tipo_operacion', 'VENTA')
        signo = self.signo_comision(tipo_operacion)
        acumulado_ventas = Decimal(0)

        for item in items:
            # Solo procesar ítems de esta factura
            if item.get('idfactura') != venta.get('id'):
                continue

            resultado = self.calcular_item(
                item, contexto, tipo_operacion, signo, acumulado_ventas
            )
            if resultado:
                resultados.append(resultado)
                # Acumular para cálculo escalonado
                base_item = self.calcular_base(plan.get('base_calculo', 'VENTA_TOTAL'), item)
                acumulado_ventas += abs(base_item)

        return resultados

    def calcular_item(self, item, contexto, tipo_operacion='VENTA',
                      signo=None, acumulado_ventas=None):
        """Calcula comisión para un ítem individual.

        Args:
            item: dict con datos del ítem (idfactura, id_item, idarticulo, cantidad,
                  precio_total, bonificacion, costo_unitario, rubro_id, marca_id, etc.)
            contexto: dict con {plan, reglas, tramos}
            tipo_operacion: 'VENTA', 'CREDITO', o 'DEBITO'
            signo: +1 para VENTA/DEBITO, -1 para CREDITO
            acumulado_ventas: acumulado previo para cálculo escalonado

        Returns:
            dict con el resultado de la comisión calculada, o None si no hay regla aplicable.
        """
        if signo is None:
            signo = Decimal(1)

        plan = contexto.get('plan')
        if not plan:
            return None

        reglas = contexto.get('reglas', [])
        tramos = contexto.get('tramos', [])

        # Calcular base según configuración del plan
        base_calculo_tipo = plan.get('base_calculo', 'VENTA_TOTAL')
        base = self.calcular_base(base_calculo_tipo, item)
        base_con_signo = base * signo

        # Costo y margen (para trazabilidad)
        costo_unitario = item.get('costo_unitario', Decimal(0))
        cantidad = item.get('cantidad', Decimal(0))
        importe_venta = item.get('precio_total', Decimal(0)) * signo
        importe_costo = (costo_unitario * cantidad) * signo
        importe_margen = importe_venta - importe_costo

        # Encontrar regla aplicable
        regla_aplicada = None
        for regla in reglas:
            if self.regla_aplica(regla, item):
                if regla.get('tipo_regla') == 'EXCLUSIVA':
                    regla_aplicada = regla
                    break
                # ACUMULABLE: acumular todas las que apliquen
                if regla_aplicada is None:
                    regla_aplicada = regla
                # TODO: soporte completo para múltiples reglas acumulables

        if regla_aplicada is None:
            return None

        # Calcular comisión según tipo
        importe_comision = self.aplicar_regla(
            regla_aplicada, plan, base_con_signo, item,
            tramos, acumulado_ventas or Decimal(0)
        )

        return {
            'idfactura': item.get('idfactura'),
            'id_item': item.get('id_item'),
            'idusuario': item.get('idusuario'),
            'idcliente': item.get('idcliente'),
            'tipo_movimiento': self.tipo_movimiento_from_operacion(tipo_operacion),
            'id_regla': regla_aplicada.get('id'),
            'tipo_comision': plan.get('tipo_calculo', 'PORCENTAJE_VENTA'),
            'base_calculo': base_calculo_tipo,
            'cantidad': cantidad,
            'costo_unitario': costo_unitario,
            'importe_venta': importe_venta,
            'importe_costo': importe_costo,
            'importe_margen': importe_margen,
            'porcentaje': regla_aplicada.get('porcentaje', Decimal(0)),
            'importe_comision': importe_comision,
            'observaciones': self._generar_observacion(item, regla_aplicada, tipo_operacion),
        }

    # ----------------------------------------------------------------
    # Obtención de datos (recibe del contexto)
    # ----------------------------------------------------------------

    def obtener_plan(self, usuario_id, fecha, contexto):
        """Retorna el plan del contexto para un vendedor y fecha.
        El contexto debe contener 'plan_asignado' ya resuelto por la capa de servicios.
        """
        return contexto.get('plan')

    def obtener_reglas(self, plan_id, contexto):
        """Retorna las reglas del contexto para un plan."""
        return contexto.get('reglas', [])

    # ----------------------------------------------------------------
    # Aplicación de reglas
    # ----------------------------------------------------------------

    def aplicar_regla(self, regla, plan, base, item, tramos=None,
                      acumulado_ventas=None):
        """Aplica una regla a un ítem y retorna el monto de comisión.

        Args:
            regla: dict con la regla a aplicar
            plan: dict con el plan de comisiones
            base: monto base (con signo según tipo de operación)
            item: dict con datos del ítem
            tramos: lista de tramos para cálculo escalonado
            acumulado_ventas: acumulado previo para escalonado

        Returns:
            Decimal con el monto de comisión calculado.
        """
        importe_fijo = Decimal(str(regla.get('importe_fijo', 0)))
        porcentaje = Decimal(str(regla.get('porcentaje', 0)))
        tipo_calculo = plan.get('tipo_calculo', 'PORCENTAJE_VENTA')

        # Escalonada: buscar tramo
        if tipo_calculo == 'ESCALONADA':
            return self._calcular_escalonada(
                base, tramos or [], acumulado_ventas or Decimal(0), plan
            )

        # Por unidad fija
        if tipo_calculo == 'POR_UNIDAD':
            cantidad = Decimal(str(item.get('cantidad', 0)))
            return (importe_fijo * cantidad).quantize(
                Decimal('0.000001'), rounding=ROUND_HALF_UP
            )

        # Porcentaje sobre base
        if porcentaje > 0:
            return (base * porcentaje / Decimal(100)).quantize(
                Decimal('0.000001'), rounding=ROUND_HALF_UP
            )

        # Importe fijo directo (no por unidad)
        if importe_fijo > 0:
            return importe_fijo * signo_abs(base)

        return Decimal(0)

    # ----------------------------------------------------------------
    # Cálculo de base
    # ----------------------------------------------------------------

    def calcular_base(self, base_calculo, item):
        """Calcula el monto base para el cálculo de comisión.

        Args:
            base_calculo: tipo de base (constante BaseCalculo)
            item: dict con datos del ítem

        Returns:
            Decimal con el monto base (siempre positivo).
        """
        precio_total = Decimal(str(item.get('precio_total', 0)))
        bonificacion = Decimal(str(item.get('bonificacion', 0)))
        costo_unitario = Decimal(str(item.get('costo_unitario', 0)))
        cantidad = Decimal(str(item.get('cantidad', 0)))

        if base_calculo == 'VENTA_TOTAL':
            return precio_total

        if base_calculo == 'VENTA_NETA':
            return precio_total - bonificacion

        if base_calculo == 'VENTA_DESPUES_BONIFICACION':
            return precio_total - bonificacion

        if base_calculo == 'MARGEN':
            costo_total = costo_unitario * cantidad
            return precio_total - costo_total

        if base_calculo == 'CANTIDAD':
            return cantidad

        # Fallback: venta total
        return precio_total

    # ----------------------------------------------------------------
    # Helpers de tipo de operación
    # ----------------------------------------------------------------

    def es_nota_credito(self, tipo_operacion):
        """Indica si la operación es una nota de crédito."""
        return tipo_operacion == 'CREDITO'

    def signo_comision(self, tipo_operacion):
        """Retorna +1 para VENTA/DEBITO, -1 para CREDITO."""
        if tipo_operacion == 'CREDITO':
            return Decimal(-1)
        return Decimal(1)

    def tipo_movimiento_from_operacion(self, tipo_operacion):
        """Convierte tipo de operación a tipo de movimiento."""
        mapping = {
            'VENTA': 'VENTA',
            'CREDITO': 'NOTA_CREDITO',
            'DEBITO': 'NOTA_DEBITO',
        }
        return mapping.get(tipo_operacion, 'VENTA')

    # ----------------------------------------------------------------
    # Escalonado
    # ----------------------------------------------------------------

    def _calcular_escalonada(self, base, tramos, acumulado_ventas, plan):
        """Calcula comisión usando tramos de escala.

        Modo TASA_ALCANZADA: toda la base usa la tasa del tramo alcanzado.
        Modo PROGRESIVA: cada porción usa la tasa de su tramo.

        Args:
            base: monto base del ítem actual (con signo)
            tramos: lista de tramos ordenados por orden ASC
            acumulado_ventas: suma de bases previas en la venta
            plan: dict con modo_escalas

        Returns:
            Decimal con la comisión calculada.
        """
        if not tramos:
            return Decimal(0)

        base_abs = abs(base)
        acumulado = abs(acumulado_ventas)
        modo = plan.get('modo_escalas', 'TASA_ALCANZADA')
        signo = Decimal(1) if base >= 0 else Decimal(-1)

        if modo == 'TASA_ALCANZADA':
            # Buscar el tramo donde cae el acumulado + base actual
            total_acumulado = acumulado + base_abs
            for tramo in tramos:
                desde = Decimal(str(tramo.get('desde', 0)))
                hasta = Decimal(str(tramo.get('hasta', 0)))
                if hasta == 0:
                    hasta = Decimal('999999999999')
                if desde <= total_acumulado <= hasta:
                    porcentaje = Decimal(str(tramo.get('porcentaje', 0)))
                    importe_fijo = Decimal(str(tramo.get('importe_fijo', 0)))
                    if porcentaje > 0:
                        return (base_abs * porcentaje / Decimal(100)).quantize(
                            Decimal('0.000001'), rounding=ROUND_HALF_UP
                        ) * signo
                    if importe_fijo > 0:
                        return importe_fijo * signo

            # Si no encontró tramo, usar el último
            ultimo = tramos[-1]
            porcentaje = Decimal(str(ultimo.get('porcentaje', 0)))
            if porcentaje > 0:
                return (base_abs * porcentaje / Decimal(100)).quantize(
                    Decimal('0.000001'), rounding=ROUND_HALF_UP
                ) * signo
            return Decimal(0)

        if modo == 'PROGRESIVA':
            # Calcular porción de base en cada tramo
            comision_total = Decimal(0)
            posicion = acumulado
            restante = base_abs

            for tramo in tramos:
                if restante <= 0:
                    break
                desde = Decimal(str(tramo.get('desde', 0)))
                hasta = Decimal(str(tramo.get('hasta', 0)))
                if hasta == 0:
                    hasta = Decimal('999999999999')

                porcentaje = Decimal(str(tramo.get('porcentaje', 0)))

                # Cuánto de este tramo cubre la base restante
                inicio = max(posicion, desde)
                fin = min(posicion + restante, hasta)
                if fin > inicio:
                    volumen_tramo = fin - inicio
                    if porcentaje > 0:
                        comision_tramo = volumen_tramo * porcentaje / Decimal(100)
                        comision_total += comision_tramo
                    restante -= volumen_tramo
                posicion = fin

            return (comision_total * signo).quantize(
                Decimal('0.000001'), rounding=ROUND_HALF_UP
            )

        return Decimal(0)

    # ----------------------------------------------------------------
    # Helpers internos
    # ----------------------------------------------------------------

    def regla_aplica(self, regla, item):
        """Verifica si una regla aplica a un ítem según su criterio.

        Criterios soportados:
        - TODOS: aplica a todos los ítems
        - RUBRO: compara con idrubro del artículo
        - MARCA: compara con idmarca del artículo
        - ARTICULO: compara con idarticulo
        - TIPO_COMPROBANTE: compara con idtipocomprobante de la factura
        """
        criterio = regla.get('criterio', '')
        valor = regla.get('valor_criterio')

        if criterio == 'TODOS':
            return True

        if criterio == 'RUBRO':
            return str(item.get('rubro_id')) == str(valor)

        if criterio == 'MARCA':
            return str(item.get('marca_id')) == str(valor)

        if criterio == 'ARTICULO':
            return str(item.get('idarticulo')) == str(valor)

        if criterio == 'TIPO_COMPROBANTE':
            return str(item.get('idtipocomprobante')) == str(valor)

        return False

    def _generar_observacion(self, item, regla, tipo_operacion):
        """Genera texto de observación para trazabilidad."""
        parts = []
        if tipo_operacion == 'CREDITO':
            parts.append('NC')
        parts.append(f"Regla: {regla.get('nombre', '')}")
        criterio = regla.get('criterio', '')
        if criterio != 'TODOS':
            parts.append(f"Criterio: {criterio}={regla.get('valor_criterio', '')}")
        return ' | '.join(parts) if parts else None


def signo_abs(valor):
    """Retorna +1 si valor >= 0, -1 si es negativo."""
    return Decimal(1) if valor >= 0 else Decimal(-1)
