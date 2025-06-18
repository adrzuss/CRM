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
    print(f'usuario: {usuario}')
    if (usuario != '' and usuario != 0):
        resultados = db.session.query(
            PagosCobros.pagos_cobros.label('tipo_ingreso'),  # Nombre del tipo de ingreso
            func.sum(PagosFC.total).label('total_ingreso')   # Suma de los totales
            ).join(PagosFC, PagosFC.idpago == PagosCobros.id).join(FacturaC, and_(FacturaC.id == PagosFC.idfactura , FacturaC.idusuario == usuario)).filter(FacturaC.fecha.between(desde, hasta)).group_by(PagosCobros.pagos_cobros).all()            
    else:    
        resultados = db.session.query(
            PagosCobros.pagos_cobros.label('tipo_ingreso'),  # Nombre del tipo de ingreso
            func.sum(PagosFC.total).label('total_ingreso')   # Suma de los totales
            ).join(PagosFC, PagosFC.idpago == PagosCobros.id).join(FacturaC, FacturaC.id == PagosFC.idfactura).filter(FacturaC.fecha.between(desde, hasta)).group_by(PagosCobros.pagos_cobros).all()
        
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
        try:
            sql = "SELECT SUM(f.total) as total, COUNT(ic.idarticulo) as articulos " \
                "FROM facturac f " \
                "JOIN itemsc ic ON f.id = ic.idfactura " \
                "WHERE f.fecha BETWEEN :desde AND :hasta and " \
                "f.idtipocomprobante IN (SELECT id_tipo_comp FROM tipo_comp_aplica WHERE id_tipo_oper = 2)" \
                "having COUNT(ic.idarticulo) > 0"
            params = {'desde': desde, 'hasta': hasta}
            resultado = db.session.execute(text(sql), params)
            resultado = resultado.fetchone()
            if resultado :
                valores.append(resultado.total)
                detalle.append('Egresos (Compras)')
        except Exception as e:
            valores.append(100)
            detalle.append(f'Compras error: {e}')
            print(f'Error obteniendo egresos de compras: {e}')
        #Gastos
        try:
            sql = "SELECT SUM(f.total) as total " \
                "FROM facturac f " \
                "LEFT JOIN itemsc ic ON f.id = ic.idfactura " \
                "WHERE f.fecha BETWEEN :desde AND :hasta and " \
                "f.idtipocomprobante IN (SELECT id_tipo_comp FROM tipo_comp_aplica WHERE id_tipo_oper = 2) and " \
                "f.id NOT IN (SELECT DISTINCT idfactura FROM itemsc)"
            params = {'desde': desde, 'hasta': hasta}
            resultado = db.session.execute(text(sql), params)
            resultado = resultado.fetchone()
            if resultado :
                valores.append(resultado.total)
                detalle.append('Egresos (Gastos)')
        except Exception as e:
            valores.append(100)
            detalle.append(f'Gastos error: {e}')
            print(f'Error obteniendo egresos de gastos: {e}')
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
            
def get_saldo_ctas_ctes_cli():
    try:
        saldos_cta_cte = db.session.execute(text("CALL get_saldos_cc_cli(:empresa)"), {'empresa': 1}).fetchall()
        saldoActual = float(saldos_cta_cte[0][0])
        saldoVencido = float(saldos_cta_cte[0][1])
        return saldoActual, saldoVencido
    except Exception as e:
        print(f"Error obteniendo saldo ctas ctes clientes: {e}")
        return 0.0, 0.0    

def get_saldo_ctas_ctes_prov():
    try:
        saldos_cta_cte = db.session.execute(text("CALL get_saldos_cc_prov(:empresa)"), {'empresa': 1}).fetchall()
        saldoActual = float(saldos_cta_cte[0][0]) * -1
        saldoVencido = float(saldos_cta_cte[0][1]) * -1
        return saldoActual, saldoVencido
    except Exception as e:
        print(f"Error obteniendo saldo ctas ctes proveedores: {e}")
        return 0.0, 0.0    

def get_estado_resultado(desde, hasta):
    try:
        # Obtener la conexión y el cursor nativo
        connection = db.engine.raw_connection()
        try:
            cursor = connection.cursor()
            cursor.callproc('estado_resultado', [desde, hasta])

            # Primer resultset
            detalleVentas = cursor.fetchall()
                
            # Tercer resultset
            detalleCompras = []
            if cursor.nextset():
                detalleCompras = cursor.fetchall()

            return detalleVentas, detalleCompras
        finally:
            cursor.close()
            connection.close()
    except Exception as e:
        print(f"Error obteniendo estado resultado: {e}")
        return [], []