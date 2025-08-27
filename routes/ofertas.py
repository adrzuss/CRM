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
    
    print("Entrando a nueva_oferta")
    
    servicio = OfertaService()
    
    if request.method == 'POST':
        try:
            print('1')
            datos_oferta = {
                'nombre': request.form['nombre'],
                'tipo_descuento': TipoDescuento(request.form['tipo_descuento']),
                'valor_descuento': float(request.form['valor_descuento']),
                'cantidad_minima': float(request.form['cantidad_minima']),
                'multiplos': 'multiplos' in request.form,
                'fecha_inicio': datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d'),
                'fecha_fin': datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d')
            }
            print('2')
            tipo_oferta = request.form.get('tipo_oferta')
            print('3')
            if tipo_oferta == 'vinculada':
                print('4')
                articulo_origen = request.form.get('id_articulo_origen')
                articulo_destino = request.form.get('id_articulo_destino')
                servicio.crear_oferta_vinculada(datos_oferta, articulo_origen, articulo_destino)
                print('5')
            
            elif tipo_oferta == 'regla_seleccion':
                print('6')
                regla = ReglaSeleccion(request.form.get('regla_seleccion'))
                print('7')
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
                print('8')
                servicio.crear_oferta_regla_seleccion(datos_oferta, condiciones, regla)
                print('9')
            
            else:
                # Oferta normal
                print('10')
                # Obtener las listas de tipos y referencias
                tipos = request.form.getlist('tipo_condicion[]')
                referencias = request.form.getlist('referencia[]')
                print(f'12/1 - {referencias}')
                
                # Filtrar solo las condiciones válidas (con tipo y referencia)
                condiciones = [
                    {
                        'id_tipo_condicion': tipo,
                        'id_referencia': ref
                    }
                    for tipo, ref in zip(tipos, referencias)
                    if tipo and ref  # Solo incluir si ambos valores no están vacíos
                ]
                
                print(f'12/2 - {condiciones}')
                if not condiciones:
                    raise ValueError("Debe especificar al menos una condición válida")
                    
                servicio.crear_oferta(datos_oferta, condiciones)    
                print('13')

            flash('Oferta actualizada exitosamente', 'success')
            return redirect(url_for('ofertas.ofertas'))
            
        except Exception as e:
            flash(f'Error al actualizar la oferta: {str(e)}', 'error')
    
    # GET request
    resultado = servicio.obtener_oferta_por_id(id)
    if not resultado:
        oferta_=[]
        condiciones_= None
        vinculos_= None
        #flash('Oferta no encontrada', 'error')
        #return redirect(url_for('ofertas.ofertas'))
    else:
        oferta_=resultado['oferta']
        condiciones_=resultado['condiciones']
        vinculos_=resultado['vinculos']  
    
    print("Datos de la oferta obtenidos:")    
    print(oferta_, condiciones_, vinculos_)    
          
    return render_template(
        'nueva-oferta.html',
        oferta=oferta_,
        condiciones=condiciones_,
        vinculos=vinculos_,
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
    ofertas = OfertaService().obtener_ofertas_activas()
    return render_template('ofertas.html', ofertas= ofertas, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)


@bp_ofertas.route('/get_referencias/<int:tipo_condicion_id>')
@check_session
def get_referencias(tipo_condicion_id):
    servicio = OfertaService()
    referencias = servicio.obtener_referencias_por_tipo(tipo_condicion_id)
    return jsonify(referencias)

@bp_ofertas.route('/edit/<int:id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def edit(id):
    print("Entrando a edit_oferta")
    
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
            
            if tipo_oferta == 'vinculada':
                articulo_origen = request.form.get('id_articulo_origen')
                articulo_destino = request.form.get('id_articulo_destino')
                servicio.actualizar_oferta_vinculada(id, datos_oferta, articulo_origen, articulo_destino)
            
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
                servicio.actualizar_oferta_regla_seleccion(id, datos_oferta, condiciones, regla)
            
            else:
                # Oferta normal
                print('10')
                # Obtener las listas de tipos y referencias
                tipos = request.form.getlist('tipo_condicion[]')
                referencias = request.form.getlist('referencia[]')
                print(f'11 - Referencias: {referencias} - Condicones: {tipos}')
                
                # Filtrar solo las condiciones válidas (con tipo y referencia)
                condiciones = [
                    {
                        'id_tipo_condicion': tipo,
                        'id_referencia': ref
                    }
                    for tipo, ref in zip(tipos, referencias)
                    if tipo and ref  # Solo incluir si ambos valores no están vacíos
                ]
                
                print(f'12 - {condiciones}')
                if not condiciones:
                    raise ValueError("Debe especificar al menos una condición válida")
                    
                servicio.actualizar_oferta(id, datos_oferta, condiciones)
                print('13')
                

            flash('Oferta actualizada exitosamente', 'success')
            return redirect(url_for('ofertas.ofertas'))
            
        except Exception as e:
            flash(f'Error al actualizar la oferta: {str(e)}', 'error')
    
    # GET request
    resultado = servicio.obtener_oferta_por_id(id)
    if not resultado:
        oferta_=[]
        condiciones_=[]
        vinculos_=[],
        #flash('Oferta no encontrada', 'error')
        #return redirect(url_for('ofertas.ofertas'))
    else:
        oferta_=resultado['oferta']
        condiciones_=resultado['condiciones']
        vinculos_=resultado['vinculos']  
    
    print("Datos de la oferta obtenidos:")    
    print(f'Ofertas: {oferta_}')
    print(f'Condiciones: {condiciones_}')
    print(f'Vinculos: {vinculos_}')    
          
    return render_template(
        'nueva-oferta.html',
        oferta=oferta_,
        condiciones=condiciones_,
        vinculos=vinculos_,
        tipos_descuento=TipoDescuento,
        tipos_condiciones=servicio.obtener_tipos_condiciones(),
        reglas_seleccion=ReglaSeleccion,
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )


@bp_ofertas.route('/delete/<int:id>', methods=['POST'])
@check_session
@alertas_mensajes
def delete(id):
    pass
