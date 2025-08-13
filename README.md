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

*Desarrollado por Adrian Zussino - SoftTech.*