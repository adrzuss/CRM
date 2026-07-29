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


def get_articulo_by_codigo(codigo):
    articulo = Articulo.query.filter_by(codigo=codigo).first()
    if articulo:
        return {'success': True, 'articulo': articulo}
    else:
        return {'success':False, 'articulo':{}}


def guardar_articulo(id, form, files):
    """
    Guarda un artículo (nuevo o actualización).
    
    Args:
        id: ID del artículo ('0' para nuevo, otro valor para actualizar)
        form: Datos del formulario (request.form)
        files: Archivos del formulario (request.files)
    
    Returns:
        dict con 'success', 'message' y opcionalmente 'articulo'
    """
    try:
        # Verificar si el código está vacío para asignar uno temporal (la columna es NOT NULL)
        codigo_temporal = 'TEMP' if form['codigo'].strip() == '' else form['codigo']
        idrubro = form['idrubro']
        
        if id == '0':
            # Crear nuevo artículo
            articulo = Articulo(
                codigo=codigo_temporal,
                detalle=form['detalle'].upper(),
                costo=form['costo'],
                costo_total=form['costo_total'],
                exento=form['exento'],
                impint=form['impint'],
                idiva=form['idiva'],
                idib=form['idib'],
                idrubro=idrubro,
                idmarca=form['idmarca'],
                idtipoarticulo=form['idtipoarticulo'],
                imagen='',
                es_compuesto=form.get("es_compuesto") != None,
                pedir_en_ventas=form.get("pedir_en_ventas"),
                con_colores=form.get("con_colores") != None,
                con_talles=form.get("con_talles") != None
            )
            db.session.add(articulo)
        else:
            # Actualizar artículo existente
            articulo = db.session.get(Articulo, id)
            if not articulo:
                return {'success': False, 'message': 'Artículo no encontrado'}
            
            articulo.codigo = codigo_temporal
            articulo.detalle = form['detalle'].upper()
            articulo.costo = form['costo']
            articulo.costo_total = form['costo_total']
            articulo.exento = form['exento']
            articulo.impint = form['impint']
            articulo.idiva = form['idiva']
            articulo.idib = form['idib']
            articulo.idtipoarticulo = form['idtipoarticulo']
            articulo.es_compuesto = form.get("es_compuesto") != None
            articulo.con_colores = form.get("con_colores") != None
            articulo.con_talles = form.get("con_talles") != None
            articulo.pedir_en_ventas = form.get("pedir_en_ventas")
            articulo.idmarca = form['idmarca']
            articulo.idrubro = idrubro
        
        db.session.flush()
        idarticulo = articulo.id
        
        # Si el código estaba vacío, asignar código automático: idrubro + id con formato de 6 dígitos
        if codigo_temporal == 'TEMP':
            articulo.codigo = f"{idrubro}{str(idarticulo).zfill(6)}"
        
        # Manejar la imagen
        if 'imagen' in files:
            file = files['imagen']
            if file.filename != '':
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    articulo.imagen = filename
                else:
                    return {'success': False, 'message': 'Tipo de archivo inválido'}
        
        # Actualizar precios
        _guardar_precios(form, id, articulo.id)
        
        # Actualizar stocks
        _guardar_stocks(form, id, articulo.id)
        
        # Manejar colores del artículo
        _guardar_colores(form, id, articulo)
        
        # Manejar detalles del artículo
        _guardar_detalles(form, id, articulo)
        
        db.session.commit()
        return {'success': True, 'message': 'Artículo grabado', 'articulo': articulo}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Error grabando artículo: {e}'}


def _guardar_precios(form, id_original, idarticulo):
    """Guarda los precios del artículo."""
    items = form
    item_count = len([key for key in items.keys() if key.startswith('precio') and key.endswith('[precio]')])
    
    for i in range(item_count):
        try:
            idlista = form[f'precio[{i+1}][idlista]']
            pvp = form[f'precio[{i+1}][precio]']
            if idlista and pvp:
                precio = db.session.get(Precio, (idlista, id_original))
                if precio:
                    precio.precio = pvp
                    precio.ult_modificacion = datetime.now()
                else:
                    precio = Precio(idlista, idarticulo, pvp, datetime.now())
                    db.session.add(precio)
                db.session.flush()
        except Exception as e:
            flash(f'Error grabando precios {e}', 'error')


def _guardar_stocks(form, id_original, idarticulo):
    """Guarda los stocks del artículo."""
    items = form
    item_count = len([key for key in items.keys() if key.startswith('stock') and key.endswith('[id]')])
    
    for i in range(item_count):
        try:
            idstock = form[f'stock[{i+1}][id]']
            idsucstock = form[f'stock[{i+1}][idsucursal]']
            deseable = form[f'stock[{i+1}][deseable]']
            maximo = form[f'stock[{i+1}][maximo]']
            if idstock and deseable and maximo:
                stock = db.session.get(Stock, (idstock, id_original, idsucstock))
                if stock:
                    stock.deseable = deseable
                    stock.maximo = maximo
                else:
                    stock = Stock(idstock, idarticulo, idsucstock, deseable, maximo)
                    db.session.add(stock)
                db.session.flush()
        except Exception as e:
            flash(f'Error grabando stocks {e}', 'error')


def _guardar_colores(form, id_original, articulo):
    """Guarda los colores del artículo."""
    try:
        if not articulo.con_colores:
            ArticulosColores.query.filter_by(id_articulo=articulo.id).delete()
        else:
            # Eliminar colores existentes si se está editando
            if id_original != '0':
                ArticulosColores.query.filter_by(id_articulo=articulo.id).delete()
            
            # Procesar colores seleccionados
            colores_data = form.get('colores', '')
            if colores_data:
                try:
                    colores_seleccionados = json.loads(colores_data)
                    for color_data in colores_seleccionados:
                        if isinstance(color_data, dict) and 'id' in color_data:
                            color_id = color_data['id']
                            if db.session.get(Colores, color_id):
                                articulo_color = ArticulosColores(id_articulo=articulo.id, id_color=color_id)
                                db.session.add(articulo_color)
                                db.session.flush()
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    flash(f'Error procesando colores: {e}', 'warning')
    except Exception as e:
        flash(f'Error grabando colores: {e}', 'error')


def _guardar_detalles(form, id_original, articulo):
    """Guarda los detalles/talles del artículo."""
    try:
        if not articulo.con_talles:
            ArticulosDetalles.query.filter_by(id_articulo=articulo.id).delete()
        else:
            # Eliminar detalles existentes si se está editando
            if id_original != '0':
                ArticulosDetalles.query.filter_by(id_articulo=articulo.id).delete()
            
            # Procesar detalles seleccionados
            detalles_data = form.get('detalles', '')
            if detalles_data:
                try:
                    detalles_seleccionados = json.loads(detalles_data)
                    for detalle_data in detalles_seleccionados:
                        if isinstance(detalle_data, dict) and 'id' in detalle_data:
                            detalle_id = detalle_data['id']
                            if db.session.get(DetallesArticulos, detalle_id):
                                articulo_detalle = ArticulosDetalles(id_articulo=articulo.id, id_detalle=detalle_id)
                                db.session.add(articulo_detalle)
                                db.session.flush()
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    flash(f'Error procesando detalles: {e}', 'warning')
    except Exception as e:
        flash(f'Error grabando detalles: {e}', 'error')


def update_insert_articulo_compuesto(idarticulo, idarticulo_compuesto, cantidad):
    try:
        articulo = db.session.query(Articulo).filter(Articulo.codigo==idarticulo_compuesto).first()
        art_compuesto = db.session.query(ArticuloCompuesto).filter(and_(ArticuloCompuesto.idarticulo==idarticulo, ArticuloCompuesto.idart_comp==articulo.id)).first()
        if art_compuesto:
            art_compuesto.cantidad = Decimal(cantidad)
        else:
            art_compuesto = ArticuloCompuesto(idarticulo, articulo.id, Decimal(cantidad))
            db.session.add(art_compuesto)
        articulo = db.session.get(Articulo, idarticulo)
        articulo.es_compuesto = True
        db.session.flush()
        #recalculo de costo artículo compuesto
        compuestos = db.session.query(ArticuloCompuesto.cantidad,
                                      ArticuloCompuesto.idart_comp,
                                      Articulo.costo
                                      ).join(Articulo, (Articulo.id == ArticuloCompuesto.idart_comp)).filter(ArticuloCompuesto.idarticulo == idarticulo).all()
        costo = Decimal(0)
        for compuesto in compuestos:
            costo += Decimal(compuesto.costo) * Decimal(compuesto.cantidad)
        articulo.costo = costo
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error SQL: {e}")
        raise Exception(f"Error SQL: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        raise
    

def eliminarComp(idarticulo, idart_comp):
    try:
        db.session.delete(ArticuloCompuesto.query.filter_by(idarticulo=idarticulo, idart_comp=idart_comp).first())
        db.session.flush()
        sigueCompuesto = False
        if ArticuloCompuesto.query.filter_by(idarticulo=idarticulo).count() > 0:
            sigueCompuesto = True
        else:
            articulo = db.session.get(Articulo, idarticulo)
            articulo.es_compuesto = False
        db.session.commit()
        return sigueCompuesto
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error SQL: {e}")
        raise Exception(f"Error SQL: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        raise
    

def actulizarProvByArt(codigo, idarticulo, idproveedor):
    try:
        provByArt = ProvByArt.query.filter(ProvByArt.idarticulo == idarticulo, ProvByArt.idproveedor == idproveedor).first()
        if provByArt is None:
            provByArt = ProvByArt(idarticulo=idarticulo, idproveedor=idproveedor, cod_proveedor=codigo)
            db.session.add(provByArt)
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error procesando provByArt: {e}")
        raise Exception(f"Error al actualizar el provByArt: {e}")
            

def obtenerArticulosMarcaRubro(marca, rubro, lista_precio, porcentaje):
    query = db.session.query(Articulo.id,
                             Articulo.codigo,
                             Articulo.detalle,
                             func.coalesce(Precio.precio, 0).label('precio')
                             ).outerjoin(Precio, and_(Articulo.id == Precio.idarticulo, Precio.idlista == lista_precio)
                             ).filter(Articulo.baja <= date(1900, 1, 1))  # Filtrar artículos no dados de baja
    if marca:
        query = query.filter(Articulo.idmarca == marca)
    if rubro:
        query = query.filter(Articulo.idrubro == rubro)
    articulos = query.all()
    resultado = []
    for articulo in articulos:
        precio_actual = articulo.precio
        precio_nuevo = Decimal(precio_actual) * Decimal((1 + porcentaje / 100))
        resultado.append({
            'codigo': articulo.codigo,
            'descripcion': articulo.detalle,
            'precio_actual':round(precio_actual, 2),
            'precio_nuevo': round(precio_nuevo, 2),
        })    
    return resultado
