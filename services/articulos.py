from models.articulos import Articulo, Marca, Stock, Precio, ListasPrecios, Rubro
from sqlalchemy import func, and_, join
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
        