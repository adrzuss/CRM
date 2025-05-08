from flask import request, session, jsonify, json
from decimal import Decimal
from datetime import date, timedelta
from utils.utils import format_currency
from services.articulos import actualizarStock
from services.configs import discrimina_iva

from utils.utils import format_currency, precio
from models.ventas import Factura, Item, PagosFV
from models.clientes import Clientes
from models.articulos import Articulo, ListasPrecios, Stock
from models.ctactecli import CtaCteCli
from models.configs import PagosCobros, AlcIva, AlcIB, PuntosVenta, TipoComprobantes
from sqlalchemy import func, extract, text, and_
from sqlalchemy.exc import SQLAlchemyError
from utils.db import db
from utils.config import Config
from services.facturador import Facturador

def get_certificado_clave_fe(id_punto_vta):
    try:
        punto_vta = PuntosVenta.query.get(id_punto_vta)
        if punto_vta.fac_electronica == True:
            #cert_file = os.path.join(os.getcwd(), Config.FE_FILES_FOLDER, punto_vta.certificado_p12)
            cert_file =  Config.FE_FILES_FOLDER + '/' + punto_vta.certificado_p12
            msg = ''
            return cert_file, punto_vta.clave_certificado, msg
        else:
            cert_file = None
            clave = None
            msg = 'Este punto de venta no está habilitado para factura electrónica'
        return cert_file, clave, msg
    except Exception as e:
        cert_file = None
        clave = None
        msg = 'Este punto de venta no tiene certificado para facturas electrónicas'
        return cert_file, clave, msg

def getNroComprobante(id_tipo_comprobante):
    try:
        idPuntoVta = session.get('idPuntoVenta', None)
        puntoVta = PuntosVenta.query.get(idPuntoVta)
        nro = 0
        tipoComp = int(id_tipo_comprobante)
        if tipoComp == 1:
            nro = puntoVta.ultima_fac_a
            puntoVta.ultima_fac_a += 1
        elif tipoComp == 2:
            nro = puntoVta.ultima_fac_b
            puntoVta.ultima_fac_b += 1
        elif tipoComp == 3:
            nro = puntoVta.ultima_tkt
            puntoVta.ultima_tkt += 1
        elif tipoComp == 4:
            nro = puntoVta.ultima_nc_a
            puntoVta.ultima_nc_a += 1
        elif (tipoComp == 5) or (tipoComp == 6): 
            nro = puntoVta.ultima_nc_b
            puntoVta.ultima_nc_b += 1
        elif tipoComp == 7:
            nro = puntoVta.ultima_deb_c
            puntoVta.ultima_deb_c += 1
        elif (tipoComp == 8) or (tipoComp == 9): 
            nro = puntoVta.ultima_deb_b
            puntoVta.ultima_deb_b += 1
        elif ((tipoComp == 10)or(tipoComp == 11)or(tipoComp == 12)or(tipoComp == 19)):
            nro = puntoVta.ultima_fac_c
            puntoVta.ultima_fac_c += 1
        elif (tipoComp == 13)or(tipoComp == 14)or(tipoComp == 15):
            nro = puntoVta.ultima_nc_c
            puntoVta.ultima_nc_c += 1
        elif (tipoComp == 16)or(tipoComp == 17)or(tipoComp == 18):
            nro = puntoVta.ultima_deb_c
            puntoVta.ultima_deb_c += 1
        elif (tipoComp == 20)or(tipoComp == 21)or(tipoComp == 22)or(tipoComp == 23)or\
             (tipoComp == 24)or(tipoComp == 25)or(tipoComp == 26)or(tipoComp == 27):
            nro = puntoVta.ultimo_rem_x
            puntoVta.ultimo_rem_x += 1 
        else:
            nro = 0       
        db.session.commit()    
        return idPuntoVta.zfill(4) + '-' + str(nro).zfill(8) 
    except Exception as e:
        print(f"Error al obtener el número de comprobante: {e}")
        return "0000-00000000"
    
def facturar_fe(ptovta, idfactura):
    #ptoVta = PuntosVenta.query.get(ptovta)
    if ptovta: #aca
        #AFIP_CERT_PATH = f'cert_fe/{ptoVta.certificado_p12}'
        #AFIP_CERT_PASSWORD = ptoVta.clave_certificado
        AFIP_CERT_PATH, AFIP_CERT_PASSWORD, msg = get_certificado_clave_fe(ptovta)
    if AFIP_CERT_PATH == None:
        return jsonify({'success': False, 'error': msg}), 400
    try:
        # 1. Obtener datos de la factura desde la DB
        print('1- Obtener datos de la factura desde la DB')
        result_proxy = db.session.execute(text("CALL get_datosfac_fe(:id)"), {'id': idfactura})
        result = result_proxy.fetchall()
        result_proxy.close
        print('2- Obtener datos de la factura desde la DB')
        if not result:
            return jsonify({"error": "Factura no encontrada"}), 404
        # 2. Parsear el JSON
        
        print('2- Parsear el JSON')
        factura_db = json.loads(result[0][0])  # Asume que el SP devuelve JSON como cadena
        # 3. Mapear a la estructura esperada por Facturador
        print('3- Mapear a la estructura esperada por Facturador')
        datos_factura = {
            "cliente": {
                "tipo_doc": factura_db["cliente"]["tipo_doc"],
                "nro_doc": factura_db["cliente"]["nro_doc"],
                "nombre": factura_db["cliente"].get("nombre", ""),  # Opcional
            },
            "items": [
                {
                    "codigo": item["codigo"],
                    "descripcion": item["descripcion"],
                    "cantidad": item["cantidad"],
                    "precio": float(item["precio"]),
                    "iva": float(item["iva"]),  # Asegurar que sea float
                    "importe_neto": float(item["importe_neto"]),
                    "importe_iva": float(item["importe_iva"])
                }
                for item in factura_db["items"]
            ],
            "tipo_comprobante": int(factura_db["tipo_comprobante"]),
            "punto_venta": int(factura_db.get("punto_venta", 1))  # Default 1 si no existe
        }
        # 4. Validar datos antes de enviar a AFIP
        if not datos_factura["items"]:
            return jsonify({"error": "La factura no tiene items"}), 400
        # Crear facturador
        print('4- Crear facturador')
        facturador = Facturador({
            'cert_path': AFIP_CERT_PATH,
            'cert_password': AFIP_CERT_PASSWORD,
            'punto_venta': datos_factura["punto_venta"]
        })
        
        print('5- Emitir factura')
        # Emitir factura
        resultado = facturador.emitir_factura(
            cliente=datos_factura["cliente"],
            items=datos_factura["items"],
            tipo_comprobante=datos_factura["tipo_comprobante"],
            punto_venta=datos_factura["punto_venta"])
        
        # 6. Actualizar la factura en DB con el CAE
        print('6- Actualizar la factura en DB con el CAE')
        try:
            db.session.execute(
                text("""
                    UPDATE facturav 
                    SET cae = :cae, 
                        cae_vto = :cae_vto,
                        nro_comprobante = :nro_cbte,
                        fecha_emision = NOW()
                    WHERE id = :id
                """),
                {
                    'cae': resultado['cae'],
                    'cae_vto': resultado['cae_fch_vto'],
                    'nro_cbte': ptovta.zfill(4) + '-' + str(resultado['nro_cbte']).zfill(8),
                    'id': idfactura
                }
            )
            db.session.commit()
            print('7- Actualizado')
            return jsonify({
                'success': True,
                'result': resultado
            }), 200
        except Exception as e:  
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500        
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
def procesar_nueva_venta(form, id_sucursal):
    try:
        idcliente = request.form['idcliente']
        fecha = request.form['fecha']
        idlista = request.form['idlista']
        id_tipo_comprobante = request.form['id_tipo_comprobante']
        efectivo = float(request.form['efectivo'])
        tarjeta = float(request.form['tarjeta'])
        entidad = request.form['entidad']
        ctacte = float(request.form['ctacte'])
        #Obtener nuemero de comprobante
        nro_comprobante = getNroComprobante(id_tipo_comprobante)
        discrimina = discrimina_iva(id_tipo_comprobante)
        # Crear la factura
        nueva_factura = Factura(
            idcliente=idcliente,
            idlista=idlista,
            fecha=fecha,
            total=0,  # Se calculará más adelante
            id_tipo_comprobante=id_tipo_comprobante,
            idsucursal=id_sucursal,
            idusuario=session['user_id'],
            nro_comprobante=nro_comprobante,
            punto_vta=session['idPuntoVenta']
        )
        db.session.add(nueva_factura)
        db.session.flush()
        idfactura = nueva_factura.id

        # Procesar los items
        total = 0
        total, total_iva, total_exento, total_impint = procesar_items(form, idfactura, discrimina, id_sucursal)
        nueva_factura.total = total
        if not discrimina:
            total_iva = 0
        else:    
            nueva_factura.iva = total_iva
        nueva_factura.exento = total_exento
        nueva_factura.impint = total_impint
        # Registrar los pagos
        procesar_pagos(idfactura, idcliente, fecha, efectivo, tarjeta, entidad, ctacte)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Error grabando venta: {e}")
    return nro_comprobante
    
def procesar_items(form, idfactura, discrimina, id_sucursal):
    total = Decimal(0)
    total_iva = Decimal(0)
    total_exento = Decimal(0)
    total_impint = Decimal(0)
    
    #stock = db.session.query(Stock).filter_by(idsucursal=id_sucursal).first()
    for key, value in form.items():
        if key.startswith('items') and key.endswith('[codigo]'):
            precio_total = Decimal(0)
            index = key.split('[')[1].split(']')[0]
            codigo = value
            cantidad = Decimal(form[f'items[{index}][cantidad]'])
            precioUnit = Decimal(form[f'items[{index}][precio_unitario]'])
            articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
            iva = AlcIva.query.get(articulo.idiva)
            ingbto = AlcIB.query.get(articulo.idib)
            precios = precio(precioUnit, articulo.impint, articulo.exento, Decimal(0), Decimal(0), Decimal(iva.alicuota), Decimal(ingbto.alicuota))
            #precio = Precio.query.filter_by(idarticulo=articulo.id, idlista=idlista).first()
            #precio_unitario = precio.precio if precio else Decimal(0)
            precio_total = precios['PFinal'] * cantidad
            if not discrimina:
                idalciva = 0
                iva = 0
            else:    
                idalciva = articulo.idiva
                iva = precios['Iva'] * cantidad
            exento = precios['Exento'] * cantidad
            impint = precios['ImpInt'] * cantidad
            ingbrutos = precios['IngBto'] * cantidad
            nuevo_item = Item(
                idfactura=idfactura,
                id=index,
                idarticulo=articulo.id,
                cantidad=cantidad,
                precio_unitario=precios['PFinal'],
                precio_total=precio_total,
                iva=iva,
                idalciva=idalciva,
                ingbto=ingbrutos,
                idingbto=ingbto.id,
                exento=exento,  
                impint=impint
            )
            db.session.add(nuevo_item)
            total += precio_total
            total_iva += iva
            total_exento += exento
            total_impint += impint

            # Actualizar el stock
            actualizarStock(id_sucursal, articulo.id, -cantidad, id_sucursal)
    
    return total, total_iva, total_exento, total_impint

def procesar_pagos(idfactura, idcliente, fecha, efectivo, tarjeta, entidad, ctacte):
    try:
        if efectivo > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=1, tipo=1, entidad=0, total=Decimal(efectivo)))
        if tarjeta > 0:
            entidad = int(request.form['entidad'])
            db.session.add(PagosFV(idfactura=idfactura, idpago=2, tipo=2, entidad=entidad, total=Decimal(tarjeta)))
        if ctacte > 0:
            db.session.add(PagosFV(idfactura=idfactura, idpago=3, tipo=3, entidad=0, total=Decimal(ctacte)))
            db.session.add(CtaCteCli(idcliente=idcliente, fecha=fecha, debe=Decimal(ctacte), haber=Decimal(0)), idcomp=idfactura)
        #db.session.commit()
    except SQLAlchemyError as e:
        raise Exception(f"Error procesando pagos: {e}")

def procesar_nuevo_remito(form, id_sucursal):
    try:
        idcliente = request.form['idcliente']
        fecha = request.form['fecha']
        idlista = 0
        id_tipo_comprobante = request.form['id_tipo_comprobante']
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
        if key.startswith('items') and key.endswith('[codigo]'):
            index = key.split('[')[1].split(']')[0]
            codigo = value
            cantidad = Decimal(form[f'items[{index}][cantidad]'])
            articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
            #precio = Precio.query.filter_by(idarticulo=articulo.id, idlista=idlista).first()
            #precio_unitario = precio.precio if precio else Decimal(0)
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
                impint=0
            )
            db.session.add(nuevo_item)
            # Actualizar el stock
            actualizarStock(stock.idstock, articulo.id, -cantidad, id_sucursal)
    
    return True


def get_vta_hoy():
    hoy = date.today()
    try:
        vta_hoy = db.session.query(func.sum(Factura.total).label('total')).filter(Factura.fecha == hoy).all()
        return format_currency(vta_hoy[0][0])
    except:
        return 0.0

def get_vta_semana():
    hoy = date.today()
    # Calcular el inicio de la semana (lunes)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    try:
        # Realizar la consulta para obtener el total de ventas de la semana
        vta_semana = db.session.query(
            func.sum(Factura.total).label('total_ventas')
        ).filter(
            Factura.fecha >= inicio_semana,
            Factura.fecha <= hoy
        ).scalar()
        return format_currency(vta_semana)
    except:
        return 0.0

def get_vta_desde_hasta(desde, hasta):
    try:
        # Realizar la consulta para obtener el total de ventas de la semana
        vta_desde_hasta = db.session.query(
            func.sum(Factura.total).label('total_ventas'),
            func.count(Factura.id).label('cantidad_ventas')
        ).filter(
            Factura.fecha >= desde,
            Factura.fecha <= hasta
        ).all()
        return vta_desde_hasta
    except:
        return []

def ventas_desde_hasta(desde, hasta):
    try:
        ventas = db.session.query(Factura.id,
                                Factura.fecha,
                                Factura.total,
                                Factura.nro_comprobante,
                                Factura.cae,
                                Clientes.nombre.label('cliente'),
                                TipoComprobantes.nombre.label('tipo_comprobante')
                                ).join(Clientes, Factura.idcliente == Clientes.id 
                                ).join(TipoComprobantes, Factura.idtipocomprobante == TipoComprobantes.id
                                ).filter(Factura.fecha >= desde, Factura.fecha <= hasta).all()
        return ventas                        
    except Exception as e:
        print(f'error: {e}')
        return []

def get_operaciones_hoy():
    hoy = date.today()
    try:
        op_hoy = db.session.query(func.count(Factura.id).label('operaciones')).filter(
                 and_(
                        Factura.fecha == hoy,
                        Factura.idsucursal == session['id_sucursal']
                    )
                ).all()
        return op_hoy[0][0]
    except Exception as e:
        print(f'error: {e}')
        return 0
    
def get_operaciones_semana():
    hoy = date.today()
    # Calcular el inicio de la semana (lunes)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    try:
        # Realizar la consulta para obtener el total de ventas de la semana
        vta_semana = db.session.query(
            func.count(Factura.id).label('total_op')
        ).filter(
            Factura.fecha >= inicio_semana,
            Factura.fecha <= hoy,
            Factura.idsucursal == session['id_sucursal']
        ).scalar()
        return vta_semana
    except:
        return 0.0
    
def get_op_este_mes():
    hoy = date.today()
    # Calcular el inicio de la semana (lunes)
    inicio_mes = hoy.replace(day=1)
    try:
        # Realizar la consulta para obtener el total de ventas de la semana
        op_este_mes = db.session.query(
            func.count(Factura.id).label('total_op')
        ).filter(
            Factura.fecha >= inicio_mes,
            Factura.fecha <= hoy,
            Factura.idsucursal == session['id_sucursal']
        ).scalar()
        return op_este_mes
    except:
        return 0.0

def get_op_este_mes_anterior():
    hoy = date.today()
    hoy = hoy.replace(year=hoy.year-1)
    # Calcular el inicio de la semana (lunes)
    inicio_mes = hoy.replace(day=1)
    try:
        # Realizar la consulta para obtener el total de ventas de la semana
        op_este_mes_ant = db.session.query(
            func.count(Factura.id).label('total_op')
        ).filter(
            Factura.fecha >= inicio_mes,
            Factura.fecha <= hoy,
            Factura.idsucursal == session['id_sucursal']
        ).scalar()
        return op_este_mes_ant
    except:
        return 0.0
    
def operaciones_por_mes():
    # Obtener la fecha de hoy
    fecha_hoy = date.today()

    # Calcular la fecha 6 meses atrás
    fecha_inicio = fecha_hoy - timedelta(days=180)

    # Crear listas para los nombres de los meses y la cantidad de operaciones
    nombres_meses = []
    cantidades_operaciones = []
    try:
        # Realizar la consulta para obtener la cantidad de operaciones por mes
        resultados = db.session.query(
            func.date_format(Factura.fecha, '%M').label('mes'),
            func.count(Factura.id).label('cantidad_operaciones')
        ).filter(
            Factura.fecha >= fecha_inicio
        ).group_by(
            extract('month', Factura.fecha)
        ).order_by(
            extract('year', Factura.fecha), extract('month', Factura.fecha)
        ).all()

        # Procesar los resultados para llenar las listas
        for resultado in resultados:
            nombres_meses.append(resultado.mes)
            cantidades_operaciones.append(resultado.cantidad_operaciones)

        # Devolver las listas como respuesta
        return {
            'meses': nombres_meses,
            'operaciones': cantidades_operaciones
        }
    except:  
        nombres_meses = []
        cantidades_operaciones = []  
        return {
            'meses': nombres_meses,
            'operaciones': cantidades_operaciones
        }
        
def get_ultimas_operaciones():
    try:
        sucursal = session['id_sucursal']
        resultado = db.session.execute(text("CALL ultimas_10_ventas(:sucursal)"), {'sucursal': sucursal})
    except Exception as e:
        print(f'error: {e}')
        resultado = []
    return resultado

def get_10_mas_vendidos():
    #obtiene los 10 articulos mas vendidos
    try:
        sucursal = session['id_sucursal']
        # Obtener la fecha de hoy
        hasta = date.today()
        # Calcular la fecha 6 meses atrás
        desde = hasta - timedelta(days=180)
        cantidad = 10
        det_arts = []
        vtas_arts = []
        sql = text("CALL mas_vendidos(:sucursal, :desde, :hasta, :cantidad)")
        params = {'sucursal': sucursal, 'desde': desde, 'hasta': hasta, 'cantidad': cantidad}
        resultados = db.session.execute(sql, params)
        resultados = resultados.fetchall()
        for resultado in resultados:
            det_arts.append(resultado.detalle)
            vtas_arts.append(resultado.cantidad)
        return {
            'det_arts': det_arts,
            'vta_arts': vtas_arts
        }    
    except Exception as e:
        print(f'error: {e}')
        det_arts = []
        vtas_arts = []
        return {
            'det_arts': det_arts,
            'vta_arts': vtas_arts
        }

def ventas_por_mes():
    # Obtener la fecha de hoy
    fecha_hoy = date.today()

    # Calcular la fecha 6 meses atrás
    fecha_inicio = fecha_hoy - timedelta(days=180)

    # Crear listas para los nombres de los meses y la cantidad de operaciones
    nombres_meses = []
    cantidades_operaciones = []
    try:
        # Realizar la consulta para obtener la cantidad de operaciones por mes
        db.session.execute(text("SET lc_time_names = 'es_ES'"))
        resultados = db.session.execute(text("CALL get_vta_desde_hasta(:desde, :hasta)"),
                         {'desde': fecha_inicio, 'hasta': fecha_hoy}).fetchall()
        # Procesar los resultados para llenar las listas
        for resultado in resultados:
            nombres_meses.append(resultado.mes)
            cantidades_operaciones.append(resultado.cantidad_operaciones)
        # Devolver las listas como respuesta
        return {
            'meses': nombres_meses,
            'operaciones': cantidades_operaciones
        }
    except Exception as e:  
        print('Error calculando ventas por mes:', str(e))
        nombres_meses = []
        cantidades_operaciones = []  
        return {
            'meses': nombres_meses,
            'operaciones': cantidades_operaciones
        }
        
def pagos_hoy():
    fecha = date.today()
    try:
        resultados = db.session.query(
                    func.sum(PagosFV.total).label('total_pago'),
                    PagosCobros.pagos_cobros
                    ).join(Factura, Factura.id == PagosFV.idfactura) \
                    .join(PagosCobros, PagosFV.idpago == PagosCobros.id) \
                    .filter(Factura.fecha == fecha) \
                    .group_by(PagosCobros.pagos_cobros).all()

        # Convertir el resultado a una lista de diccionarios
        tipo_pago = []
        total_pago = []
        
        for resultado in resultados:
            tipo_pago.append(resultado.pagos_cobros)
            total_pago.append(resultado.total_pago)

            # Devolver las listas como respuesta
        return {
            'tipo_pago': tipo_pago,
            'total_pago': total_pago
        }
    except Exception as e:  
        print('Error calculando pagos:', str(e))
        tipo_pago = []
        total_pago = []
        return {
            'tipo_pago': tipo_pago,
            'total_pago': total_pago
        }    

def get_factura(id):
    factura = db.session.query(
                Factura.id,
                Factura.fecha,
                Factura.total,
                Factura.iva,
                Factura.exento,
                Factura.impint,
                Factura.nro_comprobante,
                Factura.punto_vta,
                Factura.cae,
                Factura.cae_vto,
                Factura.fecha_emision,
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
            Item.cantidad,
            Item.precio_unitario,
            Item.precio_total,
            Articulo.codigo,
            Articulo.detalle) \
            .join(Articulo, Articulo.id == Item.idarticulo) \
            .filter(Item.idfactura == id)
    pagos = db.session.query(
            PagosFV.total,
            PagosCobros.pagos_cobros
            ).join(PagosCobros, PagosCobros.id == PagosFV.idpago
            ).filter(PagosFV.idfactura == id
            ).all()
    return factura[0], items, pagos

def get_vta_sucursales_data(desde, hasta):
    ventas = db.session.execute(text("CALL get_vta_sucursales(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
    ventas_list = []
    for venta in ventas:
        ventas_list.append({
            'sucursal': venta[0],
            'total': format_currency(venta[1]),
            'cantidad': venta[2],
            'tktProm': format_currency(venta[3])
        })
    return ventas_list    


def get_vta_vendedores_data(desde, hasta):
    ventas = db.session.execute(text("CALL get_vta_vendedores(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
    ventas_list = []
    for venta in ventas:
        ventas_list.append({
            'vendedor': venta[0],
            'total': format_currency(venta[1]),
            'cantidad': venta[2],
            'tktProm': format_currency(venta[3])
        })
    return ventas_list
