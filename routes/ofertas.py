from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, current_app, session
from flask import g

from utils.utils import check_session, convertir_decimal
from utils.msg_alertas import alertas_mensajes
from services.ofertas import OfertaService
from models.ofertas import TipoDescuento, ReglaSeleccion
from datetime import datetime
from decimal import Decimal

bp_ofertas = Blueprint('ofertas', __name__, template_folder='../templates/ofertas')

@bp_ofertas.route('/nueva_oferta', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def nueva_oferta():
    servicio = OfertaService()
    
    if request.method == 'POST':
        try:
            datos_oferta = {
                'nombre': request.form['nombre'],
                'tipo_descuento': TipoDescuento(request.form['tipo_descuento']),
                'valor_descuento': float(request.form['valor_descuento']),
                'cantidad_minima': float(request.form['cantidad_minima']),
                'multiplos': 'multiplos' in request.form,
                'fecha_inicio': datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d'),
                'fecha_fin': datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d')
            }

            tipo_oferta = request.form.get('tipo_oferta')
            print(f'Tipo de oferta: {tipo_oferta}')
            if tipo_oferta == 'vinculada':
                articulo_origen = request.form.get('articulo_origen')
                articulo_destino = request.form.get('articulo_destino')
                servicio.crear_oferta_vinculada(datos_oferta, articulo_origen, articulo_destino)
            
            elif tipo_oferta == 'regla_seleccion':
                regla = ReglaSeleccion(request.form.get('regla_seleccion'))
                condiciones = [
                    {
                        'id_tipo_condicion': tipo,
                        'id_referencia': ref
                    }
                    for tipo, ref in zip(
                        request.form.getlist('tipo_condicion[]'),
                        request.form.getlist('referencia[]')
                    )
                ]
                servicio.crear_oferta_regla_seleccion(datos_oferta, condiciones, regla)
            
            else:
                # Oferta normal
                condiciones = [
                    {
                        'id_tipo_condicion': tipo,
                        'id_referencia': ref
                    }
                    for tipo, ref in zip(
                        request.form.getlist('tipo_condicion[]'),
                        request.form.getlist('referencia[]')
                    )
                ]
                print('oferta normal')
                servicio.crear_oferta(datos_oferta, condiciones)

            flash('Oferta creada exitosamente', 'success')
            return redirect(url_for('ofertas.ofertas'))
            
        except Exception as e:
            flash(f'Error al crear la oferta: {str(e)}', 'error')
            
    return render_template(
        'nueva-oferta.html',
        tipos_descuento=TipoDescuento,
        tipos_condiciones=servicio.obtener_tipos_condiciones(),
        reglas_seleccion=ReglaSeleccion,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@bp_ofertas.route('/ofertas')
@check_session
@alertas_mensajes
def ofertas():
    return render_template('ofertas.html', alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)


@bp_ofertas.route('/get_referencias/<int:tipo_condicion_id>')
@check_session
def get_referencias(tipo_condicion_id):
    servicio = OfertaService()
    referencias = servicio.obtener_referencias_por_tipo(tipo_condicion_id)
    return jsonify(referencias)