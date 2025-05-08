from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, current_app, session
from flask import g
from werkzeug.utils import secure_filename
import os
from models.articulos import Articulo, Marca, Stock, Precio, ListasPrecios, Rubro, ArticuloCompuesto
from models.configs import AlcIva, TipoArticulos, TipoBalances, AlcIB
from models.sucursales import Sucursales
from services.articulos import get_listado_precios, obtener_stock_sucursales, update_insert_articulo_compuesto, \
                               eliminarComp, obtenerArticulosMarcaRubro, procesar_nuevo_balance, \
                               procesar_articulo, procesar_cambio_precio, procesar_remito_a_sucursal, get_listado_articulos, \
                               get_listado_stock
from sqlalchemy import func, and_, case
from sqlalchemy.sql import text
from utils.db import db
from utils.config import allowed_file
from utils.utils import check_session, convertir_decimal, alertas_mensajes
from datetime import datetime

bp_articulos = Blueprint('articulos', __name__, template_folder='../templates/articulos')

@bp_articulos.route('/articulos')
@check_session
@alertas_mensajes
def articulos():
    marcas = Marca.query.order_by(Marca.nombre).all()
    rubros = Rubro.query.order_by(Rubro.nombre).all()
    return render_template('articulos.html', rubros=rubros, marcas=marcas, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

#Esta funcion devulve los datos de los articulos paginados
#para asi poder manejar grandes cantidades de datos
@bp_articulos.route('/api/articulos', methods=['GET'])
@check_session
def api_articulos(): 
    # Obtener parámetros de DataTables
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)  # Índice del primer registro
    length = request.args.get('length', type=int)  # Número de registros por página
    search_value = request.args.get('search[value]', '', type=str)  # Valor de búsqueda
    idmarca = request.args.get('idmarca', type=int)
    idrubro = request.args.get('idrubro', type=int)
    order_column = request.args.get('order[0][column]', type=int)  # Índice de la columna
    order_dir = request.args.get('order[0][dir]', 'asc')  # Dirección del ordenamiento
    
    draw, total_records, total_records, data = get_listado_articulos(idmarca, idrubro, draw, search_value, start, length, order_column, order_dir)

    # Respuesta para DataTables
    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': total_records,  # Cambiar si aplicas filtros
        'data': data
    }
    return jsonify(response)

@bp_articulos.route('/add_articulo', methods=['POST'])
@check_session
def add_articulo():
    procesar_articulo(request.form)
    flash('Articulo agregado')
    return redirect('/articulos')
    
     
@bp_articulos.route('/update_articulo/<id>', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def update_articulo(id):
    marcas = Marca.query.order_by(Marca.nombre).all()
    ivas = AlcIva.query.all()
    ibs = AlcIB.query.all()
    rubros = Rubro.query.order_by(Rubro.nombre).all()
    tipoarticulos = TipoArticulos.query.all()
    
    if request.method == 'GET':
        if int(id) == 0:
            articulo = []
            listas_precios = ListasPrecios.query.all()
            stocks = []
        else:    
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
                    Stock.idstock.label("id"),
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
        return render_template('upd-articulos.html', articulo=articulo, rubros=rubros, marcas=marcas, ivas=ivas, ibs=ibs, tipoarticulos=tipoarticulos, listas_precio=listas_precios, stocks=stocks, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)
    
    if request.method == 'POST':
        
        if (id == '0'):
            try:
                codigo=request.form['codigo']
                detalle=request.form['detalle']
                costo=request.form['costo']
                exento=request.form['exento']
                impint=request.form['impint']
                idiva=request.form['idiva']
                idib=request.form['idib']
                idrubro=request.form['idrubro']
                idmarca=request.form['idmarca']
                idTipoArticulo=request.form['idtipoarticulo']
                esCompuesto=request.form.get("es_compuesto") != None
                articulo = Articulo(codigo=codigo, detalle=detalle, costo=costo, exento=exento, impint=impint, idiva=idiva, idib=idib, idrubro=idrubro, idmarca=idmarca, idtipoarticulo=idTipoArticulo, imagen='', es_compuesto=esCompuesto) 
                db.session.add(articulo)
                
            except Exception as e:
                flash(f'Error grabando articulo nuevo: {e}', 'error')
                return redirect('/articulos')
        else:
            try:
                articulo = Articulo.query.get(id)
                articulo.codigo = request.form['codigo']
                articulo.detalle = request.form['detalle']
                articulo.costo = request.form['costo']
                articulo.exento = request.form['exento']
                articulo.impint = request.form['impint']
                articulo.idiva = request.form['idiva']
                articulo.idib = request.form['idib']
                articulo.idtipoarticulo = request.form['idtipoarticulo']
                articulo.es_compuesto = request.form.get("es_compuesto") != None
                articulo.idmarca = request.form['idmarca']
                articulo.idrubro = request.form['idrubro']
            except Exception as e: 
                flash(f'Error grabando articulo modificado: {e}', 'error')
                return redirect('/articulos')
            
        db.session.flush()
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
        
        
        #Actauliza precios    
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
                
        #Actauliza stocks
        items = request.form  # Obtener todo el formulario
        item_count = 0  # Contador de items agregados
        item_count = len([key for key in items.keys() if key.startswith('stock') and key.endswith('[id]')])
        
        idsucursal = session['id_sucursal']    
        for i in range(item_count):
            try:
                idstock = request.form[f'stock[{i+1}][id]']
                deseable = request.form[f'stock[{i+1}][deseable]']
                maximo = request.form[f'stock[{i+1}][maximo]']
                if (idstock != None) and (deseable != None) and (maximo != None):
                    stock = Stock.query.get((idstock, id, idsucursal))
                    if stock:
                        stock.deseable = deseable
                        stock.maximo = maximo
                        db.session.commit()
                    else:    
                        stock = Stock(idstock, articulo.id, idsucursal, deseable, maximo)
                        db.session.add(stock)
                    db.session.commit()
            except Exception as e:
                flash(f'Error grabando stocks {e}', 'error')

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
@alertas_mensajes
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
    return render_template('componer-art.html', articulo=articulo, compuestos=compuestos, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

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
@alertas_mensajes
def cambio_precio():
    if request.method == 'POST':
        procesar_cambio_precio(request.form)
        #---------------------
        flash('Cambio de precio realizado')
        return redirect(url_for('index'))
    else:
        listas_precios = ListasPrecios.query.all()
        rubros = Rubro.query.all()
        marcas = Marca.query.all()
        return render_template('cambio-precio.html', listaRubros = rubros, listaMarcas = marcas, listas_precios=listas_precios, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)


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
    articulo = db.session.query(Articulo.id,
                                Articulo.codigo,
                                Articulo.detalle,
                                Articulo.costo,
                                Marca.nombre.label('marca')
                                ).outerjoin(Marca, Marca.id == Articulo.idmarca
                                ).filter(Articulo.codigo ==codigo).first()
    
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
        return jsonify(success=True, articulo={"id": articulo.id, "codigo": articulo.codigo, "marca": articulo.marca, "detalle": articulo.detalle, "costo": articulo.costo, "precio": precio.precio})   
    elif idlista == 0:
        # Obtener el precio del artículo según la lista especificada (idlista)
        # Si la lista es 0 es porque vengo desde las compra y en precio se pasa el costo
        return jsonify(success=True, articulo={"id": articulo.id, "codigo": articulo.codigo, "marca": articulo.marca, "detalle": articulo.detalle, "costo": articulo.costo, "precio": articulo.costo})
    else:    
        # Devolver la información requerida
        return jsonify(success=True, articulo={"id": articulo.id, "codigo": articulo.codigo, "marca": articulo.marca, "detalle": articulo.detalle, "costo": articulo.costo})
    
    
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
                                         Marca.nombre.label('marca'),
                                         Precio.precio
                                        ).join(Precio, Precio.idarticulo == Articulo.id
                                        ).outerjoin(Marca, Marca.id == Articulo.idmarca
                                        ).filter(Articulo.detalle.like(f"%{detalle}%"), Precio.idlista == idlista).all()
        else:
            articulos = db.session.query(Articulo.id,
                                         Articulo.codigo,
                                         Articulo.detalle,
                                         Articulo.costo,
                                         Marca.nombre.label('marca'),
                                         Articulo.costo.label('precio'),
                                         ).outerjoin(Marca, Marca.id == Articulo.idmarca
                                         ).filter(Articulo.detalle.like(f"%{detalle}%")).all()    
    else:
        articulos = []
    return jsonify([{'id': a.id, 'codigo': a.codigo, 'marca': a.marca, 'detalle': a.detalle, 'costo': a.costo, 'precio': a.precio} for a in articulos])
    
@bp_articulos.route('/lst_precios', methods=['GET']) 
@check_session
@alertas_mensajes
def lst_precios():
    listas_precios = ListasPrecios.query.all()
    lista_marcas = Marca.query.all()
    lista_rubros = Rubro.query.all()
    return render_template('precios-articulos.html', listas_precios=listas_precios, lista_marcas=lista_marcas, lista_rubros=lista_rubros, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

@bp_articulos.route('/api/lst_precios', methods=['GET']) 
@check_session
def api_lst_precios():
    # Obtener parámetros de DataTables aca_2
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', 0, type=int)  # Índice del primer registro
    length = request.args.get('length', 25, type=int)  # Número de registros por página
    search_value = request.args.get('search[value]', '', type=str)  # Valor de búsqueda
    idlista = request.args.get('idlista', type=int)
    idmarca = request.args.get('idmarca', type=int)
    idrubro = request.args.get('idrubro', type=int)
    
    order_column = request.args.get('order[0][column]', type=int)  # Índice de la columna
    order_dir = request.args.get('order[0][dir]', 'asc')  # Dirección del ordenamiento

    # Construir la consulta
    if not idlista :
        response = {
            'draw': draw,
            'recordsTotal': 0,
            'recordsFiltered': 0,  # Cambiar si aplicas filtros
            'data': []
        }
        
    draw, total_records, total_filtered, data = get_listado_precios(idlista, idmarca, idrubro, draw, search_value, start, length, order_column, order_dir)    
    resposne = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': total_filtered,  # Cambiar si aplicas filtros
        'data': data
    }    
    return jsonify(resposne)


@bp_articulos.route('/lst_compuestos')
@check_session
@alertas_mensajes
def lst_compuestos():
    try:
        # Ejecutar el procedimiento almacenado
        resultado = db.session.execute(text("CALL lst_compuesto()"))
        
        # Procesar los resultados
        listado = resultado.fetchall()
        # Cerrar el resultado
        resultado.close()
        
        # Retornar los datos procesados
        return render_template('compuestos-articulos.html', listado=listado, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None
    

@bp_articulos.route('/stock_art') 
@check_session
@alertas_mensajes
def stock_art():
    lista_marcas = Marca.query.all()
    lista_rubros = Rubro.query.all()
    return render_template('stock-articulos.html', nombre_sucursal=session['nombre_sucursal'], lista_marcas=lista_marcas, lista_rubros=lista_rubros, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

@bp_articulos.route('/api/lst_stock', methods=['GET']) 
@check_session
def api_lst_stock():
    # Obtener parámetros de DataTables aca_2
    
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', 0, type=int)  # Índice del primer registro
    length = request.args.get('length', 25, type=int)  # Número de registros por página
    search_value = request.args.get('search[value]', '', type=str)  # Valor de búsqueda
    idmarca = request.args.get('idmarca', type=int)
    idrubro = request.args.get('idrubro', type=int)
    
    order_column = request.args.get('order[0][column]', type=int)  # Índice de la columna
    order_dir = request.args.get('order[0][dir]', 'asc')  # Dirección del ordenamiento

    # Construir la consulta
    if (not idmarca)or(not idrubro) :
        response = {
            'draw': draw,
            'recordsTotal': 0,
            'recordsFiltered': 0,  # Cambiar si aplicas filtros
            'data': []
        }
        
    draw, total_records, total_filtered, data = get_listado_stock(idmarca, idrubro, draw, search_value, start, length, order_column, order_dir)    
    resposne = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': total_filtered,  # Cambiar si aplicas filtros
        'data': data
    }    
    return jsonify(resposne)


@bp_articulos.route('/stock_art_faltantes') 
@check_session
@alertas_mensajes
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
    return render_template('stock-articulos.html', listado=listado, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)


@bp_articulos.route('/stock_faltantes') 
@check_session
@alertas_mensajes
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
    return render_template('stock-articulos.html', listado=listado, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

@bp_articulos.route('/stock_sucursales') 
@check_session
@alertas_mensajes
def stock_sucursales():
    lista_marcas = Marca.query.all()
    lista_rubros = Rubro.query.all()
    sucursales = Sucursales.query.all()
    columnas = ['codigo', 'marca', 'rubro', 'detalle']
    for sucursal in sucursales:
        columnas.append(sucursal.nombre)
    return render_template('stock-sucursales.html', columnas=columnas, lista_marcas=lista_marcas, lista_rubros=lista_rubros, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

                          
@bp_articulos.route('/api/lst_stock_sucursales', methods=['GET']) 
@check_session
@alertas_mensajes
def api_lst_stock_sucursales():
    # Obtener parámetros de DataTables aca_2
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', 0, type=int)  # Índice del primer registro
    length = request.args.get('length', 25, type=int)  # Número de registros por página
    search_value = request.args.get('search[value]', '', type=str)  # Valor de búsqueda
    idmarca = request.args.get('idmarca', type=int)
    idrubro = request.args.get('idrubro', type=int)
    
    order_column = request.args.get('order[0][column]', type=int)  # Índice de la columna
    order_dir = request.args.get('order[0][dir]', 'asc')  # Dirección del ordenamiento

    # Construir la consulta
    if (not idmarca)or(not idrubro) :
        response = {
            'draw': draw,
            'recordsTotal': 0,
            'recordsFiltered': 0,  # Cambiar si aplicas filtros
            'data': []
        }
    try:
        # Obtener los datos de stock por sucursal
        # y aplicar los filtros de búsqueda y ordenamiento
        draw, total_records, total_filtered, data, columnas = obtener_stock_sucursales(idmarca, idrubro, draw, search_value, start, length, order_column, order_dir)    
        resposne = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_filtered,  # Cambiar si aplicas filtros
            'data': data
        }    
        return jsonify(resposne)
    except Exception as e:
        current_app.logger.error(f"Error en api_lst_stock_sucursales: {e}")
        return jsonify({'error': str(e)}), 500
    
#------------- Marcas y Rubros ---------------------        
@bp_articulos.route('/rubros_marcas/<int:id>/<string:tipo>', methods=['GET'])    
@bp_articulos.route('/rubros_marcas', methods=['GET'])        
@check_session
@alertas_mensajes
def rubros_marcas(id=None, tipo=None):    
    rubros = Rubro.query.all()
    marcas = Marca.query.all()
    if id and tipo:
        if tipo == 'marca':
            idrubro = None
            nombre_rubro = None            
            marca = Marca.query.get(id)
            if marca:
                idmarca = marca.id
                nombre_marca = marca.nombre
        elif tipo == 'rubro':
            idmarca = None
            nombre_marca = None
            rubro = Rubro.query.get(id)
            if rubro:
                idrubro = rubro.id
                nombre_rubro = rubro.nombre
    else:
        idmarca = None
        nombre_marca = None
        idrubro = None
        nombre_rubro = None            
    return render_template('rubros-marcas.html', rubros=rubros, idrubro=idrubro, nombre_rubro=nombre_rubro, marcas=marcas, idmarca=idmarca, nombre_marca=nombre_marca, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)
    
#------------- Marcas ---------------------    
@bp_articulos.route('/marcas')    
@check_session
@alertas_mensajes
def marcas():
    marcas = Marca.query.all()
    return render_template('marcas.html', marcas=marcas, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

@bp_articulos.route('/add_marca', methods=['POST'])
@check_session
def add_marca():
    idmarca = request.form["idmarca"]
    det_marca = request.form["marca"]
    try:
        if idmarca != '':
            marca = Marca.query.get(idmarca)
            if marca:
                marca.nombre = det_marca
                db.session.commit()
                flash('Marca modificada')
        else:
            marca = Marca(det_marca)
            db.session.add(marca)
            db.session.commit()
            flash('Marca agregada')
    except Exception as e:  
        flash(f'Error grabando marca: {e}', 'error')        
    return redirect(url_for('articulos.rubros_marcas'))

#------------- Rubros ---------------------    
@bp_articulos.route('/rubros')    
@check_session
def rubros():
    rubro = Rubro.query.all()
    return render_template('rubros.html', rubro=rubro, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

@bp_articulos.route('/add_rubro', methods=['POST'])
@check_session
def add_rubro():
    idrubro = request.form["idrubro"]
    det_rubro = request.form["rubro"]
    try:
        if idrubro != '':
            rubro = Rubro.query.get(idrubro)
            if rubro:
                rubro.nombre = det_rubro
                db.session.commit()
                flash('Rubro modificado')
        else:
            rubro = Rubro(det_rubro)
            db.session.add(rubro)
            db.session.commit()
            flash('Rubro agregado')
    except Exception as e:  
        flash(f'Error grabando rubro: {e}', 'error')        
    return redirect(url_for('articulos.rubros_marcas'))

@bp_articulos.route('/ing_balance', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def ing_balance():
    if request.method == 'POST':
        procesar_nuevo_balance(request.form, session['id_sucursal'])
        
        flash('Balance grabado')
        
        return redirect(url_for('index'))
    else:
        tipoBalances = TipoBalances.query.all()
        return render_template('ing-balance.html', tipoBalances=tipoBalances, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

# -------------------- Remitos a sucursales --------------------

@bp_articulos.route('/remitos_sucursales', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def remitos_sucursales():
    if request.method == 'POST':
        procesar_remito_a_sucursal(request.form)

        flash('Remito a sucursal grabado')
        
        return redirect(url_for('index'))
    else:
        sucursales = Sucursales.query.all()
        return render_template('ing-remitos-sucursales.html', sucursales=sucursales, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)
        