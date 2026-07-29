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


def get_listado_precios(idlista, idmarca, idrubro, draw, search_value, start, length, order_column, order_dir):
    
    # Mapear el índice de la columna al nombre de la columna en la base de datos
    columns = ['codigo', 'rubro', 'marca', 'detalle', 'costo', 'precio']
    order_by = columns[order_column] if order_column < len(columns) else 'codigo'
        
    query = db.session.query(
        Articulo.id.label('id'),
        Articulo.codigo.label('codigo'),
        Articulo.detalle.label('detalle'),
        Articulo.costo.label('costo'),
        Rubro.nombre.label('rubro'),
        Marca.nombre.label('marca'),
        func.coalesce(Precio.precio.label('precio'), 0).label('precio')
            ).join(
                Rubro, (Articulo.idrubro == Rubro.id)
            ).join(
                Marca, (Articulo.idmarca == Marca.id)
            ).outerjoin(
                Precio, (Articulo.id == Precio.idarticulo) & (Precio.idlista==idlista)
            )
    # Aplicar búsqueda
    if search_value:
        query = query.filter(
            Articulo.detalle.ilike(f"%{search_value}%", Articulo.idmarca == idmarca, Articulo.idrubro == idrubro)
        )
    else:
        query = query.filter(Articulo.idmarca == idmarca, Articulo.idrubro == idrubro)
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
            'detalle': articulo.detalle,
            'costo': articulo.costo,
            'precio': articulo.precio,
            'rubro': articulo.rubro,
            'marca': articulo.marca
        }
        for articulo in paginated_query
    ]
    # Respuesta para DataTables
    return draw, total_records, total_records, data


def actualizarPrecio(idlista, idarticulo, precio_nuevo):
    #El commit se raliza en el proceso principal de grabación de precios
    idart = db.session.query(Precio.idarticulo).filter(Precio.idlista == idlista, Precio.idarticulo == idarticulo).first()
    if idart:
        db.session.execute(
            update(Precio).
            where(Precio.idlista == idlista, Precio.idarticulo == idarticulo).
            values(precio=precio_nuevo, ult_modificacion=datetime.now())    
        )
    else:
        precioNuevo = Precio(idlista=idlista, idarticulo=idarticulo, precio=precio_nuevo, ult_modificacion=datetime.now())
        db.session.add(precioNuevo)
    

def procesar_cambio_precio(form):
    #---------------------
    try:
        fecha = form['fecha']
        idusuario = session['user_id']
        idsucursal = session['id_sucursal']
        idlista = form['lista_precio']
                                                
        nuevo_cambio_precio = CambioPrecios(fecha, idsucursal, idusuario, idlista)
        db.session.add(nuevo_cambio_precio)
        db.session.flush()

        idcambioprecio = nuevo_cambio_precio.id
            
        # Procesar los items
        items = form
        for key, value in items.items():
            if key.startswith('items') and key.endswith('[codigo]'):
                # Extraer el índice del item
                index = key.split('[')[1].split(']')[0]
                codigo = value
                precio_actual = form.get(f'items[{index}][precio_actual]')
                precio_nuevo = form.get(f'items[{index}][precio_nuevo]')
                # Obtener el artículo por código
                articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
                if articulo:
                    # Crear un registro de item_cambio_precios
                    nuevo_item = CambioPreciosItem(
                        idcambioprecio=idcambioprecio,
                        id=index,
                        idarticulo=articulo.id,
                        precio_de=precio_actual,
                        precio_a=precio_nuevo
                    )
                    db.session.add(nuevo_item)
                    actualizarPrecio(idlista, articulo.id, precio_nuevo)
        # Confirmar los cambios
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error SQL: {e}")
        raise Exception(f"Error SQL: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        raise
