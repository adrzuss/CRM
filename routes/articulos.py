from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, current_app, session
from werkzeug.utils import secure_filename
import os
from models.articulos import Articulo, Marca, Stock, Precio, ListasPrecios, Rubro, Balance, ItemBalance, ArticuloCompuesto, RemitoSucursales, ItemRemitoSucs, CambioPrecios, CambioPreciosItem
from models.configs import AlcIva, TipoArticulos, TipoBalances
from models.sucursales import Sucursales
from services.articulos import get_listado_precios, obtenerStockSucursales, update_insert_articulo_compuesto, actualizarPrecio
from services.articulos import actualizarStock, eliminarComp, obtenerArticulosMarcaRubro
from sqlalchemy import func, and_, case
from sqlalchemy.sql import text
from utils.db import db
from utils.config import allowed_file
from utils.utils import check_session, convertir_decimal
from datetime import datetime

bp_articulos = Blueprint('articulos', __name__, template_folder='../templates/articulos')

@bp_articulos.route('/articulos')
@check_session
def articulos():
    #articulos = Articulo.query.all()
    
    articulos = (db.session.query(
            Articulo.id,
            Articulo.detalle,
            Articulo.codigo,
            Articulo.costo,
            Articulo.es_compuesto,
            Articulo.imagen,
            Rubro.nombre.label('rubro'),
            Marca.nombre.label('marca')
            ).join(
                Rubro, and_(Articulo.idrubro == Rubro.id)
            ).join(
                Marca, and_(Articulo.idmarca == Marca.id)    
            ).order_by(
                Articulo.id    
            ).all()
        )
    
    marcas = Marca.query.all()
    rubros = Rubro.query.all()
    ivas = AlcIva.query.all()
    tipoarticulos = TipoArticulos.query.all()
    listas_precio = ListasPrecios.query.all()
    return render_template('articulos.html', articulos=articulos, rubros=rubros, marcas=marcas, ivas=ivas, tipoarticulos=tipoarticulos, listas_precio=listas_precio)

@bp_articulos.route('/add_articulo', methods=['POST'])
@check_session
def add_articulo():
    #FIXME al agregar articulo insertar stcok en cero
    codigo = request.form['codigo']
    detalle = request.form['detalle']
    costo = request.form['costo']
    idiva = request.form['idiva']
    idmarca = request.form['idmarca']
    idTipoArticulo = request.form['idtipoarticulo']
    esCompuesto = request.form.get("es_compuesto") != None
    idrubro = request.form['idrubro']
    
    # Manejar la imagen
    if 'imagen' not in request.files:
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
    articulo = Articulo(codigo, detalle, costo, idiva, idrubro, idmarca, idTipoArticulo, filename, esCompuesto)
    db.session.add(articulo)
    db.session.commit()
    idarticulo = articulo.id
        
    items = request.form  # Obtener todo el formulario
    item_count = 0  # Contador de items agregados
    item_count = len([key for key in items.keys() if key.startswith('precio') and key.endswith('[precio]')])
        
    for i in range(item_count):
        try:
            idlista = request.form[f'precio[{i+1}][idlista]']
            pvp = request.form[f'precio[{i+1}][precio]']
            if (idlista != None) and (pvp != None):
                precio = Precio(idlista, idarticulo, pvp, datetime.now())
                db.session.add(precio)
                db.session.commit()
        except Exception as e:
            flash(f'Error grabando precios {e}', 'error')    
        
    flash('Articulo agregado')
    return redirect('/articulos')
    
     
@bp_articulos.route('/update_articulo/<id>', methods=['GET', 'POST'])
@check_session
def update_articulo(id):
    marcas = Marca.query.all()
    ivas = AlcIva.query.all()
    rubros = Rubro.query.all()
    tipoarticulos = TipoArticulos.query.all()
    articulo = Articulo.query.get(id)
    listas_precios = db.session.query(
                ListasPrecios.id.label('id'),
                ListasPrecios.nombre.label('nombre'),
                ListasPrecios.markup.label('markup'),
                func.coalesce(Precio.precio, 0).label('precio'),
                Precio.ult_modificacion.label('ult_modificacion')
                ).outerjoin(
                    Precio, and_(ListasPrecios.id == Precio.idlista, Precio.idarticulo == articulo.id)
                ).filter(
                    Articulo.id == articulo.id
                ).order_by(
                    ListasPrecios.id
                ).all()
    #stocks = db.session.query(Stock).join(Articulo, Stock.idarticulo == Articulo.id).filter(Articulo.id == articulo.id)
    # Consulta para obtener el stock discriminado por sucursales
    stocks = (
        db.session.query(
            Stock.actual.label("stock_actual"),
            Stock.maximo.label("stock_maximo"),
            Stock.deseable.label("stock_deseable"),
            Stock.idsucursal.label("idsucursal"),
            Sucursales.nombre.label("nombre_sucursal")
        )
        .join(Articulo, Stock.idarticulo == Articulo.id)  # Vincular Stock con Articulo
        .join(Sucursales, Stock.idsucursal == Sucursales.id)  # Vincular Stock con Sucursales
        .filter(Articulo.id == articulo.id)  # Filtrar por el ID del artículo
        .all()  # Obtener los resultados
    )
    if request.method == 'GET':
        return render_template('upd-articulos.html', articulo=articulo, rubros=rubros, marcas=marcas, ivas=ivas, tipoarticulos=tipoarticulos, listas_precio=listas_precios, stocks=stocks)
    if request.method == 'POST':
        articulo.codigo = request.form['codigo']
        articulo.detalle = request.form['detalle']
        articulo.costo = request.form['costo']
        articulo.idiva = request.form['idiva']
        articulo.idtipoarticulo = request.form['idtipoarticulo']
        articulo.es_compuesto = request.form.get("es_compuesto") != None
        articulo.idmarca = request.form['idmarca']
        articulo.idrubro = request.form['idrubro']
        
        # Manejar la imagen
        if 'imagen' not in request.files:
            flash('No file part')
            return redirect('/articulos')
            
        file = request.files['imagen']
            
        if file.filename != '':
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)  # Asegura que el nombre del archivo sea seguro para el sistema de archivos
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))  # Guarda el archivo en la carpeta de subida
                    
                #imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)  # Guarda la ruta del archivo en la base de datos
                imagen_path = filename
                articulo.imagen = imagen_path
            else:
                flash('Tipo de archivo inválido')
                return redirect('/articulos')    
        
        db.session.commit()
            
        items = request.form  # Obtener todo el formulario
        item_count = 0  # Contador de items agregados
        item_count = len([key for key in items.keys() if key.startswith('precio') and key.endswith('[precio]')])
            
        for i in range(item_count):
            try:
                idlista = request.form[f'precio[{i+1}][idlista]']
                pvp = request.form[f'precio[{i+1}][precio]']
                if (idlista != None) and (pvp != None):
                    precio = Precio.query.get((idlista, id))
                    if precio:
                        precio.precio = pvp 
                        precio.ult_modificacion = datetime.now()
                    else:    
                        precio = Precio(idlista, articulo.id, pvp, datetime.now())
                        db.session.add(precio)
                    db.session.commit()
            except Exception as e:
                flash(f'Error grabando precios {e}', 'error')
        """
        if 'deseable' in items:        
            stock_deseable = convertir_decimal(request.form['deseable'])
            stock_maximo = convertir_decimal(request.form['maximo'])
            stocks[0].deseable = stock_deseable
            stocks[0].maximo = stock_maximo
            db.session.commit()
        """        
        flash('Articulo grabado')
        return redirect('/articulos')

# ------------------- Composición de artículos -----------------------------        
@bp_articulos.route('/update_composicion/<id>', methods=['GET', 'POST'])
@check_session
def update_composicion(id):        
    idartComp = request.form['codigo']   
    cantidad = request.form['cantidad']
    cant = convertir_decimal(cantidad)
    update_insert_articulo_compuesto(id, idartComp, cant)
    flash(f'Articulo agregado como composición')
    return redirect(url_for('articulos.componer_art', id=id))

@bp_articulos.route('/componer_art/<int:id>', methods=['GET', 'POST'])
@check_session
def componer_art(id):
    articulo = Articulo.query.get(id)
    compuestos = db.session.query(ArticuloCompuesto.idarticulo, 
                                 ArticuloCompuesto.idart_comp,
                                 ArticuloCompuesto.cantidad,
                                 Articulo.codigo,
                                 Articulo.detalle,
                                 Marca.nombre.label('marca'),
                                 Rubro.nombre.label('rubro')
                                ).join(Articulo, ArticuloCompuesto.idart_comp == Articulo.id
                                ).join(Marca, Articulo.idmarca == Marca.id
                                ).join(Rubro, Articulo.idrubro == Rubro.id
                                ).filter(ArticuloCompuesto.idarticulo == articulo.id).all()
    return render_template('componer-art.html', articulo=articulo, compuestos=compuestos)

@bp_articulos.route('/eliminarCompuesto/<int:idarticulo>/<int:idart_comp>')
@check_session
def eliminarCompuesto(idarticulo, idart_comp):
    sigueCompuesto = eliminarComp(idarticulo, idart_comp) 
    if sigueCompuesto:
        flash('Producto compositor eliminado')
    else:
        flash('Producto compositor eliminado, ya no es mas compuesto')
    return redirect(url_for('articulos.componer_art', id=idarticulo))
# ------------------- Cambio de precio -----------------------------

@bp_articulos.route('/cambio_precio', methods=['GET', 'POST'])
@check_session
def cambio_precio():
    print(f'cambio de precio')
    print(request.method)
    if request.method == 'POST':
        #---------------------
        fecha = request.form['fecha']
        idusuario = session['user_id']
        idsucursal = session['id_sucursal']
        idlista = request.form['lista_precio']
                                            
        nuevo_cambio_precio = CambioPrecios(fecha, idsucursal, idusuario, idlista)
        db.session.add(nuevo_cambio_precio)
        db.session.flush()

        idcambioprecio = nuevo_cambio_precio.id
        
        # Procesar los items
        items = request.form
        for key, value in items.items():
            if key.startswith('items') and key.endswith('[codigo]'):
                # Extraer el índice del item
                index = key.split('[')[1].split(']')[0]
                codigo = value
                precio_actual = request.form.get(f'items[{index}][precio_actual]')
                precio_nuevo = request.form.get(f'items[{index}][precio_nuevo]')

                # Obtener el artículo por código
                articulo = db.session.query(Articulo).filter_by(codigo=codigo).first()
                if articulo:
                    # Crear un registro de item_cambio_precios
                    nuevo_item = CambioPreciosItem(
                        idcambioprecio=idcambioprecio,
                        idarticulo=articulo.id,
                        precio_de=precio_actual,
                        precio_a=precio_nuevo
                    )
                    db.session.add(nuevo_item)
                    actualizarPrecio(idlista, articulo.id, precio_nuevo)

        # Confirmar los cambios
        db.session.commit()
        #---------------------
        flash('Cambio de precio realizado')
        return redirect(url_for('index'))
    else:
        listas_precios = ListasPrecios.query.all()
        rubros = Rubro.query.all()
        marcas = Marca.query.all()
        return render_template('cambio-precio.html', listaRubros = rubros, listaMarcas = marcas, listas_precios=listas_precios, )


"""
filtra los articulos según las condiciones de la petición
para pasarlos a la carga de precios
"""
@bp_articulos.route('/filtrar_articulos/<int:marca>/<int:rubro>/<int:lista_precio>/<int:porcentaje>')
def filtrar_articulos(marca, rubro, lista_precio, porcentaje):
    resultado = obtenerArticulosMarcaRubro(marca, rubro, lista_precio, porcentaje)
    return jsonify(success=True, articulos=resultado)

    
@bp_articulos.route('/articulo/<string:codigo>/<int:idlista>')
@check_session
def get_articulo(codigo, idlista):
    # Buscar el artículo por código
    articulo = Articulo.query.filter_by(codigo=codigo).first()
    
    if not articulo:
        return jsonify(success=False, articulo={}), 404
    
    # Obtener el precio del artículo según la lista especificada (idlista)
    # Si la lista es 0 es porque vengo desde las compra 
    if idlista > 0 :
        precio = Precio.query.filter_by(idarticulo=articulo.id, idlista=idlista).first()
    
        # Verificar si se encontró un precio para el idlista especificado
        if not precio:
            return {"error": "Precio no disponible para el artículo en la lista solicitada"}, 404
        # Devolver la información requerida
        return jsonify(success=True, articulo={"id": articulo.id, "codigo": articulo.codigo, "detalle": articulo.detalle, "costo": articulo.costo, "precio": precio.precio})
    else:    
        # Devolver la información requerida
        return jsonify(success=True, articulo={"id": articulo.id, "codigo": articulo.codigo, "detalle": articulo.detalle, "costo": articulo.costo})
    
    
@bp_articulos.route('/get_articulos')
@check_session
def get_articulos():
    # Buscar el artículo por detalle
    detalle = request.args.get('detalle', '')
    idlista = request.args.get('idlista', '')
    if detalle and idlista:
        if idlista != "0":
            articulos = db.session.query(Articulo.id,
                                         Articulo.codigo,
                                         Articulo.detalle,
                                         Articulo.costo,
                                         Precio.precio
                                         ).join(Precio, Precio.idarticulo == Articulo.id).filter(Articulo.detalle.like(f"%{detalle}%"), Precio.idlista == idlista).all()
        else:
            articulos = db.session.query(Articulo.id,
                                         Articulo.codigo,
                                         Articulo.detalle,
                                         Articulo.costo,
                                         Articulo.costo.label('precio'),
                                         ).filter(Articulo.detalle.like(f"%{detalle}%")).all()    
    else:
        articulos = []
    return jsonify([{'id': a.id, 'codigo': a.codigo, 'detalle': a.detalle, 'costo': a.costo, 'precio': a.precio} for a in articulos])
    
@bp_articulos.route('/lst_precios', methods=['GET', 'POST']) 
@check_session
def lst_precios():
    listas_precios = ListasPrecios.query.all()
    if request.method == 'GET':
        listado = []
    else:        
        idlista = request.form['idlista']
        if idlista :
            listado = get_listado_precios(idlista)
        else:
            listado = []    
    return render_template('precios-articulos.html', listas_precios=listas_precios, listado=listado)

@bp_articulos.route('/lst_compuestos')
@check_session
def lst_compuestos():
    try:
        # Ejecutar el procedimiento almacenado
        resultado = db.session.execute(text("CALL lst_compuesto()"))
        
        # Procesar los resultados
        listado = resultado.fetchall()
        print(listado)
        # Cerrar el resultado
        resultado.close()
        
        # Retornar los datos procesados
        return render_template('compuestos-articulos.html', listado=listado)
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None
    

@bp_articulos.route('/stock_art') 
@check_session
def stock_art():
    listado = db.session.query(
        Articulo.id,
        Articulo.codigo,
        Articulo.detalle,
        Stock.actual,
        Stock.maximo,
        Stock.deseable
    ).join(
        Stock, Articulo.id == Stock.idarticulo
    ).filter(
        Stock.idsucursal == session['id_sucursal']    
    ).all()  
    return render_template('stock-articulos.html', nombre_sucursal=session['nombre_sucursal'], listado=listado)

@bp_articulos.route('/stock_art_faltantes') 
@check_session
def stock_art_faltantes():
    listado = db.session.query(
        Articulo.id,
        Articulo.codigo,
        Articulo.detalle,
        Stock.actual,
        Stock.maximo,
        Stock.deseable
    ).join(
        Stock, Articulo.id == Stock.idarticulo
    ).filter(
        Stock.actual <= 0     
    ).all()  
    return render_template('stock-articulos.html', listado=listado)


@bp_articulos.route('/stock_faltantes') 
@check_session
def stock_faltantes():
    listado = db.session.query(
        Articulo.id,
        Articulo.codigo,
        Articulo.detalle,
        Stock.actual,
        Stock.maximo,
        Stock.deseable
    ).join(
        Stock, Articulo.id == Stock.idarticulo
    ).filter(Stock.actual <= 0
    ).all()  
    return render_template('stock-articulos.html', listado=listado)

@bp_articulos.route('/stock_sucursales') 
@check_session
def stock_sucursales():
    resultado, column_names = obtenerStockSucursales()
    return render_template('stock-sucursales.html', listado=resultado, columnas=column_names)
    
#------------- Marcas y Rubros ---------------------        
@bp_articulos.route('/rubros_marcas')    
@check_session
def rubros_marcas():    
    rubros = Rubro.query.all()
    marcas = Marca.query.all()
    return render_template('rubros-marcas.html', rubros=rubros, marcas=marcas)
    
#------------- Marcas ---------------------    
@bp_articulos.route('/marcas')    
@check_session
def marcas():
    marcas = Marca.query.all()
    return render_template('marcas.html', marcas=marcas)

@bp_articulos.route('/add_marca', methods=['POST'])
@check_session
def add_marca():
    det_marca = request.form["marca"]
    marca = Marca(det_marca)
    db.session.add(marca)
    db.session.commit()
    flash('Marca agregada')
    return redirect(url_for('articulos.rubros_marcas'))

#------------- Rubros ---------------------    
@bp_articulos.route('/rubros')    
@check_session
def rubros():
    rubro = Rubro.query.all()
    return render_template('rubros.html', rubro=rubro)

@bp_articulos.route('/add_rubro', methods=['POST'])
@check_session
def add_rubro():
    det_rubro = request.form["rubro"]
    rubro = Rubro(det_rubro)
    db.session.add(rubro)
    db.session.commit()
    flash('Rubro agregado')
    return redirect(url_for('articulos.rubros_marcas'))

@bp_articulos.route('/ing_balance', methods=['GET', 'POST'])
@check_session
def ing_balance():
    if request.method == 'POST':
        fecha = request.form['fecha']
        nuevo_balance = Balance(idUsuario=session['user_id'], fecha=fecha, tipo_balance=1)
        db.session.add(nuevo_balance)
        db.session.commit()

        idbalance = nuevo_balance.id
        
        items = request.form  # Obtener todo el formulario
        item_count = 0  # Contador de items agregados

        item_count = len([key for key in items.keys() if key.startswith('items') and key.endswith('[idarticulo]')])
        idstock = current_app.config['IDSTOCK']

        for i in range(item_count):
            idarticulo = request.form[f'items[{i}][idarticulo]']
            cantidad = int(request.form[f'items[{i}][cantidad]'])
            articulo = db.session.query(Articulo.id, Articulo.costo).filter(Articulo.codigo == idarticulo).first()
            precio_unitario = articulo.costo if articulo else 0
            precio_total = precio_unitario * cantidad

            nuevo_item = ItemBalance(idbalance=idbalance, idarticulo=articulo.id, cantidad=cantidad, precio_unitario=precio_unitario, precio_total=precio_total)
            db.session.add(nuevo_item)
            # Actualizar la tabla de stocks
            actualizarStock(idstock, articulo.id, cantidad, session['id_sucursal'])
            
        
        nuevo_balance = Balance.query.get(idbalance)
                
        db.session.commit()

        flash('Balance grabado')
        
        return redirect(url_for('index'))
    else:
        tipoBalances = TipoBalances.query.all()
        for tipo in tipoBalances:
            print(tipo.nombre)
        return render_template('ing-balance.html', tipoBalances=tipoBalances)

# -------------------- Remitos a sucursales --------------------

@bp_articulos.route('/remitos_sucursales', methods=['GET', 'POST'])
@check_session
def remitos_sucursales():
    if request.method == 'POST':
        idsucursal = session['id_sucursal']
        iddestino = request.form['iddestino']
        fecha = request.form['fecha']
                
        nuevo_remito = RemitoSucursales(idsucursal=idsucursal, iddestino=iddestino, fecha=fecha, idusuario=session['idusuario'])
        db.session.add(nuevo_remito)
        db.session.commit()

        idremito = nuevo_remito.id
        
        items = request.form  # Obtener todo el formulario
        item_count = 0  # Contador de items agregados

        item_count = len([key for key in items.keys() if key.startswith('items') and key.endswith('[idarticulo]')])
        idstock = current_app.config['IDSTOCK']

        for i in range(item_count):
            idarticulo = request.form[f'items[{i}][idarticulo]']
            cantidad = int(request.form[f'items[{i}][cantidad]'])
            articulo = db.session.query(Articulo.id, Articulo.costo).filter(Articulo.codigo == idarticulo).first()
            
            nuevo_item = ItemRemitoSucs(idremito=idremito, idarticulo=articulo.id, cantidad=cantidad)
            db.session.add(nuevo_item)
            # Actualizar la tabla de stocks
            actualizarStock(idstock, articulo.id, -cantidad, session['id_sucursal'])
            actualizarStock(idstock, articulo.id, cantidad, iddestino)
                
        db.session.commit()

        flash('Remito a sucursal grabado')
        
        return redirect(url_for('index'))
    else:
        sucursales = Sucursales.query.all()
        return render_template('ing-remitos-sucursales.html', sucursales=sucursales)
        