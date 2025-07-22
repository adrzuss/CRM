#!/usr/bin/env python3
"""
Script para configurar las tareas básicas del sistema de permisos.
Este script debe ejecutarse una sola vez para inicializar las tareas en la base de datos.
"""

import sys
import os

# Agregar el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from utils.config import Config
from utils.db import db
from models.sessions import Tareas, Usuarios, TareasUsuarios

def create_app():
    """Crear la aplicación Flask para acceder a la base de datos"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def configurar_tareas():
    """Configurar las tareas básicas del sistema"""
    
    # Definir las tareas básicas
    tareas_basicas = [
        {"id": 1, "tarea": "Administrador"},
        {"id": 2, "tarea": "Vendedor"},
        {"id": 3, "tarea": "Cobrador"},
        {"id": 4, "tarea": "Almacenero"},
        {"id": 5, "tarea": "Gestor de Créditos"},
        {"id": 6, "tarea": "Comprador"},
        {"id": 7, "tarea": "Cajero"},
    ]
    
    with app.app_context():
        print("Configurando tareas del sistema...")
        
        # Crear las tareas
        for tarea_data in tareas_basicas:
            # Verificar si la tarea ya existe
            tarea_existente = Tareas.query.get(tarea_data["id"])
            
            if tarea_existente:
                print(f"Tarea '{tarea_data['tarea']}' ya existe (ID: {tarea_data['id']})")
            else:
                nueva_tarea = Tareas(tarea=tarea_data["tarea"])
                nueva_tarea.id = tarea_data["id"]  # Asignar ID específico
                db.session.add(nueva_tarea)
                print(f"Tarea '{tarea_data['tarea']}' creada (ID: {tarea_data['id']})")
        
        # Commit de los cambios
        try:
            db.session.commit()
            print("✅ Tareas configuradas exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al configurar tareas: {e}")
            return False
        
        return True

def asignar_tareas_admin():
    """Asignar todas las tareas al primer usuario (administrador)"""
    
    with app.app_context():
        print("\nAsignando tareas al administrador...")
        
        # Obtener el primer usuario (asumiendo que es el admin)
        usuario = Usuarios.query.first()
        
        if not usuario:
            print("❌ No se encontró ningún usuario en la base de datos")
            return False
        
        print(f"Usuario encontrado: {usuario.nombre} (ID: {usuario.id})")
        
        # Obtener todas las tareas
        tareas = Tareas.query.all()
        
        if not tareas:
            print("❌ No se encontraron tareas en la base de datos")
            return False
        
        # Asignar todas las tareas al usuario
        for tarea in tareas:
            # Verificar si ya tiene la tarea asignada
            tarea_asignada = TareasUsuarios.query.filter_by(
                idusuario=usuario.id, 
                idtarea=tarea.id
            ).first()
            
            if not tarea_asignada:
                nueva_asignacion = TareasUsuarios(
                    idusuario=usuario.id,
                    idtarea=tarea.id
                )
                db.session.add(nueva_asignacion)
                print(f"Tarea '{tarea.tarea}' asignada al usuario")
        
        # Commit de los cambios
        try:
            db.session.commit()
            print("✅ Tareas asignadas al administrador exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al asignar tareas: {e}")
            return False
        
        return True

def mostrar_usuarios_tareas():
    """Mostrar todos los usuarios y sus tareas asignadas"""
    
    with app.app_context():
        print("\n=== USUARIOS Y SUS TAREAS ===")
        
        usuarios = Usuarios.query.all()
        
        for usuario in usuarios:
            print(f"\n👤 Usuario: {usuario.nombre} (ID: {usuario.id})")
            
            # Obtener tareas asignadas
            tareas_asignadas = TareasUsuarios.query.filter_by(idusuario=usuario.id).all()
            
            if tareas_asignadas:
                print("   Tareas asignadas:")
                for ta in tareas_asignadas:
                    tarea = Tareas.query.get(ta.idtarea)
                    if tarea:
                        print(f"   - {tarea.tarea} (ID: {tarea.id})")
            else:
                print("   ❌ No tiene tareas asignadas")

if __name__ == "__main__":
    app = create_app()
    
    print("🚀 Configurando sistema de permisos...")
    print("=" * 50)
    
    # Configurar tareas básicas
    if configurar_tareas():
        # Asignar tareas al administrador
        asignar_tareas_admin()
        
        # Mostrar estado final
        mostrar_usuarios_tareas()
        
        print("\n" + "=" * 50)
        print("✅ Configuración completada")
        print("\n📝 Próximos pasos:")
        print("1. Verificar que las tareas se crearon correctamente")
        print("2. Asignar tareas específicas a cada usuario según su rol")
        print("3. Probar el sistema de permisos en la aplicación")
    else:
        print("❌ Error en la configuración")
        sys.exit(1) 