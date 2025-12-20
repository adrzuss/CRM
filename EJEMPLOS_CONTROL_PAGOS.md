# 🎯 GUÍA COMPLETA: CONTROL DE MÉTODOS DE PAGO

## 📋 MÉTODOS DISPONIBLES

### 1. **Control por Template (Al cargar la página)**
```html
<!-- Solo efectivo y tarjetas -->
{% include 'partials/_modal-transacciones.html' with {
    'modal_methods': ['efectivo', 'tarjetas'],
    'modal_context': 'venta',
    'modal_title': 'Cobro Rápido'
} %}

<!-- Solo cuenta corriente -->
{% include 'partials/_modal-transacciones.html' with {
    'modal_methods': ['ctacte'],
    'modal_context': 'cobranza'
} %}
```

### 2. **Control por Contexto (Ya configurado)**
- **Ventas**: efectivo, tarjetas, ctacte, credito, bonificacion, valores
- **Cobranzas**: efectivo, tarjetas, ctacte, bonificacion, valores  
- **Proveedores**: efectivo, ctacte, bonificacion, cheques

### 3. **Control Dinámico con JavaScript**

#### Configuraciones Predefinidas:
```javascript
// En tu página, después de abrir el modal:

// Solo efectivo
aplicarConfiguracion('solo_efectivo');

// Venta rápida (efectivo + tarjetas)
aplicarConfiguracion('venta_rapida');

// Sin crédito
aplicarConfiguracion('venta_sin_credito');

// Solo cheques para proveedores
aplicarConfiguracion('proveedor_cheques');
```

#### Control Manual:
```javascript
// Habilitar métodos específicos
configurarMetodosPago(['efectivo', 'tarjetas'], 'Cliente nuevo');

// Deshabilitar un método temporalmente
deshabilitarMetodo('credito', 'Cliente con deuda vencida');

// Habilitar método nuevamente
habilitarMetodo('credito');
```

#### Control por Condiciones:
```javascript
configurarSegunCondiciones({
    esVenta: true,
    clienteSinCredito: true,
    montoMinimo: 1000,
    montoActual: 500,
    fueraDeHorario: false
});
```

## 🎯 EJEMPLOS PRÁCTICOS

### **Ejemplo 1: Cliente con Restricciones**
```javascript
function abrirModalVenta(idCliente) {
    // Cargar datos del cliente
    const cliente = obtenerDatosCliente(idCliente);
    
    // Abrir modal
    $('#transaccionesModal').modal('show');
    
    // Configurar métodos según cliente
    if (cliente.solo_efectivo) {
        aplicarConfiguracion('cobranza_solo_efectivo');
    } else if (cliente.sin_credito) {
        aplicarConfiguracion('venta_sin_credito');
    } else {
        aplicarConfiguracion('venta_completa');
    }
}
```

### **Ejemplo 2: Control por Monto**
```javascript
function validarMetodosPorMonto() {
    const total = parseFloat(document.getElementById('modal_total_factura').textContent) || 0;
    
    if (total < 500) {
        // Montos bajos: solo efectivo
        configurarMetodosPago(['efectivo'], 'Monto menor a $500');
    } else if (total > 10000) {
        // Montos altos: sin efectivo
        configurarMetodosPago(['tarjetas', 'ctacte', 'credito'], 'Monto mayor a $10,000');
    }
}
```

### **Ejemplo 3: Control por Horario**
```javascript
function verificarHorarioComercial() {
    const hora = new Date().getHours();
    const esFueraDeHorario = hora < 8 || hora > 18;
    
    configurarSegunCondiciones({
        esVenta: true,
        fueraDeHorario: esFueraDeHorario
    });
}
```

### **Ejemplo 4: Deshabilitación Temporal**
```javascript
function verificarConectividadTarjetas() {
    // Simular verificación de conectividad
    fetch('/api/verificar-posnet')
        .then(response => {
            if (!response.ok) {
                deshabilitarMetodo('tarjetas', 'POSNET fuera de servicio');
            } else {
                habilitarMetodo('tarjetas');
            }
        })
        .catch(() => {
            deshabilitarMetodo('tarjetas', 'Error de conectividad');
        });
}
```

## 📋 CONFIGURACIONES DISPONIBLES

| Configuración | Métodos Incluidos | Uso Recomendado |
|---|---|---|
| `venta_completa` | Todos para ventas | Ventas normales |
| `venta_rapida` | efectivo, tarjetas | Mostrador rápido |
| `venta_credito` | efectivo, credito | Ventas a plazo |
| `cobranza_solo_efectivo` | efectivo | Cobranzas especiales |
| `proveedor_cheques` | cheques | Pagos grandes |
| `solo_cuenta_corriente` | ctacte | Ajustes contables |

## 🔧 INTEGRACIÓN CON PÁGINAS EXISTENTES

### En `nueva_venta.js`:
```javascript
function abrirModalPagos() {
    $('#transaccionesModal').modal('show');
    
    // Configurar según tipo de cliente
    if (clienteActual.tipo === 'MAYORISTA') {
        aplicarConfiguracion('venta_sin_credito');
    } else {
        aplicarConfiguracion('venta_completa');
    }
}
```

### En `seleccion-cuotas-pagos.js`:
```javascript
function abrirModalPagos() {
    $('#transaccionesModal').modal('show');
    aplicarConfiguracion('cobranza_completa');
}
```

### En `nueva_compra.js`:
```javascript
function abrirModalPagos() {
    $('#transaccionesModal').modal('show');
    aplicarConfiguracion('proveedor_completa');
}
```

## 🎮 EVENTOS Y CALLBACKS

```javascript
// Evento cuando se cambia la configuración
document.addEventListener('metodosConfigurados', function(e) {
    console.log('Métodos configurados:', e.detail.metodos);
});

// Evento cuando se deshabilita un método
document.addEventListener('metodoDeshabilitado', function(e) {
    console.log('Método deshabilitado:', e.detail.metodo, e.detail.razon);
});
```

¡Con estas herramientas tienes **control total** sobre qué métodos de pago están disponibles en cada situación! 🚀