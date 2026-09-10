# comisiones/constants.py
# Constantes y enumeraciones del módulo de comisiones

from enum import Enum


class TipoComision(str, Enum):
    """Tipos de cálculo de comisión disponibles."""
    PORCENTAJE_VENTA = "PORCENTAJE_VENTA"
    PORCENTAJE_NETO = "PORCENTAJE_NETO"
    PORCENTAJE_MARGEN = "PORCENTAJE_MARGEN"
    POR_ARTICULO = "POR_ARTICULO"
    POR_RUBRO = "POR_RUBRO"
    POR_MARCA = "POR_MARCA"
    POR_DESCUENTO = "POR_DESCUENTO"
    POR_UNIDAD = "POR_UNIDAD"
    ESCALONADA = "ESCALONADA"


class BaseCalculo(str, Enum):
    """Bases sobre las cuales se calcula la comisión."""
    VENTA_TOTAL = "VENTA_TOTAL"
    VENTA_NETA = "VENTA_NETA"
    VENTA_DESPUES_BONIFICACION = "VENTA_DESPUES_BONIFICACION"
    MARGEN = "MARGEN"
    CANTIDAD = "CANTIDAD"


class ModoEscalas(str, Enum):
    """Modos de cálculo para escalas / tramos."""
    TASA_ALCANZADA = "TASA_ALCANZADA"
    PROGRESIVA = "PROGRESIVA"


class EstadoLiquidacion(str, Enum):
    """Estados del ciclo de vida de una liquidación."""
    BORRADOR = "BORRADOR"
    CALCULADA = "CALCULADA"
    CONFIRMADA = "CONFIRMADA"
    PAGADA = "PAGADA"
    ANULADA = "ANULADA"


class TipoMovimiento(str, Enum):
    """Tipos de movimiento que generan comisión."""
    VENTA = "VENTA"
    NOTA_CREDITO = "NOTA_CREDITO"
    NOTA_DEBITO = "NOTA_DEBITO"


class TipoRegla(str, Enum):
    """Indica si una regla se combina con otras o es excluyente."""
    EXCLUSIVA = "EXCLUSIVA"
    ACUMULABLE = "ACUMULABLE"


# Mapeo de estados permitidos para transiciones
TRANSICIONES_LIQUIDACION = {
    EstadoLiquidacion.BORRADOR: [EstadoLiquidacion.CALCULADA, EstadoLiquidacion.CONFIRMADA, EstadoLiquidacion.ANULADA],
    EstadoLiquidacion.CALCULADA: [EstadoLiquidacion.CONFIRMADA, EstadoLiquidacion.ANULADA],
    EstadoLiquidacion.CONFIRMADA: [EstadoLiquidacion.PAGADA],
    EstadoLiquidacion.PAGADA: [],
    EstadoLiquidacion.ANULADA: [],
}
