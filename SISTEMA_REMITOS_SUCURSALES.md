# Sistema de Gestión de Remitos entre Sucursales

## Resumen de Implementación

Se ha implementado un sistema completo de gestión de remitos entre sucursales con tres estados y control de stock en tránsito.

## Estados del Remito

### 1. PENDIENTE (Estado inicial)
- Se crea al grabar un nuevo remito
- **Acción en Stock:**
  - Sucursal origen: aumenta `en_transito_salida`
  - Sucursal destino: aumenta `en_transito_entrada`
- **Visible para:** Sucursal de origen

### 2. ENVIADO
- Se activa con el botón "Enviar" en la sucursal origen
- **Acción en Stock:**
  - Sucursal origen: descuenta de `actual` y `en_transito_salida`
- **Visible para:** Sucursal destino

### 3. RECIBIDO
- Se activa con el botón "Controlar" en la sucursal destino
- **Acción en Stock:**
  - Sucursal destino: aumenta `actual` y descuenta de `en_transito_entrada`
- **Estado final**

## Archivos Modificados/Creados

### Modificados:
1. **models/articulos.py**
   - Ya tenía el enum `EstadosRemitoSucursales` con los 3 estados necesarios

2. **services/articulos.py**
   - `procesar_remito_a_sucursal()`: Actualizada para manejar `en_transito_salida` y `en_transito_entrada`
   - `enviar_remito_sucursal()`: Nueva función para cambiar estado a ENVIADO
   - `recibir_remito_sucursal()`: Nueva función para cambiar estado a RECIBIDO
   - `get_remitos_sucursales()`: Nueva función para listar remitos con filtros
   - `get_detalle_remito()`: Nueva función para ver detalle de un remito

3. **routes/articulos.py**
   - Importadas las nuevas funciones de services
   - `/enviar_remito_sucursal/<int:idremito>` (POST): API para enviar remitos
   - `/recibir_remito_sucursal/<int:idremito>` (POST): API para recibir remitos
   - `/listado_remitos_sucursales`: Vista para listar todos los remitos
   - `/detalle_remito_sucursal/<int:idremito>`: API para ver detalle de un remito

### Creados:
4. **templates/articulos/listado-remitos-sucursales.html**
   - Interfaz completa para visualizar remitos
   - Filtros: Todos, Pendientes, Enviados, Recibidos, Enviados por mí, Recibidos por mí
   - Botones contextuales según estado y sucursal
   - Modal para ver detalle completo del remito

5. **static/js/listado_remitos_sucursales.js**
   - Manejo de eventos para ver detalle
   - Manejo de eventos para enviar remito
   - Manejo de eventos para controlar/recibir remito
   - Validaciones y confirmaciones

## Flujo de Uso

### Para crear un remito:
1. Ir a "Remitos a sucursales" (ruta existente: `/articulos/remitos_sucursales`)
2. Seleccionar sucursal destino
3. Agregar artículos
4. Grabar → Estado: **PENDIENTE**

### Para enviar un remito:
1. Ir a "Listado de Remitos" (`/articulos/listado_remitos_sucursales`)
2. Filtrar por "Pendientes" o "Enviados por mí"
3. Hacer clic en botón "Enviar" → Estado: **ENVIADO**
4. Se descuenta del stock actual de la sucursal origen

### Para recibir un remito:
1. Ir a "Listado de Remitos" (desde la sucursal destino)
2. Filtrar por "Enviados" o "Recibidos por mí"
3. Ver el remito para verificar artículos
4. Hacer clic en botón "Controlar" → Estado: **RECIBIDO**
5. Se suma al stock actual de la sucursal destino

## Validaciones Implementadas

1. **Al enviar remito:**
   - Verifica que el remito esté en estado PENDIENTE
   - Verifica que haya stock suficiente en sucursal origen
   - Rollback si hay algún error

2. **Al recibir remito:**
   - Verifica que el remito esté en estado ENVIADO
   - Crea registro de stock si no existe
   - Rollback si hay algún error

## URLs Importantes

- Crear remito: `/articulos/remitos_sucursales`
- Listar remitos: `/articulos/listado_remitos_sucursales`
- API Enviar: `/articulos/enviar_remito_sucursal/<id>` (POST)
- API Recibir: `/articulos/recibir_remito_sucursal/<id>` (POST)
- API Detalle: `/articulos/detalle_remito_sucursal/<id>` (GET)

## Notas Técnicas

- Se eliminó el uso de `idstock` de la configuración
- Se consulta directamente la tabla `Stock` por `idarticulo` e `idsucursal`
- Se crean registros de stock automáticamente si no existen
- Los campos `en_transito_entrada` y `en_transito_salida` ya existían en la tabla Stock
- Se importaron `Colores` y `DetallesArticulos` en services/articulos.py para las consultas
