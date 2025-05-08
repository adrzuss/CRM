from flask import session, flash, redirect, request, current_app, jsonify
from werkzeug.utils import secure_filename
import os
from models.articulos import Articulo, Marca, Stock, Precio, Rubro, ArticuloCompuesto, Balance, ItemBalance, CambioPrecios, CambioPreciosItem, \
                             RemitoSucursales, ItemRemitoSucs
from models.sucursales import Sucursales
from utils.config import allowed_file
from sqlalchemy import func, and_, case, update, insert, text, desc
from sqlalchemy.exc import SQLAlchemyError
from utils.db import db
from datetime import datetime, date
from decimal import Decimal

def procesar_articulo(form, idarticulo):
    #FIXME al agregar articulo insertar stcok en cero
    codigo = form['codigo']
    detalle = form['detalle']
    costo = form['costo']
    impint = form['impint']
    exento = form['exento']
    idiva = form['idiva']
    idib = form['idib']
    idmarca = form['idmarca']
    idTipoArticulo = form['idtipoarticulo']
    esCompuesto = form.get("es_compuesto") != None
    idrubro = form['idrubro']
    
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
    articulo = Articulo(codigo=codigo, detalle=detalle, costo=costo, exento=exento, impint=impint, idiva=idiva, idib=idib, idrubro=idrubro, idmarca=idmarca, idTipoArticulo=idTipoArticulo, filename=filename, esCompuesto=esCompuesto)
    db.session.add(articulo)
    db.session.commit()
    idarticulo = articulo.id
        
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
            
def get_listado_articulos(idmarca, idrubro, draw, search_value, start, length, order_column, order_dir):            
     # Mapear el índice de la columna al nombre de la columna en la base de datos
    columns = ['codigo', 'rubro', 'marca', 'detalle', 'costo', 'es_compuesto']
    order_by = columns[order_column] if order_column < len(columns) else 'codigo'
    
    # Consulta base
    query = db.session.query(
        Articulo.id,
        Articulo.detalle,
        Articulo.codigo,
        Articulo.costo,
        Articulo.es_compuesto,
        Articulo.imagen,
        Rubro.nombre.label('rubro'),
        Marca.nombre.label('marca')
    ).join(
        Rubro, and_(Articulo.idrubro == Rubro.id, Rubro.id == idrubro if idrubro else True)
    ).join(
        Marca, and_(Articulo.idmarca == Marca.id, Marca.id == idmarca if idmarca else True)
    )

    # Aplicar búsqueda
    if search_value:
        query = query.filter(
            Articulo.detalle.ilike(f"%{search_value}%")
        )

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
            'es_compuesto': 'Si' if articulo.es_compuesto else 'No',
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
        return cantidad, {'titulo': 'Stock', 'subtitulo': f'Hay {cantidad} artículos con stock en 0 o negativo', 'tipo': 'peligro', 'url': 'articulos.stock_faltantes'}
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
            stock = Stock(idstock=idstock, idarticulo=idarticulo, idsucursal=idsucursal, actual=cantidad, maximo=0, deseable=0)
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
    except SQLAlchemyError as e:
        raise Exception(f"Error al actualizar el stock ({tipoActualizacion}): {e}")
            
            
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
                             ).outerjoin(Precio, and_(Articulo.id == Precio.idarticulo, Precio.idlista == lista_precio))
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
        if key.startswith('items') and key.endswith('[codigo]'):
            index = key.split('[')[1].split(']')[0]
            codigo = value
            cantidad = Decimal(form[f'items[{index}][cantidad]'])

            articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
            precio = Precio.query.filter_by(idarticulo=articulo.id, idlista=1).first()
            precio_unitario = precio.precio if precio else Decimal(0)
            precio_total = precio_unitario * cantidad

            nuevo_item = ItemBalance(idbalance=idbalance, idarticulo=articulo.id, cantidad=cantidad, precio_unitario=precio_unitario, precio_total=precio_total)
            db.session.add(nuevo_item)
            # Actualizar el stock
            actualizarStock(id_sucursal, articulo.id, cantidad, id_sucursal)
    
    return total

def get_stocks_negativos():
    sucursal = session['id_sucursal']
    stk_neg = db.session.execute(text("CALL get_stock_negativos(:sucursal)"),
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
    idsucursal = session['id_sucursal']
    iddestino = form['iddestino']
    fecha = form['fecha']
                
    nuevo_remito = RemitoSucursales(idsucursal=idsucursal, iddestino=iddestino, fecha=fecha, idusuario=session['user_id'])
    db.session.add(nuevo_remito)
    db.session.flush()
    idremito = nuevo_remito.id
        
    items = form  # Obtener todo el formulario
    idstock = current_app.config['IDSTOCK']
    for key, value in items.items():
        if key.startswith('items') and key.endswith('[codigo]'):
            index = key.split('[')[1].split(']')[0]
            codigo = value
            cantidad = Decimal(request.form[f'items[{index}][cantidad]'])
            articulo = db.session.query(Articulo.id, Articulo.costo).filter(Articulo.codigo == codigo).first()
            nuevo_item = ItemRemitoSucs(id=index, idremito=idremito, idarticulo=articulo.id, cantidad=cantidad)
            db.session.add(nuevo_item)
            # Actualizar la tabla de stocks
            actualizarStock(idstock, articulo.id, -cantidad, session['id_sucursal'])
            actualizarStock(idstock, articulo.id, cantidad, iddestino)
    db.session.commit()
    
def remitos_mercaderia():    
    pass