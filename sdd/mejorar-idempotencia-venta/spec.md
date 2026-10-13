# Spec: Mejoras de Idempotencia en Nueva Venta

## Resumen Ejecutivo

Este cambio documenta y consolida el alcance real implementado para evitar ventas duplicadas en el flujo de nueva venta del CRM. La solución no introduce endpoints nuevos ni una tabla separada de idempotencia: reutiliza el mismo `POST /ventas/nueva_venta`, apoya la persistencia en `facturav.idempotency_key` y diferencia explícitamente la respuesta cuando el servidor detecta que la venta ya fue registrada.

## Alcance real del cambio

**Incluido en este slice:**
- Reutilización del endpoint existente `POST /ventas/nueva_venta`
- Detección server-side de duplicados por `_idempotency_key`
- Respuesta `200` con `success: true` y `duplicate: true` cuando la clave ya existe
- Devolución de `id` y `nro_comprobante` de la venta ya registrada
- Manejo cliente del caso duplicado en las dos rutas JS actuales de envío
- Prevención de efectos secundarios en duplicado: no imprimir y no limpiar automáticamente el formulario

**Explícitamente fuera de alcance:**
- Endpoints nuevos como `/ventas/validate_duplicate` o `/ventas/create`
- Validación previa separada antes del alta
- Tabla adicional como `sales_idempotency_keys`
- Modo offline, recuperación de sesión o flujos extra no presentes en el diseño aprobado

## Problema que resuelve

El flujo de nueva venta ya enviaba una `_idempotency_key`, pero faltaba cerrar el contrato funcional completo para distinguir claramente un alta nueva de un reenvío duplicado. Sin esa señal explícita, el cliente no podía informar correctamente al usuario que la venta ya existía ni evitar tratar el duplicado como una venta recién creada.

## Objetivo del sistema

Garantizar que un reenvío de `POST /ventas/nueva_venta` con la misma `_idempotency_key` no cree una segunda venta y que el frontend informe el duplicado sin ejecutar el flujo de impresión ni el de limpieza de una venta nueva.

## Requisitos funcionales

### R1: Alta de venta por el endpoint existente

**SCENARIO SCE-001 - Alta normal con clave nueva**
- DADO que el usuario envía una venta válida a `POST /ventas/nueva_venta`
- Y la `_idempotency_key` no existe previamente
- CUANDO el backend procesa la solicitud
- ENTONCES el sistema crea la venta
- Y responde `200`
- Y devuelve `success: true`
- Y devuelve `duplicate: false`
- Y devuelve `id` y `nro_comprobante` de la venta creada

**SCENARIO SCE-002 - Reenvío con clave ya registrada**
- DADO que ya existe una venta grabada con la misma `_idempotency_key`
- CUANDO el cliente vuelve a enviar `POST /ventas/nueva_venta`
- ENTONCES el sistema no crea una nueva venta
- Y responde `200`
- Y devuelve `success: true`
- Y devuelve `duplicate: true`
- Y devuelve `id` y `nro_comprobante` de la venta ya existente

### R2: Persistencia de idempotencia en la venta

**SCENARIO SCE-003 - La clave se asocia a `facturav`**
- DADO que se procesa una venta nueva correctamente
- CUANDO la operación se persiste
- ENTONCES la idempotencia queda respaldada en `facturav.idempotency_key`
- Y no se requiere una tabla separada para registrar claves

### R3: Manejo cliente del duplicado en ambas rutas JS

**SCENARIO SCE-004 - Duplicado detectado desde `procesarTransaccion()`**
- DADO que la ruta JS `procesarTransaccion()` recibe una respuesta con `duplicate: true`
- CUANDO procesa la respuesta del backend
- ENTONCES muestra una advertencia de venta ya registrada
- Y no continúa el flujo de éxito de una venta nueva

**SCENARIO SCE-005 - Duplicado detectado desde el listener `submit`**
- DADO que el listener `submit` de `#invoice_form` recibe una respuesta con `duplicate: true`
- CUANDO procesa la respuesta del backend
- ENTONCES muestra una advertencia de venta ya registrada
- Y detiene el flujo normal de éxito o redirección de una venta nueva

### R4: Sin efectos secundarios en caso de duplicado

**SCENARIO SCE-006 - No imprimir en duplicado**
- DADO que el backend responde `duplicate: true`
- CUANDO el frontend maneja la respuesta
- ENTONCES no debe abrir el flujo de impresión
- Y no debe tratar la operación como una factura recién emitida

**SCENARIO SCE-007 - No limpiar automáticamente el formulario en duplicado**
- DADO que el backend responde `duplicate: true`
- CUANDO el frontend maneja la respuesta
- ENTONCES no debe limpiar automáticamente el formulario
- Y el usuario debe conservar el contexto visible de la operación reenviada

## Contrato de respuesta esperado

### Respuesta exitosa de alta nueva
```json
{
  "success": true,
  "duplicate": false,
  "id": 12345,
  "nro_comprobante": "001-001-00001"
}
```

### Respuesta exitosa de duplicado detectado
```json
{
  "success": true,
  "duplicate": true,
  "message": "Venta ya registrada previamente (reenvío detectado)",
  "id": 12345,
  "nro_comprobante": "001-001-00001"
}
```

## Criterios de aceptación

1. El sistema mantiene el mismo `POST /ventas/nueva_venta` como punto de entrada.
2. Un reenvío con la misma `_idempotency_key` no genera una nueva venta.
3. La respuesta de duplicado usa `200` con `success: true` y `duplicate: true`.
4. La venta existente se identifica con `id` y `nro_comprobante` en la respuesta de duplicado.
5. Las dos rutas JS actuales reconocen `duplicate: true` y muestran advertencia.
6. En duplicado no se dispara impresión ni limpieza automática del formulario.
7. La persistencia de la idempotencia se apoya en `facturav.idempotency_key`.

## Qué no cambia

- El endpoint funcional sigue siendo `POST /ventas/nueva_venta`.
- No se agrega validación previa separada.
- No se agrega una tabla nueva de claves de idempotencia.
- No se redefine el flujo general de creación de venta fuera del caso de duplicado.
