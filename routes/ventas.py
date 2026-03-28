from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, session, g
from models.articulos import ListasPrecios, PedirEnVentas
from models.clientes import Clientes
from models.entidades_cred import EntidadesCred
from models.configs import PuntosVenta
from models.sessions import Usuarios
from models.sucursales import Sucursales
from services.ventas import get_factura, procesar_nueva_venta, get_vta_sucursales_data, get_vta_vendedores_data, procesar_nuevo_remito, \
                            ventas_desde_hasta, facturar_fe, generar_factura, procesar_nuevo_presupuesto, get_presupuesto, get_remito, \
                            generar_presupuesto, get_comprobantes_para_nc, get_items_comprobante_venta
from services.configs import getDatosSucEmpresa, getPosPrinter
from utils.db import db
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes
from utils.print_send_invoices import generar_factura_pdf, enviar_factura_por_email
from datetime import date
from sqlalchemy import text

from services.printer_service import get_printer_service, WindowsPrinterService, LinuxPrinterService

bp_ventas = Blueprint('ventas', __name__, template_folder='../templates/ventas', static_folder='../static')


@bp_ventas.route('/ventas', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ventas():
    if request.method == 'GET':
        desde = request.args.get('desde', date.today())
        hasta = request.args.get('hasta', date.today())
        facturas = ventas_desde_hasta(desde, hasta)
        return render_template('ventas.html', facturas=facturas, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        return redirect(url_for('ventas.ventas', desde=desde, hasta=hasta))

@bp_ventas.route('/get_punto_vta')
#@check_session
def get_punto_vta():
    try:
        if not ('idPuntoVenta' in session):
            punto_vta = None
            fac_electronica = False
            pos_printer = None
        else:    
            punto_vta = session['idPuntoVenta']
            session['posPrinter'], session['facElectronica'] = getPosPrinter(punto_vta)
            fac_electronica = session.get('facElectronica', False)
            pos_printer = session.get('posPrinter', None)
        #punto_vta = 1    
        return jsonify({'success': True, 'punto_vta': punto_vta, 'fac_electronica': fac_electronica, 'pos_printer': pos_printer})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp_ventas.route('/get_puntos_vta_sucursal')
@check_session
def get_puntos_vta_sucursal():
    try:
        session['posPrinter'] = None
        puntosVtaSucursal = db.session.query(PuntosVenta.id, 
                                            PuntosVenta.punto_vta, 
                                            PuntosVenta.fac_electronica).filter(PuntosVenta.idsucursal == session['id_sucursal']).all()
        return jsonify([{'id': pv.id, 'puntoVta': pv.punto_vta, 'facElectronica': 'Si' if pv.fac_electronica else 'No'} for pv in puntosVtaSucursal])
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp_ventas.route('/set_punto_vta', methods=['POST'])
@check_session
def set_punto_vta():
    try:
        # Obtener el ID del punto de venta desde la solicitud
        punto_vta_id = request.json.get('punto_vta_id')
        if not punto_vta_id:
            return jsonify({'success': False, 'message': 'ID de punto de venta no proporcionado'}), 400

        # Asignar el valor a la sesión
        session['idPuntoVenta'] = punto_vta_id
        puntoVta = PuntosVenta.query.get(punto_vta_id)
        session['posPrinter'] = puntoVta.pos_printer
        
        return jsonify({'success': True, 'message': 'Punto de venta asignado correctamente', 'posPrinter': puntoVta.pos_printer, 'facElectronica': puntoVta.fac_electronica})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al asignar el punto de venta: {str(e)}'}), 500
    
@bp_ventas.route('/nueva_venta', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nueva_venta():
    if request.method == 'POST':
        # DEBUG: Retorno inmediato para verificar que el código nuevo se ejecuta
        # return jsonify({'debug': True, 'message': 'Código actualizado OK - v2'}), 200
        try:
            nro_comprobante, id_factura = procesar_nueva_venta(request.form, session['id_sucursal'])
            # No usar flash aquí, ya que retornamos JSON y el mensaje se muestra con SweetAlert en el frontend
            return jsonify({
                'success': True,
                'message': f'Factura grabada exitosamente: {nro_comprobante}',
                'nro_comprobante': nro_comprobante,
                'id': id_factura 
            })
        except Exception as e:
            import traceback
            error_detalle = traceback.format_exc()
            print(f'Error al procesar venta: {error_detalle}')  # Log para el servidor
            return jsonify({
                'success': False,
                'message': f'Error al procesar la venta en servidor: {str(e)}',
                'error_detalle': error_detalle
            }), 500
    if request.method == 'GET':
        hoy = date.today()
        entidades = EntidadesCred.query.all()
        listas_precio = ListasPrecios.query.all()
        return render_template('nueva_venta.html', hoy=hoy, entidades=entidades, listas_precio=listas_precio, pedirEnVentas=PedirEnVentas, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_ventas.route('/nueva_nota_credito', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nueva_nota_credito():
    if request.method == 'POST':
        # DEBUG: Retorno inmediato para verificar que el código nuevo se ejecuta
        # return jsonify({'debug': True, 'message': 'Código actualizado OK - v2'}), 200
        try:
            nro_comprobante, id_factura = procesar_nueva_venta(request.form, session['id_sucursal'])
            # No usar flash aquí, ya que retornamos JSON y el mensaje se muestra con SweetAlert en el frontend
            return jsonify({
                'success': True,
                'message': f'Factura grabada exitosamente: {nro_comprobante}',
                'nro_comprobante': nro_comprobante,
                'id': id_factura 
            })
        except Exception as e:
            import traceback
            error_detalle = traceback.format_exc()
            print(f'Error al procesar nota de crédito: {error_detalle}')  # Log para el servidor
            return jsonify({
                'success': False,
                'message': f'Error al procesar la nota de crédito en servidor: {str(e)}',
                'error_detalle': error_detalle
            }), 500
    if request.method == 'GET':
        hoy = date.today()
        entidades = EntidadesCred.query.all()
        listas_precio = ListasPrecios.query.all()
        return render_template('nueva_ncredito.html', hoy=hoy, entidades=entidades, listas_precio=listas_precio, pedirEnVentas=PedirEnVentas, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)


@bp_ventas.route('/buscar_comprobantes_nc', methods=['POST'])
@check_session
def buscar_comprobantes_nc():
    """
    Endpoint para buscar comprobantes disponibles para generar nota de crédito.
    Recibe: fecha (date), nro_comprobante (string, opcional)
    Retorna: Lista de comprobantes encontrados
    """
    try:
        data = request.get_json()
        fecha = data.get('fecha')
        nro_comprobante = data.get('nro_comprobante', '')
        
        if not fecha:
            return jsonify({
                'success': False,
                'message': 'Debe proporcionar una fecha'
            }), 400
        
        # Buscar comprobantes usando la fecha como desde y hasta
        comprobantes = get_comprobantes_para_nc(fecha, fecha, nro_comprobante)
        
        return jsonify({
            'success': True,
            'comprobantes': comprobantes,
            'cantidad': len(comprobantes)
        })
    except Exception as e:
        import traceback
        error_detalle = traceback.format_exc()
        print(f'Error al buscar comprobantes para NC: {error_detalle}')
        return jsonify({
            'success': False,
            'message': f'Error al buscar comprobantes: {str(e)}'
        }), 500


@bp_ventas.route('/get_items_comprobante/<int:idcomprobante>', methods=['GET'])
@check_session
def get_items_comprobante(idcomprobante):
    """
    Endpoint para obtener los items de un comprobante de venta.
    Se usa para cargar los artículos cuando se selecciona un comprobante para nota de crédito.
    """
    try:
        items = get_items_comprobante_venta(idcomprobante)
        
        return jsonify({
            'success': True,
            'items': items,
            'cantidad': len(items)
        })
    except Exception as e:
        import traceback
        error_detalle = traceback.format_exc()
        print(f'Error al obtener items del comprobante: {error_detalle}')
        return jsonify({
            'success': False,
            'message': f'Error al obtener items: {str(e)}'
        }), 500

    
@bp_ventas.route('/ver_factura_vta/<id>') 
@check_session
@alertas_mensajes
def ver_factura_vta(id):
    factura, items, pagos = get_factura(id)
    return render_template('factura-vta.html', factura=factura, items=items, pagos=pagos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

#----------------- factura electronica ------------------#
#----------------- factura desde la ventana donde se ve el comprobante realizado -------------------------#
@bp_ventas.route('/facturar/<ptovta>/<idfactura>', methods=['GET', 'POST'])
def facturar(ptovta, idfactura):
    try:
        paso = 1
        print(f'Paso {paso}: Iniciando facturación electrónica para factura ID {idfactura} en punto de venta {ptovta}')
        response, statuscode = facturar_fe(ptovta, idfactura)  
        paso = 2
        print(f'Paso {paso}: Respuesta recibida del servicio de facturación electrónica para factura ID {idfactura}')
        data = response.get_json()
        if data.get('success') == True:
            paso = 3
            cae = data.get('result', {}).get('cae')
            nro_cbte = data.get('result', {}).get('nro_cbte')
            flash(f'Factura {nro_cbte} emitida correctamente. CAE: {cae}')
            paso = 4
            # Generar PDF
            return redirect(url_for('ventas.ver_factura_vta', id=idfactura))
        else:
            flash(f'Ocurrió un error al procesar la venta (1)-({paso}): {data.get("error")}. Status: {statuscode}', 'error')
            return redirect(url_for('ventas.ver_factura_vta', id=idfactura))
    except Exception as e:
        print(f'Error al generar factura electrónica: {e}')
        return redirect(url_for('ventas.ver_factura_vta', id=idfactura))

#----------------- factura desde la ventana de venta -------------------------#
@bp_ventas.route('/facturar_venta/<ptovta>/<idfactura>', methods=['GET', 'POST'])
def facturar_venta(ptovta, idfactura):
    try:
        paso = 1
        print(f'Paso {paso}: Iniciando facturación electrónica para factura ID {idfactura} en punto de venta {ptovta}')
        response, statuscode = facturar_fe(ptovta, idfactura)  
        paso = 2
        print(f'Paso {paso}: Respuesta recibida del servicio de facturación electrónica para factura ID {idfactura}')
        data = response.get_json()
        if data.get('success') == True:
            paso = 3
            cae = data.get('result', {}).get('cae')
            nro_cbte = data.get('result', {}).get('nro_cbte')
            paso = 4
            # Retornar JSON - el mensaje se muestra con SweetAlert en el frontend
            return {'success': True, 'message': f'Factura {nro_cbte} emitida correctamente. CAE: {cae}', 'nro_comprobante': nro_cbte, 'cae': cae}
        else:
            return {'success': False, 'message': f'Ocurrió un error al procesar la venta (1)-({paso}): {data.get("error")}. Status: {statuscode}'}
    except Exception as e:
        print(f'Error al generar factura electrónica: {e}')
        return {'success': False, 'message': f'Error al generar factura electrónica: {e}'}


#----------------- fin factura electronica ------------------#

#----------------- imprimir factura  ------------------#

@bp_ventas.route('/imprimir_factura_vta/<id>') 
@check_session
def imprimir_factura_vta(id):
    return generar_factura(id)

@bp_ventas.route('/imprimir_factura_vta2/<id>') 
@check_session
@alertas_mensajes
def imprimir_factura_vta2(id):
    return render_template('factura-print.html', factura_id=id, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)


@bp_ventas.route('/api/facturas/<int:factura_id>', methods=['GET'])
def obtener_factura(factura_id):
    try:
        # Obtener datos de la factura de tu base de datos
        
        factura, items, pagos = get_factura(factura_id)  
        empresa = getDatosSucEmpresa()  # Implementa esta función
        
        # Obtener datos del cliente para el QR
        cliente = Clientes.query.get(factura.idcliente)
        
        laFactura = {'id': factura.id,
                   'nro_comprobante': factura.nro_comprobante,
                   'fecha': factura.fecha.strftime('%Y-%m-%d'),
                   'cliente': factura.idcliente,
                   'cliente_nombre': cliente.nombre if cliente else '',
                   'cliente_documento': cliente.documento if cliente else '',
                   'cliente_tipo_doc': cliente.id_tipo_doc if cliente else 99,
                   'tipo_comprobante': factura.tipo_comprobante,
                   'letra_comprobante': factura.letra_comprobante,
                   'id_tipo_comprobante': factura.idtipocomprobante,
                   'total': factura.total,
                   'bonificacion': factura.bonificacion,
                   'iva': factura.iva,
                   'exento': factura.exento,
                   'impint': factura.impint,
                   'cae': factura.cae,
                   'cae_vto': factura.cae_vto.strftime('%Y-%m-%d') if factura.cae_vto else '',
                   'punto_vta': factura.punto_vta                   
                   }
        losItems = []
        for item in items:
            losItems.append({'id': item.id,
                             'codigo': item.codigo,
                             'descripcion': item.detalle,
                             'cantidad': item.cantidad,
                             'precio_unitario': item.precio_unitario,
                             'precio_total': item.precio_total,
                             'iva': item.iva,
                             'exento': item.exento,
                             'impint': item.impint,
                             'bonificacion': item.bonificacion
                             })
        
        return jsonify({
            'success': True,
            'factura': laFactura,
            'items': losItems,
            'empresa': empresa
        })
    except Exception as e:
        print(f'Error al obtener la factura: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
#----------------- fin imprimir factura  ------------------#
        

@bp_ventas.route('/enivar_factura_vta_mail/<id>/<idcliente>') 
@check_session
def enivar_factura_vta_mail(id, idcliente):
    generar_factura_pdf(id, footer_text="")
    cliente = Clientes.query.get(idcliente)
    if cliente.email != None:
        pdf_path = f"factura-{id}.pdf"
        enviar_factura_por_email(cliente.email, pdf_path)
    return redirect(url_for('ventas.ver_factura_vta', id=id))

@bp_ventas.route('/ventasArticulos', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ventasArticulos():
    if request.method == 'GET':
        if 'desde' in request.args:
            desde = request.args.get('desde')
        else:
            desde = date.today()   
        if 'hasta' in request.args:    
            hasta = request.args.get('hasta')
        else:
            hasta = date.today()    
        if 'con_detalles' in request.args:
            con_detalles = request.args.get('con_detalles', 'false').lower() == 'true'
        else:
            con_detalles = False    
        if 'con_colores' in request.args:    
            con_colores = request.args.get('con_colores', 'false').lower() == 'true'
        else:
            con_colores = False    
        
        articulos = db.session.execute(text("CALL venta_articulos(:desde, :hasta, :con_detalles, :con_colores)"),
                         {'desde': desde, 'hasta': hasta, 'con_detalles': con_detalles, 'con_colores': con_colores}).fetchall()
        return render_template('ventas-articulos.html', articulos=articulos, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        con_detalles = 'con_talle' in request.form
        con_colores = 'con_colores' in request.form
        return redirect(url_for('ventas.ventasArticulos', desde=desde, hasta=hasta, con_detalles=con_detalles, con_colores=con_colores))    

@bp_ventas.route('/ventasClientes', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ventasClientes():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
        ventas = []
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        ventas = db.session.execute(text("CALL venta_clientes(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
    return render_template('ventas-clientes.html', ventas=ventas, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_ventas.route('/ventasUnCliente', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ventasUnCliente():
    if request.method == 'GET':
        desde = request.args.get('desde', date.today())
        hasta = request.args.get('hasta', date.today())
        id = request.args.get('idcliente', None)
        if id:
            
            cliente = Clientes.query.get(id)
            ventas = db.session.execute(text("CALL ventas_un_cliente(:idcliente, :desde, :hasta)"),
                            {'idcliente': id, 'desde': desde, 'hasta': hasta}).fetchall()
            articulos = db.session.execute(text("CALL ventas_art_un_cliente(:idcliente, :desde, :hasta)"),
                            {'idcliente': id, 'desde': desde, 'hasta': hasta}).fetchall()
        else:
            cliente = []
            ventas = []
            articulos = []    
        return render_template('ventas-un-cliente.html', cliente=cliente, ventas=ventas, articulos=articulos, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    else:
        id = request.form['idcliente']
        desde = request.form['desde']
        hasta = request.form['hasta']
        return redirect(url_for('ventas.ventasUnCliente', idcliente=id, desde=desde, hasta=hasta))
        
    

@bp_ventas.route('/ventasVendedores', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ventasVendedores():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
        ventas = []
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        ventas = db.session.execute(text("CALL venta_vendedores(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
    return render_template('ventas-vendedores.html', ventas=ventas, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_ventas.route('/ventasTipoPago', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ventasTipoPago():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
        porVentas = []
        porListaPrecio = []
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        porVentas = db.session.execute(text("CALL ventas_formas_pago(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
        porListaPrecio = db.session.execute(text("CALL ventas_listas_precios(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
        
    return render_template('ventas-tipo-pagos.html', porVentas=porVentas, porListaPrecio=porListaPrecio, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_ventas.route('/ventasUnVendedor', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ventasUnVendedor():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
        vendedor = {}
        ventas = []
        articulos = []
    else:
        id = request.form['idVendedor']
        desde = request.form['fechaDesde']
        hasta = request.form['fechaHasta']
        
        vendedor = Usuarios.query.get(id)
        ventas = db.session.execute(text("CALL ventas_un_vendedor(:idvendedor, :desde, :hasta)"),
                         {'idvendedor': id, 'desde': desde, 'hasta': hasta}).fetchall()
        articulos = db.session.execute(text("CALL ventas_art_un_vendedor(:idvendedor, :desde, :hasta)"),
                         {'idvendedor': id, 'desde': desde, 'hasta': hasta}).fetchall()
    return render_template('ventas-un-vendedor.html', vendedor=vendedor, ventas=ventas, articulos=articulos, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)


@bp_ventas.route('/get_vta_sucursales/<desde>/<hasta>')
@check_session
def get_vta_sucursales(desde, hasta):
    ventas = get_vta_sucursales_data(desde, hasta)
    return jsonify(success=True, ventas=ventas) 

        
@bp_ventas.route('/get_vta_vendedores/<desde>/<hasta>')
@check_session
def get_vta_vendedores(desde, hasta):
    ventas = get_vta_vendedores_data(desde, hasta)
    return jsonify(success=True, ventas=ventas) 

#----------------------- Remitos -----------------------#

@bp_ventas.route('/nuevo_remito', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nuevo_remito():
    if request.method == 'POST':
        try:
            nro_comprobante = procesar_nuevo_remito(request.form, session['id_sucursal'])
            flash(f'Remito grabado exitosamente: {nro_comprobante}')
            return redirect(url_for('ventas.nuevo_remito'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar el remito: {e}', 'error')
            return redirect(url_for('ventas.nuevo_remito'))
    hoy = date.today()
    listas_precio = ListasPrecios.query.all()
    return render_template('nuevo_remito.html', hoy=hoy, listas_precio=listas_precio, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_ventas.route('/remitos_vta', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def remitos_vta():
    if request.method == 'GET':
        desde = request.args.get('desde', date.today())
        hasta = request.args.get('hasta', date.today())
        remitos = []
        remitos = db.session.execute(text("CALL get_remitos(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
        return render_template('remitos.html', remitos=remitos, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        return redirect(url_for('ventas.remitos_vta', desde=desde, hasta=hasta))

@bp_ventas.route('/ver_remito/<id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ver_remito(id):
    remito, items, pagos = get_factura(id)
    if not remito:
        flash('Remito no encontrado', 'error')
        return redirect(url_for('ventas.remitos_vta'))
    return render_template('remito-vta.html', remito=remito, items=items, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_ventas.route('/facturar_remito/<id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def facturar_remito(id):
    if request.method == 'POST':
        try:
            nro_comprobante = procesar_nueva_venta(request.form, session['id_sucursal'])
            flash(f'Factura grabada exitosamente: {nro_comprobante}')
            return redirect(url_for('ventas.nueva_venta'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar la venta (2): {e}', 'error')
            return redirect(url_for('ventas.nueva_venta'))
    else:    
        id_remito = id
        remito = None
        articulos_remito = []
        if id_remito:
            remito, articulos_remito = get_remito(id_remito)
        hoy = date.today()
        entidades = EntidadesCred.query.all()
        listas_precio = ListasPrecios.query.all()   
        return render_template('nueva_venta.html', hoy=hoy, entidades=entidades, listas_precio=listas_precio, remito=remito, articulos_remito=articulos_remito, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
#----------------------- Fin Remitos ------------------------#

#----------------------- Presupuestos -----------------------#
@bp_ventas.route('/nuevo_presupuesto', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nuevo_presupuesto():
    if request.method == 'POST':
        try:
            nro_comprobante = procesar_nuevo_presupuesto(request.form, session['id_sucursal'])
            flash(f'Presupuesto grabado exitosamente: {nro_comprobante}')
            return redirect(url_for('ventas.nuevo_presupuesto'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar el presupuesto (2): {e}', 'error')
            return redirect(url_for('ventas.nuevo_presupuesto'))
    hoy = date.today()
    listas_precio = ListasPrecios.query.all()
    return render_template('nuevo_presupuesto.html', hoy=hoy, listas_precio=listas_precio, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)


@bp_ventas.route('/presupuestos', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def presupuestos():
    if request.method == 'GET':
        desde = request.args.get('desde', date.today())
        hasta = request.args.get('hasta', date.today())
        presupuestos = []
        presupuestos = db.session.execute(text("CALL get_presupuestos(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
        return render_template('presupuestos.html', presupuestos=presupuestos, desde=desde, hasta=hasta, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        return redirect(url_for('ventas.presupuestos', desde=desde, hasta=hasta))
    

@bp_ventas.route('/ver_presupuesto/<id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ver_presupuesto(id):
    presupuesto, itemsP = get_presupuesto(id)
    if not presupuesto:
        flash('Presupuesto no encontrado', 'error')
        return redirect(url_for('ventas.presupuestos'))
    return render_template('presupuesto.html', presupuesto=presupuesto, itemsP=itemsP, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_ventas.route('/facturar_presupuesto/<id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def facturar_presupuesto(id):
    if request.method == 'POST':
        try:
            nro_comprobante = procesar_nueva_venta(request.form, session['id_sucursal'])
            flash(f'Factura grabada exitosamente: {nro_comprobante}')
            return redirect(url_for('ventas.nueva_venta'))
        except Exception as e:
            flash(f'Ocurrió un error al procesar la venta (2): {e}', 'error')
            return redirect(url_for('ventas.nueva_venta'))
    else:    
        id_presupuesto = id
        presupuesto = None
        articulos_presupuesto = []
        if id_presupuesto:
            presupuesto, articulos_presupuesto = get_presupuesto(id_presupuesto)
        hoy = date.today()
        entidades = EntidadesCred.query.all()
        listas_precio = ListasPrecios.query.all()   
        return render_template('nueva_venta.html', hoy=hoy, entidades=entidades, listas_precio=listas_precio, presupuesto=presupuesto, articulos_presupuesto=articulos_presupuesto, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_ventas.route('/imprimir_presupuesto/<id>') 
@check_session
def imprimir_presupuesto(id):
    return generar_presupuesto(id)
    
#------------- impresion de comprobantes -------------#
                   
@bp_ventas.route('/imprimir_factura_vta_pos/<id>')
@check_session
def imprimir_factura_vta_pos(id):
    try:
        
        factura, items, pagos = get_factura(id)
        empresa = getDatosSucEmpresa()
        posPrinterName = getPosPrinter(session['idPuntoVenta'])
        printer_service = get_printer_service()
        # "POS Printer 203DPI Series"
        if isinstance(printer_service, WindowsPrinterService):
            printer_service.printer_name = posPrinterName 
        elif isinstance(printer_service, LinuxPrinterService):
            printer_service.printer_name = posPrinterName
        else:
            printer_service.vendor_id = 0x0483
            printer_service.product_id = 0x5740
        
        printer_service.print_invoice(factura, items, empresa)
        
        return jsonify({
            'success': True,
            'message': 'Factura impresa correctamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al imprimir: {str(e)}'
        }), 500
        
@bp_ventas.route('/list_printers')
@check_session
def list_printers():
    try:
        printer_service = get_printer_service()
        
        result = printer_service.list_printers()
        if result['success']:
            for printer in result['printers']:
                print(printer)
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f'Error listando impresoras: {e}')        

@bp_ventas.route('/ivaVentas', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ivaVentas():
    sucursales = Sucursales.query.all()
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
        iva_ventas = []
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
        iva_ventas = db.session.execute(text("CALL iva_ventas(:desde, :hasta, :sucursal)"),
                         {'desde': desde, 'hasta': hasta, 'sucursal': session['id_sucursal']}).fetchall()
    return render_template('iva-ventas.html', iva_ventas=iva_ventas, desde=desde, hasta=hasta, sucursales=sucursales, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)