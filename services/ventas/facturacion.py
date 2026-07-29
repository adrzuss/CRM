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


def get_certificado_clave_fe(id_punto_vta):
    try:
        punto_vta = db.session.get(PuntosVenta, id_punto_vta)
        if punto_vta.fac_electronica == True:
            #cert_file = os.path.join(os.getcwd(), Config.FE_FILES_FOLDER, punto_vta.certificado_p12)
            cert_file =  Config.FE_FILES_FOLDER + '/' + punto_vta.certificado_p12
            if not os.path.exists(cert_file):
                msg = f'El certificado {punto_vta.certificado_p12} no existe'
                return None, None, msg
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
        puntoVta = db.session.get(PuntosVenta, idPuntoVta)
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
            nro = puntoVta.ultima_deb_c
            puntoVta.ultima_deb_c += 1
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
        db.session.rollback()
        print(f"Error al obtener el número de comprobante: {e}")
        return "0000-00000000"
    

def facturar_fe(ptovta, idfactura):
    #ptoVta = PuntosVenta.query.get(ptovta)
    #print('0- Empezamos facturar_fe')
    if ptovta: #aca
        #AFIP_CERT_PATH = f'cert_fe/{ptoVta.certificado_p12}'
        #AFIP_CERT_PASSWORD = ptoVta.clave_certificado
        AFIP_CERT_PATH, AFIP_CERT_PASSWORD, msg = get_certificado_clave_fe(ptovta)
    if AFIP_CERT_PATH == None:
        return jsonify({'success': False, 'error': msg}), 400
    try:
        # 1. Obtener datos de la factura desde la DB
        paso = 1
        #print('1- Obtener datos de la factura desde la DB')
        result_proxy = db.session.execute(text("CALL get_datosfac_fe(:id)"), {'id': idfactura})
        result = result_proxy.fetchall()
        result_proxy.close
        paso = 2
        #print('2- Obtener datos de la factura desde la DB')
        if not result:
            return jsonify({"error": "Factura no encontrada"}), 404
        # 2. Parsear el JSON
        
        #print('2- Parsear el JSON')
        paso = 3
        factura_db = json.loads(result[0][0])  # Asume que el SP devuelve JSON como cadena
        # 3. Mapear a la estructura esperada por Facturador
        #print('------------------------------------------------------')
        #print('3- Mapear a la estructura esperada por Facturador')
        #print('------------------------------------------------------') 
        #print(f'Datos factura_db: {factura_db}')
        #print(f'Datos items: {factura_db["items"]}')
        #print('------------------------------------------------------')
        paso = 4
        datos_factura = {
            "cliente": {
                "tipo_doc": factura_db["cliente"]["tipo_doc"],
                "nro_doc": factura_db["cliente"]["nro_doc"],
                "tipo_iva": factura_db["cliente"]["tipo_iva"],
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
        paso = 5
        if not datos_factura["items"]:
            return jsonify({"error": "La factura no tiene items"}), 400
        # Crear facturador
        print('4- Crear facturador')
        facturador = Facturador({
            'cert_path': AFIP_CERT_PATH,
            'cert_password': AFIP_CERT_PASSWORD,
            'punto_venta': datos_factura["punto_venta"]
        })
        paso = 6
        #print('5- Emitir factura')
        # Emitir factura
        resultado = facturador.emitir_factura(
            cliente=datos_factura["cliente"],
            items=datos_factura["items"],
            tipo_comprobante=datos_factura["tipo_comprobante"],
            punto_venta=datos_factura["punto_venta"])
        
        # 6. Actualizar la factura en DB con el CAE
        paso = 7
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
            #print('7- Actualizado')
            return jsonify({
                'success': True,
                'result': resultado
            }), 200
        except Exception as e:  
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e) + '-1-'
            }), 500        
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e) + f'- Paso: {paso}-'
        }), 500
        

def generar_factura(id_factura):
    # Simulación de datos (reemplazar con consulta a la BD)
    config = db.session.query(
                            Configuracion.nombre_fantasia,
                            Configuracion.documento,
                            Configuracion.direccion,
                            Configuracion.localidad,                            
                            Configuracion.provincia,
                            TipoIva.descripcion.label('condicion_iva'),
                            ).join(TipoIva, TipoIva.id == Configuracion.tipo_iva) \
                            .first()
    cabecera = db.session.query(
                            Factura.fecha,
                            Factura.nro_comprobante,
                            Factura.punto_vta,
                            Factura.total,
                            Factura.iva,
                            Factura.exento, 
                            Factura.impint,
                            Factura.cae,
                            Factura.cae_vto,
                            Clientes.nombre,
                            Clientes.documento,
                            Clientes.direccion,
                            Localidades.localidad.label('localidad'),
                            Provincias.provincia.label('provincia'),
                            TipoIva.descripcion.label('condicion_iva'),
                            TipoComprobantes.id_afip.label('tipo_comprobante'),
                            TipoComprobantes.letra.label('letra_comprobante')) \
                            .join(Clientes, Clientes.id == Factura.idcliente) \
                            .join(TipoIva, TipoIva.id == Clientes.id_tipo_iva) \
                            .join(TipoComprobantes, TipoComprobantes.id == Factura.idtipocomprobante) \
                            .outerjoin(Localidades, Localidades.id == Clientes.idlocalidad) \
                            .outerjoin(Provincias, Provincias.id == Clientes.idprovincia) \
                            .filter(Factura.id == id_factura) \
                            .first()        
                            
    
    datos_factura = {
        "tipo_comprobante": cabecera.tipo_comprobante,
        "letra_comprobante": cabecera.letra_comprobante,
        "emisor_nombre": config.nombre_fantasia,
        "emisor_cuit": config.documento,
        "emisor_condicion_iva": config.condicion_iva,
        "emisor_domicilio": f"{config.direccion} - {config.localidad}, {config.provincia}",
        "receptor_nombre": cabecera.nombre,
        "receptor_cuit": cabecera.documento,
        "fecha_emision": cabecera.fecha.strftime('%d/%m/%Y'),
        "periodo_desde": cabecera.fecha.strftime('%d/%m/%Y'),
        "periodo_hasta": cabecera.fecha.strftime('%d/%m/%Y'),
        "vto_pago": cabecera.fecha.strftime('%d/%m/%Y'),
        "condicion_venta": 'otra',
        "nro_comprobante": cabecera.nro_comprobante, 
        "punto_venta": cabecera.punto_vta,
        "emisor_localidad": cabecera.localidad,
        "emisor_provincia": cabecera.provincia,
        "receptor_condicion_iva": cabecera.condicion_iva,
        "receptor_domicilio": f"{cabecera.direccion} - {cabecera.localidad}, {cabecera.provincia}",
        "subtotal": round(cabecera.total - cabecera.iva - cabecera.exento - cabecera.impint, 2),
        "total":  round(cabecera.total, 2),
        "cae": cabecera.cae,
        "vencimiento_cae": cabecera.cae_vto
    }
    
    items_fac = db.session.query(
                            Item.cantidad,
                            Item.precio_unitario,
                            Item.precio_total,
                            Item.iva,
                            Item.exento,
                            Item.impint,
                            Articulo.codigo,
                            Articulo.detalle) \
                            .join(Articulo, Articulo.id == Item.idarticulo) \
                            .filter(Item.idfactura == id_factura) \
                            .all()
    items = []                        
    for item in items_fac:
        items.append({"codigo": item.codigo,
                      "descripcion": item.detalle,
                      "cantidad": round(item.cantidad, 2),
                      "unidad_medida": "unidad",
                      "precio_unitario": round(item.precio_unitario, 2),
                      "subtotal": round(item.precio_total - item.iva - item.exento - item.impint, 2)})                            
    
    with tempfile.TemporaryDirectory() as tempdir:
        nombrePDF = f"Factura-{datos_factura['letra_comprobante']}-{datos_factura['nro_comprobante']}.pdf"
        pdf_path = os.path.join(tempdir, nombrePDF)
        generar_factura_pdf(pdf_path, datos_factura, items)
        # ✅ — Enviamos el archivo
        with open(pdf_path, 'rb') as f:
            response = Response(f.read(), mimetype='application/pdf')
            response.headers['Content-Disposition'] = f'attachment; filename={nombrePDF}'
            return response
