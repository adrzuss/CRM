# Redondeo en upd-articulos — Specification

## Purpose

Aplicar reglas de redondeo comercial al calcular `precioVP` en el formulario de edición de artículos (`upd-articulos`). Cuando el costo cambia, el precio de venta debe respetar múltiplos y dirección de redondeo configurados en `reglas_redondeo`, evitando ajustes manuales.

## Requirements

### REQ-001: Backend carga reglas activas

El handler GET de `update_articulo` DEBE consultar las reglas de redondeo con `activo=True` desde `ReglaRedondeo` y pasarlas al template como variable `reglas_redondeo`.

#### Scenario: Reglas se pasan al template

- GIVEN existen 2 reglas de redondeo activas en la DB
- WHEN se carga el formulario de edición de un artículo
- THEN el template recibe la variable `reglas_redondeo` con ambas reglas

### REQ-002: Template serializa reglas a JSON

El template `upd-articulos.html` DEBE serializar `reglas_redondeo` a JSON en un `<script>` tag accesible para JavaScript.

#### Scenario: JSON disponible en el cliente

- GIVEN el backend pasó 2 reglas de redondeo al template
- WHEN el browser renderiza la página
- THEN existe una variable JS `REGLAS_REDONDEO` con las reglas serializadas como array de objetos

### REQ-003: Función `aplicarRedondeo()` en JavaScript

La función `aplicarRedondeo(precio, reglas)` DEBE buscar la primera regla cuyo rango `[desde_precio, hasta_precio]` contenga el precio, y aplicar el redondeo según `tipo_redondeo`. Si `restar_unidades` es verdadero, DEBE restar `multiplo` antes de redondear.

#### Scenario: SCE-001 — Redondeo arriba (multiplo=100)

- GIVEN precio=4327 y regla con multiplo=100, tipo=arriba, restar=false
- WHEN se ejecuta `aplicarRedondeo(4327, reglas)`
- THEN el resultado es 4400

#### Scenario: SCE-002 — Redondeo abajo (multiplo=100)

- GIVEN precio=4327 y regla con multiplo=100, tipo=abajo, restar=false
- WHEN se ejecuta `aplicarRedondeo(4327, reglas)`
- THEN el resultado es 4300

#### Scenario: SCE-003 — Redondeo cercano (multiplo=100)

- GIVEN precio=4327 y regla con multiplo=100, tipo=cercano, restar=false
- WHEN se ejecuta `aplicarRedondeo(4327, reglas)`
- THEN el resultado es 4300

#### Scenario: SCE-004 — Redondeo arriba con restar

- GIVEN precio=4327 y regla con multiplo=100, tipo=arriba, restar=true (restar=100)
- WHEN se ejecuta `aplicarRedondeo(4327, reglas)`
- THEN el resultado es 4390

### REQ-004: Integración en `calcularPrecio()`

La función `calcularPrecio()` DEBE aplicar `aplicarRedondeo()` sobre cada `precioVP` calculado después de la operación `markup × costoTotal`.

#### Scenario: precioVP se redondea al calcular

- GIVEN un artículo con costoTotal=100 y markup=43.27 (precioVP=4327)
- WHEN se ejecuta `calcularPrecio()`
- THEN el `precioVP` mostrado refleja el valor redondeado según la regla activa

### REQ-005: Fallback sin reglas

Si no existe regla aplicable para el precio dado, el sistema DEBE mantener el precio sin redondear (comportamiento actual).

#### Scenario: SCE-005 — Precio sin regla aplicable

- GIVEN precio=50 y la regla cubre rangos desde=100 hasta=1000
- WHEN se ejecuta `aplicarRedondeo(50, reglas)`
- THEN el resultado es 50 (sin cambios)

#### Scenario: SCE-006 — Sin reglas activas en DB

- GIVEN no existen reglas de redondeo activas
- WHEN el usuario carga upd-articulos y cambia el costo
- THEN todos los `precioVP` se calculan sin redondear (comportamiento actual)
