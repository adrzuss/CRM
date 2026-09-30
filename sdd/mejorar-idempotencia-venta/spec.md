# Spec: Mejoras de Idempotencia en Nueva Venta

## Resumen Ejecutivo

Este spec documenta las mejoras necesarias para implementar un sistema completo de prevención de duplicados en el módulo de creación de ventas del CRM. El sistema actual implementa una base técnica básica para idempotencia, pero requiere mejoras significativas para proporcionar una protección robusta contra ventas duplicadas y una mejor experiencia de usuario.

## Problema Actual

El módulo de ventas (`templates/ventas/nueva_venta.html` y `static/js/nueva_venta.js`) implementa una solución parcial:

**Implementado Actualmente:**
- Generador de UUID (`generarUUID()`) - Genera identificadores únicos usando `crypto.randomUUID()`
- Bandera de envío múltiple (`isFormSubmited`) - Previene envíos concurrentes
- Clave de idempotencia (`_idempotency_key`) - Se añade al formulario antes del envío

**Brechas Identificadas:**
1. **Detección de Duplicados:** No existe validación cliente-side para prevenir ventas duplicadas
2. **Manejo de Errores:** Respuestas genéricas del servidor sin manejo específico de casos de duplicado
3. **Interfaz de Usuario:** Sin indicadores visuales claros de estado o advertencias por duplicados
4. **Flujo de Usuario:** Sin información clara sobre intentos de duplicado y siguientes pasos

## Objetivos del Sistema

### Objetivo Principal
Implementar un sistema completo de prevención de duplicados que detecte proactivamente ventas duplicadas antes de su creación y proporcione una clara comunicación al usuario sobre el estado y cualquier conflicto de duplicado.

### Requisitos Específicos

#### R1: Validación Previa al Envío

**SCENARIO SCE-001 - Validación con campos válidos**
- DADO que el usuario completa el formulario de venta con datos válidos (cliente, fecha, total, lista de precios)
- CUANDO el usuario hace clic en "Validar Duplicados"
- ENTONCES el sistema verifica la existencia de ventas duplicadas basadas en los mismos criterios clave
- Y el sistema devuelve respuesta de éxito indicando validación completada

**SCENARIO SCE-002 - Validación con campos incompletos**
- DADO que el usuario intenta validar sin campos requeridos
- CUANDO el usuario hace clic en "Validar Duplicados"
- ENTONCES el sistema devuelve error indicando campos requeridos para validación

**SCENARIO SCE-003 - Detección de duplicado**
- DADO que existe una venta con los mismos criterios clave (cliente, fecha, total, lista de precios)
- CUANDO el usuario intenta validar
- ENTONCES el sistema devuelve advertencia clara indicando duplicado detectado

#### R2: Endpoint de Creación con Deduplicación Completa

**SCENARIO SCE-004 - Creación exitosa sin duplicados**
- DADO que no existe duplicado y validación pasó
- CUANDO el usuario hace clic en "Crear Venta"
- ENTONCES el sistema crea nueva venta y devuelve ID de venta y número de comprobante
- Y el sistema registra clave de idempotencia en base de datos
- Y el sistema limpia formulario para próxima venta

**SCENARIO SCE-005 - Intento de creación con duplicado**
- DADO que se detectó duplicado en validación previa
- CUANDO el usuario intenta crear venta
- ENTONCES el sistema devuelve error 409 indicando venta duplicada
- Y el sistema muestra detalles del duplicado (número de comprobante, fecha, monto, cliente)
- Y el sistema sugiere acciones para resolver conflicto

#### R3: Interfaz de Usuario con Indicadores de Estado

**SCENARIO SCE-006 - Inicio de validación**
- DADO que el usuario hace clic en "Validar Duplicados"
- CUANDO validación comienza
- ENTONCES el sistema muestra indicador de carga con mensaje "Validando para prevenir duplicados..."
- Y el botón de validación se deshabilita

**SCENARIO SCE-007 - Validación completada exitosamente**
- DADO que validación pasó
- CUANDO validación completa
- ENTONCES el sistema muestra indicador de éxito con clave de idempotencia
- Y el botón de crear venta se habilita
- Y el indicador de validación se oculta

**SCENARIO SCE-008 - Duplicado detectado**
- DADO que se detectó duplicado
- CUANDO validación completa
- ENTONCES el sistema muestra advertencia clara con detalles del duplicado
- Y el botón de crear venta se deshabilita
- Y se muestra botón "Resolver Conflicto"

#### R4: Manejo de Errores Especificado

**SCENARIO SCE-009 - Error de validación servidor**
- DADO que servidor retorna error durante validación
- CUANDO el usuario intenta continuar
- ENTONCES el sistema muestra mensaje de error específico
- Y el usuario puede intentar nuevamente

**SCENARIO SCE-010 - Error de red**
- DADO que falla conexión con servidor
- CUANDO el usuario intenta validar
- ENTONCES el sistema muestra error de red
- Y el usuario puede reintentar

**SCENARIO SCE-011 - Sin conexión a internet**
- DADO que no hay conexión a internet
- CUANDO el usuario intenta validar o crear
- ENTONCES el sistema usa modo offline con advertencia
- Y el usuario es notificado cuando se restablece conexión

#### R5: Recuperación de Sesión

**SCENARIO SCE-012 - Reingreso a aplicación**
- DADO que usuario cierra sesión durante validación
- CUANDO el usuario regresa
- ENTONCES el sistema pregunta si desea continuar con validación previa
- Y el usuario puede continuar o iniciar nueva validación

**SCENARIO SCE-013 - Cierre de sesión durante creación**
- DADO que usuario cierra sesión durante creación de venta
- CUANDO el usuario regresa
- ENTONCES el sistema muestra resumen de progreso
- Y el usuario puede continuar o iniciar nueva venta

## Arquitectura del Sistema

### 1. Interfaz de Usuario (Frontend)
**Componentes Requeridos:**
- Indicador de Estado: Muestra estado actual de validación
- Botones de Acción: Validar, Regenerar, Crear
- Notificaciones: Advertencias, éxitos, errores
- Modales: Duplicado detectado, Resolver conflicto
- Cache Local: Almacenamiento temporal de claves de idempotencia

**Endpoints de API:**
- `POST /ventas/validate_duplicate` - Validación de duplicados
- `POST /ventas/create` - Creación de ventas con deduplicación

### 2. Backend API
**Endpoints Implementados:**

#### Endpoint de Validación
```http
POST /ventas/validate_duplicate HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded
_idempotency_key=<uuid>&idcliente=<id>&fecha=<date>&totalFactura=<amount>&idlista=<price_list_id>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Validación completada",
  "validation_passed": true,
  "idempotency_key": "uuid-generated"
}
```

**Response (409 Conflict):**
```json
{
  "success": false,
  "message": "No se puede validar: venta duplicada detectada",
  "duplicate_exists": true,
  "duplicate_info": {
    "nro_comprobante": "001-001-00001",
    "fecha": "2024-01-15",
    "monto": 15000.00,
    "cliente": "Nombre Cliente"
  }
}
```

#### Endpoint de Creación
```http
POST /ventas/create HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded
_idempotency_key=<uuid>&idcliente=<id>&fecha=<date>&totalFactura=<amount>&idlista=<price_list_id>&items[0][codigo]=...
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Venta creada exitosamente",
  "sale_id": 12345,
  "nro_comprobante": "001-001-00001",
  "idempotency_key": "uuid-used"
}
```

**Response (409 Conflict):**
```json
{
  "success": false,
  "message": "No se puede crear: venta duplicada detectada",
  "duplicate_info": {
    "nro_comprobante": "001-001-00001",
    "fecha": "2024-01-15",
    "monto": 15000.00,
    "cliente": "Nombre Cliente"
  }
}
```

### 3. Base de Datos
**Tablas Requeridas:**

```sql
CREATE TABLE sales_idempotency_keys (
    idempotency_key VARCHAR(36) PRIMARY KEY,
    sale_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL 24 HOUR),
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE SET NULL,
    INDEX idx_expires_at (expires_at),
    INDEX idx_created_at (created_at)
);

CREATE INDEX idx_sales_duplicate_check 
ON sales (idcliente, fecha, total, idlista) 
WHERE activa = TRUE;
```

## Datos Clave del Dominio

### Campos Clave para Detección de Duplicados

Una venta se considera duplicada
