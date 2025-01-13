from flask import session
from models.articulos import Articulo, Marca, Stock, Precio, Rubro, ArticuloCompuesto
from models.sucursales import Sucursales
from sqlalchemy import func, and_, case, update
from sqlalchemy.exc import SQLAlchemyError
from utils.db import db
from datetime import datetime
from decimal import Decimal


def get_listado_precios(idlista):
    return db.session.query(
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
                ).order_by(
                    Articulo.id    
                ).all()

def alerta_stocks():
    cantidad = db.session.query(func.count(Articulo.id))\
                .join(Stock, Stock.idarticulo == Articulo.id)\
                .filter(Stock.actual <= 0).scalar()
    if cantidad > 0:            
        return cantidad, {'titulo': 'Stock', 'subtitulo': f'Hay {cantidad} artículos con stock en 0 o negativo', 'tipo': 'peligro', 'url': 'articulos.stock_faltantes'}
    else:
        return cantidad, {}
        
def obtenerStockSucursales():
    # Obtener la lista de sucursales
    sucursales = db.session.query(Sucursales.id, Sucursales.nombre).all()

    # Construir dinámicamente las columnas de la consulta
    columns = [
        Articulo.codigo.label("codigo"),
        Articulo.detalle.label("detalle"),
    ]

    for sucursal in sucursales:
        columns.append(
            func.coalesce(
                func.sum(
                    case(
                        (Stock.idsucursal == sucursal.id, Stock.actual), else_=0
                    )
                ), 0
        ).label(sucursal.nombre)  # Usar el nombre de la sucursal como label
    )
     
    # Construir la consulta con las columnas dinámicas
    pivot_query = (
        db.session.query(*columns)
        .join(Stock, Articulo.id == Stock.idarticulo)
        .filter(Stock.actual.isnot(None))
        .group_by(Articulo.codigo, Articulo.detalle)
        
    )
    resultado = pivot_query.all()
    column_names = [column["name"] for column in pivot_query.column_descriptions]
    return resultado, column_names

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
        #db.session.commit() 
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
    db.session.execute(
        update(Precio).
        where(Precio.idlista == idlista, Precio.idarticulo == idarticulo).
        values(precio=precio_nuevo, ult_modificacion=datetime.now())    
    )   
    
def obtenerArticulosMarcaRubro(marca, rubro, lista_precio, porcentaje):
    print('empezamos a filtrar')
    query = db.session.query(Articulo.id,
                             Articulo.codigo,
                             Articulo.detalle,
                             Precio.precio
                             ).join(Precio, Articulo.id == Precio.idarticulo)
    if marca:
        query = query.filter(Articulo.idmarca == marca)
    if rubro:
        query = query.filter(Articulo.idrubro == rubro)
    if lista_precio:
        query = query.filter(Precio.idlista == lista_precio)
    print('el query es:', query)
    articulos = query.all()
    print('Los articulos son:')
    print(articulos)
    resultado = []
    for articulo in articulos:
        print('articulo:', articulo)
        print('---------------------')
        precio_actual = articulo.precio
        precio_nuevo = Decimal(precio_actual) * Decimal((1 + porcentaje / 100))
        resultado.append({
            'codigo': articulo.codigo,
            'descripcion': articulo.detalle,
            'precio_actual':round(precio_actual, 2),
            'precio_nuevo': round(precio_nuevo, 2),
        })    
    return resultado    