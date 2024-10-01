from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from models.articulos import Articulo, Marca, Stock, Precio, ListasPrecios, Rubro
from models.configs import AlcIva
from services.articulos import get_listado_precios
from sqlalchemy import func, and_, join
from utils.db import db
from utils.config import allowed_file

bp_articulos = Blueprint('articulos', __name__, template_folder='../templates/articulos')

@bp_articulos.route('/articulos')
def articulos():
    #articulos = Articulo.query.all()
    
    articulos = (db.session.query(
            Articulo.id,
            Articulo.detalle,
            Articulo.codigo,
            Articulo.costo,
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
    listas_precio = ListasPrecios.query.all()
    return render_template('articulos.html', articulos=articulos, rubros=rubros, marcas=marcas, ivas=ivas, listas_precio=listas_precio)

@bp_articulos.route('/add_articulo', methods=['POST'])
def add_articulo():
    #FIXME al agregar articulo insertar stcok en cero
    codigo = request.form['codigo']
    detalle = request.form['detalle']
    costo = request.form['costo']
    idiva = request.form['idiva']
    idmarca = request.form['idmarca']
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
    
    articulo = Articulo(codigo, detalle, costo, idiva, idrubro, idmarca, filename)
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
                precio = Precio(idlista, idarticulo, pvp)
                db.session.add(precio)
                db.session.commit()
        except Exception as e:
            flash(f'Error grabando precios {e}', 'error')    
        
    flash('Articulo agregado')
    return redirect('/articulos')
    
     
@bp_articulos.route('/update_articulo/<id>', methods=['GET', 'POST'])
def update_articulo(id):
    marcas = Marca.query.all()
    ivas = AlcIva.query.all()
    rubros = Rubro.query.all()
    articulo = Articulo.query.get(id)
    listas_precios = db.session.query(
                ListasPrecios.id.label('id'),
                ListasPrecios.nombre.label('nombre'),
                ListasPrecios.markup.label('markup'),
                func.coalesce(Precio.precio, 0).label('precio')
                ).outerjoin(
                    Precio, and_(ListasPrecios.id == Precio.idlista, Precio.idarticulo == articulo.id)
                ).filter(
                    Articulo.id == articulo.id
                ).order_by(
                    ListasPrecios.id
                ).all()
    stocks = db.session.query(Stock).join(Articulo, Stock.idarticulo == Articulo.id).filter(Articulo.id == articulo.id)
        
    if request.method == 'GET':
        return render_template('upd-articulos.html', articulo=articulo, rubros=rubros, marcas=marcas, ivas=ivas, listas_precio=listas_precios, stocks=stocks)
    if request.method == 'POST':
        articulo.codigo = request.form['codigo']
        articulo.detalle = request.form['detalle']
        articulo.costo = request.form['costo']
        articulo.idiva = request.form['idiva']
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
                    else:    
                        precio = Precio(idlista, articulo.id, pvp)
                        db.session.add(precio)
                    db.session.commit()
            except Exception as e:
                flash(f'Error grabando precios {e}', 'error')
        if 'deseable' in items:        
            stock_deseable = request.form['deseable']        
            stock_maximo = request.form['maximo']
            stocks[0].deseable = stock_deseable
            stocks[0].maximo = stock_maximo
            db.session.commit()
        flash('Articulo grabado')
        return redirect('/articulos')
        
                

@bp_articulos.route('/articulo/<string:codigo>/<int:idlista>')
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
    
@bp_articulos.route('/lst_precios', methods=['GET', 'POST']) 
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

@bp_articulos.route('/stock_art') 
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
    ).all()  
    return render_template('stock-articulos.html', listado=listado)

@bp_articulos.route('/stock_faltantes') 
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

    
#------------- Marcas y Rubros ---------------------        
@bp_articulos.route('/rubros_marcas')    
def rubros_marcas():    
    rubros = Rubro.query.all()
    marcas = Marca.query.all()
    return render_template('rubros-marcas.html', rubros=rubros, marcas=marcas)
    
#------------- Marcas ---------------------    
@bp_articulos.route('/marcas')    
def marcas():
    marcas = Marca.query.all()
    return render_template('marcas.html', marcas=marcas)

@bp_articulos.route('/add_marca', methods=['POST'])
def add_marca():
    det_marca = request.form["marca"]
    marca = Marca(det_marca)
    db.session.add(marca)
    db.session.commit()
    flash('Marca agregada')
    return redirect(url_for('articulos.rubros_marcas'))

#------------- Rubros ---------------------    
@bp_articulos.route('/rubros')    
def rubros():
    rubro = Rubro.query.all()
    return render_template('rubros.html', rubro=rubro)

@bp_articulos.route('/add_rubro', methods=['POST'])
def add_rubro():
    det_rubro = request.form["rubro"]
    rubro = Rubro(det_rubro)
    db.session.add(rubro)
    db.session.commit()
    flash('Rubro agregado')
    return redirect(url_for('articulos.rubros_marcas'))