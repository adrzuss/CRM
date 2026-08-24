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


def alerta_stocks_faltante():
    cantidad = db.session.query(func.count(Articulo.id))\
                .join(Stock, (Stock.idarticulo == Articulo.id)&(Stock.idsucursal==session['id_sucursal']))\
                .filter(Stock.actual <= 0).scalar()
    if cantidad > 0:            
        return cantidad, {'titulo': 'Stock', 'subtitulo': f'Hay {cantidad} artículos con stock en 0 o negativo', 'tipo': 'peligro', 'url': 'articulos.stock_art_faltantes'}
    else:
        return cantidad, {}
    

def alerta_stocks_limite():
    cantidad = db.session.query(func.count(Articulo.id))\
                .join(Stock, (Stock.idarticulo == Articulo.id)&(Stock.idsucursal==session['id_sucursal']))\
                .filter(and_(Stock.deseable > 0, Stock.actual < Stock.deseable)).scalar()
    if cantidad > 0:            
        return cantidad, {'titulo': 'Stock', 'subtitulo': f'Hay {cantidad} artículos con stock por debajo del deseable', 'tipo': 'cuidado', 'url': 'articulos.stock_art'}
    else:
        return cantidad, {}


def alerta_precios_nuevos():
    hoy = date.today()
    cantidad = db.session.query(func.count(func.distinct(Articulo.id)))\
                .join(Precio, (Precio.idarticulo == Articulo.id))\
                .filter(and_(Precio.ult_modificacion==hoy, Precio.precio > 0)).scalar()
    if cantidad > 0:            
        #articulos.precios_nuevos
        return cantidad, {'titulo': 'Precios', 'subtitulo': f'Hay {cantidad} artículos con precios nuevos', 'tipo': 'info', 'url': ''}
    else:
        return cantidad, {}


def obtener_stock_sucursales(idmarca, idrubro, draw, search_value, start, length, order_column, order_dir):
    # Obtener la lista de sucursales
    sucursales = db.session.query(Sucursales.id, Sucursales.nombre).all()
    # Construir dinámicamente las columnas de la consulta
    columns_names = [
        Articulo.id.label("id"),
        Articulo.codigo.label("codigo"),
        Marca.nombre.label("marca"),
        Rubro.nombre.label("rubro"),
        Articulo.detalle.label("detalle")
       
    ]
    
    
    for sucursal in sucursales:
        columns_names.append(
            func.coalesce(
                func.sum(
                    case(
                        (Stock.idsucursal == sucursal.id, Stock.actual), else_=0
                    )
                ), 0
        ).label(sucursal.nombre)  # Usar el nombre de la sucursal como label
    )
    # Construir la consulta con las columnas dinámicas
    if idmarca and idrubro:
        pivot_query = (
            db.session.query(*columns_names)
            .join(Marca, Articulo.idmarca == Marca.id)
            .join(Rubro, Articulo.idrubro == Rubro.id)
            .join(Stock, Articulo.id == Stock.idarticulo)
            .filter(Stock.actual.isnot(None), Rubro.id == idrubro, Marca.id == idmarca) 
            .group_by(Articulo.codigo, Articulo.detalle)
            
        )
    elif (idmarca) and (not idrubro):   
        pivot_query = (
            db.session.query(*columns_names)
            .join(Marca, Articulo.idmarca == Marca.id)
            .join(Rubro, Articulo.idrubro == Rubro.id)
            .join(Stock, Articulo.id == Stock.idarticulo)
            .filter(Stock.actual.isnot(None), Marca.id == idmarca) 
            .group_by(Articulo.codigo, Articulo.detalle)
            
        )
    elif (not idmarca) and (idrubro):
        pivot_query = (
            db.session.query(*columns_names)
            .join(Marca, Articulo.idmarca == Marca.id)
            .join(Rubro, Articulo.idrubro == Rubro.id)
            .join(Stock, Articulo.id == Stock.idarticulo)
            .filter(Stock.actual.isnot(None), Rubro.id == idrubro) 
            .group_by(Articulo.codigo, Articulo.detalle)
            
        )    
    else:
        pivot_query = (
            db.session.query(*columns_names)
            .outerjoin(Marca, Articulo.idmarca == Marca.id)
            .outerjoin(Rubro, Articulo.idrubro == Rubro.id)
            .join(Stock, Articulo.id == Stock.idarticulo)
            .filter(Stock.actual.isnot(None)) 
            #.group_by(Articulo.codigo, Articulo.detalle)
            
        )    
    #resultado = pivot_query.all()
    # Aplicar ordenamiento
    columns_names = [column["name"] for column in pivot_query.column_descriptions]
    # Mapear el índice de la columna al nombre de la columna en la base de datos
    #columns = ['codigo', 'rubro', 'marca', 'detalle', 'actual', 'maximo', 'deseable']
    #Sumo 1 a las columnas porque el primer elemento es el id y no se muestra en la tabla
    order_by = columns_names[order_column+1] if order_column is not None and order_column+1 < len(columns_names) else 'codigo'
    
    if order_dir == 'desc':
        pivot_query = pivot_query.order_by(desc(order_by))
    else:
        pivot_query = pivot_query.order_by(order_by)
    pivot_query = pivot_query.group_by(Articulo.id, Articulo.codigo, Articulo.detalle, Marca.nombre, Rubro.nombre)
    
    total_records = pivot_query.count()
    
    # Aplicar paginación
    paginated_query = pivot_query.offset(start).limit(length).all()
    
    
    # Construir los datos dinámicamente
    data = []
    for row in paginated_query:
        row_data = {}
        for column_name in columns_names:
            row_data[column_name] = getattr(row, column_name)
        data.append(row_data)
    
    return draw, total_records, total_records, data, columns_names


def actualizarStock(idsucursal, idarticulo, cantidad, tipoMovimiento='Venta'):
    tipoActualizacion = 'Nada'
    try:
        articulo = db.session.get(Articulo, idarticulo)
        stock = Stock.query.filter(Stock.idsucursal == idsucursal, 
                                   Stock.idarticulo == idarticulo).first()
        if articulo.idtipoarticulo == 2: #servico
            cantidad = (cantidad * -1)
        match tipoMovimiento:
            case 'Venta':
                cantidad = cantidad
            case 'Compra':   
                cantidad = (cantidad * -1)
            case 'Balance':
                cantidad = cantidad
            case 'NotaCredito':
                cantidad = (cantidad * -1)
            case _:
                cantidad = cantidad
        if tipoMovimiento == 'Balance':
            if stock != None:
                tipoActualizacion = 'Actualizando'
                db.session.execute(
                    update(Stock).
                    where(Stock.idsucursal == idsucursal, Stock.idarticulo == idarticulo).
                    values(actual= cantidad)
                )
            else:    
                tipoActualizacion = 'Insertando'
                stock = Stock(idarticulo=idarticulo, idsucursal=idsucursal, actual=cantidad, maximo=0, deseable=0)
                db.session.add(stock)
        else:                         
            if stock != None:
                tipoActualizacion = 'Actualizando'
                db.session.execute(
                    update(Stock).
                    where(Stock.idsucursal == idsucursal, Stock.idarticulo == idarticulo).
                    values(actual= (stock.actual + cantidad))
                )
            else:    
                tipoActualizacion = 'Insertando'
                stock = Stock(idarticulo=idarticulo, idsucursal=idsucursal, actual=cantidad, maximo=0, deseable=0)
                db.session.add(stock)
            compuestos = db.session.query(ArticuloCompuesto.idarticulo, 
                                        ArticuloCompuesto.idart_comp,
                                        ArticuloCompuesto.cantidad,
                                        ).filter(ArticuloCompuesto.idarticulo == idarticulo).all()
            for compuesto in compuestos:
                if cantidad > 0:
                    actualizarStock(idsucursal, compuesto.idart_comp, compuesto.cantidad)
                else:
                    actualizarStock(idsucursal, compuesto.idart_comp, -1*compuesto.cantidad)
    except Exception as e:
        print(f"Error procesando stock: {e}")
        raise Exception(f"Error al actualizar el stock ({tipoActualizacion}): {e}")
          

def get_stocks_negativos():
    sucursal = session['id_sucursal']
    stk_neg = db.session.execute(text("CALL get_stock_negativos(:sucursal)"),{'sucursal': sucursal}).fetchall()
    stk_list = []
    for stk in stk_neg:
        stk_list.append({
            'id': stk[0],
            'codigo': stk[1],
            'detalle': stk[2],
            'cantidad': stk[3]
        })
    return stk_list


def get_stocks_faltantes():
    sucursal = session['id_sucursal']
    stk_neg = db.session.execute(text("CALL get_stock_faltantes(:sucursal)"),
                         {'sucursal': sucursal}).fetchall()
    stk_list = []
    for stk in stk_neg:
        stk_list.append({
            'id': stk[0],
            'codigo': stk[1],
            'detalle': stk[2],
            'cantidad': stk[3]
        })
    return stk_list
