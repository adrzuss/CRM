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

from .facturacion import getNroComprobante


def procesar_nuevo_remito(form, id_sucursal):
    try:
        idcliente = form['idcliente']
        fecha = form['fecha']
        idlista = form['idlista']
        id_tipo_comprobante = form['id_tipo_comprobante']
        #Obtener nuemero de comprobante
        nro_comprobante = getNroComprobante(id_tipo_comprobante)
        
        # Crear la factura
        nuevo_remito = Factura(
            idcliente=idcliente,
            idlista=idlista,
            fecha=fecha,
            total=0,  # Se calculará más adelante
            iva=0,
            exento=0,
            impint=0, 
            id_tipo_comprobante=id_tipo_comprobante,
            idsucursal=id_sucursal,
            idusuario=session['user_id'],
            nro_comprobante=nro_comprobante,
            punto_vta=session['idPuntoVenta']
        )
        db.session.add(nuevo_remito)
        db.session.flush()
        idremito = nuevo_remito.id

        # Procesar los items
        total = 0
        procesar_items_remito(form, idremito, id_sucursal)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Error grabando remito: {e}")
    return nro_comprobante
    

def procesar_items_remito(form, idremito, id_sucursal):
    stock = db.session.query(Stock).filter_by(idsucursal=id_sucursal).first()
    for key, value in form.items():
        response = get_articulo_by_codigo(value)
        if response['success'] == True:
            if key.startswith('items') and key.endswith('[codigo]'):
                index = key.split('[')[1].split(']')[0]
                codigo = value
                cantidad = Decimal(form[f'items[{index}][cantidad]'])
                articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
                
                # Obtener color y detalle si están presentes
                possible_color_keys = [
                    f'items[{index}][id_color]',
                    f'id_color[{index}]', 
                    f'id_color[]'
                ]
                possible_detalle_keys = [
                    f'items[{index}][id_detalle]',
                    f'id_detalle[{index}]', 
                    f'id_detalle[]'
                ]
                
                id_color = None
                id_detalle = None
                
                # Buscar color
                for key in possible_color_keys:
                    if key in form:
                        id_color = form.get(key)
                        break
                
                # Buscar detalle
                for key in possible_detalle_keys:
                    if key in form:
                        id_detalle = form.get(key)
                        break
                
                # Convertir a int si tienen valor, sino 0
                id_color = int(id_color) if id_color and id_color != '' and id_color != 'None' else 0
                id_detalle = int(id_detalle) if id_detalle and id_detalle != '' and id_detalle != 'None' else 0
                
                nuevo_item = Item(
                    idfactura=idremito,
                    id=index,
                    idarticulo=articulo.id,
                    cantidad=cantidad,
                    precio_unitario=0,
                    precio_total=0,
                    iva=0,
                    idalciva=0,
                    ingbto=0,
                    idingbto=0,
                    exento=0,  
                    impint=0,
                    id_color=id_color,
                    id_detalle=id_detalle
                )
                db.session.add(nuevo_item)
                # Actualizar el stock
                actualizarStock(id_sucursal, articulo.id, -cantidad)
    
    return True


def get_remito(id):
    factura = db.session.query(
                Factura.id,
                Factura.fecha,
                Factura.total,
                Factura.nro_comprobante,
                Factura.punto_vta,
                Clientes.id.label('idcliente'),
                Clientes.nombre,
                Clientes.direccion,
                ListasPrecios.nombre.label('lista'),
                TipoComprobantes.nombre.label('tipo_comprobante')) \
            .join(Clientes, Clientes.id == Factura.idcliente) \
            .outerjoin(ListasPrecios, ListasPrecios.id == Factura.idlista) \
            .join(TipoComprobantes, TipoComprobantes.id == Factura.idtipocomprobante) \
            .filter(Factura.id == id).all()
   #Factura.query.get(id)
    items = db.session.query(
            Item.id,
            Item.idarticulo,
            Item.cantidad,
            Item.precio_unitario,
            Item.precio_total,
            Articulo.codigo,
            Articulo.detalle) \
            .join(Articulo, Articulo.id == Item.idarticulo) \
            .filter(Item.idfactura == id)
    return factura[0], items
