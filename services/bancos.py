# services/bancose.py

from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from utils.db import db
from models.bancos import Banco, BancoPropio, TipoMovBancos, BancoPropioProveedor  # Asumo que tus modelos están en models/banco_model.py
from models.proveedores import Proveedores
from decimal import Decimal


class BancoService:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los bancos activos (soft delete)"""
        try:
            return Banco.query.filter(Banco.baja == date(1900, 1, 1)).all()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error al obtener bancos: {str(e)}")

    @staticmethod
    def obtener_por_id(banco_id):
        """Obtiene un banco por ID"""
        try:
            return Banco.query.filter_by(id=banco_id, baja=date(1900, 1, 1)).first()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error al obtener banco: {str(e)}")

    @staticmethod
    def crear(nombre, direccion, telefono, email):
        """Crea un nuevo banco"""
        try:
            banco = Banco(
                nombre=nombre,
                direccion=direccion,
                telefono=telefono,
                email=email
            )
            db.session.add(banco)
            db.session.commit()
            return banco
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error al crear banco: {str(e)}")

    @staticmethod
    def actualizar(banco_id, nombre, direccion, telefono, email):
        """Actualiza un banco existente"""
        try:
            banco = Banco.query.filter_by(id=banco_id, baja=date(1900, 1, 1)).first()
            if not banco:
                raise Exception("Banco no encontrado")
            banco.nombre = nombre
            banco.direccion = direccion
            banco.telefono = telefono
            banco.email = email
            db.session.commit()
            return banco
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error al actualizar banco: {str(e)}")

    @staticmethod
    def eliminar(banco_id):
        """Elimina (baja lógica) un banco"""
        try:
            banco = Banco.query.filter_by(id=banco_id, baja=date(1900, 1, 1)).first()
            if not banco:
                raise Exception("Banco no encontrado")
            banco.baja = date.today()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error al eliminar banco: {str(e)}")


class BancoPropioService:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los movimientos bancarios activos"""
        try:
            return BancoPropio.query.filter(BancoPropio.baja == date(1900, 1, 1)).all()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error al obtener movimientos: {str(e)}")

    @staticmethod
    def obtener_por_id(movimiento_id):
        """Obtiene un movimiento por ID"""
        try:
            return BancoPropio.query.filter_by(id=movimiento_id, baja=date(1900, 1, 1)).first()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error al obtener movimiento: {str(e)}")

    @staticmethod
    def obtener_por_banco(banco_id, desde, hasta):
        """Obtiene todos los movimientos de un banco específico"""
        try:
            return db.session.query(BancoPropio.id,
                                    BancoPropio.fecha_emision,
                                    BancoPropio.fecha_vencimiento,
                                    TipoMovBancos.nombre.label('tipo_movimiento'),
                                    BancoPropio.nro_movimiento,
                                    BancoPropio.monto,
                                    BancoPropio.id_banco,
                                    Banco.nombre.label('banco'),
                                    Proveedores.nombre.label('proveedor'),
                                    
                                    ).join(Banco, BancoPropio.id_banco == Banco.id
                                    ).join(TipoMovBancos, BancoPropio.tipo_movimiento == TipoMovBancos.id
                                    ).outerjoin(BancoPropioProveedor, BancoPropioProveedor.id_banco_propio == BancoPropio.id       
                                    ).outerjoin(Proveedores, BancoPropioProveedor.id_proveedor == Proveedores.id
                                    ).filter(BancoPropio.id_banco==banco_id, 
                                             BancoPropio.baja==date(1900, 1, 1), 
                                             BancoPropio.fecha_emision >= desde, 
                                             BancoPropio.fecha_emision <= hasta
                                    ).all()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error al obtener movimientos del banco: {str(e)}")

    @staticmethod
    def crear(fecha_emision, fecha_vencimiento, tipo_movimiento, nro_movimiento, monto, id_banco):
        """Crea un nuevo movimiento bancario"""
        try:
            # Validar que el banco exista y esté activo
            banco = BancoService.obtener_por_id(id_banco)
            if not banco:
                raise Exception("El banco especificado no existe o está dado de baja.")

            movimiento = BancoPropio(
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                tipo_movimiento=tipo_movimiento,
                nro_movimiento=nro_movimiento,
                monto=Decimal(monto),
                id_banco=id_banco
            )
            db.session.add(movimiento)
            db.session.commit()
            return movimiento
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error al crear movimiento: {str(e)}")
            raise Exception(f"Error al crear movimiento: {str(e)}")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear movimiento: {str(e)}")
            raise Exception(f"Error al crear movimiento: {str(e)}")
    
    @staticmethod
    def crear_desde_op(idproveedor, fecha_emision, fecha_vencimiento, tipo_movimiento, nro_movimiento, monto, id_banco):
        """Crea un nuevo movimiento bancario enviado desde una orden de pago"""
        try:
            # Validar que el banco exista y esté activo
            banco = BancoService.obtener_por_id(id_banco)
            if not banco:
                raise Exception("El banco especificado no existe o está dado de baja.")

            movimiento = BancoPropio(
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                tipo_movimiento=tipo_movimiento,
                nro_movimiento=nro_movimiento,
                monto=Decimal(monto),
                id_banco=id_banco
            )
            db.session.add(movimiento)
            db.session.flush()
            bancoPropioProveedor = BancoPropioProveedor(id_banco_propio=movimiento.id, id_proveedor=idproveedor)
            db.session.add(bancoPropioProveedor)
            return movimiento
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error al crear movimiento: {str(e)}")
            raise Exception(f"Error al crear movimiento: {str(e)}")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear movimiento: {str(e)}")
            raise Exception(f"Error al crear movimiento: {str(e)}")
    

    @staticmethod
    def actualizar(movimiento_id, fecha_emision, fecha_vencimiento, tipo_movimiento, nro_movimiento, monto, id_banco):
        """Actualiza un movimiento bancario"""
        try:
            movimiento = BancoPropio.query.filter_by(id=movimiento_id, baja=date(1900, 1, 1)).first()
            if not movimiento:
                raise Exception("Movimiento no encontrado")

            banco = BancoService.obtener_por_id(id_banco)
            if not banco:
                raise Exception("El banco especificado no existe.")

            movimiento.fecha_emision = fecha_emision
            movimiento.fecha_vencimiento = fecha_vencimiento
            movimiento.tipo_movimiento = tipo_movimiento
            movimiento.nro_movimiento = nro_movimiento
            movimiento.monto = Decimal(monto)
            movimiento.id_banco = id_banco

            db.session.commit()
            return movimiento
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error al actualizar movimiento: {str(e)}")

    @staticmethod
    def eliminar(movimiento_id):
        """Elimina (baja lógica) un movimiento bancario"""
        try:
            movimiento = BancoPropio.query.filter_by(id=movimiento_id, baja=date(1900, 1, 1)).first()
            if not movimiento:
                raise Exception("Movimiento no encontrado")
            movimiento.baja = date.today()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error al eliminar movimiento: {str(e)}")
        
class BancoPropioProveedorService:
    @staticmethod
    def insertar_desde_op(idproveedor, id_banco_propio):
        try:
            bancoPropioProveedor = BancoPropioProveedor(id_proveedor=idproveedor, id_banco_propio=id_banco_propio)
            db.session.add(bancoPropioProveedor)
        except SQLAlchemyError as e:
            print(f"Error al insertar banco propio proveedor: {str(e)}")
            raise Exception(f"Error al insertar banco propio proveedor: {str(e)}")