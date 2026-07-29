from flask import session, jsonify, json, Response, current_app
import os
import tempfile
from decimal import Decimal
from datetime import date, timedelta, datetime
from services.articulos import actualizarStock, get_articulo_by_codigo
from services.configs import discrimina_iva

from utils.utils import format_currency, precio
from models.ventas import Factura, Item, PagosFV, ControlNc, Presupuesto, ItemP, PresupuestoFactura, RemitosVtaFactura
from models.clientes import Clientes
from models.articulos import Articulo, ListasPrecios, Stock, Colores, DetallesArticulos
from models.entidades_cred import MovEntidades
from models.ctactecli import CtaCteCli
from models.configs import Configuracion, PagosCobros, AlcIva, AlcIB, PuntosVenta, TipoComprobantes, TipoIva, \
                           TipoCompAplica, Localidades, Provincias
from models.creditos import Creditos 
from sqlalchemy import func, extract, text, and_
from sqlalchemy.exc import SQLAlchemyError
from utils.db import db
from utils.config import Config
from services.facturador import Facturador
from services.generar_factura import generar_factura_pdf


def procesar_nueva_nc(idfactura, id_comprobante_original):
    try:
        control_nc = ControlNc(id_comprobante=idfactura, id_comprobante_org=id_comprobante_original, fecha=datetime.now())
        db.session.add(control_nc)
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error procesando nueva nota de crédito: {e}")
        raise Exception(f"Error procesando nueva nota de crédito: {e}")

#----------------- notas de credito ------------------#

def get_comprobantes_para_nc(desde, hasta, nro_comprobante=''):
    """
    Busca comprobantes de venta disponibles para generar nota de crédito.
    Llama al procedimiento almacenado get_comprobantes_para_nc.
    
    Args:
        desde: Fecha desde (formato YYYY-MM-DD)
        hasta: Fecha hasta (formato YYYY-MM-DD)
        nro_comprobante: Número de comprobante a buscar (puede ser vacío)
    
    Returns:
        Lista de diccionarios con los comprobantes encontrados
    """
    try:
        resultado = db.session.execute(
            text("CALL get_comprobantes_para_nc(:desde, :hasta, :nro_comprobante)"),
            {'desde': desde, 'hasta': hasta, 'nro_comprobante': nro_comprobante or ''}
        ).fetchall()
        
        comprobantes = []
        for row in resultado:
            # Soportar ambos nombres de campo: nrocomprobante o nro_comprobante
            
            comprobantes.append({
                'id': row.id,
                'idcliente': row.idcliente,
                'idtipocomp': row.idtipocomp,
                'total': float(row.total) if row.total else 0,
                'cliente': row.cliente,
                'tipo_comp': row.tipo_comp,
                'nro_comprobante': row.nro_comprobante,
                'idlista': row.idlista
            })
        
        return comprobantes
    except Exception as e:
        print(f"Error al buscar comprobantes para NC: {e}")
        return []


def get_items_comprobante_venta(idcomprobante):
    """
    Obtiene los items de un comprobante de venta para generar nota de crédito.
    Llama al procedimiento almacenado get_items_comprobante_venta y complementa
    con datos del artículo (código y descripción).
    
    Args:
        idcomprobante: ID del comprobante de venta
    
    Returns:
        Lista de diccionarios con los items del comprobante
    """
    try:
        resultado = db.session.execute(
            text("CALL get_items_comprobante_venta(:idcomprobante)"),
            {'idcomprobante': idcomprobante}
        ).fetchall()
        
        items = []
        for row in resultado:
            # Obtener datos del artículo (código y descripción)
            articulo = db.session.get(Articulo, row.idarticulo)
            
            cantidad = float(row.cantidad) if row.cantidad else 0
            precio_unitario = float(row.precio_unitario) if row.precio_unitario else 0
            precio_total = cantidad * precio_unitario
            
            items.append({
                'idarticulo': row.idarticulo,
                'codigo': articulo.codigo if articulo else '',
                'descripcion': articulo.detalle if articulo else '',
                'idcolor': row.idcolor or 0,
                'iddetalle': row.iddetalle or 0,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'precio_total': round(precio_total, 2)
            })
        
        return items
    except Exception as e:
        print(f"Error al obtener items del comprobante: {e}")
        return []


def get_vale_disponible(nro_comprobante):
    """
    Busca un vale (nota de crédito) disponible para usar como medio de pago.
    Llama al procedimiento almacenado vales_disponibles.
    
    El número de comprobante tiene formato 0000-00000000
    
    Args:
        nro_comprobante: Número del vale/nota de crédito a buscar
    
    Returns:
        Diccionario con los datos del vale si está disponible, None si no existe o ya fue usado
        Campos: id_comprobante, nro_comprobante, fecha, total, cliente
    """
    try:
        resultado = db.session.execute(
            text("CALL vales_disponibles(:nro_comprobante)"),
            {'nro_comprobante': nro_comprobante}
        ).fetchall()
        db.session.commit()  # Asegurar que se liberen los locks del SP
        if resultado:
            print(f"Vale encontrado: {resultado[0].nro_comprobante} - Total: {resultado[0].total} - Cliente: {resultado[0].nombre}")
            return {
                'id_comprobante': resultado[0].id_comprobante,
                'nro_comprobante': resultado[0].nro_comprobante,
                'fecha': str(resultado[0].fecha) if resultado[0].fecha else '',
                'total': float(resultado[0].total) if resultado[0].total else 0,
                'cliente': resultado[0].nombre
            }
        print(f"No se encontró un vale disponible con número: {nro_comprobante}")
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error al buscar vale disponible: {e}")
        return None


#----------------- fin notas de credito ------------------#
