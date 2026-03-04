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
            articulo = Articulo.query.get(id)
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
                precio = Precio.query.get((idlista, id_original))
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
                stock = Stock.query.get((idstock, id_original, idsucstock))
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
                            if Colores.query.get(color_id):
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
                            if DetallesArticulos.query.get(detalle_id):
                                articulo_detalle = ArticulosDetalles(id_articulo=articulo.id, id_detalle=detalle_id)
                                db.session.add(articulo_detalle)
                                db.session.flush()
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    flash(f'Error procesando detalles: {e}', 'warning')
    except Exception as e:
        flash(f'Error grabando detalles: {e}', 'error')


"""

def procesar_articulo(form, idarticulo):
    #FIXME al agregar articulo insertar stcok en cero
    print('-----------------------------------------------')
    codigo = form['codigo']
    detalle = form['detalle']
    costo = form['costo']
    costo_total = form['costo_total']
    impint = form['impint']
    exento = form['exento']
    idiva = form['idiva']
    idib = form['idib']
    idmarca = form['idmarca']
    idTipoArticulo = form['idtipoarticulo']
    esCompuesto = form.get("es_compuesto") != None
    idrubro = form['idrubro']
    print('-----------------------------------------------')
    print(f'El codigo: {codigo}')
    print('-----------------------------------------------')
    # Manejar la imagen
    if 'imagen' not in form.files:
        flash('No file part')
        return redirect('/articulos')
        
    file = request.files['imagen']
        
    if file.filename != '':
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Asegura que el nombre del archivo sea seguro para el sistema de archivos
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))  # Guarda el archivo en la carpeta de subida
                    
            #imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)  # Guarda la ruta del archivo en la base de datos
            imagen_path = filename
        else:
            flash('Tipo de archivo inválido')
            return redirect('/articulos') 
    else:
        filename = ''    
    
    # Verificar si el código está vacío para asignar uno temporal (la columna es NOT NULL)
    codigo_vacio = not codigo or codigo.strip() == ''
    codigo_temporal = 'TEMP' if codigo_vacio else codigo
    
    articulo = Articulo(codigo=codigo_temporal, detalle=detalle, costo=costo, costo_total=costo_total, exento=exento, impint=impint, idiva=idiva, idib=idib, idrubro=idrubro, idmarca=idmarca, idTipoArticulo=idTipoArticulo, filename=filename, esCompuesto=esCompuesto)
    db.session.add(articulo)
    db.session.flush()  # Obtener el id sin hacer commit completo
    idarticulo = articulo.id
    
    # Si el código estaba vacío, asignar código automático: idrubro + id con formato de 6 dígitos
    if codigo_vacio:
        articulo.codigo = f"{idrubro}{str(idarticulo).zfill(6)}"
    
    db.session.commit()
        
    items = form  # Obtener todo el formulario
    item_count = 0  # Contador de items agregados
    item_count = len([key for key in items.keys() if key.startswith('precio') and key.endswith('[precio]')])
        
    for i in range(item_count):
        try:
            idlista = form[f'precio[{i+1}][idlista]']
            pvp = form[f'precio[{i+1}][precio]']
            if (idlista != None) and (pvp != None):
                precio = Precio(idlista, idarticulo, pvp, datetime.now())
                db.session.add(precio)
                db.session.commit()
        except Exception as e:
            flash(f'Error grabando precios {e}', 'error')    
"""            
            
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

# ---------------- Stocks        

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
    order_by = columns_names[order_column+1] if order_column < len(columns_names) else 'codigo'
    
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

def update_insert_articulo_compuesto(idarticulo, idarticulo_compuesto, cantidad):
    articulo = db.session.query(Articulo).filter(Articulo.codigo==idarticulo_compuesto).first()
    art_compuesto = db.session.query(ArticuloCompuesto).filter(and_(ArticuloCompuesto.idarticulo==idarticulo, ArticuloCompuesto.idart_comp==articulo.id)).first()
    if art_compuesto:
        art_compuesto.cantidad = Decimal(cantidad)
    else:
        art_compuesto = ArticuloCompuesto(idarticulo, articulo.id, Decimal(cantidad))
        db.session.add(art_compuesto)
    articulo = Articulo.query.get(idarticulo)
    articulo.es_compuesto = True
    db.session.commit()
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
    
def eliminarComp(idarticulo, idart_comp):
    db.session.delete(ArticuloCompuesto.query.filter_by(idarticulo=idarticulo, idart_comp=idart_comp).first())
    db.session.commit()
    sigueCompuesto = False
    if ArticuloCompuesto.query.filter_by(idarticulo=idarticulo).count() > 0:
        sigueCompuesto = True
    else:
        articulo = Articulo.query.get(idarticulo)
        articulo.es_compuesto = False
        db.session.commit()    
    return sigueCompuesto
    
def actualizarStock(idstock, idarticulo, cantidad, idsucursal):
    tipoActualizacion = 'Nada'
    try:
        articulo = Articulo.query.get(idarticulo)
        stock = Stock.query.filter(Stock.idstock == idstock,
                                   Stock.idsucursal == idsucursal, 
                                   Stock.idarticulo == idarticulo).first()
        if articulo.idtipoarticulo == 2: #servico
            cantidad = (cantidad * -1)
        if stock != None:
            tipoActualizacion = 'Actualizando'
            db.session.execute(
                update(Stock).
                where(Stock.idstock == idstock, Stock.idsucursal == idsucursal, Stock.idarticulo == idarticulo).
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
                actualizarStock(idstock, compuesto.idart_comp, compuesto.cantidad, idsucursal)
            else:
                actualizarStock(idstock, compuesto.idart_comp, -1*compuesto.cantidad, idsucursal)
    except Exception as e:
        print(f"Error procesando stock: {e}")
        raise Exception(f"Error al actualizar el stock ({tipoActualizacion}): {e}")
          
def actulizarProvByArt(codigo, idarticulo, idproveedor):
    try:
        provByArt = ProvByArt.query.filter(ProvByArt.idarticulo == idarticulo, ProvByArt.idproveedor == idproveedor).first()
        if provByArt is None:
            provByArt = ProvByArt(idarticulo=idarticulo, idproveedor=idproveedor, cod_proveedor=codigo)
            db.session.add(provByArt)
    except SQLAlchemyError as e:
        print(f"Error procesando provByArt: {e}")
        raise Exception(f"Error al actualizar el provByArt: {e}")
            
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
                actualizarStock(id_sucursal, articulo.id, cantidad, id_sucursal)
    
    return total

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

def procesar_cambio_precio(form):
    #---------------------
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
    
    remito = RemitoSucursales.query.get(idremito)
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
    
    remito = RemitoSucursales.query.get(idremito)
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