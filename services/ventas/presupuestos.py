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


#----------------- presupuestos ------------------#
def procesar_nuevo_presupuesto(form, id_sucursal):
    try:
        idcliente = form['idcliente']
        fecha = form['fecha']
        validez = form['validez']
        idlista = form['idlista']
        id_tipo_comprobante = form['id_tipo_comprobante']
        
        #Obtener nuemero de comprobante
        nro_comprobante = getNroComprobante(id_tipo_comprobante)
        # Crear la factura
        nuevo_presupuesto = Presupuesto(
            idcliente=idcliente,
            idlista=idlista,
            fecha=fecha,
            validez=validez,
            total=0,  # Se calculará más adelante
            id_tipo_comprobante=id_tipo_comprobante,
            idsucursal=id_sucursal,
            idusuario=session['user_id'],
            nro_comprobante=nro_comprobante,
            punto_vta=session['idPuntoVenta'],
            estado='Pendiente'  # Estado inicial del presupuesto
        )
        db.session.add(nuevo_presupuesto)
        db.session.flush()
        idpresupuesto = nuevo_presupuesto.id

        # Procesar los items
        total = 0
        total = procesar_itemsP(form, idpresupuesto, id_sucursal)
        nuevo_presupuesto.total = total
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Error grabando presupuesto: {e}")
    return nro_comprobante
    

def procesar_itemsP(form, idpresupuesto, id_sucursal):
    total = Decimal(0)
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
                    articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
                    
                    #precios = precio(precioUnit, articulo.impint, articulo.exento, Decimal(0), Decimal(0), Decimal(iva.alicuota), Decimal(ingbto.alicuota))
                    #precio = Precio.query.filter_by(idarticulo=articulo.id, idlista=idlista).first()
                    #precio_unitario = precio.precio if precio else Decimal(0)
                    precio_total = precioUnit * cantidad
                    
                    # Obtener color y detalle si están presentes
                    id_color = form.get(f'items[{index}][id_color]')
                    id_detalle = form.get(f'items[{index}][id_detalle]')
                    
                    # Convertir a int si tienen valor, sino None
                    id_color = int(id_color) if id_color and id_color != '' else None
                    id_detalle = int(id_detalle) if id_detalle and id_detalle != '' else None
                    
                    nuevo_item = ItemP(
                        idpresupuesto=idpresupuesto,
                        id=index,
                        idarticulo=articulo.id,
                        cantidad=cantidad,
                        precio_unitario=precioUnit,
                        precio_total=precio_total,
                        id_color=id_color,
                        id_detalle=id_detalle
                    )
                    db.session.add(nuevo_item)
                    total += precio_total
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error procesando items: {e}")            
    return total


def get_presupuesto(id):
    factura = db.session.query(
                Presupuesto.id,
                Presupuesto.fecha,
                Presupuesto.validez,
                Presupuesto.total,
                Presupuesto.nro_comprobante,
                Presupuesto.punto_vta,
                Clientes.id.label('idcliente'),
                Clientes.nombre,
                Clientes.direccion,
                ListasPrecios.nombre.label('lista'),
                TipoComprobantes.nombre.label('tipo_comprobante')) \
            .join(Clientes, Clientes.id == Presupuesto.idcliente) \
            .outerjoin(ListasPrecios, ListasPrecios.id == Presupuesto.idlista) \
            .join(TipoComprobantes, TipoComprobantes.id == Presupuesto.idtipocomprobante) \
            .filter(Presupuesto.id == id).all()
   #Factura.query.get(id)
    items = db.session.query(
            ItemP.id,
            ItemP.idarticulo,
            ItemP.cantidad,
            ItemP.precio_unitario,
            ItemP.precio_total,
            Articulo.codigo,
            Articulo.detalle) \
            .join(Articulo, Articulo.id == ItemP.idarticulo) \
            .filter(ItemP.idpresupuesto == id)
    return factura[0], items


def generar_presupuesto(id_presupuesto):
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
                            Presupuesto.fecha,
                            Presupuesto.nro_comprobante,
                            Presupuesto.punto_vta,
                            Presupuesto.total,
                            Clientes.nombre,
                            Clientes.documento,
                            Clientes.direccion,
                            Clientes.localidad,
                            Clientes.provincia,
                            TipoIva.descripcion.label('condicion_iva'),
                            TipoComprobantes.id_afip.label('tipo_comprobante'),
                            TipoComprobantes.letra.label('letra_comprobante')) \
                            .join(Clientes, Clientes.id == Presupuesto.idcliente) \
                            .join(TipoIva, TipoIva.id == Clientes.id_tipo_iva) \
                            .join(TipoComprobantes, TipoComprobantes.id == Presupuesto.idtipocomprobante) \
                            .filter(Presupuesto.id == id_presupuesto) \
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
        "condicion_venta": 'Presupuesto',
        "nro_comprobante": cabecera.nro_comprobante, 
        "punto_venta": cabecera.punto_vta,
        "emisor_localidad": cabecera.localidad,
        "emisor_provincia": cabecera.provincia,
        "receptor_condicion_iva": cabecera.condicion_iva,
        "receptor_domicilio": f"{cabecera.direccion} - {cabecera.localidad}, {cabecera.provincia}",
        "subtotal": round(cabecera.total, 2),
        "total":  round(cabecera.total, 2),
        "cae": '',
        "vencimiento_cae": ''
    }
    
    items_fac = db.session.query(
                            ItemP.cantidad,
                            ItemP.precio_unitario,
                            ItemP.precio_total,
                            Articulo.codigo,
                            Articulo.detalle) \
                            .join(Articulo, Articulo.id == ItemP.idarticulo) \
                            .filter(ItemP.idpresupuesto == id_presupuesto) \
                            .all()
    items = []                        
    for item in items_fac:
        items.append({"codigo": item.codigo,
                      "descripcion": item.detalle,
                      "cantidad": round(item.cantidad, 2),
                      "unidad_medida": "unidad",
                      "precio_unitario": round(item.precio_unitario, 2),
                      "subtotal": round(item.precio_total, 2)})                            
  
    # Generar el PDF
    #archivo = Config.INVOICES_FOLDER + f"/factura_{datos_factura['tipo']}_{datos_factura['punto_venta']}_{datos_factura['nro_comprobante']}.pdf"
    #print(archivo)
    
    with tempfile.TemporaryDirectory() as tempdir:
        nombrePDF = f"Presupuesto-{datos_factura['letra_comprobante']}-{datos_factura['nro_comprobante']}.pdf"
        pdf_path = os.path.join(tempdir, nombrePDF)
        generar_factura_pdf(pdf_path, datos_factura, items)
        # ✅ — Enviamos el archivo
        with open(pdf_path, 'rb') as f:
            response = Response(f.read(), mimetype='application/pdf')
            response.headers['Content-Disposition'] = f'attachment; filename={nombrePDF}'
            return response

#----------------- fin presupuestos ------------------#
