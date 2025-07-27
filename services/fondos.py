from sqlalchemy import func, and_, text
from models.ventas import Factura, PagosFV
from models.proveedores import FacturaC, PagosFC
from models.configs import PagosCobros, MonedasBilletes, TipoRendiciones, RendicionesCaja, ItemsRendicionesCaja
from models.sessions import Usuarios
from utils.db import db
from utils.utils import format_currency
from datetime import date

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
 
# -------------- rendiciones --------------

def getTiposRendiciones():
    tipos_rendicion = TipoRendiciones.query.all()
    return tipos_rendicion

def getMonedasBilletes():
    monedas_billetes = MonedasBilletes.query.all()
    return monedas_billetes

def getRendicion(idRendicion):
    rendicion = []
    valoresRendidos = []
    try:
        if int(idRendicion) > 0:
            rendicion = db.session.query(RendicionesCaja.id,
                                         RendicionesCaja.fecha,
                                         RendicionesCaja.idusuario,
                                         RendicionesCaja.idpunto_vta,
                                         RendicionesCaja.idsucursal,
                                         RendicionesCaja.idtipo_rendicion,
                                         RendicionesCaja.total_ventas,
                                         RendicionesCaja.total_efectivo,
                                         Usuarios.nombre) \
                                         .join(Usuarios, RendicionesCaja.idusuario == Usuarios.id) \
                                         .filter(RendicionesCaja.id == idRendicion) \
                                         .first()
        else:
            rendicion = []    
        valoresRendidos = db.session.execute(text("call get_items_rendidos(:idrendicion)"), {'idrendicion':idRendicion}).fetchall()
        return rendicion, valoresRendidos
    except Exception as e:
        print(f"Error obteniendo rendición: {e}")
        return [], []
    
def procesarRendicion(form):
    id = int(form['idRendicion'])
    fecha = form['fecha']
    usuario = form['usuario']
    tipoRendicion = form['tipo-rendicion']
    puntoVta = form['punto-vta']
    idSucursal = form['sucursal']
    try:
        rendicion = []
        if id > 0:
            rendicion = RendicionesCaja.query.get(id)
        if rendicion:
            rendicion.fecha = fecha
            rendicion.usuario = usuario
            rendicion.tipo_rendicion = tipoRendicion
            rendicion.punto_vta = puntoVta
            rendicion.idsucursal = idSucursal
        else:
            print('creando rendicion')
            rendicion = RendicionesCaja(fecha = fecha, idusuario = usuario, idpunto_vta = puntoVta, idsucursal = idSucursal, idtipo_rendicion = tipoRendicion, total_ventas = 0, total_efectivo = 0)
            db.session.add(rendicion)
        db.session.flush()
        procesados, mensaje = procesarItemsRendicon(rendicion.id, form)    
        if not procesados:
            raise Exception(f'Error procesando items: {mensaje}')
        db.session.commit()
        if rendicion.idtipo_rendicion == 3:
            setTotalRendidoTotalCobrado(rendicion.id)
        return rendicion.id, mensaje
    except Exception as e:
        print(f'error: {e}')
        return 0, f'error: {e}' 

def procesarItemsRendicon(idrendicion, form):
    try:
        # Eliminar todos los items de la caja
        ItemsRendicionesCaja.query.filter_by(idrendicion=idrendicion).delete()
        
        for key in form:
            if key.startswith('item') and key.endswith('[valor]'):
                index = key.split('[')[1].split(']')[0]
                idMoneda = form.get(f'item[{index}][idMoneda]', 0)
                cantidad = form.get(f'item[{index}][cantidad]', 0)
                # Procesar cada item: crear o actualizar ItemsRendicionesCaja
                if int(cantidad) > 0:
                    nuevo_item = ItemsRendicionesCaja(idrendicion=idrendicion, idmoneda_billete=idMoneda, cantidad=cantidad)
                    db.session.add(nuevo_item)
        return True, 'ok'    
            
    except Exception as e:
        print(f"Error procesando items: {e}")            
        return False, e
    
def setTotalRendidoTotalCobrado(idrendicion):
    try:
        db.session.execute(text("CALL update_total_rendido_cobrado(:idrendicion)"), {'idrendicion': idrendicion})
        db.session.commit()
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        raise Exception(f"Error al ejecutar el procedimiento almacenado: {e}")
    
def getRendiciones(desde, hasta):
    try:
        rendiciones = db.session.execute(text("CALL get_rendiciones(:desde, :hasta)"),
                         {'desde': desde, 'hasta': hasta}).fetchall()
        db.session.commit()
        return rendiciones
    except Exception as e:
        rendiciones = []
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return rendiciones
        