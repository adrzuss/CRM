from sqlalchemy import func, and_, text
from models.ventas import Factura, PagosFV
from models.proveedores import FacturaC, PagosFC
from models.configs import PagosCobros
from utils.db import db
from utils.utils import format_currency

def obtener_total_ventas_por_tipo_ingreso(desde, hasta, usuario=0):
    # Realizamos el JOIN entre las tablas y agrupamos por el tipo de ingreso
    if usuario == 0:
            resultados = db.session.query(
            PagosCobros.pagos_cobros.label('tipo_ingreso'),  # Nombre del tipo de ingreso
            func.sum(PagosFV.total).label('total_ingreso')   # Suma de los totales
            ).join(PagosFV, PagosFV.idpago == PagosCobros.id).join(Factura, Factura.id == PagosFV.idfactura).filter(Factura.fecha.between(desde, hasta)).group_by(PagosCobros.pagos_cobros).all()
    else:    
        resultados = db.session.query(
            PagosCobros.pagos_cobros.label('tipo_ingreso'),  # Nombre del tipo de ingreso
            func.sum(PagosFV.total).label('total_ingreso')   # Suma de los totales
            ).join(PagosFV, PagosFV.idpago == PagosCobros.id).join(Factura, and_(Factura.id == PagosFV.idfactura , Factura.idusuario == usuario)).filter(Factura.fecha.between(desde, hasta)).group_by(PagosCobros.pagos_cobros).all()
    return resultados

def obtener_total_compras_por_tipo_ingreso(desde, hasta, usuario=0):
    # Realizamos el JOIN entre las tablas y agrupamos por el tipo de ingreso
    if usuario == 0:
            resultados = db.session.query(
            PagosCobros.pagos_cobros.label('tipo_ingreso'),  # Nombre del tipo de ingreso
            func.sum(PagosFC.total).label('total_ingreso')   # Suma de los totales
            ).join(PagosFC, PagosFC.idpago == PagosCobros.id).join(FacturaC, FacturaC.id == PagosFC.idfactura).filter(FacturaC.fecha.between(desde, hasta)).group_by(PagosCobros.pagos_cobros).all()
    else:    
        resultados = db.session.query(
            PagosCobros.pagos_cobros.label('tipo_ingreso'),  # Nombre del tipo de ingreso
            func.sum(PagosFC.total).label('total_ingreso')   # Suma de los totales
            ).join(PagosFC, PagosFC.idpago == PagosCobros.id).join(FacturaC, and_(FacturaC.id == PagosFC.idfactura , FacturaC.idusuario == usuario)).filter(FacturaC.fecha.between(desde, hasta)).group_by(PagosCobros.pagos_cobros).all()
    return resultados

def get_ventas_compras(desde, hasta):
    #obtiene los 10 articulos mas vendidos
    try:
        detalle = []
        valores = []
        #Ventas
        sql = "SELECT SUM(total) as total FROM facturav WHERE fecha BETWEEN :desde AND :hasta"
        params = {'desde': desde, 'hasta': hasta}
        resultado = db.session.execute(text(sql), params)
        resultado = resultado.fetchone()
        valores.append(resultado.total)
        detalle.append('Ingresos (Ventas)')
        #Compras
        sql = "SELECT SUM(total) as total FROM facturac WHERE fecha BETWEEN :desde AND :hasta and idplancuenta=0"
        params = {'desde': desde, 'hasta': hasta}
        resultado = db.session.execute(text(sql), params)
        resultado = resultado.fetchone()
        valores.append(resultado.total)
        detalle.append('Egresos (Compras)')
        #Gastos
        sql = "SELECT SUM(total) as total FROM facturac WHERE fecha BETWEEN :desde AND :hasta and idplancuenta>0"
        params = {'desde': desde, 'hasta': hasta}
        resultado = db.session.execute(text(sql), params)
        resultado = resultado.fetchone()
        valores.append(resultado.total)
        detalle.append('Egresos (Gastos)')
        return {
            'valores': valores,
            'detalle': detalle
        }    
    except Exception as e:
        print(f'error: {e}')
        valores = []
        detalle = []
        return {
            'valores': valores,
            'detalle': detalle
        }
         

def get_detalle_gastos(desde, hasta):
    #obtiene los 10 articulos mas vendidos
    try:
        detalle = []
        valores = []
        #Gastos
        sql = "SELECT SUM(f.total) as total, pc.nombre as nombre FROM facturac f join plan_ctas pc on f.idplancuenta = pc.id WHERE f.fecha BETWEEN :desde AND :hasta group by pc.nombre"
        params = {'desde': desde, 'hasta': hasta}
        resultados = db.session.execute(text(sql), params)
        resultados = resultados.fetchall()
        for resultado in resultados:
            valores.append(resultado.total)
            detalle.append(resultado.nombre)
        
        return {
            'valores': valores,
            'detalle': detalle
        }    
    except Exception as e:
        print(f'error: {e}')
        valores = []
        detalle = []
        return {
            'valores': valores,
            'detalle': detalle
        }
            
    
