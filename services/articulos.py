from models.articulos import Articulo, Marca, Stock, Precio, Rubro, ArticuloCompuesto
from models.sucursales import Sucursales
from sqlalchemy import func, and_, join, case
from utils.db import db


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
        art_compuesto.cantidad = cantidad
    else:
        art_compuesto = ArticuloCompuesto(idarticulo, articulo.id, cantidad)
        db.session.add(art_compuesto)
    db.session.commit()
    