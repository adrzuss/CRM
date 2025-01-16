from flask import request, session
from datetime import date, timedelta
from models.proveedores import Proveedores, FacturaC, ItemC, PagosFC
from models.articulos import Articulo, Stock
from models.ctacteprov import CtaCteProv
from services.articulos import actualizarStock
from utils.utils import check_session
from utils.db import db
from decimal import Decimal
from utils.utils import format_currency
from services.articulos import actualizarStock
from models.configs import PagosCobros
from sqlalchemy import func, extract
from sqlalchemy.exc import SQLAlchemyError

def procesar_nueva_compra(form, id_sucursal):
    try:
        idproveedor = request.form['idproveedor']
        fecha = request.form['fecha']
        id_tipo_comprobante = request.form['id_tipo_comprobante']
        
        efectivo = float(request.form['efectivo'])
        ctacte = float(request.form['ctacte'])

        # Crear la factura
        nueva_factura = FacturaC(
            idproveedor=idproveedor,
            fecha=fecha,
            total=0,  # Se calculará más adelante
            idtipocomprobante=id_tipo_comprobante,
            idsucursal=id_sucursal,
            idusuario=session['user_id']
        )
        db.session.add(nueva_factura)
        db.session.flush()
        idfactura = nueva_factura.id

        # Procesar los items
        total = 0
        total = procesar_items(form, idfactura, id_sucursal)
        nueva_factura.total = total
        # Registrar los pagos
        procesar_pagos(idfactura, idproveedor, fecha, efectivo, ctacte)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Error grabando compra: {e}")

def procesar_items(form, idfactura, id_sucursal):
    try:
        total = Decimal(0)
        stock = db.session.query(Stock).filter_by(idsucursal=id_sucursal).first()

        for key, value in form.items():
            if key.startswith('items') and key.endswith('[codigo]'):
                index = key.split('[')[1].split(']')[0]
                codigo = value
                cantidad = Decimal(form[f'items[{index}][cantidad]'])
                precio_unitario = Decimal(form[f'items[{index}][precio_unitario]'])
                articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
                
                precio_total = precio_unitario * cantidad
                total += precio_total

                nuevo_item = ItemC(
                    idfactura=idfactura,
                    id=index, 
                    idarticulo=articulo.id,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    precio_total=precio_total
                )
                db.session.add(nuevo_item)
                # Actualizar el stock
                actualizarStock(stock.idstock, articulo.id, cantidad, id_sucursal)
        return total
    except SQLAlchemyError as e:
        raise Exception(f"Error procesando items: {e}")
    
def procesar_pagos(idfactura, idproveedor, fecha, efectivo, ctacte):
    try:
        if efectivo > 0:
            db.session.add(PagosFC(idfactura=idfactura, idpago=1, tipo=1, total=Decimal(efectivo)))
        if ctacte > 0:
            db.session.add(PagosFC(idfactura=idfactura, idpago=3, tipo=3, total=Decimal(ctacte)))
            db.session.add(CtaCteProv(idproveedor=idproveedor, fecha=fecha, debe=Decimal(0), haber=Decimal(ctacte)))
        #db.session.commit()
    except SQLAlchemyError as e:
        raise Exception(f"Error procesando pagos: {e}")


def procesar_nuevo_gasto(form, idsucursal):
    try:
        idproveedor = request.form['idproveedor']
        fecha = request.form['fecha']
        id_tipo_comprobante = request.form['id_tipo_comprobante']
        gasto = float(request.form['total'])
        efectivo = float(form['efectivo'])
        ctacte = float(form['ctacte'])
        # Crear la factura
        nueva_gasto = FacturaC(idproveedor=idproveedor, fecha=fecha, total=gasto, idsucursal=idsucursal, idtipocomprobante=id_tipo_comprobante)
        db.session.add(nueva_gasto)
        db.session.flush()
        
        idfactura = nueva_gasto.id

        # Registrar los pagos
        procesar_pagos(idfactura, idproveedor, fecha, efectivo, ctacte)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Error grabando gasto: {e}")