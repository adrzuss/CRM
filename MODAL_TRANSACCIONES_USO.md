# Guía de Uso del Modal de Transacciones

## Problema Resuelto
El modal de transacciones ahora se abre correctamente en la tab correspondiente al método de pago seleccionado, en lugar de abrir siempre en "efectivo".

## Cambios Realizados

### 1. Modal Dinámico
- ✅ Eliminada la clase `active` fija del tab de efectivo
- ✅ Eliminadas las clases `show active` del panel de efectivo
- ✅ Agregadas funciones JavaScript para activación dinámica

### 2. Funciones Disponibles

#### `configurarModalTransacciones(configuracion)`
```javascript
// Configurar qué tab debe estar activa
configurarModalTransacciones({
    tabActiva: 'credito'  // o 'efectivo', 'tarjetas', 'ctacte', etc.
});

// Luego abrir el modal
$('#transaccionesModal').modal('show');
```

#### `abrirModalEnTab(tabName)`
```javascript
// Función directa para abrir el modal en una tab específica
abrirModalEnTab('credito');  // Abre directamente en crédito
```

## Implementación en Ventas

### Cuando se selecciona CRÉDITO:
```javascript
// En lugar de solo abrir el modal:
$('#transaccionesModal').modal('show');

// Usar:
abrirModalEnTab('credito');
```

### Cuando se selecciona EFECTIVO:
```javascript
abrirModalEnTab('efectivo');
```

### Cuando se selecciona TARJETAS:
```javascript
abrirModalEnTab('tarjetas');
```

## Tabs Disponibles
- `efectivo` - Pago en efectivo
- `tarjetas` - Tarjetas de crédito/débito
- `ctacte` - Cuenta corriente
- `credito` - Crédito (solo ventas)
- `bonificacion` - Bonificaciones/descuentos
- `cheques` - Cheques (proveedores)
- `valores` - Valores recibidos (ventas/cobranzas)

## Ejemplo de Uso Completo

```javascript
// En el evento de seleccionar un método de pago en ventas
function seleccionarMetodoPago(metodo) {
    switch(metodo) {
        case 'credito':
            // Marcar visualmente el botón de crédito como seleccionado
            marcarBotonActivo('credito');
            // Abrir modal directamente en la tab de crédito
            abrirModalEnTab('credito');
            break;
            
        case 'efectivo':
            marcarBotonActivo('efectivo');
            abrirModalEnTab('efectivo');
            break;
            
        case 'tarjetas':
            marcarBotonActivo('tarjetas');
            abrirModalEnTab('tarjetas');
            break;
            
        // ... otros casos
    }
}
```

## Beneficios
1. **Coherencia Visual**: El botón seleccionado en la venta coincide con la tab activa en el modal
2. **Mejor UX**: No hay confusión entre el método seleccionado y la pantalla mostrada
3. **Flujo Lógico**: La experiencia del usuario es más intuitiva y eficiente
4. **Compatibilidad**: Funciona con todos los métodos de pago existentes

## Testing
Para probar que funciona correctamente:
1. Seleccionar "Crédito" en una venta → Modal debe abrir en tab "Crédito"
2. Seleccionar "Efectivo" → Modal debe abrir en tab "Efectivo"  
3. Seleccionar "Tarjetas" → Modal debe abrir en tab "Tarjetas"
4. Sin selección previa → Modal debe abrir en la primera tab disponible