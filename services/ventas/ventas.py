from flask import session, jsonify, json, Response, current_app
import os
import tempfile
from decimal import Decimal
from datetime import date, timedelta, datetime
import uuid
from services.articulos import actualizarStock, get_articulo_by_codigo
from services.configs import discrimina_iva

from utils.utils import format_currency, precio, convertir_decimal
from models.ventas import Factura, Item, PagosFV, ControlNc, Presupuesto, ItemP, PresupuestoFactura, RemitosVtaFactura
from models.clientes import Clientes
from models.articulos import Articulo, ListasPrecios, Stock, Colores, DetallesArticulos
from models.entidades_cred import MovEntidades
from models.ctactecli import CtaCteCli
from models.configs import Configuracion, PagosCobros, AlcIva, AlcIB, PuntosVenta, TipoComprobantes, TipoIva, \
                           TipoCompAplica, Localidades, Provincias
from models.creditos import Creditos 
from sqlalchemy import func, extract, text, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from utils.db import db
from utils.config import Config
from services.facturador import Facturador
from services.generar_factura import generar_factura_pdf

from .facturacion import getNroComprobante
from .notas_credito import procesar_nueva_nc


def procesar_nueva_venta(form, id_sucursal):
    try:
        # --- Idempotency check ---
        idempotency_key = form.get('_idempotency_key')
        if idempotency_key:
            try:
                uuid.UUID(idempotency_key, version=4)
            except ValueError:
                raise ValueError("Formato de clave de idempotencia inválido")
            factura_existente = Factura.query.filter_by(idempotency_key=idempotency_key).first()
            if factura_existente:
                return factura_existente.nro_comprobante, factura_existente.id
        # --- End idempotency check ---

        idcliente = form['idcliente']
        fecha = form['fecha']
        idlista = form['idlista']
        id_tipo_comprobante = form['id_tipo_comprobante']
        efectivo = convertir_decimal(form['efectivo'])
        #datos de la tarjeta
        tarjeta = convertir_decimal(form['tarjeta'])
        cuotas = form.get('cuotas', 1)
        coeficiente = form.get('coeficiente', 1)
        documento = form['documento']
        telefono = form['telefono']
        entidad = form['entidad']
        #fin datos de la tarjeta
        ctacte = convertir_decimal(form['ctacte'])
        bonificacion = convertir_decimal(form['bonificacion'])
        idcredito = form.get('idcredito', None)
        credito = convertir_decimal(form.get('credito', '0'))
        idPresupuesto = form.get('idPresupuesto', None)
        idRemito = form.get('idRemito', None)
        totalFactura = convertir_decimal(form.get('totalFactura', '0'))
        descuento = bonificacion * Decimal(100) / totalFactura
        #Obtener datos del vale
        idVale = form.get('id_vale_comprobante', None)
        vale = form.get('vale', None)
        discrimina = discrimina_iva(id_tipo_comprobante)
        #Datos del comprobante original si es una noa de crédito
        id_comprobante_original = form.get('id_comprobante_original', None)
        total_comp_original = form.get('total_comp_original', None)
        nota_credito = form.get('nota_credito', 0)
        # Crear la factura (sin nro_comprobante aún — se asigna justo antes del commit)
        nueva_factura = Factura(
            idcliente=idcliente,
            idlista=idlista,
            fecha=fecha,
            total=0,  # Se calculará más adelante
            bonificacion=0,  # Se calculará más adelante
            id_tipo_comprobante=id_tipo_comprobante,
            idsucursal=id_sucursal,
            idusuario=session['user_id'],
            nro_comprobante='',
            punto_vta=session['idPuntoVenta']
        )
        db.session.add(nueva_factura)
        db.session.flush()
        idfactura = nueva_factura.id

        # Procesar los items
        total = 0
        neto = 0
        total_bonificacion = 0
        total, neto, total_bonificacion, total_iva, total_exento, total_impint = procesar_items(form, idfactura, discrimina, id_sucursal, descuento, id_tipo_comprobante)
        nueva_factura.total = total
        nueva_factura.neto = neto
        nueva_factura.bonificacion = total_bonificacion
        if not discrimina:
            total_iva = 0
        else:    
            nueva_factura.iva = total_iva
        nueva_factura.exento = total_exento 
        nueva_factura.impint = total_impint
        # Registrar los pagos
        procesar_pagos(idfactura, idcliente, fecha, total, efectivo, tarjeta, entidad, cuotas, coeficiente, documento, telefono, ctacte, bonificacion, idcredito, credito, nota_credito, idVale, vale )
        #Grabo el comprobante original si es una nota de crédito
        if id_comprobante_original:
            procesar_nueva_nc(idfactura, id_comprobante_original)
        # Si se está facturando un presupuesto se vincula el mismo a la factura 
        if idPresupuesto:
            presupuesto = db.session.get(Presupuesto, idPresupuesto)
            presupuesto.estado = 'Facturado'
            db.session.flush()
            presupuestoFactura = PresupuestoFactura(
                idpresupuesto=idPresupuesto,
                idfactura=idfactura
            )
            db.session.add(presupuestoFactura)
            db.session.flush()
        # Si se está facturando un remito se vincula el mismo a la factura 
        if idRemito:
            remitoFactura = RemitosVtaFactura(
                idremito=idRemito,
                idfactura=idfactura
            )
            db.session.add(remitoFactura)
            db.session.flush()
        # Late assignment: obtener correlativo justo antes del commit
        nro_comprobante = getNroComprobante(id_tipo_comprobante)
        nueva_factura.nro_comprobante = nro_comprobante
        nueva_factura.idempotency_key = idempotency_key or None

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if idempotency_key:
                factura_existente = Factura.query.filter_by(idempotency_key=idempotency_key).first()
                if factura_existente:
                    return factura_existente.nro_comprobante, factura_existente.id
            raise
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error sql grabando venta: {e}")
        raise Exception(f"Error sql grabando venta: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Error grabando venta: {e}")
        raise Exception(f"Error grabando venta: {e}")
    return nro_comprobante, idfactura


def procesar_items(form, idfactura, discrimina, id_sucursal, descuento, id_tipo_comprobante):
    total = Decimal(0)
    total_neto = Decimal(0)
    total_bonificacion = Decimal(0)
    total_iva = Decimal(0)
    total_exento = Decimal(0)
    total_impint = Decimal(0)
    
    #stock = db.session.query(Stock).filter_by(idsucursal=id_sucursal).first()
    try:
        for key, value in form.items():
            response = get_articulo_by_codigo(value)
            if response['success'] == True:
                if key.startswith('items') and key.endswith('[codigo]'):
                    precio_total = Decimal(0)
                    index = key.split('[')[1].split(']')[0]
                    codigo = value
                    cantidad = Decimal(form[f'items[{index}][cantidad]'])
                    precioUnit = Decimal(form[f'items[{index}][precio_unitario]'])
                    if descuento > 0:
                        original = precioUnit
                        precioUnit = precioUnit * (Decimal(1) - descuento / Decimal(100))
                        bonificacion = (original - precioUnit) * cantidad
                    else:
                        bonificacion = 0    
                    articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
                    iva = db.session.get(AlcIva, articulo.idiva)
                    ingbto = db.session.get(AlcIB, articulo.idib)
                    precios = precio(precioUnit, articulo.impint, articulo.exento, Decimal(0), Decimal(0), Decimal(iva.alicuota), Decimal(ingbto.alicuota))
                    #precio = Precio.query.filter_by(idarticulo=articulo.id, idlista=idlista).first()
                    #precio_unitario = precio.precio if precio else Decimal(0)
                    precio_total = precioUnit * cantidad
                    if not discrimina:
                        idalciva = 0
                        iva = 0
                    else:    
                        idalciva = articulo.idiva
                        iva = precios['Iva'] * cantidad
                    neto = precios['Neto'] * cantidad    
                    exento = precios['Exento'] * cantidad
                    impint = precios['ImpInt'] * cantidad
                    ingbrutos = precios['IngBto'] * cantidad
                    idoferta = form[f'items[{index}][idoferta]']
                    if idoferta:
                        idoferta = int(idoferta)
                    else:
                        idoferta = 0    
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
                        idfactura=idfactura,
                        id=index,
                        idarticulo=articulo.id,
                        cantidad=cantidad,
                        precio_unitario=precioUnit,
                        precio_total=precio_total,
                        neto = neto,
                        bonificacion=bonificacion,
                        iva=iva,
                        idalciva=idalciva,
                        ingbto=ingbrutos,
                        idingbto=ingbto.id,
                        exento=exento,  
                        impint=impint,
                        idoferta=idoferta,
                        id_color=id_color,
                        id_detalle=id_detalle
                    )
                    db.session.add(nuevo_item)
                    total += precio_total
                    total_neto += neto
                    total_bonificacion += bonificacion
                    total_iva += iva
                    total_exento += exento
                    total_impint += impint

                    # Actualizar el stock
                    if int(id_tipo_comprobante) in [1, 2, 3, 10, 11, 12]: # Solo actualizamos stock para facturas A, B y C
                        tipoMovimiento = 'Venta'
                    else:
                        tipoMovimiento = 'NotaCredito'    
                    actualizarStock(id_sucursal, articulo.id, -cantidad, tipoMovimiento)
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error procesando items: {e}")            
    
    return total, total_neto, total_bonificacion, total_iva, total_exento, total_impint


def procesar_pagos(idfactura, idcliente, fecha, total, efectivo, tarjeta, entidad, cuotas, coeficiente, documento, telefono, ctacte, bonificacion, idcredito, credito, nota_credito, id_vale, vale):
    #Calculamos el total de pagos para calcular si hay vuelto
    #El vuelto solo impacta en el total del efectivo
    
    #Calculo de intereses de pago con tarjeta
    intereses = Decimal(0)
    if tarjeta > 0:
        try:
            intereses = tarjeta / Decimal(coeficiente)
        except ZeroDivisionError:
            intereses = Decimal(0)
            
    
    totalPagos = efectivo + (tarjeta - intereses) + ctacte + bonificacion + credito
    totalPagos = totalPagos - total
    if totalPagos > 0:
        efectivo = efectivo - totalPagos
    try:
        if efectivo > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=1, tipo=1, entidad=0, total=efectivo))
        if tarjeta > 0:
            entidad = int(entidad)
            db.session.add(PagosFV(idfactura=idfactura, idpago=2, tipo=2, entidad=entidad, total=tarjeta))
            try:
                db.session.add(MovEntidades(idfactura=idfactura, identidad=int(entidad), cuotas=int(cuotas), total=tarjeta, intereses=intereses, documento=documento, telefono=telefono))
            except Exception as e:
                print(f'Error insertando movimiento de entidad: {e}')
        if ctacte > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=3, tipo=3, entidad=0, total=ctacte))
            db.session.add(CtaCteCli(idcliente=idcliente, fecha=fecha, debe=ctacte, haber=Decimal(0), idcomp=idfactura))
        if bonificacion > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=4, tipo=4, entidad=0, total=bonificacion))
        if idcredito and credito > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=5, tipo=5, entidad=0, total=credito))
            credito_obj = db.session.get(Creditos, idcredito)
            if credito_obj:
                credito_obj.estado = 5 #facturado
                credito_obj.idfactura = idfactura
                credito_obj.fecha_inicio = datetime.now()
        if nota_credito and Decimal(nota_credito) > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=20, tipo=20, entidad=0, total=-1*Decimal(nota_credito)))
        if id_vale and Decimal(vale) > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=21, tipo=21, entidad=0, total=Decimal(vale)))    
        #Si hay vuelto lo registramos        
        if (totalPagos) > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=99, tipo=1, entidad=0, total=totalPagos))
        
    except SQLAlchemyError as e:
        print(f"Error de base de datos procesando pagos: {e}")
        raise Exception(f"Error de base de datos procesando pagos: {e}")
    except Exception as e:
        print(f"Error procesando pagos: {e}")
        raise Exception(f"Error procesando pagos: {e}")


#---------------- recibos de cta cte ------------------#

def procesar_recibo_cta_cte(form, ctactecli):
    efectivo = convertir_decimal(form['efectivo'])
    tarjeta = convertir_decimal(form['tarjeta'])
    entidad = form['entidad']
    try:
        recibo = Factura(
            idsucursal=session['id_sucursal'],
            idusuario=session['user_id'],
            idcliente=ctactecli.idcliente,
            idlista=1,
            id_tipo_comprobante=12, #Recibo
            fecha=form['fecha'],
            total= Decimal(ctactecli.haber),
            iva=0,
            exento=0,
            impint=0,
            nro_comprobante=getNroComprobante(12),
            punto_vta=session['idPuntoVenta']
        )
        db.session.add(recibo)
        db.session.flush()
        procesar_pagos(recibo.id, recibo.idcliente, recibo.fecha, efectivo, tarjeta, entidad, 0, 0, None, 0)
        return recibo
    except SQLAlchemyError as e:
        db.session.rollback()
        recibo = []
        print(f"Error procesando recibo de cta cte: {e}")
        raise Exception(f"Error procesando recibo de cta cte: {e}")
    except Exception as e:
        db.session.rollback()
        recibo = []
        print(f"Error procesando recibo de cta cte: {e}")
        raise Exception(f"Error procesando recibo de cta cte: {e}")
    

#---------------- recibos de cobranza cuota credito ------------------#

def procesar_recibo_cuota_credito(idCliente, fecha, pagoTotal, efectivo, tarjeta, entidad):
    try:
        recibo = Factura(
            idsucursal=session['id_sucursal'],
            idusuario=session['user_id'],
            idcliente=idCliente,
            idlista=1,
            id_tipo_comprobante=12, #Recibo
            fecha=fecha,
            total= Decimal(pagoTotal),
            iva=0,
            exento=0,
            impint=0,
            nro_comprobante=getNroComprobante(12),
            punto_vta=session['idPuntoVenta']
        )
        db.session.add(recibo)
        db.session.flush()
        cuotas = 1
        coeficiente = 1
        documento = ''
        telefono = ''
        procesar_pagos(recibo.id, recibo.idcliente, recibo.fecha, Decimal(pagoTotal), Decimal(efectivo), Decimal(tarjeta), entidad, cuotas, coeficiente, documento, telefono, 0, 0, None, 0)
        return recibo
    except SQLAlchemyError as e:
        db.session.rollback()
        recibo = []
        print(f"Error SQLAlchemy, procesando recibo de cta cte: {e}")
        raise Exception(f"Error procesando recibo de cta cte: {e}")
    except Exception as e:
        db.session.rollback()
        recibo = []
        print(f"Error procesando recibo de cta cte: {e}")
        raise Exception(f"Error procesando recibo de cta cte: {e}")
