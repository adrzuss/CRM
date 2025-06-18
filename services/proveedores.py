from flask import request, session
from datetime import datetime
from models.proveedores import Proveedores, FacturaC, ItemC, PagosFC, RemitoFacturas
from models.articulos import Articulo, Stock
from models.ctacteprov import CtaCteProv
from models.configs import AlcIva
from services.articulos import actualizarStock, get_articulo_by_codigo
from utils.db import db
from decimal import Decimal
from services.articulos import actualizarStock
from models.configs import PagosCobros
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, func

def procesar_nueva_compra(form, id_sucursal):
    try:
        idproveedor = form['idproveedor']
        fecha = form['fecha']
        periodo = form['periodo']   
        id_tipo_comprobante = form['id_tipo_comprobante']
        nro_comprobante = form['nro_factura']
        id_plan_cuenta = form['id_plan_cuenta']
                
        #iva = Decimal(request.form['iva'])
        #exento = Decimal(request.form['exento'])
        #impint = Decimal(request.form['impint'])
        
        efectivo = float(request.form['efectivo'])
        ctacte = float(request.form['ctacte'])
        periodoFormateado = datetime.strptime(periodo, "%Y-%m").replace(day=1)
        # Crear la factura
        nueva_factura = FacturaC(
            idproveedor=idproveedor,
            fecha=fecha,
            periodo=periodoFormateado,
            total=0,  # Se calculará más adelante
            iva=0,
            exento=0,
            impint=0,
            idtipocomprobante=id_tipo_comprobante,
            idsucursal=id_sucursal,
            idusuario=session['user_id'],
            nro_comprobante=nro_comprobante,
            idplancuenta=id_plan_cuenta
            )
        db.session.add(nueva_factura)
        db.session.flush()
        idfactura = nueva_factura.id
        # Procesar los items
        total = 0
        actualizoCostos = False
        
        total,actualizoCostos = procesar_items(form, idfactura, id_sucursal, actualizoCostos)
        
        nueva_factura.total = total
        # Registrar los pagos
        procesar_pagos(idfactura, idproveedor, fecha, efectivo, ctacte)
        procesar_remitos(idfactura, form)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Error grabando compra: {e}")
    return actualizoCostos

def procesar_items(form, idfactura, id_sucursal, actualizoCostos=False):
    try:
        total = Decimal(0)
        iva = Decimal(0)
        impint = Decimal(0)
        exento = Decimal(0)
        for key, value in form.items():
            response = get_articulo_by_codigo(value)
            if response['success'] == True:
                if key.startswith('items') and key.endswith('[codigo]'):
                    index = key.split('[')[1].split(']')[0]
                    codigo = value
                    cantidad = Decimal(form[f'items[{index}][cantidad]'])
                    precio_unitario = Decimal(form[f'items[{index}][precio_unitario]'])
                    articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
                    precio_total = precio_unitario * cantidad
                    alcIva = AlcIva.query.get(articulo.idiva)
                    iva += Decimal(Decimal(alcIva.alicuota) * precio_total / Decimal(100))
                    impint += Decimal(Decimal(articulo.impint) * precio_total / Decimal(100))
                    exento += Decimal(Decimal(articulo.exento) * precio_total / Decimal(100))
                    total += precio_total
                    nuevo_item = ItemC(
                        idfactura=idfactura,
                        id=index, 
                        idarticulo=articulo.id,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        precio_total=precio_total,
                        idalciva=articulo.idiva,
                        iva=Decimal(Decimal(alcIva.alicuota) * precio_total / Decimal(100)),
                        exento=articulo.exento * cantidad,
                        impint=articulo.impint * cantidad
                    )
                    db.session.add(nuevo_item)
                    if articulo.costo != precio_unitario:
                        actualizoCostos = True
                        articulo.costo = precio_unitario
                    # Actualizar el stock
                    actualizarStock(id_sucursal, articulo.id, cantidad, id_sucursal)
        return total, actualizoCostos
    except SQLAlchemyError as e:
        raise Exception(f"Error procesando items: {e}")
    
def procesar_pagos(idfactura, idproveedor, fecha, efectivo, ctacte):
    try:
        if efectivo > 0:
            db.session.add(PagosFC(idfactura=idfactura, idpago=1, tipo=1, total=Decimal(efectivo)))
        if ctacte > 0:
            db.session.add(PagosFC(idfactura=idfactura, idpago=3, tipo=3, total=Decimal(ctacte)))
            db.session.add(CtaCteProv(idproveedor=idproveedor, fecha=fecha, debe=Decimal(0), haber=Decimal(ctacte)))
    except SQLAlchemyError as e:
        raise Exception(f"Error procesando pagos: {e}")

def procesar_remitos(idfactura, form):
    try:
        # Iterar por los ítems y verificar los checkboxes
        for key, value in form.items():
            if key.startswith('remito') and key.endswith('[check]'):  # Verificar si es un checkbox
                index = key.split('[')[1].split(']')[0]  # Obtener el índice del ítem
                if value == 'on':  # Si el checkbox está marcado
                    # Obtener el ID del remito asociado
                    id_remito = form[f'remito[{index}][id]']
                    # Procesar el remito seleccionado (por ejemplo, asociarlo a la factura)
                    nuevo_remito_factura = RemitoFacturas(
                        idremito=id_remito,
                        idfactura=idfactura
                    )
                    db.session.add(nuevo_remito_factura)
    except SQLAlchemyError as e:
        raise Exception(f"Error procesando remitos: {e}")

def procesar_nuevo_gasto(form, idsucursal):
    try:
        idproveedor = form['idproveedor']
        fecha = form['fecha']
        periodo = form['periodo']
        periodoFormateado = datetime.strptime(periodo, "%Y-%m").replace(day=1)
        id_tipo_comprobante = form['id_tipo_comprobante']
        id_plan_cuenta = form['id_plan_cuenta']
        nro_comprobante = form['nro_factura']
        gasto = float(form['total'])
        efectivo = float(form['efectivo'])
        ctacte = float(form['ctacte'])
        # Crear la factura
        nueva_gasto = FacturaC(idproveedor=idproveedor, 
                               fecha=fecha,
                               periodo=periodoFormateado, 
                               total=gasto,
                               idsucursal=idsucursal,
                               idtipocomprobante=id_tipo_comprobante,
                               idplancuenta=id_plan_cuenta,
                               idusuario=session['user_id'],
                               nro_comprobante=nro_comprobante)
        db.session.add(nueva_gasto)
        db.session.flush()
        
        idfactura = nueva_gasto.id

        # Registrar los pagos
        procesar_pagos(idfactura, idproveedor, fecha, efectivo, ctacte)
        procesar_remitos(idfactura, form)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Error grabando gasto: {e}")
    
def get_factura(id):
    factura = db.session.query(
                FacturaC.id,
                FacturaC.fecha,
                func.date_format(FacturaC.periodo, "%Y-%m").label("periodo"),
                FacturaC.nro_comprobante,
                FacturaC.total,
                FacturaC.iva,
                FacturaC.exento,
                FacturaC.impint,
                Proveedores.id.label('idcliente'),
                Proveedores.nombre,
                Proveedores.direccion) \
            .join(Proveedores, Proveedores.id == FacturaC.idproveedor) \
            .filter(FacturaC.id == id).all()
    items = db.session.query(
            ItemC.id,
            ItemC.cantidad,
            ItemC.precio_unitario,
            ItemC.precio_total,
            ItemC.iva,
            Articulo.codigo,
            Articulo.detalle) \
            .join(Articulo, Articulo.id == ItemC.idarticulo) \
            .filter(ItemC.idfactura == id)
    pagos = db.session.query(
            PagosFC.total,
            PagosCobros.pagos_cobros
            ).join(PagosCobros, PagosCobros.id == PagosFC.idpago
            ).filter(PagosFC.idfactura == id
            ).all()
    # Formatear el periodo a "YYYY-MM"        
    print(factura[0])
    return factura[0], items, pagos

def actualizar_precios_por_compras(id):
    db.session.execute(text("CALL actualizar_precios_por_compra(:idfacc)"), {'idfacc': id})
    db.session.commit() 
    return True

#--------------- Remitos ------------------

def get_remito(id):
    remito = db.session.query(
                FacturaC.id,
                FacturaC.fecha,
                Proveedores.id.label('idcliente'),
                Proveedores.nombre,
                Proveedores.direccion) \
            .join(Proveedores, Proveedores.id == FacturaC.idproveedor) \
            .filter(FacturaC.id == id).all()
    items = db.session.query(
            ItemC.id,
            ItemC.cantidad,
            Articulo.codigo,
            Articulo.detalle) \
            .join(Articulo, Articulo.id == ItemC.idarticulo) \
            .filter(ItemC.idfactura == id)
    return remito[0], items

def procesar_nuevo_remito(form, idsucursal):
    try:
        idproveedor = request.form['idproveedor']
        fecha = request.form['fecha']
        periodo = fecha
        nro_remito = request.form['nro_remito']
        idplancuenta = 0
        idtipocomprobante = 11  # ID del tipo de comprobante para remitos
        # Crear el remito
        nuevo_remito = FacturaC(idproveedor=idproveedor, nro_comprobante=nro_remito, fecha=fecha, periodo=periodo, idtipocomprobante=idtipocomprobante, idplancuenta=idplancuenta, idsucursal=idsucursal, idusuario=session['user_id'], total=0)
        db.session.add(nuevo_remito)
        db.session.flush()
        idremito = nuevo_remito.id
        # Procesar los items
        procesar_itemsR(form, idremito, idsucursal)
        db.session.commit()
    except SQLAlchemyError as e:
        raise Exception(f"Error grabando remito: {e}")
    
def procesar_itemsR(form, idremito, id_sucursal):
    try:
        stock = db.session.query(Stock).filter_by(idsucursal=id_sucursal).first()
        for key, value in form.items():
            response = get_articulo_by_codigo(value)
            if response['success'] == True:
                if key.startswith('items') and key.endswith('[codigo]'):
                    index = key.split('[')[1].split(']')[0]
                    codigo = value
                    cantidad = Decimal(form[f'items[{index}][cantidad]'])
                    articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
                    nuevo_item = ItemC(
                        idfactura=idremito,
                        id=index, 
                        idarticulo=articulo.id,
                        cantidad=cantidad,
                        precio_unitario=0,
                        precio_total=0,
                    )
                    db.session.add(nuevo_item)
                    # Actualizar el stock
                    actualizarStock(stock.idstock, articulo.id, cantidad, id_sucursal)
    except SQLAlchemyError as e:
        raise Exception(f"Error procesando items: {e}")
