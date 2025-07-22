from flask import session, current_app, flash, jsonify
import math
from sqlalchemy import text, func, and_, or_
from utils.db import db
from models.creditos import PlanesCreditos, DocumentosCreditos, EstadosCreditos, Creditos, DocumentosParaCreditos, \
                            CategoriasCreditos, VencimientosCreditos, GarantesCreditos, DocumentosDelCreditos, \
                            PagosCreditos    
from models.clientes import Clientes                            
from models.configs import Categorias
from services.ventas import procesar_recibo_cuota_credito
from datetime import date, timedelta
from decimal import Decimal
import os
from werkzeug.utils import secure_filename

def get_planes_creditos():
    planes_creditos = PlanesCreditos.query.all()
    return planes_creditos

def get_planes_creditos_categoria(categoria):
    planes_creditos = db.session.query(PlanesCreditos.id,
                                       PlanesCreditos.nombre,
                                       PlanesCreditos.tasa_interes,
                                       PlanesCreditos.cuotas,
                                       PlanesCreditos.anticipo,
                                       PlanesCreditos.garantes
                                       ).join(CategoriasCreditos, and_(PlanesCreditos.id == CategoriasCreditos.idplan, CategoriasCreditos.idcategoria == categoria)).all()
    return planes_creditos

def procesar_plan_credito(nombre, descripcion, tasa_interes, cuotas, anticipo, baja):
    try:
        # Validar los datos de entrada
        if not descripcion or not tasa_interes or not cuotas:
            flash('Todos los campos son obligatorios', 'error')
            return None
        
        # Crear una nueva instancia del plan de crédito
        plan_credito = PlanesCreditos(
            nombre=nombre,
            descripcion=descripcion,
            tasa_interes=float(tasa_interes),
            cuotas=int(cuotas),
            anticipo=bool(anticipo),
            baja=baja
        )
        
        # Agregar el plan a la base de datos
        db.session.add(plan_credito)
        db.session.commit()
        
        return plan_credito
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar el plan de crédito: {str(e)}', 'error')
        return None

def get_documentos_creditos():
    documentos_creditos = DocumentosCreditos.query.all()
    return documentos_creditos

def procesar_documento_creditos(nombre_documentos):
    try:
        # Validar los datos de entrada
        if not nombre_documentos:
            flash('Todos los campos son obligatorios', 'error')
            return None
        
        # Crear una nueva instancia del documento de crédito
        documento_credito = DocumentosCreditos(nombre=nombre_documentos)
        
        # Agregar el documento a la base de datos
        db.session.add(documento_credito)
        db.session.commit()
        
        return documento_credito
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar el documento de crédito: {str(e)}', 'error')
        return None

def get_docs_por_plan(idPlan = None):
    if idPlan:
        try:
            documentos_por_plan = db.session.query(DocumentosCreditos.id, 
                                                DocumentosCreditos.nombre,
                                                DocumentosParaCreditos.iddocumento_credito,
                                                DocumentosParaCreditos.idplan_credito
                                                ).outerjoin(DocumentosParaCreditos, and_(DocumentosCreditos.id == DocumentosParaCreditos.iddocumento_credito, DocumentosParaCreditos.idplan_credito == idPlan)).all()
        except Exception as e:
            print(f'Error al obtener los documentos para el plan: {e}')
            documentos_por_plan = []
    else:
        documentos_por_plan = []
    return documentos_por_plan
    
def get_cats_por_plan(idPlan = None):
    if idPlan:
        try:
            categorias_por_plan = db.session.query(Categorias.id, 
                                                Categorias.nombre,
                                                CategoriasCreditos.idcategoria,
                                                CategoriasCreditos.idplan
                                                ).outerjoin(CategoriasCreditos, and_(CategoriasCreditos.idcategoria == Categorias.id, CategoriasCreditos.idplan == idPlan)).all()
        except Exception as e:
            print(f'Error al obtener las categorias para el plan: {e}')
            categorias_por_plan = []
    else:
        categorias_por_plan = []
    return categorias_por_plan
    
def get_estados_creditos():
    estados_creditos = EstadosCreditos.query.all()
    return estados_creditos

def procesar_estado_creditos(nombre_estado, descripcion):
    try:
        # Validar los datos de entrada
        if not nombre_estado or not descripcion:    
            flash('Todos los campos son obligatorios', 'error')
            return None
        
        # Crear una nueva instancia del documento de crédito
        estado_credito = EstadosCreditos(nombre=nombre_estado, descripcion=descripcion)
        
        # Agregar el documento a la base de datos
        db.session.add(estado_credito)
        db.session.commit()
        
        return estado_credito
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar el estado de crédito: {str(e)}', 'error')
        return None
   
def limpiar_documentos_para_plan(idPlan):
    try:
        db.session.query(DocumentosParaCreditos).filter(DocumentosParaCreditos.idplan_credito == idPlan).delete()
    except Exception as e:
        db.session.rollback()
        print(f'Error al limpiar los documentos para el plan: {e}')
        raise Exception(f'Error al limpiar los documentos para el plan: {e}')
    
def limpiar_categorias_para_plan(idPlan):
    try:
        db.session.query(CategoriasCreditos).filter(CategoriasCreditos.idplan == idPlan).delete()
    except Exception as e:
        db.session.rollback()
        print(f'Error al limpiar las categorias para el plan: {e}')
        raise Exception(f'Error al limpiar las categorias para el plan: {e}')
    
def asignar_documento_para_plan(documento, idplan_credito):
    try:
        documento_por_plan_credito = DocumentosParaCreditos.query.filter_by(iddocumento_credito=documento, idplan_credito=idplan_credito).first()
        if not documento_por_plan_credito:
            documento_por_plan_credito = DocumentosParaCreditos(iddocumento_credito=documento, idplan_credito=idplan_credito)
            db.session.add(documento_por_plan_credito)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f'Error al asignar el documento a la plan: {e}')
        raise Exception(f'Error al asignar el documento a la plan: {e}')
    
def asignar_categoria_para_plan(categoria, idplan_credito):
    try:
        categoria_por_plan_credito = CategoriasCreditos.query.filter_by(idcategoria=categoria, idplan=idplan_credito).first()
        if not categoria_por_plan_credito:
            categoria_por_plan_credito = CategoriasCreditos(idcategoria=categoria, idplan=idplan_credito)
            db.session.add(categoria_por_plan_credito)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f'Error al asignar la categoria a la plan: {e}')
        raise Exception(f'Error al asignar la categoria a la plan: {e}')
    
def calcular_cuota_frances(monto, tasa_mensual, plazo_meses):
    """
    Calcula la cuota mensual fija bajo el sistema francés
    """
    if tasa_mensual == 0:
        return monto / plazo_meses
    cuota = monto * (tasa_mensual * (1 + tasa_mensual) ** plazo_meses) / \
            (((1 + tasa_mensual) ** plazo_meses) - 1)
    return cuota

def generar_cronograma_frances(monto, tasa_mensual, plazo_meses):
    cuota = calcular_cuota_frances(monto, tasa_mensual, plazo_meses)
    cuota_org = cuota
    saldo = monto
    cronograma = []
    saldoRedondeo = 0
    saldoRedondeo = (round(cuota, 2) - round(cuota,0)) * plazo_meses
        
    for mes in range(1, plazo_meses + 1):
        interes = saldo * tasa_mensual
        capital = cuota - interes
        if mes == plazo_meses:
            cuota = cuota + saldoRedondeo
            auxCuota = round(cuota, 2)
        else:
            auxCuota = round(cuota, 0)
        saldo -= capital
        
        cronograma.append({
            'nro_cuota': mes,
            'cuota' :round(auxCuota, 2),
            'interes':round(interes, 2),
            'capital':round(capital, 2),
            'saldo': round(saldo if saldo > 0 else 0, 2)
        })

    return cronograma, round(cuota_org, 2)

def grabar_cuotas(idcredito, idplan, cronograma):
    try:
        plan = PlanesCreditos.query.get(idplan)
        if not plan:
            raise Exception(f'Plan de crédito no encontrado: {idplan}')
        if plan.anticipo:
            # Si el plan tiene anticipo, la primera cuota es el anticipo
            for cuota in cronograma:
                vencimiento = VencimientosCreditos(
                    idcredito=idcredito,
                    numero_cuota=cuota['nro_cuota'],
                    monto=cuota['cuota'],
                    fecha_vencimiento=date.today() + timedelta(days=((cuota['nro_cuota']-1) * 30))  # Asumiendo vencimiento mensual
                )
                db.session.add(vencimiento)
        else:
            for cuota in cronograma:
                vencimiento = VencimientosCreditos(
                    idcredito=idcredito,
                    numero_cuota=cuota['nro_cuota'],
                    monto=cuota['cuota'],
                    fecha_vencimiento=date.today() + timedelta(days=(cuota['nro_cuota'] * 30))  # Asumiendo vencimiento mensual
                )
                db.session.add(vencimiento)        
        db.session.flush()
        #El commit lo hace actualizar_credito al grabar alguna posible modificación de crédito
        return True
    except Exception as e:
        db.session.rollback()
        print(f'Error al grabar las cuotas: {e}')
        raise Exception(f'Error al grabar las cuotas: {e}')
        
def actualizar_credito(idcredito, estado, monto_total, tasa_interes, cuotas, observaciones):
    try:
        credito = Creditos.query.get(idcredito)
        credito.estado = estado
        credito.monto_total = monto_total
        credito.tasa_interes = tasa_interes
        credito.cuotas = cuotas
        credito.observaciones = observaciones
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f'Error al actualizar el crédito: {e}')
        raise Exception(f'Error al actualizar el crédito: {e}')

def get_requisitos(idPlan):
    try:
        requisitos = db.session.query(DocumentosParaCreditos.idplan_credito,
                                    DocumentosCreditos.id, 
                                    DocumentosCreditos.nombre 
                                    ).join(DocumentosCreditos, and_(DocumentosParaCreditos.iddocumento_credito == DocumentosCreditos.id, DocumentosParaCreditos.idplan_credito == idPlan)
                                    ).all()
        return requisitos
    except Exception as e:
        print(f'Error al obtener los requisitos del plan: {e}')
        raise Exception(f'Error al obtener los requisitos del plan: {e}')
    
def generar_credito_cliente(form, files):
    idcliente = form.get('idcliente')
    idplan = form.get('idplan')
    cuotas = form.get('cuotas')
    monto_total = form.get('monto_total')
    monto_cuotas = form.get('cuota_credito')
    fecha_solicitud = date.today()
    fecha_inicio = date(1900,1,1)  # Asignar una fecha por defecto, puede ser modificada más adelante
    fecha_fin = date(1900,1,1)  # Asignar una fecha por defecto, puede ser modificada más adelante
    observaciones = form.get('observaciones', '')
    
    garantes = []
    i = 1
    while True:
        id_key = f'garante_id_{i}'
        nombre_key = f'garante_nombre_{i}'
        if id_key in form and nombre_key in form:
            garante_id = form[id_key]
            garante_nombre = form[nombre_key]
            if garante_id.strip() == "" and garante_nombre.strip() == "":
                break
            garantes.append({
                "id": garante_id,
                "nombre": garante_nombre
            })
            i += 1
        else:
            break
    
    documentos = []
    i = 1
    while True:
        file_key = f'documento{i}'
        id_key = f'idDocumento{i}'
        if file_key in files and id_key in form:
            archivo = files[file_key]
            id_documento = form[id_key]
            if archivo.filename == "":
                break
            documentos.append({
                "id": id_documento,
                "archivo": archivo
            })
            i += 1
        else:
            break   
    
    try:
        paso = 'Creando crédito'
        try:
            credito = Creditos(
                idsucursal=session['id_sucursal'],
                idcliente=int(idcliente),
                idplan=int(idplan),
                cuotas=int(cuotas),
                monto_total=Decimal(monto_total),
                estado=1,  # Asignar un estado por defecto, por ejemplo, 1 para "Solicitado"
                fecha_solicitud=date.today(),
                fecha_inicio=date(1900,1,1),
                fecha_fin=date(1900,1,1),
                idfactura=None,  # Asignar None si no hay factura asociada
                observaciones=observaciones
            )
        except Exception as e:
            paso = paso + f' - Error al crear el crédito: {e}'
            return None, paso    
        paso = 'Guardando crédito en la base de datos'
        db.session.add(credito)
        db.session.flush()
        idcredito = credito.id
        
        """
        Las cuotas las generamos al aprobar el crédito, no al crearlo
        # Generar las cuotas del crédito
        
        for x in range(int(cuotas)):
            cuota = VencimientosCreditos(
                idcredito=idcredito,
                nro_cuota=x + 1,
                monto=float(monto_cuotas),
                fecha_vencimiento=fecha_inicio + timedelta(days=(x + 1) * 30)  # Asumiendo vencimiento mensual
            )
            db.session.add(cuota)
        """    
        paso = 'Asignando garantes'
        for garante in garantes:
            garante_credito = GarantesCreditos(idcredito=idcredito, idgarante=int(garante['id']))
            db.session.add(garante_credito)    
        
        paso = 'Asignando documentos'
        if not os.path.exists(current_app.config['UPLOAD_FOLDER_CREDITOS']):
            print('El directorio no existe, creándolo...')
            os.makedirs(current_app.config['UPLOAD_FOLDER_CREDITOS'])

        for documento in documentos:
            archivo = documento['archivo']
            id_doc = documento['id']
            if archivo.filename and id_doc:
                # Guardar el archivo en el sistema de archivos
                filename = f"{idcredito}_{id_doc}_{archivo.filename}"
                filename = secure_filename(filename)  # Asegura que el nombre del archivo sea seguro para el sistema de archivos
                archivo.save(os.path.join(current_app.config['UPLOAD_FOLDER_CREDITOS'], filename))

                # Crear la relación entre el crédito y el documento
                try:
                    doc_credito = DocumentosDelCreditos(
                        idcredito=idcredito,
                        iddocumento_credito=id_doc,
                        documento=filename  # Guardar el nombre del archivo
                    )
                    db.session.add(doc_credito)
                except Exception as e:
                    paso = paso + f' - Error al crear el documento del crédito: {e}'    
                    print(f'Error al crear el documento del crédito: {e}')
                    return None, paso
        db.session.commit()
        return idcredito, 'ok'    
    except Exception as e:
        print(f'Error al crear el crédito: {e}')
        return None, f'Error al crear el crédito: {e} - {paso}'
    
def get_credito_by_id(id_credito):
    try:
        credito = db.session.query(Creditos.id,
                                   Creditos.idcliente,
                                   Creditos.idplan,
                                   Creditos.cuotas,
                                   Creditos.monto_total,
                                   Creditos.estado,
                                   Creditos.observaciones,
                                   Creditos.fecha_solicitud,
                                   EstadosCreditos.nombre.label('estado_credito'),
                                   Creditos.fecha_solicitud,
                                   Creditos.fecha_inicio,
                                   Creditos.fecha_fin,
                                   Creditos.idfactura,
                                   Clientes.nombre,
                                   Clientes.telefono,
                                   Clientes.idcategoria,
                                   Categorias.nombre.label('categoria'),
                                   PlanesCreditos.nombre.label('plan_nombre'),
                                   PlanesCreditos.tasa_interes,
                                   PlanesCreditos.cuotas.label('plan_cuotas'),
                                   PlanesCreditos.anticipo.label('plan_anticipo'),
                                   PlanesCreditos.garantes.label('plan_garantes'),
                                   ).join(PlanesCreditos, Creditos.idplan == PlanesCreditos.id
                                   ).join(Clientes, Creditos.idcliente == Clientes.id
                                   ).join(Categorias, Clientes.idcategoria == Categorias.id
                                   ).join(EstadosCreditos, Creditos.estado == EstadosCreditos.id       
                                   ).filter(Creditos.id == id_credito).first()
        if not credito:
            return None, None, None, None
        garantes = db.session.query(GarantesCreditos.idcredito,
                                    GarantesCreditos.idgarante,
                                    Clientes.nombre.label('garante_nombre')
                                    ).join(Clientes, GarantesCreditos.idgarante == Clientes.id
                                    ).filter(GarantesCreditos.idcredito == id_credito).all()
        documentos = db.session.query(DocumentosDelCreditos.idcredito,
                                      DocumentosDelCreditos.iddocumento_credito,
                                      DocumentosDelCreditos.documento,
                                      DocumentosCreditos.nombre.label('documento_nombre'),
                                     ).join(DocumentosCreditos, DocumentosDelCreditos.iddocumento_credito == DocumentosCreditos.id
                                     ).filter(DocumentosDelCreditos.idcredito == id_credito).all()
        cuotas_generadas = db.session.query(VencimientosCreditos.id,
                                            VencimientosCreditos.idcredito,
                                            VencimientosCreditos.numero_cuota,
                                            VencimientosCreditos.monto,
                                            VencimientosCreditos.fecha_vencimiento
                                            ).filter(VencimientosCreditos.idcredito == id_credito).all()                             
        return credito, garantes, documentos, cuotas_generadas
    except Exception as e:
        print(f'Error al obtener el crédito: {e}')
        return None, None, None
    
def get_creditos_by_estado(desde, hasta, *args):
    try:
        # Obtener los datos de los créditos nuevos
        nuevos = []
        for arg in args:
            if isinstance(arg, int):
                resultado = db.session.execute(text("CALL get_creditos_by_estado(:desde, :hasta,:estado)"), {'desde': desde, 'hasta': hasta, 'estado': arg}).fetchall()
                if resultado:
                    nuevos.extend(resultado)
        # Pasar los resultados a la plantilla
        if nuevos is None:
            return []   
        return nuevos
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None
    
def buscar_documento_descarga(idcredito, iddocumento):
    paso = db.session.query(DocumentosDelCreditos.documento
                           ).filter(and_(DocumentosDelCreditos.idcredito == idcredito, DocumentosDelCreditos.iddocumento_credito == iddocumento)
                           ).scalar()
    if not paso:
        return None
    paso = os.path.join(current_app.config['UPLOAD_FOLDER_CREDITOS'], paso)
    if not os.path.exists(paso):
        print(f"El archivo {paso} no existe.")
        return None
    return paso

def get_credito_by_idcliente(idcliente):
    try:
        credito = db.session.query(Creditos.id,
                                   Creditos.cuotas,
                                   Creditos.monto_total,
                                   Creditos.estado,
                                   ).filter(and_(Creditos.idcliente == idcliente, Creditos.estado == 3)).first()
        return credito
    except Exception as e:
        print(f'Error al obtener el crédito por cliente: {e}')
        return None
    
def vencimientos_cuotas_creditos(desde, hasta):
    try:
        vencimientos = db.session.execute(text("CALL get_vencimientos_cuotas_creditos(:desde, :hasta)"),{'desde': desde, 'hasta': hasta}).fetchall()
        return vencimientos
    except Exception as e:
        print(f"Error obteniendo vencimientos de cuotas de créditos: {e}")
        return []
    
def get_datos_creditos():
    hoy = date.today()
    try:
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        print(f"Inicio de semana: {inicio_semana}, Fecha de hoy: {hoy}")
        # Realizar la consulta para obtener el total de créditos de la semana
        creditos_semana = db.session.query(
            func.coalesce(func.sum(Creditos.monto_total), 0.0).label('total_creditos'),
            func.coalesce(func.count(Creditos.id), 0).label('cantidad_creditos')
        ).filter(
            Creditos.fecha_solicitud >= inicio_semana,
            Creditos.fecha_solicitud <= hoy,
            or_(Creditos.estado == 3, Creditos.estado == 5)  # Considerar solo créditos aprobados o facturados
        ).first()
        
    except Exception as e:
        print(f"Error obteniendo datos de créditos de la semana: {e}")
        return []
    
    try:
        inicio_mes = hoy.replace(day=1)
        print(f"Inicio del mes: {inicio_mes}, Fecha de hoy: {hoy}")
        # Realizar la consulta para obtener el total de créditos de la semana
        creditos_mes = db.session.query(
            func.coalesce(func.sum(Creditos.monto_total), 0.0).label('total_creditos'),
            func.coalesce(func.count(Creditos.id), 0).label('cantidad_creditos')
        ).filter(
            Creditos.fecha_solicitud >= inicio_mes,
            Creditos.fecha_solicitud <= hoy,
            or_(Creditos.estado == 3, Creditos.estado == 5)  # Considerar solo créditos aprobados o facturados
        ).first()

    except Exception as e:
        print(f"Error obteniendo datos de créditos del mes: {e}")
        return []
    resultado = {
        'creditos_semana': {
            'total_creditos': creditos_semana[0],
            'cantidad_creditos': creditos_semana[1]
        },
        'creditos_mes': {
            'total_creditos': creditos_mes[0],
            'cantidad_creditos': creditos_mes[1]
        }
    }
    return resultado


def get_cuotas_pendientes(idcliente):
    try:
        cuotasPendientes = db.session.execute(text("CALL get_cuotas_pendientes(:idcliente)"), {'idcliente': idcliente}).fetchall()
        if not cuotasPendientes:
            return []
        return cuotasPendientes
    except Exception as e:
        print(f"Error al obtener cuotas pendientes: {e}")
        return None
    
def generarRecibo(idCliente, cuotas, totalCuotas, efectivo, tarjeta, entidad):
    try:
        if not cuotas or idCliente is None:
            return jsonify(success=False, mensaje='Datos incompletos.')

        fecha = date.today()
        recibo = procesar_recibo_cuota_credito(idCliente, fecha, totalCuotas, efectivo, tarjeta, entidad)    
        for cuota in cuotas:
            idCredito = cuota.get('id')
            numeroCuota = cuota.get('numero')
            vencimiento = VencimientosCreditos.query.filter_by(idcredito=idCredito, numero_cuota=numeroCuota).first()
            pagoCredito = PagosCreditos(
                            idcredito=idCredito,
                            idvencimiento=vencimiento.id,
                            idfactura=recibo.id,
                            fecha_pago=fecha,
                            monto=vencimiento.monto,
                            punitorios=0.0
                        )
            db.session.add(pagoCredito)
            db.session.flush()
            # Aquí iría la lógica para procesar el cobro de cada cuota
            print(f"Cobrando cuota {numeroCuota} del crédito {idCredito} para el cliente {idCliente}. Registro de pago: {pagoCredito.id}")
        db.session.commit()
        
        return {'success':True, 'mensaje': 'Cuotas cobradas exitosamente.'}
    except Exception as e:
        print(f"Error al generar recibo: {e}")
        return {'success':False, 'mensaje': f'Error al generar recibo: {e}'}
