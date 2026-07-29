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

from .stock import actualizarStock
from .articulos import get_articulo_by_codigo


def get_listado_articulos(idmarca, idrubro, verBaja, draw, search_value, start, length, order_column, order_dir):            
     # Mapear el índice de la columna al nombre de la columna en la base de datos
    columns = ['codigo', 'rubro', 'marca', 'detalle', 'costo', 'detalle_articulo', 'color', 'es_compuesto']
    order_by = columns[order_column] if order_column < len(columns) else 'codigo'
    
    # Consulta base
    query = db.session.query(
        Articulo.id,
        Articulo.detalle,
        Articulo.codigo,
        Articulo.costo,
        Articulo.con_talles.label('detalle_articulo'),
        Articulo.con_colores.label('color'),
        Articulo.es_compuesto,
        Articulo.imagen,
        Articulo.baja,
        Rubro.nombre.label('rubro'),
        Marca.nombre.label('marca')
    ).join(
        Rubro, and_(Articulo.idrubro == Rubro.id, Rubro.id == idrubro if idrubro else True)
    ).join(
        Marca, and_(Articulo.idmarca == Marca.id, Marca.id == idmarca if idmarca else True)
    )

    # Aplicar búsqueda
    if search_value:
        if search_value[0:2] == '//':
            if len(search_value) > 2:
                codBusqueda = search_value[2:]
                if verBaja == 1:
                    query = query.filter(and_(Articulo.codigo.ilike(f"{codBusqueda}%"), Articulo.baja >= date(1900, 1, 1)))
                else:
                    query = query.filter(and_(Articulo.codigo.ilike(f"{codBusqueda}%"), Articulo.baja == date(1900, 1, 1)))
        else:
            if verBaja == 1:
                query = query.filter(and_(Articulo.detalle.ilike(f"%{search_value}%"), Articulo.baja >= date(1900, 1, 1)))
            else:
                query = query.filter(and_(Articulo.detalle.ilike(f"%{search_value}%"), Articulo.baja == date(1900, 1, 1)))
    else:
        if verBaja == 1:
            query = query.filter(Articulo.baja >= date(1900, 1, 1))
        else:
            query = query.filter(Articulo.baja == date(1900, 1, 1))

    # Aplicar ordenamiento
    if order_dir == 'desc':
        query = query.order_by(desc(order_by))
    else:
        query = query.order_by(order_by)
    # Total de registros sin filtrar
    
    total_records = query.count()

    # Aplicar paginación
    paginated_query = query.offset(start).limit(length).all()

    # Formatear los datos para DataTables
    data = [
        {
            'id': articulo.id,
            'codigo': articulo.codigo,
            'detalle': articulo.detalle,
            'costo': articulo.costo,
            'detalle_articulo': 'Si' if articulo.detalle_articulo else 'No',
            'color': 'Si' if articulo.color else 'No',
            'es_compuesto': 'Si' if articulo.es_compuesto else 'No',
            'baja': 'Si' if articulo.baja > date(1900, 1, 1) else 'No',
            'imagen': articulo.imagen,
            'rubro': articulo.rubro,
            'marca': articulo.marca
        }
        for articulo in paginated_query
    ]
    return draw, total_records, total_records, data


def get_listado_stock(idmarca, idrubro, draw, search_value, start, length, order_column, order_dir):
    
    # Mapear el índice de la columna al nombre de la columna en la base de datos
    columns = ['codigo', 'rubro', 'marca', 'detalle', 'actual', 'maximo', 'deseable']
    order_by = columns[order_column] if order_column < len(columns) else 'codigo'
    query = db.session.query(
        Articulo.id.label('id'),
        Articulo.codigo.label('codigo'),
        Articulo.detalle.label('detalle'),
        Stock.actual.label('actual'),
        Stock.maximo.label('maximo'),
        Stock.deseable.label('deseable'),
        Rubro.nombre.label('rubro'),
        Marca.nombre.label('marca'),
            ).join(
                Stock, (Articulo.id == Stock.idarticulo)&(Stock.idsucursal==session['id_sucursal'])
            ).outerjoin(
                Rubro, (Articulo.idrubro == Rubro.id)
            ).outerjoin(
                Marca, (Articulo.idmarca == Marca.id)
            )
    # Aplicar búsqueda
    if search_value:
        if idmarca != None and idrubro != None:
            query = query.filter(Articulo.detalle.ilike(f"%{search_value}%", Articulo.idmarca == idmarca, Articulo.idrubro == idrubro))
        elif idmarca != None or idrubro != None:
            if idmarca != None:
                query = query.filter(Articulo.detalle.ilike(f"%{search_value}%", Articulo.idmarca == idmarca))
            else:
                query = query.filter(Articulo.detalle.ilike(f"%{search_value}%",Articulo.idrubro == idrubro))
        else:
            query = query.filter(Articulo.detalle.ilike(f"%{search_value}%"))        
    else:
        if idmarca != None and idrubro != None:
            query = query.filter(Articulo.idmarca == idmarca, Articulo.idrubro == idrubro)
        elif idmarca != None or idrubro != None:
            if idmarca != None:
                query = query.filter(Articulo.idmarca == idmarca)
            else:
                query = query.filter(Articulo.idrubro == idrubro)
    # Total de registros sin filtrar
    # Aplicar ordenamiento
    if order_dir == 'desc':
        query = query.order_by(desc(order_by))
    else:
        query = query.order_by(order_by)
    # Total de registros sin filtrar
    total_records = query.count()
    
    # Aplicar paginación
    paginated_query = query.offset(start).limit(length).all()
    # Formatear los datos para DataTables
    data = [
        {
            'id': articulo.id,
            'codigo': articulo.codigo,
            'rubro': articulo.rubro,
            'marca': articulo.marca,
            'detalle': articulo.detalle,
            'actual': articulo.actual,
            'deseable': articulo.deseable,
            'maximo': articulo.maximo
        }
        for articulo in paginated_query
    ]
    # Respuesta para DataTables
    return draw, total_records, total_records, data


def get_listado_stock_faltantes(idmarca, idrubro, draw, search_value, start, length, order_column, order_dir):
    
    # Mapear el índice de la columna al nombre de la columna en la base de datos
    columns = ['codigo', 'rubro', 'marca', 'detalle', 'actual', 'maximo', 'deseable']
    order_by = columns[order_column] if order_column < len(columns) else 'codigo'
    query = db.session.query(
        Articulo.id.label('id'),
        Articulo.codigo.label('codigo'),
        Articulo.detalle.label('detalle'),
        Stock.actual.label('actual'),
        Stock.maximo.label('maximo'),
        Stock.deseable.label('deseable'),
        Rubro.nombre.label('rubro'),
        Marca.nombre.label('marca'),
            ).join(
                Stock, (Articulo.id == Stock.idarticulo)&(Stock.idsucursal==session['id_sucursal'])
            ).outerjoin(
                Rubro, (Articulo.idrubro == Rubro.id)
            ).outerjoin(
                Marca, (Articulo.idmarca == Marca.id)
            )
    # Aplicar búsqueda
    if search_value:
        if idmarca != None and idrubro != None:
            query = query.filter(Stock.actual <= 0, Articulo.detalle.ilike(f"%{search_value}%", Articulo.idmarca == idmarca, Articulo.idrubro == idrubro))
        elif idmarca != None or idrubro != None:
            if idmarca != None:
                query = query.filter(Stock.actual <= 0, Articulo.detalle.ilike(f"%{search_value}%", Articulo.idmarca == idmarca))
            else:
                query = query.filter(Stock.actual <= 0, Articulo.detalle.ilike(f"%{search_value}%",Articulo.idrubro == idrubro))
        else:
            query = query.filter(Stock.actual <= 0, Articulo.detalle.ilike(f"%{search_value}%"))        
    else:
        if idmarca != None and idrubro != None:
            query = query.filter(Stock.actual <= 0, Articulo.idmarca == idmarca, Articulo.idrubro == idrubro)
        elif idmarca != None or idrubro != None:
            if idmarca != None:
                query = query.filter(Stock.actual <= 0, Articulo.idmarca == idmarca)
            else:
                query = query.filter(Stock.actual <= 0, Articulo.idrubro == idrubro)
        else:        
            query = query.filter(Stock.actual <= 0)
    # Total de registros sin filtrar
    # Aplicar ordenamiento
    if order_dir == 'desc':
        query = query.order_by(desc(order_by))
    else:
        query = query.order_by(order_by)
    # Total de registros sin filtrar
    total_records = query.count()
    
    # Aplicar paginación
    paginated_query = query.offset(start).limit(length).all()
    # Formatear los datos para DataTables
    data = [
        {
            'id': articulo.id,
            'codigo': articulo.codigo,
            'rubro': articulo.rubro,
            'marca': articulo.marca,
            'detalle': articulo.detalle,
            'actual': articulo.actual,
            'deseable': articulo.deseable,
            'maximo': articulo.maximo
        }
        for articulo in paginated_query
    ]
    # Respuesta para DataTables
    return draw, total_records, total_records, data


def procesar_nuevo_balance(form, id_sucursal):
    try:
        fecha = form['fecha']
        idTipoBalance = form['tipobalance']
        
        # Crear la factura
        nuevo_balance = Balance(idusuario=session['user_id'], fecha=fecha, tipo_balance=idTipoBalance, idsucursal=id_sucursal)
        db.session.add(nuevo_balance)
        db.session.flush()
        idbalance = nuevo_balance.id

        # Procesar los items
        procesar_items_balance(form, idbalance, id_sucursal)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Error grabando venta: {e}")


def procesar_items_balance(form, idbalance, id_sucursal):
    total = Decimal(0)

    for key, value in form.items():
        response = get_articulo_by_codigo(value)
        if response['success'] == True:
            if key.startswith('items') and key.endswith('[codigo]'):
                index = key.split('[')[1].split(']')[0]
                codigo = value
                cantidad = Decimal(form[f'items[{index}][cantidad]'])

                articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
                precio = Precio.query.filter_by(idarticulo=articulo.id, idlista=1).first()
                precio_unitario = precio.precio if precio else Decimal(0)
                precio_total = precio_unitario * cantidad

                # Obtener color y detalle si están presentes
                id_color = form.get(f'items[{index}][id_color]')
                id_detalle = form.get(f'items[{index}][id_detalle]')
                
                # Convertir a int si tienen valor, sino None
                id_color = int(id_color) if id_color and id_color != '' else None
                id_detalle = int(id_detalle) if id_detalle and id_detalle != '' else None
                
                nuevo_item = ItemBalance(
                    idbalance=idbalance, 
                    idarticulo=articulo.id, 
                    cantidad=cantidad, 
                    precio_unitario=precio_unitario, 
                    precio_total=precio_total,
                    id_color=id_color,
                    id_detalle=id_detalle
                )
                db.session.add(nuevo_item)
                # Actualizar el stock
                actualizarStock(id_sucursal, articulo.id, cantidad)
    
    return total


def get_detalle_articulo(idarticulo):
    try:
        result = db.session.execute(text("CALL recalculo_stock(:idarticulo, :sucursal)"),{'idarticulo': idarticulo, 'sucursal': session['id_sucursal']})
        detalle_art = result.fetchone()
        result.close()  # Cerrar el cursor para liberar todos los result sets
        db.session.commit()
        
        if not detalle_art:
            return None
                
        return {
            'alta' : str(detalle_art[0]) if detalle_art[0] else None,
            'balance' : float(detalle_art[1]) if detalle_art[1] else 0,
            'remitos_compras' : float(detalle_art[2]) if detalle_art[2] else 0,
            'compras' : float(detalle_art[3]) if detalle_art[3] else 0,
            'remitos_ventas' : float(detalle_art[4]) if detalle_art[4] else 0,
            'credito_ventas' : float(detalle_art[5]) if detalle_art[5] else 0,
            'ventas' : float(detalle_art[6]) if detalle_art[6] else 0,
            'salidas_a_sucursales' : float(detalle_art[7]) if detalle_art[7] else 0,
            'entradas_de_sucursales' : float(detalle_art[8]) if detalle_art[8] else 0,
            'stock_actual' : float(detalle_art[9]) if detalle_art[9] else 0}
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None   
    

def get_detalle_full_articulo(idarticulo):
    try:
        result = db.session.execute(text("CALL detalle_movimiento_art(:idarticulo, :sucursal)"),{'idarticulo': idarticulo, 'sucursal': session['id_sucursal']})
        detalle_art = result.fetchall()
        result.close()  # Cerrar el cursor para liberar todos los result sets
        db.session.commit()
        
        if not detalle_art:
            return None
        
                
        return {
            'movimientos': [{
                'tipo_movimiento': mov[0],
                'nro_comp': mov[1],
                'fecha': str(mov[2]) if mov[0] else None,
                'entradas': float(mov[3]) if mov[3] else 0,
                'salidas': float(mov[4]) if mov[4] else 0
            } for mov in detalle_art]
        }
        
        
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None
