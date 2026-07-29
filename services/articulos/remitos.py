from flask import session, flash, redirect, request, current_app, jsonify
from werkzeug.utils import secure_filename
import os
import json
from models.articulos import Articulo, Marca, Stock, Precio, Rubro, ArticuloCompuesto, Balance, ItemBalance, CambioPrecios, CambioPreciosItem, \
                             RemitoSucursales, ItemRemitoSucs, ProvByArt, Colores, DetallesArticulos, ArticulosColores, ArticulosDetalles
from models.sucursales import Sucursales
from utils.config import allowed_file
from sqlalchemy import func, and_, case, update, insert, text, desc
from sqlalchemy.exc import SQLAlchemyError
from utils.db import db
from datetime import datetime, date
from decimal import Decimal


#----------------------- remitos de mercaderia a sucursales    

def procesar_remito_a_sucursal(form):
    """
    Crea un nuevo remito en estado PENDIENTE.
    Actualiza en_transito_salida en sucursal origen y en_transito_entrada en sucursal destino.
    """
    idsucursal = session['id_sucursal']
    iddestino = form['iddestino']
    fecha = form['fecha']
                
    nuevo_remito = RemitoSucursales(idsucursal=idsucursal, iddestino=iddestino, fecha=fecha, idusuario=session['user_id'])
    db.session.add(nuevo_remito)
    db.session.flush()
    idremito = nuevo_remito.id
        
    items = form  # Obtener todo el formulario
    for key, value in items.items():
        if key.startswith('items') and key.endswith('[codigo]'):
            index = key.split('[')[1].split(']')[0]
            codigo = value
            cantidad = Decimal(request.form[f'items[{index}][cantidad]'])
            articulo = db.session.query(Articulo.id, Articulo.costo).filter(Articulo.codigo == codigo).first()
            # Obtener color y detalle si están presentes
            id_color = items.get(f'items[{index}][id_color]')
            id_detalle = items.get(f'items[{index}][id_detalle]')
            
            # Convertir a int si tienen valor, sino None
            id_color = int(id_color) if id_color and id_color != '' else None
            id_detalle = int(id_detalle) if id_detalle and id_detalle != '' else None
            
            nuevo_item = ItemRemitoSucs(
                id=index, 
                idremito=idremito, 
                idarticulo=articulo.id, 
                cantidad=cantidad,
                id_color=id_color,
                id_detalle=id_detalle
            )
            db.session.add(nuevo_item)
            
            # Actualizar en_transito en ambas sucursales (estado PENDIENTE)
            # Sucursal origen: aumenta en_transito_salida
            stock_origen = Stock.query.filter_by(idarticulo=articulo.id, idsucursal=idsucursal).first()
            if stock_origen:
                stock_origen.en_transito_salida += cantidad
            else:
                # Crear registro de stock si no existe
                nuevo_stock = Stock(
                    idarticulo=articulo.id,
                    idsucursal=idsucursal,
                    actual=0,
                    maximo=0,
                    deseable=0,
                    en_transito_salida=cantidad,
                    en_transito_entrada=0
                )
                db.session.add(nuevo_stock)
            
            # Sucursal destino: aumenta en_transito_entrada
            stock_destino = Stock.query.filter_by(idarticulo=articulo.id, idsucursal=iddestino).first()
            if stock_destino:
                stock_destino.en_transito_entrada += cantidad
            else:
                # Crear registro de stock si no existe
                nuevo_stock = Stock(
                    idarticulo=articulo.id,
                    idsucursal=iddestino,
                    actual=0,
                    maximo=0,
                    deseable=0,
                    en_transito_entrada=cantidad,
                    en_transito_salida=0
                )
                db.session.add(nuevo_stock)
                
    db.session.commit()


def enviar_remito_sucursal(idremito):
    """
    Cambia el estado del remito a ENVIADO.
    En la sucursal origen: descuenta de 'actual' y de 'en_transito_salida'.
    """
    from models.articulos import EstadosRemitoSucursales
    
    remito = db.session.get(RemitoSucursales, idremito)
    if not remito:
        return {'success': False, 'message': 'Remito no encontrado'}
    
    if remito.estado != EstadosRemitoSucursales.PENDIENTE:
        return {'success': False, 'message': f'El remito no está en estado PENDIENTE (Estado actual: {remito.estado.value})'}
    
    # Obtener los items del remito
    items = ItemRemitoSucs.query.filter_by(idremito=idremito).all()
    
    for item in items:
        # Actualizar stock en sucursal origen
        stock_origen = Stock.query.filter_by(
            idarticulo=item.idarticulo, 
            idsucursal=remito.idsucursal
        ).first()
        
        if stock_origen:
            # Verificar que haya stock suficiente
            if stock_origen.actual < item.cantidad:
                db.session.rollback()
                return {
                    'success': False, 
                    'message': f'Stock insuficiente para el artículo ID {item.idarticulo}. Actual: {stock_origen.actual}, Requerido: {item.cantidad}'
                }
            
            # Descontar del stock actual y del en_transito_salida
            stock_origen.actual -= item.cantidad
            stock_origen.en_transito_salida -= item.cantidad
        else:
            db.session.rollback()
            return {'success': False, 'message': f'No existe stock para el artículo ID {item.idarticulo} en la sucursal origen'}
    
    # Cambiar estado del remito a ENVIADO
    remito.estado = EstadosRemitoSucursales.ENVIADO
    
    db.session.commit()
    return {'success': True, 'message': 'Remito enviado correctamente'}


def recibir_remito_sucursal(idremito):
    """
    Cambia el estado del remito a RECIBIDO.
    En la sucursal destino: suma a 'actual' y descuenta de 'en_transito_entrada'.
    """
    from models.articulos import EstadosRemitoSucursales
    
    remito = db.session.get(RemitoSucursales, idremito)
    if not remito:
        return {'success': False, 'message': 'Remito no encontrado'}
    
    if remito.estado != EstadosRemitoSucursales.ENVIADO:
        return {'success': False, 'message': f'El remito no está en estado ENVIADO (Estado actual: {remito.estado.value})'}
    
    # Obtener los items del remito
    items = ItemRemitoSucs.query.filter_by(idremito=idremito).all()
    
    for item in items:
        # Actualizar stock en sucursal destino
        stock_destino = Stock.query.filter_by(
            idarticulo=item.idarticulo, 
            idsucursal=remito.iddestino
        ).first()
        
        if stock_destino:
            # Pasar de en_transito_entrada a actual
            stock_destino.actual += item.cantidad
            stock_destino.en_transito_entrada -= item.cantidad
        else:
            # Si no existe el stock, crearlo
            nuevo_stock = Stock(
                idstock=db.session.query(func.max(Stock.idstock)).scalar() + 1,
                idarticulo=item.idarticulo,
                idsucursal=remito.iddestino,
                actual=item.cantidad,
                maximo=0,
                deseable=0,
                en_transito_entrada=0,
                en_transito_salida=0
            )
            db.session.add(nuevo_stock)
    
    # Cambiar estado del remito a RECIBIDO
    remito.estado = EstadosRemitoSucursales.RECIBIDO
    
    db.session.commit()
    return {'success': True, 'message': 'Remito recibido y controlado correctamente'}


def get_remitos_sucursales(filtro='todos'):
    """
    Obtiene la lista de remitos según el filtro especificado.
    filtro: 'todos', 'enviados', 'pendientes', 'recibidos', 'origen', 'destino'
    """
    from models.articulos import EstadosRemitoSucursales
    from models.sessions import Usuarios
    
    query = db.session.query(
        RemitoSucursales.id,
        RemitoSucursales.fecha,
        RemitoSucursales.estado,
        RemitoSucursales.idsucursal,
        RemitoSucursales.iddestino,
        Sucursales.nombre.label('nombre_origen'),
        db.session.query(Sucursales.nombre).filter(Sucursales.id == RemitoSucursales.iddestino).correlate(RemitoSucursales).scalar_subquery().label('nombre_destino'),
        Usuarios.nombre.label('usuario')
    ).join(
        Sucursales, RemitoSucursales.idsucursal == Sucursales.id
    ).join(
        Usuarios, RemitoSucursales.idusuario == Usuarios.id
    )
    
    id_sucursal_actual = session.get('id_sucursal')
    
    if filtro == 'pendientes':
        query = query.filter(RemitoSucursales.estado == EstadosRemitoSucursales.PENDIENTE)
    elif filtro == 'enviados':
        query = query.filter(RemitoSucursales.estado == EstadosRemitoSucursales.ENVIADO)
    elif filtro == 'recibidos':
        query = query.filter(RemitoSucursales.estado == EstadosRemitoSucursales.RECIBIDO)
    elif filtro == 'origen':
        query = query.filter(RemitoSucursales.idsucursal == id_sucursal_actual)
    elif filtro == 'destino':
        query = query.filter(RemitoSucursales.iddestino == id_sucursal_actual)
    
    remitos = query.order_by(RemitoSucursales.fecha.desc(), RemitoSucursales.id.desc()).all()
    
    return [{
        'id': r.id,
        'fecha': r.fecha.strftime('%d/%m/%Y') if r.fecha else '',
        'estado': r.estado.value,
        'estado_key': r.estado.name,
        'origen': r.nombre_origen,
        'destino': r.nombre_destino,
        'usuario': r.usuario,
        'es_origen': r.idsucursal == id_sucursal_actual,
        'es_destino': r.iddestino == id_sucursal_actual
    } for r in remitos]


def get_detalle_remito(idremito):
    """Obtiene el detalle completo de un remito con sus items"""
    from models.sessions import Usuarios
    
    remito = db.session.query(
        RemitoSucursales.id,
        RemitoSucursales.fecha,
        RemitoSucursales.estado,
        RemitoSucursales.idsucursal,
        RemitoSucursales.iddestino,
        Sucursales.nombre.label('nombre_origen'),
        db.session.query(Sucursales.nombre).filter(Sucursales.id == RemitoSucursales.iddestino).correlate(RemitoSucursales).scalar_subquery().label('nombre_destino'),
        Usuarios.nombre.label('usuario')
    ).join(
        Sucursales, RemitoSucursales.idsucursal == Sucursales.id
    ).join(
        Usuarios, RemitoSucursales.idusuario == Usuarios.id
    ).filter(RemitoSucursales.id == idremito).first()
    
    if not remito:
        return None
    
    items = db.session.query(
        ItemRemitoSucs.id,
        ItemRemitoSucs.cantidad,
        Articulo.codigo,
        Articulo.detalle,
        Colores.nombre.label('color'),
        DetallesArticulos.nombre.label('detalle_art')
    ).join(
        Articulo, ItemRemitoSucs.idarticulo == Articulo.id
    ).outerjoin(
        Colores, ItemRemitoSucs.id_color == Colores.id
    ).outerjoin(
        DetallesArticulos, ItemRemitoSucs.id_detalle == DetallesArticulos.id
    ).filter(ItemRemitoSucs.idremito == idremito).all()
    
    id_sucursal_actual = session.get('id_sucursal')
    
    return {
        'id': remito.id,
        'fecha': remito.fecha.strftime('%d/%m/%Y %H:%M') if remito.fecha else '',
        'estado': remito.estado.value,
        'estado_key': remito.estado.name,
        'origen': remito.nombre_origen,
        'destino': remito.nombre_destino,
        'usuario': remito.usuario,
        'es_origen': remito.idsucursal == id_sucursal_actual,
        'es_destino': remito.iddestino == id_sucursal_actual,
        'items': [{
            'id': item.id,
            'cantidad': float(item.cantidad),
            'codigo': item.codigo,
            'detalle': item.detalle,
            'color': item.color,
            'detalle_art': item.detalle_art
        } for item in items]
    }
    

def remitos_mercaderia():    
    cantidad = db.session.query(func.count(RemitoSucursales.id))\
               .filter(and_(RemitoSucursales.iddestino == session['id_sucursal'], RemitoSucursales.fecha == date.today())).scalar()
    if cantidad > 0:            
        return cantidad, {'titulo': 'Remitos', 'subtitulo': f'Hay {cantidad} remitos', 'tipo': 'peligro', 'entidad': 'sistema', 'url': '#'}
    else:
        return cantidad, {}
