from flask import current_app
from models.ofertas import Oferta, OfertasCondiciones, TipoDescuento, TipoCondiciones, OfertasVinculadas, ReglaSeleccion
from utils.db import db
from datetime import datetime

class OfertaService:
    def obtener_oferta_por_id(self, id):
        """Obtiene una oferta con todas sus condiciones"""
        try:
            oferta = Oferta.query.get(id)
            if not oferta:
                return None
            
            # Obtener las condiciones
            condiciones = OfertasCondiciones.query.filter_by(id_oferta=id).all()
            
            # Si es oferta vinculada, obtener los artículos
            vinculos = None
            print(f'La oferta: {oferta}')
            vinculos = OfertasVinculadas.query.filter_by(id_oferta=id).first()
            print('Vinculos: ', vinculos)
            
            return {
                'oferta': oferta,
                'condiciones': condiciones,
                'vinculos': vinculos
            }
        except Exception as e:
            current_app.logger.error(f"Error obteniendo oferta: {str(e)}")
            return None

    def crear_oferta(self, datos_oferta, condiciones):
        """Crea una nueva oferta con sus condiciones"""
        try:
            nueva_oferta = Oferta(
                nombre=datos_oferta['nombre'],
                tipo_descuento=datos_oferta['tipo_descuento'],
                valor_descuento=datos_oferta['valor_descuento'],
                cantidad_minima=datos_oferta['cantidad_minima'],
                multiplos=datos_oferta.get('multiplos', False),
                fecha_inicio=datos_oferta['fecha_inicio'],
                fecha_fin=datos_oferta['fecha_fin'],
                es_condicion_compra=True
            )
            db.session.add(nueva_oferta)
            db.session.flush()

            # Crear las condiciones
            for condicion in condiciones:
                nueva_condicion = OfertasCondiciones(
                    id_oferta=nueva_oferta.id,
                    id_tipo_condicion=condicion['id_tipo_condicion'],
                    id_referencia=condicion['id_referencia']
                )
                db.session.add(nueva_condicion)

            db.session.commit()
            return nueva_oferta
        except Exception as e:
            db.session.rollback()
            raise e

    def crear_oferta_vinculada(self, datos_oferta, articulo_origen, articulo_destino):
        """
        Crea una oferta donde al comprar un artículo específico se aplica
        descuento a otro artículo
        """
        try:
            # Crear la oferta base
            nueva_oferta = self.crear_oferta(datos_oferta, [])
            
            # Crear el vínculo entre artículos
            vinculo = OfertasVinculadas(
                id_oferta=nueva_oferta.id,
                id_articulo_origen=articulo_origen,
                id_articulo_destino=articulo_destino
            )
            db.session.add(vinculo)
            db.session.commit()
            
            return nueva_oferta
        except Exception as e:
            db.session.rollback()
            raise e
    
    def crear_oferta_regla_seleccion(self, datos_oferta, condiciones, regla_seleccion):
        """Crea una oferta con regla de selección (mayor/menor valor)"""
        try:
            # Agregar la regla de selección a los datos de la oferta
            datos_oferta['regla_seleccion'] = regla_seleccion
            nueva_oferta = self.crear_oferta(datos_oferta, condiciones)
            return nueva_oferta
        except Exception as e:
            db.session.rollback()
            raise e

    def actualizar_oferta(self, id, datos_oferta, condiciones):
        """Actualiza una oferta existente con sus condiciones"""
        try:
            oferta = Oferta.query.get(id)
            if not oferta:
                raise ValueError("Oferta no encontrada")
                
            # Actualizar datos básicos
            oferta.nombre = datos_oferta['nombre']
            oferta.tipo_descuento = datos_oferta['tipo_descuento']
            oferta.valor_descuento = datos_oferta['valor_descuento']
            oferta.cantidad_minima = datos_oferta['cantidad_minima']
            oferta.multiplos = datos_oferta['multiplos']
            oferta.fecha_inicio = datos_oferta['fecha_inicio']
            oferta.fecha_fin = datos_oferta['fecha_fin']
            
            # Eliminar condiciones anteriores
            OfertasCondiciones.query.filter_by(id_oferta=id).delete()
            
            # Crear nuevas condiciones
            for condicion in condiciones:
                nueva_condicion = OfertasCondiciones(
                    id_oferta=id,
                    id_tipo_condicion=condicion['id_tipo_condicion'],
                    id_referencia=condicion['id_referencia']
                )
                db.session.add(nueva_condicion)
                
            db.session.commit()
            return oferta
            
        except Exception as e:
            db.session.rollback()
            raise e
        
    def actualizar_oferta_vinculada(id, datos_oferta, articulo_origen, articulo_destino):
        try:
            oferta = Oferta.query.get(id)
            if not oferta:
                raise ValueError("Oferta no encontrada")

            # Actualizar datos básicos
            oferta.nombre = datos_oferta['nombre']
            oferta.tipo_descuento = datos_oferta['tipo_descuento']
            oferta.valor_descuento = datos_oferta['valor_descuento']
            oferta.cantidad_minima = datos_oferta['cantidad_minima']
            oferta.multiplos = datos_oferta['multiplos']
            oferta.fecha_inicio = datos_oferta['fecha_inicio']
            oferta.fecha_fin = datos_oferta['fecha_fin']

            # Actualizar vínculo entre artículos
            vinculo = OfertasVinculadas.query.filter_by(id_oferta=id).first()
            if vinculo:
                vinculo.id_articulo_origen = articulo_origen
                vinculo.id_articulo_destino = articulo_destino

            db.session.commit()
            return oferta

        except Exception as e:
            db.session.rollback()
            raise e
        
    def actualizar_oferta_regla_seleccion(id, datos_oferta, condiciones, regla):
        try:
            oferta = Oferta.query.get(id)
            if not oferta:
                raise ValueError("Oferta no encontrada")

            # Actualizar datos básicos
            oferta.nombre = datos_oferta['nombre']
            oferta.tipo_descuento = datos_oferta['tipo_descuento']
            oferta.valor_descuento = datos_oferta['valor_descuento']
            oferta.cantidad_minima = datos_oferta['cantidad_minima']
            oferta.multiplos = datos_oferta['multiplos']
            oferta.fecha_inicio = datos_oferta['fecha_inicio']
            oferta.fecha_fin = datos_oferta['fecha_fin']

            # Actualizar condiciones
            OfertasCondiciones.query.filter_by(id_oferta=id).delete()
            for condicion in condiciones:
                nueva_condicion = OfertasCondiciones(
                    id_oferta=id,
                    id_tipo_condicion=condicion['id_tipo_condicion'],
                    id_referencia=condicion['id_referencia']
                )
                db.session.add(nueva_condicion)

            # Actualizar regla de selección
            oferta.regla_seleccion = regla

            db.session.commit()
            return oferta

        except Exception as e:
            db.session.rollback()
            raise e

    def calcular_descuento(self, items, oferta):
        """Calcula el descuento según el tipo de oferta"""
        try:
            if oferta.regla_seleccion:
                # Caso de menor/mayor valor
                item_seleccionado = None
                if oferta.regla_seleccion == ReglaSeleccion.MENOR_VALOR:
                    item_seleccionado = min(items, key=lambda x: x.precio)
                elif oferta.regla_seleccion == ReglaSeleccion.MAYOR_VALOR:
                    item_seleccionado = max(items, key=lambda x: x.precio)
                
                if item_seleccionado:
                    return self._aplicar_descuento(item_seleccionado, oferta)
            
            # Caso de oferta vinculada
            vinculo = OfertasVinculadas.query.filter_by(id_oferta=oferta.id).first()
            if vinculo:
                # Verificar si el artículo origen está en los items
                if any(item.id == vinculo.id_articulo_origen for item in items):
                    # Buscar el artículo destino en los items
                    item_destino = next(
                        (item for item in items if item.id == vinculo.id_articulo_destino), 
                        None
                    )
                    if item_destino:
                        return self._aplicar_descuento(item_destino, oferta)
            
            return 0
        except Exception as e:
            current_app.logger.error(f"Error calculando descuento: {str(e)}")
            return 0

    def _aplicar_descuento(self, item, oferta):
        """Aplica el descuento según el tipo (porcentaje o monto fijo)"""
        try:
            if oferta.tipo_descuento == TipoDescuento.PORCENTAJE:
                return (item.precio * oferta.valor_descuento) / 100
            else:
                return min(oferta.valor_descuento, item.precio)
        except Exception as e:
            current_app.logger.error(f"Error aplicando descuento: {str(e)}")
            return 0

    def obtener_referencias_por_tipo(self, tipo_condicion_id):
        """Obtiene las referencias según el tipo de condición"""
        try:
            tipo = TipoCondiciones.query.get(tipo_condicion_id)
            if not tipo:
                return []
                
            if tipo.nombre.lower() == 'marca':
                from models.articulos import Marca
                referencias = Marca.query.all()
            elif tipo.nombre.lower() == 'rubro':
                from models.articulos import Rubro
                referencias = Rubro.query.all()
            elif tipo.nombre.lower() == 'articulo':
                from models.articulos import Articulo
                referencias = Articulo.query.all()
            else:
                referencias = []
                
            return [{'id': ref.id, 'nombre': ref.nombre if hasattr(ref, 'nombre') else ref.detalle} 
                    for ref in referencias]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo referencias: {str(e)}")
            return []

    def listar_ofertas(self):
        return Oferta.query.all()

    def obtener_tipos_condiciones(self):
        return TipoCondiciones.query.all()
    
    def obtener_ofertas_activas(self):
        """Retorna todas las ofertas vigentes a la fecha actual"""
        fecha_actual = datetime.now()
        return Oferta.query.filter(
            Oferta.fecha_inicio <= fecha_actual,
            Oferta.fecha_fin >= fecha_actual
        ).all()
        
    def obtener_referencias_por_tipo(self, tipo_condicion_id):
        """
        Obtiene las referencias según el tipo de condición
        Por ejemplo, si es tipo marca, devuelve todas las marcas
        """
        try:
            tipo = TipoCondiciones.query.get(tipo_condicion_id)
            if not tipo:
                return []
                
            if tipo.nombre.lower() == 'marca':
                from models.articulos import Marca
                referencias = Marca.query.all()
            elif tipo.nombre.lower() == 'rubro':
                from models.articulos import Rubro
                referencias = Rubro.query.all()
            elif tipo.nombre.lower() == 'articulo':
                from models.articulos import Articulo
                referencias = Articulo.query.all()
            else:
                referencias = []
                
            return [{'id': ref.id, 'nombre': ref.nombre if hasattr(ref, 'nombre') else ref.detalle} 
                    for ref in referencias]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo referencias: {str(e)}")
            return []