# CRM - Sistema de Gestión de Clientes y Ventas

Este proyecto es un sistema CRM desarrollado en Python utilizando Flask. Permite gestionar clientes, ventas, cuentas corrientes, presupuestos, remitos y más.

## Estructura del Proyecto

```
CRM/
├── models/           # Modelos de base de datos SQLAlchemy
├── routes/           # Rutas y vistas Flask
├── services/         # Lógica de negocio y consultas
├── utils/            # Utilidades y helpers
├── static/           # Archivos estáticos (CSS, JS, imágenes)
├── templates/        # Plantillas HTML Jinja2
├── tests/            # Pruebas unitarias (pytest)
├── app.py            # Archivo principal de la aplicación Flask
└── README.md         # Documentación del proyecto
```

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/adrzuss/crm.git
    cd crm
    ```

2. Crea y activa un entorno virtual:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4. Configura la base de datos en `utils/db.py` según tus credenciales.

## Ejecución

```bash
python app.py
```

Accede a la aplicación en [http://localhost:5000](http://localhost:5000).

## Pruebas

Para ejecutar los tests unitarios:
```bash
pytest tests/
```

## Funcionalidades

- Gestión de clientes y cuentas corrientes
- Registro y consulta de ventas
- Facturación electrónica
- Remitos y presupuestos
- Reportes por artículos, clientes y vendedores

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request.

## Licencia

MIT

---

## Cambio de base de datos / Migraciones Alembic

### Comandos útiles

```bash
# Ver estado actual
flask db current

# Ver revisiones disponibles
flask db heads

# Aplicar migraciones pendientes
flask db upgrade

# Crear nueva migración tras cambios en models/
flask db migrate -m "descripción del cambio"

# Marcar DB existente como "al día" (si ya tiene el schema pero falta alembic_version)
flask db stamp head

# Rollback 1 migración
flask db downgrade -1

# Resetear migraciones (CUIDADO: borra historial)
rm -rf migrations/versions/*
flask db migrate -m "baseline"
flask db upgrade
```

### Escenarios comunes

| Situación | Qué hacer |
|-----------|-----------|
| DB nueva/vacía | `flask db upgrade` (crea tablas + alembic_version) |
| DB existente con schema pero sin `alembic_version` | `flask db stamp head` → `flask db upgrade` |
| DB con `alembic_version` vieja | `flask db upgrade` |
| Cambiaste `SQLALCHEMY_DATABASE_URI` a otra DB existente | Verificar con `flask db current` y seguir tabla arriba |
| Migración falla por conflicto | Ver error exacto → a veces requiere edición manual del script en `migrations/versions/` |

### Nota sobre `upgrade()` en `index.py`

El `upgrade()` automático al arrancar (`index.py:159`) es conveniente en desarrollo pero **no recomendado en producción** — mejor correr migraciones como paso separado del deploy.

---

*Desarrollado por Adrian Zussino - SoftTech.*