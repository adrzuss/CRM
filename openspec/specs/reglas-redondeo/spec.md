# Reglas de Redondeo — CRUD Specification

## Purpose

Agregar una nueva sección de configuración para gestionar reglas de redondeo de precios. Permite definir rangos de precio, el múltiplo al que redondear y la dirección (arriba, abajo, cercano). Sigue el patrón existente de Alícuotas IVA.

## Requirements

### REQ-009: Modelo ReglaRedondeo

El sistema DEBE tener un modelo `ReglaRedondeo` con los campos: `id` (PK), `nombre`, `desde_precio`, `hasta_precio`, `multiplo`, `tipo_redondeo` (ENUM: arriba/abajo/cercano), `restar_unidades` (boolean), `activo` (boolean).

#### Scenario: Modelo persiste datos válidos

- GIVEN un set de campos válidos (nombre, desde=10, hasta=100, multiplo=0.50, tipo=arriba)
- WHEN se crea una instancia de `ReglaRedondeo`
- THEN el registro se guarda en la tabla `reglas_redondeo`
- AND los campos se almacenan con sus tipos correctos (Decimal para precios y múltiplo)

### REQ-010: Ruta HTMX — Crear regla

La ruta `htmx_add_regla_redondeo` (POST) DEBE crear una nueva regla de redondeo y retornar la tabla actualizada como respuesta HTMX.

#### Scenario: SCE-003 — Usuario agrega regla, tabla se actualiza

- GIVEN el usuario está en la sección "Reglas de Redondeo" del acordeón
- WHEN completa el formulario inline (nombre, desde, hasta, multiplo, tipo, restar_unidades) y envía
- THEN la nueva regla se guarda en la base de datos
- AND la tabla parcial `_tabla_reglas_redondeo.html` se reemplaza vía HTMX mostrando la regla agregada
- AND el formulario se resetea

### REQ-011: Ruta HTMX — Actualizar regla

La ruta `update_regla_redondeo` (POST, id) DEBE actualizar una regla existente y retornar la tabla actualizada.

#### Scenario: SCE-004 — Usuario edita regla vía modal

- GIVEN existen reglas de redondeo en la tabla
- WHEN el usuario hace clic en "Editar" de una regla
- THEN se abre el modal `_form_edit_regla_redondeo.html` con los datos cargados
- WHEN modifica los campos y confirma
- THEN la regla se actualiza en la base de datos
- AND la tabla se reemplaza vía HTMX con los datos actualizados
- AND el modal se cierra

### REQ-012: Ruta HTMX — Eliminar regla

La ruta `delete_regla_redondeo` (POST, id) DEBE eliminar una regla y retornar la tabla actualizada.

#### Scenario: SCE-005 — Usuario elimina regla

- GIVEN existen reglas de redondeo en la tabla
- WHEN el usuario hace clic en "Eliminar" de una regla y confirma
- THEN la regla se elimina de la base de datos
- AND la tabla se reemplaza vía HTMX sin la regla eliminada

### REQ-013: Tabla parcial `_tabla_reglas_redondeo.html`

El partial `_tabla_reglas_redondeo.html` DEBE listar todas las reglas con columnas: nombre, desde, hasta, múltiplo, tipo, restar unidades, activo, acciones (editar/eliminar).

#### Scenario: Tabla muestra reglas existentes

- GIVEN existen 3 reglas de redondeo activas
- WHEN se carga la sección del acordeón
- THEN la tabla muestra 3 filas con los datos correctos de cada regla
- AND cada fila tiene botones de Editar y Eliminar

#### Scenario: Tabla vacía es válida

- GIVEN no existen reglas de redondeo
- WHEN se carga la sección del acordeón
- THEN la tabla muestra un mensaje de "Sin resultados" o similar
- AND el formulario inline está disponible para agregar la primera regla

### REQ-014: Modal de edición `_form_edit_regla_redondeo.html`

El partial `_form_edit_regla_redondeo.html` DEBE ser un formulario modal con los campos: nombre, desde_precio, hasta_precio, multiplo, tipo_redondeo (dropdown), restar_unidades (checkbox), activo (checkbox).

(Ver Scenario SCE-004 arriba)

### REQ-015: Formulario inline de alta

El accordion-body de la sección DEBE incluir un formulario inline con campos: nombre, desde_precio, hasta_precio, multiplo, tipo_redondeo (dropdown), restar_unidades (checkbox), y botón "Agregar".

#### Scenario: Formulario visible en sección expandida

- GIVEN el usuario expande la sección "Reglas de Redondeo"
- WHEN observa el contenido
- THEN el formulario inline está visible con todos los campos
- AND el botón "Agregar" envía vía HTMX a `htmx_add_regla_redondeo`

### REQ-016: Validación de rangos

El sistema DEBE validar que `desde_precio < hasta_precio` y `multiplo > 0` antes de guardar.

#### Scenario: SCE-006 — Error de validación desde >= hasta

- GIVEN el usuario completa el formulario con desde_precio=100 y hasta_precio=50
- WHEN intenta enviar el formulario
- THEN el formulario muestra un mensaje de error indicando que "desde" debe ser menor que "hasta"
- AND el registro NO se guarda en la base de datos

#### Scenario: Error de validación multiplo <= 0

- GIVEN el usuario completa el formulario con multiplo=0
- WHEN intenta enviar el formulario
- THEN el formulario muestra un mensaje de error indicando que el múltiplo debe ser mayor a 0
- AND el registro NO se guarda en la base de datos

### REQ-017: Dropdown tipo_redondeo

El campo `tipo_redondeo` DEBE ser un dropdown con las opciones: "Arriba" (redondear hacia arriba), "Abajo" (redondear hacia abajo), "Cercano" (redondear al más cercano).

#### Scenario: Opciones del dropdown

- GIVEN el usuario está en el formulario de alta o edición
- WHEN abre el dropdown de tipo_redondeo
- THEN muestra exactamente 3 opciones: arriba, abajo, cercano
- AND la opción predeterminada es "Cercano"
