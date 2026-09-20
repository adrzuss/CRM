# Especificación: fix-upload-creditos-otorgamiento

## Propósito

Corregir fallos silenciosos en la carga de documentos durante la generación de créditos (otorgamiento) que funcionan en desarrollo pero fallan en producción sin errores visibles.

---

## Requisitos

### R1: Ruta absoluta de UPLOAD_FOLDER_CREDITOS

**Prioridad**: Crítica

La configuración `UPLOAD_FOLDER_CREDITOS` SHALL resolver a una ruta absoluta usando `Path(__file__).parent.parent` relativo a la raíz del proyecto, NO una ruta relativa como `static/img/creditos`.

#### Escenario: Ruta se resuelve correctamente en producción

- DADO que la aplicación se ejecuta desde `/var/www/crm`
- CUANDO se accede a `current_app.config['UPLOAD_FOLDER_CREDITOS']`
- ENTONCES el valor SHALL ser `/var/www/crm/static/img/creditos`
- Y SHALL existir o crearse el directorio antes de guardar archivos

### R2: Rollback de sesión en error de guardado de archivo

**Prioridad**: Crítica

Si `archivo.save()` lanza una excepción, el sistema SHALL ejecutar `db.session.rollback()` antes de retornar el error. Sin rollback, la sesión SQLAlchemy queda en estado corrupto.

#### Escenario: Error al guardar archivo hace rollback

- DADO que se está generando un crédito con documentos adjuntos
- CUANDO falla el guardado de un archivo (permisos, disco lleno, etc.)
- ENTONCES `db.session.rollback()` SHALL ejecutarse
- Y se SHALL retornar un mensaje de error descriptivo
- Y la sesión SHALL quedar limpia para la siguiente operación

### R3: Seguridad de filenames con caracteres españoles

**Prioridad**: Alta

`secure_filename()` de Werkzeug elimina caracteres no-ASCII (ñ, á, é, etc.). El sistema SHALL aplicar un fallback que preserve caracteres españoles, usando un slug transliterado o reemplazo seguro.

#### Escenario: Filename con ñ se guarda correctamente

- DADO que un usuario sube un archivo llamado "informe ñ.pdf"
- CUANDO se procesa el filename en `generar_credito_cliente`
- ENTONCES el archivo SHALL guardarse con un nombre válido
- Y el nombre SHALL contener la letra 'ñ' o su equivalente transliterado
- Y el archivo SHALL ser recuperable por nombre

### R4: Handler para error 413 (Payload Too Large)

**Prioridad**: Alta

El sistema SHALL registrar un `@app.errorhandler(413)` que retorne una página amigable al usuario cuando el tamaño del payload excede `MAX_CONTENT_LENGTH` (16MB). El handler SHALL registrar el evento en log.

#### Escenario: Archivo de 20MB produce error 413 visible

- DADO que `MAX_CONTENT_LENGTH` está configurado en 16MB
- CUANDO un usuario intenta subir un archivo de 20MB
- ENTONCES se SHALL mostrar una página de error 413
- Y el evento SHALL registrarse en `app.log`

### R5: Logging estructurado en generar_credito_cliente

**Prioridad**: Alta

Cada paso del flujo `generar_credito_cliente()` SHALL registrar un evento usando `logging` (NO `print()`). Los logs SHALL incluir el idcliente, idcredito, y nombre del paso.

#### Escenario: Logging visible en app.log durante generación

- DADO que un usuario genera un crédito con documentos
- CUANDO se ejecuta `generar_credito_cliente`
- ENTONCES cada paso SHALL generar una entrada en `app.log` con nivel INFO
- Y los errores SHALL generarse con nivel ERROR incluyendo traceback

### R6: Validación de archivos con allowed_file

**Prioridad**: Media

El sistema SHALL llamar a `allowed_file()` para cada documento adjunto antes de intentar guardarlo. Si el archivo no tiene extensión permitida, SHALL retornar error sin guardar.

#### Escenario: Archivo .exe rechazado antes de guardar

- DADO que `ALLOWED_EXTENSIONS` incluye solo imágenes y PDF
- CUANDO se sube un archivo `malware.exe`
- ENTONCES el sistema SHALL rechazar el archivo
- Y NO SHALL intentar guardarlo en disco

### R7: Documentos requeridos obligatorios

**Prioridad**: Alta

Si el plan de crédito requiere documentos, TODOS los documentos del plan SHALL ser obligatorios. Si falta algún documento, el sistema SHALL rechazar la generación del crédito.

#### Escenario: Falta un documento requerido

- DADO que el plan de crédito requiere 3 documentos
- CUANDO el usuario envía solo 2 documentos
- ENTONCES el sistema SHALL rechazar la operación
- Y se SHALL mostrar un mensaje indicando que faltan documentos

### R8: Creación del directorio de uploads en producción

**Prioridad**: Crítica

El sistema SHALL crear el directorio de uploads si no existe, usando `os.makedirs(exist_ok=True)` o equivalente. Esto SHALL ejecutarse al inicio de `generar_credito_cliente`.

#### Escenario: Directorio no existe en producción

- DADO que la carpeta `static/img/creditos` no existe en el servidor
- CUANDO se genera un crédito con documentos
- ENTONCES el directorio SHALL crearse automáticamente
- Y los archivos SHALL guardarse correctamente

---

## Fuera de Alcance

- Rediseño del UX de carga de archivos
- Manejo CSRF (el bypass JS ya funciona, no confirmado roto)
- Validación de tipos de archivo más allá de `ALLOWED_EXTENSIONS`

## Dependencias

- Acceso a configuración nginx (infraestructura producción)
- No se requieren nuevos paquetes Python
