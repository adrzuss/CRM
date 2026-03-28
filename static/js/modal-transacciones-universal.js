/**
 * ================================================================
 *                JAVASCRIPT UNIVERSAL PARA MODAL TRANSACCIONES
 * ================================================================
 * 
 * Este archivo proporciona funcionalidad JavaScript universal
 * para la modal de transacciones que funciona en todos los contextos:
 * - Ventas
 * - Cobranzas  
 * - Proveedores (compras, gastos, órdenes de pago)
 */

// Verificar que BASE_URL esté disponible
if (typeof BASE_URL === 'undefined') {
    window.BASE_URL = window.BASE_URL || '';
    console.log('🔧 [UNIVERSAL] BASE_URL no estaba definida, usando cadena vacía');
}

// ================================================================
//                    CONTROL DE MÉTODOS DE PAGO
// ================================================================

/**
 * Habilita/Deshabilita métodos de pago específicos
 * @param {Array} metodosPermitidos - Array con los métodos permitidos
 * @param {String} razon - Razón del cambio (opcional, para debugging)
 */
function configurarMetodosPago(metodosPermitidos = [], razon = '') {
    console.log('🎯 [CONTROL] Configurando métodos de pago:', metodosPermitidos);
    if (razon) console.log('🎯 [CONTROL] Razón:', razon);
    
    const todosLosMetodos = ['efectivo', 'tarjetas', 'ctacte', 'credito', 'bonificacion', 'cheques', 'valores'];
    
    todosLosMetodos.forEach(metodo => {
        const tab = document.getElementById(`${metodo}-tab`);
        const tabPane = document.getElementById(`pago-${metodo}`);
        const navItem = tab?.closest('.nav-item');
        
        if (metodosPermitidos.includes(metodo)) {
            // HABILITAR método
            if (navItem) {
                navItem.style.display = 'block';
                tab.classList.remove('disabled');
                tab.removeAttribute('disabled');
            }
            if (tabPane) {
                tabPane.style.display = 'block';
            }
            console.log(`✅ [CONTROL] ${metodo.toUpperCase()} habilitado`);
        } else {
            // DESHABILITAR método
            if (navItem) {
                navItem.style.display = 'none';
            }
            if (tabPane) {
                tabPane.style.display = 'none';
                // Limpiar valores del método deshabilitado
                limpiarMetodoPago(metodo);
            }
            console.log(`❌ [CONTROL] ${metodo.toUpperCase()} deshabilitado`);
        }
    });
    
    // Activar el primer método disponible
    activarPrimerMetodoDisponible(metodosPermitidos);
}

/**
 * Deshabilita temporalmente un método de pago específico
 * @param {String} metodo - Nombre del método a deshabilitar
 * @param {String} razon - Razón del bloqueo
 */
function deshabilitarMetodo(metodo, razon = '') {
    console.log(`🚫 [CONTROL] Deshabilitando ${metodo}:`, razon);
    
    const tab = document.getElementById(`${metodo}-tab`);
    const input = document.getElementById(metodo);
    
    if (tab) {
        tab.classList.add('disabled');
        tab.setAttribute('disabled', 'true');
        tab.style.opacity = '0.5';
        tab.title = `No disponible: ${razon}`;
    }
    
    if (input) {
        input.disabled = true;
        input.value = '0';
        input.style.backgroundColor = '#f8f9fa';
    }
}

/**
 * Habilita un método de pago previamente deshabilitado
 * @param {String} metodo - Nombre del método a habilitar
 */
function habilitarMetodo(metodo) {
    console.log(`✅ [CONTROL] Habilitando ${metodo}`);
    
    const tab = document.getElementById(`${metodo}-tab`);
    const input = document.getElementById(metodo);
    
    if (tab) {
        tab.classList.remove('disabled');
        tab.removeAttribute('disabled');
        tab.style.opacity = '1';
        tab.removeAttribute('title');
    }
    
    if (input) {
        input.disabled = false;
        input.style.backgroundColor = '';
    }
}

/**
 * Limpia los valores de un método de pago específico
 * @param {String} metodo - Nombre del método a limpiar
 */
function limpiarMetodoPago(metodo) {
    const campos = {
        efectivo: ['efectivo'],
        tarjetas: ['tarjeta', 'entidad', 'cuotas', 'coeficiente', 'documento', 'telefono', 'total_tarjeta'],
        ctacte: ['ctacte'],
        credito: ['credito'],
        bonificacion: ['bonificacion'],
        cheques: ['cantCheques', 'fechaEmision', 'vtoCheque', 'diasCheques', 'importeCheques'],
        valores: ['tipoValor', 'numeroValor', 'bancoValor', 'fechaEmisionValor', 'fechaVtoValor', 'importeValor']
    };
    
    const camposALimpiar = campos[metodo] || [];
    camposALimpiar.forEach(campo => {
        const elemento = document.getElementById(campo);
        if (elemento) {
            elemento.value = elemento.type === 'number' ? '0' : '';
        }
    });
    
    // Limpiar tablas dinámicas
    if (metodo === 'cheques') {
        const tbody = document.getElementById('cheques');
        if (tbody) tbody.innerHTML = '';
        actualizarTotalCheques();
    }
    
    if (metodo === 'valores') {
        const tbody = document.getElementById('valores');
        if (tbody) tbody.innerHTML = '';
        actualizarTotalValores();
    }
}

/**
 * Activa el primer método de pago disponible
 * @param {Array} metodosDisponibles - Array con los métodos disponibles
 */
function activarPrimerMetodoDisponible(metodosDisponibles) {
    if (metodosDisponibles.length === 0) return;
    
    const primerMetodo = metodosDisponibles[0];
    const tab = document.getElementById(`${primerMetodo}-tab`);
    
    if (tab) {
        tab.click();
        console.log(`🎯 [CONTROL] Activado automáticamente: ${primerMetodo}`);
        
        // Focus en el campo principal del método
        setTimeout(() => {
            const input = document.getElementById(primerMetodo === 'tarjetas' ? 'tarjeta' : primerMetodo);
            if (input) input.focus();
        }, 100);
    }
}

// ================================================================
//                    CONFIGURACIONES PREDEFINIDAS
// ================================================================

/**
 * Configuraciones predefinidas para diferentes escenarios
 */
const CONFIGURACIONES_PAGO = {
    // VENTAS
    'venta_completa': ['efectivo', 'tarjetas', 'ctacte', 'credito', 'bonificacion', 'valores'],
    'venta_rapida': ['efectivo', 'tarjetas'],
    'venta_credito': ['efectivo', 'credito'],
    'venta_sin_credito': ['efectivo', 'tarjetas', 'ctacte', 'bonificacion', 'valores'],
    
    // COBRANZAS
    'cobranza_completa': ['efectivo', 'tarjetas', 'ctacte', 'bonificacion', 'valores'],
    'cobranza_solo_efectivo': ['efectivo'],
    'cobranza_sin_tarjetas': ['efectivo', 'ctacte', 'valores'],
    
    // PROVEEDORES  
    'proveedor_completa': ['efectivo', 'ctacte', 'bonificacion', 'cheques'],
    'proveedor_solo_efectivo': ['efectivo'],
    'proveedor_cheques': ['cheques'],
    
    // ESPECIALES
    'solo_cuenta_corriente': ['ctacte'],
    'sin_bonificaciones': ['efectivo', 'tarjetas', 'ctacte', 'credito', 'valores'],
    'efectivo_tarjetas': ['efectivo', 'tarjetas']
};

/**
 * Aplica una configuración predefinida
 * @param {String} nombreConfig - Nombre de la configuración
 */
function aplicarConfiguracion(nombreConfig) {
    const config = CONFIGURACIONES_PAGO[nombreConfig];
    if (config) {
        configurarMetodosPago(config, `Aplicando configuración: ${nombreConfig}`);
    } else {
        console.warn(`⚠️ [CONTROL] Configuración '${nombreConfig}' no encontrada`);
    }
}

/**
 * Configuraciones contextuales basadas en condiciones
 * @param {Object} condiciones - Objeto con las condiciones a evaluar
 */
function configurarSegunCondiciones(condiciones = {}) {
    console.log('🧠 [CONTROL] Evaluando condiciones:', condiciones);
    
    let metodosPermitidos = [];
    
    // Evaluar tipo de operación
    if (condiciones.esVenta) {
        metodosPermitidos = ['efectivo', 'tarjetas', 'ctacte', 'credito', 'bonificacion', 'valores'];
    } else if (condiciones.esCobranza) {
        metodosPermitidos = ['efectivo', 'tarjetas', 'ctacte', 'bonificacion', 'valores'];
    } else if (condiciones.esProveedor) {
        metodosPermitidos = ['efectivo', 'ctacte', 'bonificacion', 'cheques'];
    }
    
    // Restricciones por cliente/proveedor
    if (condiciones.clienteSinCredito) {
        metodosPermitidos = metodosPermitidos.filter(m => m !== 'credito');
    }
    
    if (condiciones.clienteSoloEfectivo) {
        metodosPermitidos = ['efectivo'];
    }
    
    if (condiciones.proveedorSinCheques) {
        metodosPermitidos = metodosPermitidos.filter(m => m !== 'cheques');
    }
    
    // Restricciones por monto
    if (condiciones.montoMinimo && condiciones.montoActual < condiciones.montoMinimo) {
        metodosPermitidos = metodosPermitidos.filter(m => m !== 'tarjetas');
    }
    
    // Restricciones por horario
    if (condiciones.fueraDeHorario) {
        metodosPermitidos = metodosPermitidos.filter(m => !['tarjetas', 'cheques'].includes(m));
    }
    
    // Aplicar configuración resultante
    configurarMetodosPago(metodosPermitidos, 'Configuración basada en condiciones');
    
    return metodosPermitidos;
}

// ================================================================
//                    FUNCIONES DE CÁLCULO UNIVERSAL
// ================================================================

/**
 * Actualiza el campo "Total a pagar" - INFORMACIÓN FIJA para el usuario
 * Muestra cuánto costaría pagar TODO el saldo restante con la tarjeta seleccionada
 * NO cambia según el importe que ingrese el usuario, es solo informativo
 */
function actualizarTotalTarjeta() {
    const totalTarjetaField = document.getElementById('total_tarjeta');
    const totalFacElement = document.getElementById('modal_total_factura');
    const coeficienteInput = document.getElementById('coeficiente');
    
    if (totalTarjetaField && totalFacElement && coeficienteInput) {
        const totalFactura = parseFloat(totalFacElement.textContent) || 0;
        const coeficiente = parseFloat(coeficienteInput.value) || 1;
        
        // Calcular otros pagos (efectivo, cheque, valores) para obtener saldo real
        const efectivo = parseFloat(document.getElementById('efectivo')?.value) || 0;
        const totalCheques = parseFloat(document.getElementById('totalCheques')?.textContent) || 0;
        const totalValores = parseFloat(document.getElementById('totalValores')?.textContent) || 0;
        const otrosPagos = efectivo + totalCheques + totalValores;
        
        // Saldo real disponible para pagar con tarjeta
        const saldoRestante = Math.max(0, totalFactura - otrosPagos);
        
        // Total a pagar = lo que costaría pagar TODO el saldo con esta tarjeta
        const totalConRecargo = saldoRestante * coeficiente;
        totalTarjetaField.value = totalConRecargo.toFixed(2);
        
        console.log('💳 [TOTAL INFORMATIVO] Campo actualizado:', {
            totalFactura: totalFactura.toFixed(2),
            otrosPagos: otrosPagos.toFixed(2),
            saldoRestante: saldoRestante.toFixed(2),
            coeficiente: coeficiente,
            totalConRecargo: totalConRecargo.toFixed(2),
            nota: 'Este es un campo INFORMATIVO - no cambia con el importe ingresado'
        });
    }
}

/**
 * Calcula el saldo de la transacción
 * Funciona en todos los contextos con los mismos nombres de campos
 */
function calcSaldo() {
    console.log('🔥 [UNIVERSAL] ═══════════════════════════════════════');
    console.log('🔥 [UNIVERSAL] calcSaldo() INICIANDO EJECUCIÓN');
    console.log('🔥 [UNIVERSAL] Timestamp:', new Date().toLocaleTimeString());
    console.log('🔥 [UNIVERSAL] ═══════════════════════════════════════');
    
    // Obtener total de la factura/transacción del modal
    console.log('🔥 [UNIVERSAL] Stack trace de llamada:');
    console.trace();
    const totalFacElement = document.getElementById('modal_total_factura');
    const totalFac = parseFloat(totalFacElement?.textContent) || 0;
    
    console.log('🧮 calcSaldo() - Total factura elemento:', totalFacElement);
    console.log('🧮 calcSaldo() - Total factura valor:', totalFac);
    
    // Obtener todos los métodos de pago
    const efectivo = parseFloat(document.getElementById('efectivo')?.value) || 0;
    const tarjeta = parseFloat(document.getElementById('tarjeta')?.value) || 0;
    const ctacte = parseFloat(document.getElementById('ctacte')?.value) || 0;
    const credito = parseFloat(document.getElementById('credito')?.value) || 0;
    const bonificacion = parseFloat(document.getElementById('bonificacion')?.value) || 0;
    
    console.log('💰 Valores de pago:', {efectivo, tarjeta, ctacte, credito, bonificacion});
    
    // Totales de cheques y valores (calculados dinámicamente)
    const totalCheques = parseFloat(document.getElementById('totalCheques')?.textContent.replace(/[^0-9.-]/g, '')) || 0;
    const totalValores = parseFloat(document.getElementById('totalValores')?.textContent.replace(/[^0-9.-]/g, '')) || 0;
    
    // Calcular total pagado/cobrado
    let totalPagado = efectivo + ctacte + credito + bonificacion + totalCheques + totalValores;
    
    // CRÍTICO: Para el SALDO, debemos calcular cuánto se paga REALMENTE de la deuda
    // Si pagas $7,500 con tarjeta pero $2,500 son intereses, solo $5,000 van a la deuda
    if (tarjeta > 0) {
        const coeficiente = parseFloat(document.getElementById('coeficiente')?.value) || 1;
        
        // ⚠️ FUNDAMENTAL: Si el importe ingresado incluye intereses, 
        // debemos calcular cuánto va realmente a pagar la deuda
        let importeAplicadoADeuda;
        
        if (coeficiente > 1) {
            // El usuario ingresó el monto TOTAL (con intereses)
            // Debemos calcular cuánto va realmente a la deuda
            importeAplicadoADeuda = tarjeta / coeficiente;
        } else {
            // Sin intereses, todo el importe va a la deuda
            importeAplicadoADeuda = tarjeta;
        }
        
        totalPagado += importeAplicadoADeuda; // Solo lo que paga la deuda real
        
        console.log('💳 [SALDO CORRECTO] Cálculo sin intereses:', {
            importeIngresado: tarjeta,
            coeficiente: coeficiente,
            'importe_aplicado_a_deuda': importeAplicadoADeuda.toFixed(2),
            'intereses_no_aplicados': (tarjeta - importeAplicadoADeuda).toFixed(2),
            totalFactura: totalFac,
            saldoResultante: (totalFac - (totalPagado)).toFixed(2),
            nota: 'Solo el importe sin intereses reduce el saldo'
        });
    }
    
    // Calcular diferencia
    const diferencia = totalFac - totalPagado;
    
    console.log('📊 Cálculo final:', {
        totalFac, 
        totalPagado, 
        diferencia,
        isNaN: isNaN(diferencia)
    });
    
    // Actualizar el contenido del saldo
    const lblSaldo = document.getElementById('saldo_factura');
    if (lblSaldo) {
        const saldoValue = isNaN(diferencia) ? '0.00' : Math.abs(diferencia).toFixed(2);
        const valorAnterior = lblSaldo.textContent;
        
        lblSaldo.textContent = saldoValue;
        console.log('💯 [UNIVERSAL] Saldo actualizado de:', valorAnterior, 'a:', saldoValue, 'en elemento:', lblSaldo);
        
        // Verificar que el cambio se aplicó visualmente
        setTimeout(() => {
            const valorFinal = lblSaldo.textContent;
            if (valorFinal === saldoValue) {
                console.log('✅ [UNIVERSAL] Cambio visual CONFIRMADO en DOM:', valorFinal);
            } else {
                console.error('❌ [UNIVERSAL] El cambio visual NO se aplicó. Esperado:', saldoValue, 'Actual:', valorFinal);
            }
        }, 50);
        
    } else {
        console.error('❌ [UNIVERSAL] Elemento saldo_factura no encontrado');
        
        // Buscar elementos alternativos para el saldo
        const alternativeSaldoElements = document.querySelectorAll('[id*="saldo"], [class*="saldo"], [id*="total"], [class*="total"]');
        console.log('🔍 [UNIVERSAL] Elementos con "saldo" o "total" encontrados:', alternativeSaldoElements.length);
        alternativeSaldoElements.forEach((el, i) => {
            console.log(`   ${i}: id="${el.id}" class="${el.className}" tagName="${el.tagName}" textContent="${el.textContent}"`);
        });
    }
    
    // Actualizar la clase del contenedor para colores
    const saldoContainer = document.getElementById('saldo-container');
    if (saldoContainer) {
        if (diferencia > 0.01) {
            saldoContainer.className = 'total-amount negativo mb-0';
        } else if (Math.abs(diferencia) <= 0.01) {
            saldoContainer.className = 'total-amount neutro mb-0';
        } else {
            saldoContainer.className = 'total-amount positivo mb-0';
        }
        console.log('🎨 [UNIVERSAL] Clase del contenedor actualizada:', saldoContainer.className);
    } else {
        console.error('❌ [UNIVERSAL] Elemento saldo-container no encontrado');
        
        // Buscar contenedores alternativos
        const alternativeContainers = document.querySelectorAll('[id*="saldo"], [class*="saldo"], [id*="container"], [class*="container"]');
        console.log('🔍 [UNIVERSAL] Contenedores encontrados:', alternativeContainers.length);
        alternativeContainers.forEach((el, i) => {
            if (el.id.includes('saldo') || el.className.includes('saldo')) {
                console.log(`   ${i}: id="${el.id}" class="${el.className}" tagName="${el.tagName}"`);
            }
        });
    }
    
    console.log('🔥 [UNIVERSAL] ═══════════════════════════════════════');
    console.log('🔥 [UNIVERSAL] calcSaldo() TERMINANDO - Diferencia:', diferencia);
    console.log('🔥 [UNIVERSAL] ═══════════════════════════════════════');
    
    return diferencia;
}

/**
 * Verifica si la transacción está balanceada
 */
function checkTotales() {
    const diferencia = calcSaldo();
    return Math.abs(diferencia) <= 0.01; // Permitir diferencia de centavos
}

// ================================================================
//                    FUNCIONES DE TARJETAS
// ================================================================

/**
 * Obtiene el coeficiente de cuotas desde el servidor
 * @param {number} entidadId - ID de la entidad (tarjeta)
 * @param {number} cuotas - Número de cuotas
 * @returns {Promise<number>} - Coeficiente calculado
 */
async function obtenerCoeficiente(entidadId, cuotas) {
    // Validaciones iniciales
    if (!cuotas || cuotas <= 0) {
        console.log('⚠️ [TARJETA] Cuotas inválidas, retornando coeficiente 1');
        return 1;
    }
    
    if (!entidadId || entidadId === '') {
        console.log('⚠️ [TARJETA] Entidad no seleccionada, retornando coeficiente 1');
        return 1;
    }
    
    try {
        console.log('🏦 [TARJETA] Obteniendo coeficiente para entidad:', entidadId, 'cuotas:', cuotas);
        
        // Usar la misma URL que nueva_venta.js
        const baseUrl = window.BASE_URL || '';
        const url = `${baseUrl}/entidades/coeficiente_cuotas/${entidadId}/${cuotas}`;
        console.log('📡 [TARJETA] Haciendo petición a:', url);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('📦 [TARJETA] Respuesta del servidor:', data);
            
            // Validar que la respuesta tenga el formato esperado
            if (data && data.coeficiente !== undefined && data.coeficiente !== null) {
                // Convertir a número si viene como string
                const coeficiente = typeof data.coeficiente === 'string' ? 
                    parseFloat(data.coeficiente) : 
                    data.coeficiente;
                
                if (!isNaN(coeficiente) && coeficiente > 0) {
                    console.log('✅ [TARJETA] Coeficiente obtenido y convertido:', coeficiente, 'tipo:', typeof coeficiente);
                    return coeficiente;
                } else {
                    console.warn('⚠️ [TARJETA] Coeficiente inválido después de conversión:', coeficiente);
                    return 1;
                }
            } else {
                console.warn('⚠️ [TARJETA] Respuesta sin coeficiente válido:', data);
                return 1;
            }
        } else {
            console.error('❌ [TARJETA] Error HTTP al obtener coeficiente:', response.status, response.statusText);
            
            // Intentar leer el error del servidor
            try {
                const errorData = await response.json();
                console.error('❌ [TARJETA] Detalle del error:', errorData);
            } catch (e) {
                console.error('❌ [TARJETA] No se pudo leer el error del servidor');
            }
            
            return 1;
        }
    } catch (error) {
        console.error('❌ [TARJETA] Error de red al obtener coeficiente:', error);
        console.error('❌ [TARJETA] Stack trace:', error.stack);
        return 1;
    }
}

/**
 * Actualiza el coeficiente cuando cambia la entidad o cuotas
 */
async function actualizarCoeficiente() {
    const entidadSelect = document.getElementById('entidad');
    const cuotasInput = document.getElementById('cuotas');
    const coeficienteInput = document.getElementById('coeficiente');
    const tarjetaInput = document.getElementById('tarjeta');
    
    console.log('🔄 [TARJETA] actualizarCoeficiente() ejecutándose...');
    console.log('   - Entidad element:', entidadSelect);
    console.log('   - Cuotas element:', cuotasInput);
    console.log('   - Coeficiente element:', coeficienteInput);
    
    if (entidadSelect && cuotasInput && coeficienteInput) {
        const entidadId = entidadSelect.value;
        const cuotas = parseInt(cuotasInput.value) || 1;
        
        console.log('🏦 [TARJETA] Valores actuales - Entidad:', entidadId, 'Cuotas:', cuotas);
        
        if (!entidadId) {
            console.log('⚠️ [TARJETA] No hay entidad seleccionada, usando coeficiente 1');
            coeficienteInput.value = '1.0000';
            calcSaldo();
            return;
        }
        
        try {
            // Mostrar indicador de carga sin cambiar el valor del input
            const originalValue = coeficienteInput.value;
            coeficienteInput.disabled = true;
            coeficienteInput.style.backgroundColor = '#f8f9fa';
            coeficienteInput.style.opacity = '0.7';
            
            // Agregar spinner visual si no existe
            let spinner = coeficienteInput.parentNode.querySelector('.coeficiente-spinner');
            if (!spinner) {
                spinner = document.createElement('div');
                spinner.className = 'coeficiente-spinner position-absolute';
                spinner.innerHTML = '<i class="fas fa-spinner fa-spin text-primary"></i>';
                spinner.style.cssText = 'top: 50%; right: 10px; transform: translateY(-50%); z-index: 10;';
                coeficienteInput.parentNode.style.position = 'relative';
                coeficienteInput.parentNode.appendChild(spinner);
            }
            
            console.log('⏳ [TARJETA] Obteniendo coeficiente...');
            
            // Obtener coeficiente del servidor
            const coeficiente = await obtenerCoeficiente(entidadId, cuotas);
            
            // Remover spinner
            if (spinner) {
                spinner.remove();
            }
            
            // Validar el coeficiente recibido
            if (typeof coeficiente === 'number' && !isNaN(coeficiente)) {
                // Actualizar campo
                const coeficienteFormateado = coeficiente.toFixed(4);
                coeficienteInput.value = coeficienteFormateado;
                coeficienteInput.disabled = false;
                coeficienteInput.style.backgroundColor = '';
                coeficienteInput.style.opacity = '';
                
                console.log('✅ [TARJETA] Coeficiente actualizado exitosamente:', {
                    original: coeficiente,
                    formateado: coeficienteFormateado,
                    campoValor: coeficienteInput.value
                });
                
                // Actualizar "Total a pagar" (campo informativo que muestra saldo × coeficiente)
                actualizarTotalTarjeta();
                console.log('💳 [TARJETA] Coeficiente actualizado, Total a pagar recalculado como información...');
            } else {
                console.error('❌ [TARJETA] Coeficiente recibido inválido:', coeficiente, typeof coeficiente);
                // Usar valor por defecto
                coeficienteInput.value = '1.0000';
                coeficienteInput.disabled = false;
                coeficienteInput.style.backgroundColor = '';
                coeficienteInput.style.opacity = '';
            }
            
            // Recalcular totales
            calcSaldo();
            
        } catch (error) {
            console.error('❌ [TARJETA] Error al actualizar coeficiente:', error);
            
            // Remover spinner si existe
            const spinner = coeficienteInput.parentNode.querySelector('.coeficiente-spinner');
            if (spinner) {
                spinner.remove();
            }
            
            coeficienteInput.value = '1.0000';
            coeficienteInput.disabled = false;
            coeficienteInput.style.backgroundColor = '';
            coeficienteInput.style.opacity = '';
            calcSaldo();
        }
    } else {
        console.warn('⚠️ [TARJETA] Elementos de tarjeta no encontrados en modal');
        
        // Debug: buscar elementos alternativos
        const allEntidadElements = document.querySelectorAll('[id*="entidad"], [name*="entidad"]');
        const allCuotasElements = document.querySelectorAll('[id*="cuotas"], [name*="cuotas"]');
        const allCoeficienteElements = document.querySelectorAll('[id*="coeficiente"], [name*="coeficiente"]');
        
        console.log('🔍 [TARJETA DEBUG] Elementos con "entidad":', allEntidadElements.length);
        allEntidadElements.forEach((el, i) => console.log(`   ${i}: id="${el.id}" name="${el.name}"`));
        
        console.log('🔍 [TARJETA DEBUG] Elementos con "cuotas":', allCuotasElements.length);
        allCuotasElements.forEach((el, i) => console.log(`   ${i}: id="${el.id}" name="${el.name}"`));
        
        console.log('🔍 [TARJETA DEBUG] Elementos con "coeficiente":', allCoeficienteElements.length);
        allCoeficienteElements.forEach((el, i) => console.log(`   ${i}: id="${el.id}" name="${el.name}"`));
    }
}

// ================================================================
//                    FUNCIONES DE CHEQUES
// ================================================================

/**
 * Genera cheques automáticamente
 */
function generarCheque() {
    const banco = document.getElementById('banco')?.value;
    const cantidad = parseInt(document.getElementById('cantCheques')?.value) || 0;
    const fechaEmision = document.getElementById('fechaEmision')?.value;
    const fechaVto = document.getElementById('vtoCheque')?.value;
    const diasEntre = parseInt(document.getElementById('diasCheques')?.value) || 30;
    const importe = parseFloat(document.getElementById('importeCheques')?.value) || 0;
    
    if (!banco || cantidad <= 0 || !fechaVto || importe <= 0) {
        mostrarAdvertencia('Por favor, complete todos los campos para generar cheques.');
        return;
    }
    
    const tbody = document.getElementById('cheques');
    if (!tbody) return;
    
    // Limpiar cheques existentes
    tbody.innerHTML = '';
    
    let fechaActual = new Date(fechaVto);
    
    for (let i = 0; i < cantidad; i++) {
        const row = document.createElement('tr');
        const numeroCheque = generarNumeroCheque(); // Implementar según tu lógica
        
        row.innerHTML = `
            <td>${numeroCheque}</td>
            <td>${fechaActual.toLocaleDateString()}</td>
            <td>$${importe.toFixed(2)}</td>
            <td>${document.getElementById('banco').options[document.getElementById('banco').selectedIndex].text}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="eliminarCheque(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
            <input type="hidden" name="cheques[${i}][numero]" value="${numeroCheque}">
            <input type="hidden" name="cheques[${i}][fecha_vto]" value="${fechaActual.toISOString().split('T')[0]}">
            <input type="hidden" name="cheques[${i}][importe]" value="${importe}">
            <input type="hidden" name="cheques[${i}][banco]" value="${banco}">
            <input type="hidden" name="cheques[${i}][fecha_emision]" value="${fechaEmision}">
        `;
        
        tbody.appendChild(row);
        
        // Avanzar fecha para el siguiente cheque
        fechaActual.setDate(fechaActual.getDate() + diasEntre);
    }
    
    // Actualizar total
    actualizarTotalCheques();
}

/**
 * Actualiza el total de cheques
 */
function actualizarTotalCheques() {
    const tbody = document.getElementById('cheques');
    const totalSpan = document.getElementById('totalCheques');
    
    if (!tbody || !totalSpan) return;
    
    let total = 0;
    const hiddenInputs = tbody.querySelectorAll('input[name*="[importe]"]');
    
    hiddenInputs.forEach(input => {
        total += parseFloat(input.value) || 0;
    });
    
    totalSpan.textContent = total.toFixed(2);
    
    // Actualizar "Total a pagar" si hay tarjeta configurada (informativo)
    const coeficienteInput = document.getElementById('coeficiente');
    if (coeficienteInput && parseFloat(coeficienteInput.value) > 1) {
        actualizarTotalTarjeta();
    }
    
    calcSaldo(); // Recalcular saldo total
}

/**
 * Elimina un cheque específico
 */
function eliminarCheque(button) {
    const row = button.closest('tr');
    row.remove();
    actualizarTotalCheques();
}

/**
 * Limpia todos los cheques
 */
function limpiarCheque() {
    const tbody = document.getElementById('cheques');
    if (tbody) {
        tbody.innerHTML = '';
        actualizarTotalCheques();
    }
}

/**
 * Genera un número de cheque único
 */
function generarNumeroCheque() {
    // Implementar según tu lógica de numeración
    return Math.floor(Math.random() * 1000000).toString().padStart(8, '0');
}

// ================================================================
//                    FUNCIONES DE VALORES
// ================================================================

/**
 * Agrega un valor (cheque recibido, pagaré, etc.)
 */
function agregarValor() {
    const tipo = document.getElementById('tipoValor')?.value;
    const numero = document.getElementById('numeroValor')?.value;
    const banco = document.getElementById('bancoValor')?.value;
    const fechaEmision = document.getElementById('fechaEmisionValor')?.value;
    const fechaVto = document.getElementById('fechaVtoValor')?.value;
    const importe = parseFloat(document.getElementById('importeValor')?.value) || 0;
    
    if (!numero || !fechaVto || importe <= 0) {
        mostrarAdvertencia('Por favor, complete número, fecha de vencimiento e importe.');
        return;
    }
    
    const tbody = document.getElementById('valores');
    if (!tbody) return;
    
    const row = document.createElement('tr');
    const index = tbody.children.length;
    
    row.innerHTML = `
        <td>${tipo}</td>
        <td>${numero}</td>
        <td>${banco ? document.getElementById('bancoValor').options[document.getElementById('bancoValor').selectedIndex].text : 'N/A'}</td>
        <td>${fechaEmision || 'N/A'}</td>
        <td>${fechaVto}</td>
        <td>$${importe.toFixed(2)}</td>
        <td>
            <button class="btn btn-sm btn-danger" onclick="eliminarValor(this)">
                <i class="fas fa-trash"></i>
            </button>
        </td>
        <input type="hidden" name="valores[${index}][tipo]" value="${tipo}">
        <input type="hidden" name="valores[${index}][numero]" value="${numero}">
        <input type="hidden" name="valores[${index}][banco]" value="${banco}">
        <input type="hidden" name="valores[${index}][fecha_emision]" value="${fechaEmision}">
        <input type="hidden" name="valores[${index}][fecha_vto]" value="${fechaVto}">
        <input type="hidden" name="valores[${index}][importe]" value="${importe}">
    `;
    
    tbody.appendChild(row);
    
    // Limpiar formulario
    document.getElementById('numeroValor').value = '';
    document.getElementById('fechaEmisionValor').value = '';
    document.getElementById('fechaVtoValor').value = '';
    document.getElementById('importeValor').value = '0';
    
    // Actualizar total
    actualizarTotalValores();
}

/**
 * Actualiza el total de valores
 */
function actualizarTotalValores() {
    const tbody = document.getElementById('valores');
    const totalSpan = document.getElementById('totalValores');
    
    if (!tbody || !totalSpan) return;
    
    let total = 0;
    const hiddenInputs = tbody.querySelectorAll('input[name*="[importe]"]');
    
    hiddenInputs.forEach(input => {
        total += parseFloat(input.value) || 0;
    });
    
    totalSpan.textContent = total.toFixed(2);
    
    // Actualizar "Total a pagar" si hay tarjeta configurada (informativo)
    const coeficienteInput = document.getElementById('coeficiente');
    if (coeficienteInput && parseFloat(coeficienteInput.value) > 1) {
        actualizarTotalTarjeta();
    }
    
    calcSaldo(); // Recalcular saldo total
}

/**
 * Elimina un valor específico
 */
function eliminarValor(button) {
    const row = button.closest('tr');
    row.remove();
    actualizarTotalValores();
}

/**
 * Limpia todos los valores
 */
function limpiarValores() {
    const tbody = document.getElementById('valores');
    if (tbody) {
        tbody.innerHTML = '';
        actualizarTotalValores();
    }
}

// ================================================================
//                    PROCESAMIENTO DE TRANSACCIÓN
// ================================================================

/**
 * Procesa la transacción (pago/cobro)
 */
async function procesarTransaccion() {
    if (!checkTotales()) {
        const diferencia = calcSaldo();
        const mensaje = diferencia > 0 ? 
            `Falta pagar $${diferencia.toFixed(2)}` : 
            `Sobra $${Math.abs(diferencia).toFixed(2)}`;
        
        const continuar = await confirmar(`${mensaje}. ¿Desea continuar de todas formas?`);
        if (!continuar) {
            return false;
        }
    }
    
    // Aquí puedes agregar validaciones específicas por contexto
    return true;
}

// ================================================================
//                    EVENT LISTENERS UNIVERSALES
// ================================================================

// LISTENERS REMOVIDOS: Ahora se configuran dinámicamente en cargarDatosModal()
// para evitar conflictos y duplicaciones

document.addEventListener('DOMContentLoaded', function() {
    // Event listener para cuando se abre el modal
    $('#transaccionesModal').on('shown.bs.modal', function() {
        // Enfocar el primer input disponible
        const primerInput = document.querySelector('#transaccionesModal input:not([readonly]):not([type="hidden"])');
        if (primerInput) {
            setTimeout(() => primerInput.focus(), 100);
        }
        
        // Calcular saldo inicial
        calcSaldo();
    });
    
    // Validación al cerrar
    $('#transaccionesModal').on('hide.bs.modal', function(e) {
        // Aquí puedes agregar validaciones antes de cerrar si es necesario
    });
});

// ================================================================
//                    FUNCIONES HELPER
// ================================================================

/**
 * Formatea un número como moneda
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS'
    }).format(amount);
}

/**
 * Función listener que se reutiliza para evitar duplicados
 */
function handlePaymentFieldChange(event) {
    const fieldId = event.target.id;
    const fieldValue = event.target.value;
    
    console.log(`🔥 [UNIVERSAL LISTENER] Campo ${fieldId} cambió a: "${fieldValue}"`);
    
    // Si cambia un campo que afecta el saldo disponible para tarjeta,
    // actualizar el "Total a pagar" (información sobre pagar todo con tarjeta)
    if (['efectivo', 'ctacte', 'credito', 'bonificacion'].includes(fieldId)) {
        console.log('📊 [UNIVERSAL] Campo afecta saldo - actualizando Total a pagar informativo...');
        // Solo actualizar si el coeficiente ya está definido
        const coeficienteInput = document.getElementById('coeficiente');
        if (coeficienteInput && parseFloat(coeficienteInput.value) > 1) {
            actualizarTotalTarjeta();
        }
    } else if (fieldId === 'tarjeta') {
        console.log('💳 [UNIVERSAL] Campo tarjeta cambió - NO afecta Total a pagar (es informativo)');
    }
    
    // Verificar que calcSaldo esté disponible
    console.log('🔍 [UNIVERSAL] Verificando calcSaldo...');
    console.log('   - typeof calcSaldo:', typeof calcSaldo);
    console.log('   - typeof window.calcSaldo:', typeof window.calcSaldo);
    console.log('   - calcSaldo === window.calcSaldo:', calcSaldo === window.calcSaldo);
    
    if (typeof calcSaldo === 'function') {
        console.log('🧮 [UNIVERSAL] Llamando calcSaldo UNIVERSAL...');
        try {
            const resultado = calcSaldo();
            console.log('✅ [UNIVERSAL] calcSaldo ejecutado exitosamente, resultado:', resultado);
        } catch (error) {
            console.error('💥 [UNIVERSAL] Error al ejecutar calcSaldo:', error);
            console.error('💥 [UNIVERSAL] Stack trace del error:', error.stack);
        }
    } else if (typeof window.calcSaldo === 'function') {
        console.log('🧮 [UNIVERSAL] Llamando window.calcSaldo...');
        try {
            const resultado = window.calcSaldo();
            console.log('✅ [UNIVERSAL] window.calcSaldo ejecutado exitosamente, resultado:', resultado);
        } catch (error) {
            console.error('💥 [UNIVERSAL] Error al ejecutar window.calcSaldo:', error);
        }
    } else {
        console.error('❌ [UNIVERSAL] calcSaldo no está disponible en ninguna forma');
        console.error('❌ [UNIVERSAL] typeof calcSaldo:', typeof calcSaldo);
        console.error('❌ [UNIVERSAL] typeof window.calcSaldo:', typeof window.calcSaldo);
    }
}

/**
 * Función para depurar event listeners duplicados
 */
function debugEventListeners() {
    const paymentFields = ['efectivo', 'tarjeta', 'ctacte', 'credito', 'bonificacion'];
    
    paymentFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            console.log(`🔍 [DEBUG] Campo ${fieldId}:`);
            console.log(`   - Valor actual: "${field.value}"`);
            console.log(`   - Elemento:`, field);
            console.log(`   - Parent container:`, field.closest('.modal') ? 'DENTRO DE MODAL ✅' : 'FUERA DE MODAL ❌');
            console.log(`   - Visible:`, field.offsetParent !== null ? 'SÍ ✅' : 'NO ❌');
            console.log(`   - Display style:`, getComputedStyle(field).display);
            
            // Si getEventListeners está disponible en DevTools
            if (typeof getEventListeners === 'function') {
                try {
                    const listeners = getEventListeners(field);
                    console.log(`   - Event listeners:`, listeners);
                } catch (e) {
                    console.log(`   - Event listeners: No disponible`);
                }
            }
        } else {
            console.log(`🔍 [DEBUG] Campo ${fieldId}: NO ENCONTRADO ❌`);
        }
    });
    
    // Buscar todos los elementos con IDs que contengan "efectivo"
    console.log('🔍 [DEBUG] Buscando TODOS los elementos con "efectivo" en el ID:');
    const allEfectivoElements = document.querySelectorAll('[id*="efectivo"]');
    allEfectivoElements.forEach((el, i) => {
        console.log(`   ${i}: id="${el.id}" value="${el.value}" visible=${el.offsetParent !== null} inModal=${el.closest('.modal') ? 'SÍ' : 'NO'}`);
    });
}

/**
 * Función para verificar que se está usando el elemento correcto
 */
function verificarElementoCorrecto(fieldId) {
    const field = document.getElementById(fieldId);
    const modalField = document.querySelector(`#transaccionesModal #${fieldId}`);
    
    console.log(`🎯 [VERIFY] Verificando ${fieldId}:`);
    console.log(`   - getElementById encontró:`, field?.id, field?.closest('.modal') ? 'en MODAL' : 'FUERA de modal');
    console.log(`   - querySelector modal encontró:`, modalField?.id, modalField ? 'en MODAL' : 'NO encontrado');
    
    if (field && modalField && field !== modalField) {
        console.warn(`⚠️ [VERIFY] CONFLICTO: getElementById y querySelector modal encuentran elementos DIFERENTES para ${fieldId}`);
        return false;
    }
    
    return true;
}

/**
 * Carga datos iniciales del modal
 */
function cargarDatosModal(totalFactura = 0) {
    console.log('🔄 [UNIVERSAL] cargarDatosModal() ejecutándose con total:', totalFactura);
    console.log('📍 [UNIVERSAL] URL actual:', window.location.pathname);
    
    const totalFacturaSpan = document.getElementById('modal_total_factura');
    if (totalFacturaSpan) {
        totalFacturaSpan.textContent = totalFactura.toFixed(2);
        console.log('✅ [UNIVERSAL] Total factura actualizado en modal:', totalFactura);
    } else {
        console.error('❌ [UNIVERSAL] Elemento modal_total_factura no encontrado');
        // Buscar elementos alternativos
        const alternativeElements = document.querySelectorAll('[id*="total"], [class*="total"]');
        console.log('🔍 [UNIVERSAL] Elementos con "total" encontrados:', alternativeElements.length);
        alternativeElements.forEach((el, i) => {
            console.log(`   ${i}: id="${el.id}" class="${el.className}"`);
        });
    }
    
    // Configurar event listeners para calcular saldo automáticamente
    const paymentFields = ['efectivo', 'tarjeta', 'ctacte', 'credito', 'bonificacion'];
    
    // Esperar un momento para asegurar que el DOM esté listo
    setTimeout(() => {
        console.log('🔧 [UNIVERSAL] Configurando event listeners...');
        console.log('🔍 [UNIVERSAL] Modal visible:', document.getElementById('transaccionesModal')?.classList.contains('show'));
        
        let successCount = 0;
        let failCount = 0;
        
        paymentFields.forEach(fieldId => {
            // Skip tarjeta field as it has its own specific handler
            if (fieldId === 'tarjeta') {
                console.log(`⏭️ [UNIVERSAL] Saltando ${fieldId} (tiene listener específico)`);
                return;
            }
            
            // Buscar específicamente dentro del modal para evitar conflictos con campos ocultos
            const modalSelector = `#transaccionesModal #${fieldId}`;
            const field = document.querySelector(modalSelector);
            
            console.log(`🎯 [UNIVERSAL] Buscando ${fieldId} en modal con selector: ${modalSelector}`);
            
            if (field) {
                console.log(`✅ [UNIVERSAL] Campo encontrado en modal: ${fieldId}`);
                console.log(`🧹 [UNIVERSAL] Limpiando listeners previos para ${fieldId}...`);
                
                // Verificar que es el elemento correcto (dentro de la modal)
                if (!field.closest('#transaccionesModal')) {
                    console.error(`❌ [UNIVERSAL] ERROR: Campo ${fieldId} NO está dentro de la modal!`);
                    failCount++;
                    return;
                }
                
                // Clonar el elemento para remover TODOS los event listeners
                const newField = field.cloneNode(true);
                field.parentNode.replaceChild(newField, field);
                
                // Referenciar el nuevo elemento usando el selector específico del modal
                const cleanField = document.querySelector(modalSelector);
                
                if (cleanField) {
                    // Agregar nuevo listener con función nombrada
                    cleanField.addEventListener('input', handlePaymentFieldChange);
                    cleanField.addEventListener('blur', handlePaymentFieldChange); // También en blur por compatibilidad
                    
                    console.log(`✅ [UNIVERSAL] Event listener configurado para ${fieldId} (valor: "${cleanField.value}", tipo: ${cleanField.type}, disabled: ${cleanField.disabled})`);
                    console.log(`🎯 [UNIVERSAL] Elemento está en modal: ${cleanField.closest('#transaccionesModal') ? 'SÍ ✅' : 'NO ❌'}`);
                    successCount++;
                    
                    // Test inmediato para verificar que funciona
                    console.log(`🧪 [UNIVERSAL] Disparando evento test para ${fieldId}...`);
                    cleanField.dispatchEvent(new Event('input', { bubbles: true }));
                } else {
                    console.error(`❌ [UNIVERSAL] Error: No se pudo referenciar el campo clonado ${fieldId}`);
                    failCount++;
                }
            } else {
                console.warn(`⚠️ [UNIVERSAL] Campo ${fieldId} no encontrado en modal`);
                failCount++;
                
                // Debug: verificar si existe fuera de la modal
                const fieldOutside = document.getElementById(fieldId);
                if (fieldOutside) {
                    console.log(`🔍 [UNIVERSAL] Campo ${fieldId} encontrado FUERA de la modal:`, fieldOutside.closest('.modal') ? 'en otra modal' : 'en página principal');
                }
                
                // Intentar encontrarlo con diferentes selectores dentro de la modal
                const alternativeField = document.querySelector(`#transaccionesModal [name="${fieldId}"], #transaccionesModal .${fieldId}, #transaccionesModal input[placeholder*="${fieldId}"]`);
                if (alternativeField) {
                    console.log(`🔍 [UNIVERSAL] Campo ${fieldId} encontrado en modal con selector alternativo:`, alternativeField.id, alternativeField.name, alternativeField.className);
                }
            }
        });
        
        console.log(`📊 [UNIVERSAL] Resultado configuración: ${successCount} exitosos, ${failCount} fallidos`);
        
        // Configurar event listeners específicos para tarjetas
        console.log('🏦 [UNIVERSAL] Configurando listeners de tarjetas...');
        
        const entidadSelect = document.querySelector('#transaccionesModal #entidad');
        const cuotasInput = document.querySelector('#transaccionesModal #cuotas');
        
        if (entidadSelect) {
            console.log('✅ [UNIVERSAL] Configurando listener para entidad');
            entidadSelect.removeEventListener('change', actualizarCoeficiente);
            entidadSelect.addEventListener('change', actualizarCoeficiente);
        } else {
            console.warn('⚠️ [UNIVERSAL] Campo entidad no encontrado en modal');
        }
        
        if (cuotasInput) {
            console.log('✅ [UNIVERSAL] Configurando listener para cuotas');
            cuotasInput.removeEventListener('input', actualizarCoeficiente);
            cuotasInput.removeEventListener('change', actualizarCoeficiente);
            cuotasInput.addEventListener('input', actualizarCoeficiente);
            cuotasInput.addEventListener('change', actualizarCoeficiente);
        } else {
            console.warn('⚠️ [UNIVERSAL] Campo cuotas no encontrado en modal');
        }
        
        // Configurar listener específico para el campo tarjeta
        const tarjetaInput = document.querySelector('#transaccionesModal #tarjeta');
        if (tarjetaInput) {
            console.log('✅ [UNIVERSAL] Configurando listener específico para campo tarjeta');
            
            // Función específica para manejar cambios en el monto de tarjeta
            const manejarCambioTarjeta = function(event) {
                // Llamar a calcSaldo para recalcular totales generales (incluye el Total a pagar)
                calcSaldo();
            };
            
            // Remover listeners previos y agregar nuevo
            tarjetaInput.removeEventListener('input', manejarCambioTarjeta);
            tarjetaInput.removeEventListener('change', manejarCambioTarjeta);
            tarjetaInput.addEventListener('input', manejarCambioTarjeta);
            tarjetaInput.addEventListener('change', manejarCambioTarjeta);
        } else {
            console.warn('⚠️ [UNIVERSAL] Campo tarjeta no encontrado en modal');
        }
        
        // Función de debug disponible en consola
        window.debugEventListeners = debugEventListeners;
        console.log('🔧 [UNIVERSAL] Función debugEventListeners() disponible en consola');
        
        // Ejecutar cálculo inicial
        console.log('🧮 [UNIVERSAL] Ejecutando calcSaldo() inicial...');
        calcSaldo();
        
    }, 100);
}

// ================================================================
//                    EXPORT PARA USO GLOBAL
// ================================================================

// ================================================================
//                    EVENT LISTENERS DE TECLADO
// ================================================================

// Atajos de teclado para el modal de transacciones
document.addEventListener('keydown', function(event) {
    // Solo actuar si el modal está visible
    const modal = document.getElementById('transaccionesModal');
    if (!modal || !modal.classList.contains('show')) return;
    
    // Prevenir comportamientos por defecto de las teclas función
    if (event.key.startsWith('F') || event.altKey) {
        event.preventDefault();
    }
    
    // F9 - Procesar transacción
    if (event.key === 'F9') {
        const btnProcesar = document.getElementById('btnProcesarTransaccion');
        if (btnProcesar) btnProcesar.click();
        return;
    }
    
    // Atajos Alt+ para cambiar tabs
    if (event.altKey) {
        switch(event.key.toLowerCase()) {
            case 'e':
                document.getElementById('efectivo-tab')?.click();
                break;
            case 't':
                document.getElementById('tarjetas-tab')?.click();
                break;
            case 'c':
                document.getElementById('ctacte-tab')?.click();
                break;
            case 'r':
                document.getElementById('credito-tab')?.click();
                break;
            case 'b':
                document.getElementById('bonificacion-tab')?.click();
                break;
            case 'q':
                document.getElementById('cheques-tab')?.click();
                break;
            case 'v':
                document.getElementById('valores-tab')?.click();
                break;
        }
    }
});

// ================================================================
//                    EXPORT PARA USO GLOBAL
// ================================================================

// Hacer funciones disponibles globalmente
window.calcSaldo = calcSaldo;
window.actualizarTotalTarjeta = actualizarTotalTarjeta;
window.checkTotales = checkTotales;
window.generarCheque = generarCheque;
window.limpiarCheque = limpiarCheque;
window.eliminarCheque = eliminarCheque;
window.agregarValor = agregarValor;
window.limpiarValores = limpiarValores;
window.eliminarValor = eliminarValor;
window.procesarTransaccion = procesarTransaccion;
window.cargarDatosModal = cargarDatosModal;
window.debugEventListeners = debugEventListeners;
window.verificarElementoCorrecto = verificarElementoCorrecto;
window.handlePaymentFieldChange = handlePaymentFieldChange;
// Funciones de tarjetas
window.actualizarCoeficiente = actualizarCoeficiente;
window.obtenerCoeficiente = obtenerCoeficiente;

/**
 * Función de testing para verificar la funcionalidad de coeficientes
 */
window.testCoeficientes = async function() {
    console.log('🧪 [TEST] Iniciando test de coeficientes...');
    
    // Verificar que los elementos existen
    const entidad = document.getElementById('entidad');
    const cuotas = document.getElementById('cuotas');
    const coeficiente = document.getElementById('coeficiente');
    
    console.log('🔍 [TEST] Elementos encontrados:');
    console.log('   - Entidad:', entidad ? `✅ id="${entidad.id}" valor="${entidad.value}"` : '❌ No encontrado');
    console.log('   - Cuotas:', cuotas ? `✅ id="${cuotas.id}" valor="${cuotas.value}"` : '❌ No encontrado');
    console.log('   - Coeficiente:', coeficiente ? `✅ id="${coeficiente.id}" valor="${coeficiente.value}"` : '❌ No encontrado');
    
    if (entidad && cuotas && coeficiente) {
        // Test con valores de ejemplo
        entidad.value = '1'; // Asumiendo que existe una entidad con ID 1
        cuotas.value = '3';  // 3 cuotas
        
        console.log('🧪 [TEST] Ejecutando actualizarCoeficiente()...');
        await actualizarCoeficiente();
        
        console.log('✅ [TEST] Test completado. Verificar resultado en campo coeficiente');
    } else {
        console.error('❌ [TEST] No se pueden realizar tests - elementos faltantes');
    }
};

/**
 * Función para probar la conectividad con el endpoint de coeficientes
 */
window.testEndpointCoeficientes = async function(entidadId = 1, cuotas = 3) {
    console.log('🌐 [TEST ENDPOINT] Probando conectividad con servidor...');
    console.log(`🎯 [TEST ENDPOINT] Parámetros: entidad=${entidadId}, cuotas=${cuotas}`);
    
    const baseUrl = window.BASE_URL || '';
    const url = `${baseUrl}/entidades/coeficiente_cuotas/${entidadId}/${cuotas}`;
    
    console.log('📡 [TEST ENDPOINT] URL completa:', url);
    console.log('🔧 [TEST ENDPOINT] BASE_URL:', window.BASE_URL);
    
    try {
        const response = await fetch(url);
        console.log('📊 [TEST ENDPOINT] Respuesta:', {
            status: response.status,
            statusText: response.statusText,
            ok: response.ok,
            headers: Object.fromEntries(response.headers.entries())
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ [TEST ENDPOINT] Datos recibidos:', data);
            
            // Probar conversión de coeficiente
            if (data && data.coeficiente !== undefined) {
                const coeficienteOriginal = data.coeficiente;
                const coeficienteConvertido = typeof coeficienteOriginal === 'string' ? 
                    parseFloat(coeficienteOriginal) : 
                    coeficienteOriginal;
                
                console.log('🔄 [TEST ENDPOINT] Conversión de coeficiente:', {
                    original: coeficienteOriginal,
                    tipoOriginal: typeof coeficienteOriginal,
                    convertido: coeficienteConvertido,
                    tipoConvertido: typeof coeficienteConvertido,
                    esValido: !isNaN(coeficienteConvertido) && coeficienteConvertido > 0,
                    formateado: coeficienteConvertido.toFixed(4)
                });
            }
            
            return data;
        } else {
            const errorText = await response.text();
            console.error('❌ [TEST ENDPOINT] Error del servidor:', errorText);
            return null;
        }
    } catch (error) {
        console.error('❌ [TEST ENDPOINT] Error de red:', error);
        return null;
    }
};

/**
 * Test completo del flujo de coeficientes con valores reales
 */
window.testCoeficientesCompleto = async function(entidadId = 1, cuotas = 12) {
    console.log('🧪 [TEST COMPLETO] Iniciando test completo del sistema...');
    
    // 1. Test del endpoint
    console.log('1️⃣ [TEST COMPLETO] Probando endpoint...');
    const datosServidor = await testEndpointCoeficientes(entidadId, cuotas);
    
    if (!datosServidor) {
        console.error('❌ [TEST COMPLETO] Falla en comunicación con servidor');
        return false;
    }
    
    // 2. Test de la función obtenerCoeficiente
    console.log('2️⃣ [TEST COMPLETO] Probando función obtenerCoeficiente...');
    const coeficienteObtenido = await obtenerCoeficiente(entidadId, cuotas);
    console.log('📊 [TEST COMPLETO] Coeficiente obtenido por función:', coeficienteObtenido);
    
    // 3. Test de actualización en el DOM
    console.log('3️⃣ [TEST COMPLETO] Probando actualización del DOM...');
    const entidadSelect = document.getElementById('entidad');
    const cuotasInput = document.getElementById('cuotas');
    
    if (entidadSelect && cuotasInput) {
        entidadSelect.value = entidadId;
        cuotasInput.value = cuotas;
        
        console.log('🎯 [TEST COMPLETO] Ejecutando actualizarCoeficiente...');
        await actualizarCoeficiente();
        
        const coeficienteInput = document.getElementById('coeficiente');
        console.log('✅ [TEST COMPLETO] Valor final en DOM:', coeficienteInput?.value);
    } else {
        console.warn('⚠️ [TEST COMPLETO] Elementos DOM no encontrados');
    }
    
    console.log('🏁 [TEST COMPLETO] Test completado');
    return true;
};

/**
 * Test específico para verificar el cálculo del "Total a pagar" = Saldo × Coeficiente
 */
window.testCalculoTotalPagar = function(totalFactura = 35500, otrosPagos = 0, coeficiente = 1.032) {
    console.log('🧮 [TEST SALDO×COEF] Iniciando test "Total a pagar = Saldo × Coeficiente"...');
    
    const saldoEsperado = totalFactura - otrosPagos;
    const totalEsperado = saldoEsperado * coeficiente;
    
    console.log('📊 [TEST SALDO×COEF] Parámetros:', {
        totalFactura,
        otrosPagos,
        saldoCalculado: saldoEsperado,
        coeficiente,
        totalEsperado: totalEsperado.toFixed(2)
    });
    
    // Simular valores en los campos
    const totalFacElement = document.getElementById('modal_total_factura');
    const coeficienteInput = document.getElementById('coeficiente');
    const efectivoInput = document.getElementById('efectivo');
    
    if (!totalFacElement || !coeficienteInput) {
        console.error('❌ [TEST SALDO×COEF] Campos básicos no encontrados');
        return false;
    }
    
    // Configurar valores
    totalFacElement.textContent = totalFactura.toString();
    coeficienteInput.value = coeficiente.toFixed(4);
    if (efectivoInput) efectivoInput.value = otrosPagos.toString();
    
    // Disparar cálculo
    calcSaldo();
    
    // Verificar resultado
    setTimeout(() => {
        const totalTarjetaField = document.getElementById('total_tarjeta');
        const totalCalculado = parseFloat(totalTarjetaField?.value) || 0;
        const diferencia = Math.abs(totalCalculado - totalEsperado);
        
        console.log('📋 [TEST SALDO×COEF] Resultados:', {
            saldoReal: (totalFactura - otrosPagos).toFixed(2),
            coeficiente: coeficiente,
            totalCalculado: totalCalculado.toFixed(2),
            totalEsperado: totalEsperado.toFixed(2),
            diferencia: diferencia.toFixed(4),
            esCorrepto: diferencia < 0.01 ? '✅ CORRECTO' : '❌ INCORRECTO'
        });
        
        if (diferencia < 0.01) {
            console.log('🎉 [TEST SALDO×COEF] ¡ÉXITO! Fórmula: Saldo × Coeficiente');
            return true;
        } else {
            console.error('💥 [TEST SALDO×COEF] FALLO en el cálculo');
            return false;
        }
    }, 200);
};

/**
 * Test del ejemplo específico: Tarjeta 6 cuotas con coeficiente 35500
 */
/**
 * Test para verificar que "Total a pagar" es informativo y NO cambia con importe tarjeta
 */
window.testComportamientoTotalPagar = function() {
    console.log('🔒 [TEST INFORMATIVO] Verificando que Total a pagar es FIJO...');
    
    // Configurar escenario inicial
    const totalFactura = 35500;
    const coeficiente = 1.032;
    const totalEsperado = totalFactura * coeficiente; // 36,636
    
    // Configurar campos
    const totalFacElement = document.getElementById('modal_total_factura');
    const coeficienteInput = document.getElementById('coeficiente');
    const tarjetaInput = document.getElementById('tarjeta');
    const totalTarjetaField = document.getElementById('total_tarjeta');
    
    if (!totalFacElement || !coeficienteInput || !tarjetaInput || !totalTarjetaField) {
        console.error('❌ [TEST] Campos necesarios no encontrados');
        return false;
    }
    
    // Establecer valores iniciales
    totalFacElement.textContent = totalFactura.toString();
    coeficienteInput.value = coeficiente.toFixed(4);
    tarjetaInput.value = '';
    
    // Actualizar Total a pagar inicialmente
    actualizarTotalTarjeta();
    
    setTimeout(() => {
        const totalInicial = parseFloat(totalTarjetaField.value);
        console.log('📊 [TEST] Total inicial:', totalInicial.toFixed(2));
        
        // Ahora cambiar importe tarjeta y verificar que Total a pagar NO cambia
        tarjetaInput.value = '5000'; // Usuario paga solo 5000 con tarjeta
        tarjetaInput.dispatchEvent(new Event('input', { bubbles: true }));
        
        setTimeout(() => {
            const totalDespues = parseFloat(totalTarjetaField.value);
            console.log('📊 [TEST] Total después de cambiar importe tarjeta:', totalDespues.toFixed(2));
            
            const noHaCambiado = Math.abs(totalInicial - totalDespues) < 0.01;
            
            console.log('🎯 [TEST] Resultado:', {
                'Total_inicial': totalInicial.toFixed(2),
                'Total_después': totalDespues.toFixed(2),
                'Importe_tarjeta_ingresado': '5000.00',
                'Total_debería_ser': totalEsperado.toFixed(2),
                'Es_informativo_(no_cambia)': noHaCambiado ? '✅ CORRECTO' : '❌ ERROR',
                'Explicación': 'Total a pagar muestra el costo de pagar TODO el saldo, no el importe parcial'
            });
            
            return noHaCambiado;
        }, 200);
    }, 200);
};

/**
 * Test para verificar que el SALDO no incluye intereses de tarjeta
 */
window.testSaldoSinIntereses = function() {
    console.log('🧮 [TEST SALDO] Verificando que saldo NO incluye intereses...');
    
    // Configurar escenario de prueba
    const totalFactura = 10000;
    const importeTarjeta = 5000;
    const coeficiente = 1.5; // 50% de recargo
    
    // Configurar campos
    const totalFacElement = document.getElementById('modal_total_factura');
    const tarjetaInput = document.getElementById('tarjeta');
    const coeficienteInput = document.getElementById('coeficiente');
    
    if (totalFacElement) totalFacElement.textContent = totalFactura.toString();
    if (tarjetaInput) tarjetaInput.value = importeTarjeta.toString();
    if (coeficienteInput) coeficienteInput.value = coeficiente.toFixed(4);
    
    // Limpiar otros pagos
    const efectivoInput = document.getElementById('efectivo');
    if (efectivoInput) efectivoInput.value = '0';
    
    // Calcular saldo
    calcSaldo();
    
    setTimeout(() => {
        const saldoElement = document.getElementById('saldo_factura');
        const saldoCalculado = parseFloat(saldoElement?.textContent) || 0;
        
        // Si el coeficiente > 1, el importe ingresado incluye intereses
        // Solo el importe base debe reducir el saldo
        const importeAplicadoADeuda = coeficiente > 1 ? importeTarjeta / coeficiente : importeTarjeta;
        const saldoEsperado = totalFactura - importeAplicadoADeuda;
        
        console.log('📊 [TEST SALDO] Resultados CORREGIDOS:', {
            totalFactura: totalFactura,
            importeTarjetaIngresado: importeTarjeta,
            coeficiente: coeficiente,
            'importe_aplicado_a_deuda': importeAplicadoADeuda.toFixed(2),
            'intereses': (importeTarjeta - importeAplicadoADeuda).toFixed(2),
            'saldo_calculado': saldoCalculado,
            'saldo_esperado': saldoEsperado.toFixed(2),
            'diferencia': Math.abs(saldoCalculado - saldoEsperado).toFixed(2),
            'correcto': Math.abs(saldoCalculado - saldoEsperado) < 0.01 ? '✅ SÍ' : '❌ NO'
        });
        
        if (Math.abs(saldoCalculado - saldoEsperado) < 0.01) {
            console.log('🎉 [TEST SALDO] ¡CORRECTO! El saldo NO incluye intereses');
            return true;
        } else {
            console.error('💥 [TEST SALDO] ERROR: El saldo incluye intereses cuando no debería');
            return false;
        }
    }, 200);
};

/**
 * Test específico: Tarjeta $7500 con $2500 de intereses
 */
window.testCaso7500ConIntereses = function() {
    console.log('💰 [TEST CASO REAL] Tarjeta $7500 (incluye $2500 intereses)...');
    
    const totalFactura = 10000;
    const importeTarjetaConIntereses = 7500; // Lo que paga el cliente
    const coeficiente = 1.5; // 50% recargo
    const importeRealADeuda = 7500 / 1.5; // = $5000
    
    // Configurar campos
    const totalFacElement = document.getElementById('modal_total_factura');
    const tarjetaInput = document.getElementById('tarjeta');
    const coeficienteInput = document.getElementById('coeficiente');
    
    if (totalFacElement) totalFacElement.textContent = totalFactura.toString();
    if (tarjetaInput) tarjetaInput.value = importeTarjetaConIntereses.toString();
    if (coeficienteInput) coeficienteInput.value = coeficiente.toFixed(4);
    
    // Limpiar otros pagos
    const efectivoInput = document.getElementById('efectivo');
    if (efectivoInput) efectivoInput.value = '0';
    
    calcSaldo();
    
    setTimeout(() => {
        const saldoElement = document.getElementById('saldo_factura');
        const saldoCalculado = parseFloat(saldoElement?.textContent) || 0;
        const saldoEsperado = totalFactura - importeRealADeuda; // 10000 - 5000 = 5000
        
        console.log('🎯 [TEST CASO REAL] Análisis:', {
            'factura_total': totalFactura,
            'pago_tarjeta_(con_intereses)': importeTarjetaConIntereses,
            'coeficiente': coeficiente,
            'importe_real_a_deuda': importeRealADeuda.toFixed(2),
            'intereses_pagados': (importeTarjetaConIntereses - importeRealADeuda).toFixed(2),
            'saldo_calculado': saldoCalculado,
            'saldo_esperado': saldoEsperado,
            'es_correcto': Math.abs(saldoCalculado - saldoEsperado) < 0.01 ? '✅ SÍ' : '❌ NO'
        });
        
        if (Math.abs(saldoCalculado - saldoEsperado) < 0.01) {
            console.log('🎉 [CASO REAL] ¡PERFECTO! Los intereses NO afectan el saldo');
        } else {
            console.error('💥 [CASO REAL] ERROR: Los intereses están afectando el saldo');
        }
    }, 200);
};

window.testEjemploTarjeta6Cuotas = function() {
    console.log('💳 [TEST 6 CUOTAS] Probando Total a pagar INFORMATIVO (no cambia con importe)...');
    
    // Simular el escenario exacto del usuario
    const saldo = 35500; // Este debería ser el saldo restante
    const coeficiente = 1.032; // El coeficiente de 6 cuotas
    
    // Configurar campos
    const totalFacElement = document.getElementById('modal_total_factura');
    const coeficienteInput = document.getElementById('coeficiente');
    
    if (totalFacElement) totalFacElement.textContent = saldo.toString();
    if (coeficienteInput) coeficienteInput.value = coeficiente.toFixed(4);
    
    // Ejecutar cálculo del Total a pagar (informativo)
    actualizarTotalTarjeta();
    
    setTimeout(() => {
        const totalTarjetaField = document.getElementById('total_tarjeta');
        const totalCalculado = parseFloat(totalTarjetaField?.value) || 0;
        const totalEsperado = saldo * coeficiente;
        
        console.log('📊 [TEST 6 CUOTAS] Resultado:', {
            saldo: saldo,
            coeficiente: coeficiente,
            'total_calculado': totalCalculado,
            'total_esperado_(saldo×coef)': totalEsperado.toFixed(2),
            'diferencia': Math.abs(totalCalculado - totalEsperado).toFixed(2),
            'estado': Math.abs(totalCalculado - totalEsperado) < 1 ? '✅ OK' : '❌ ERROR'
        });
        
        return totalCalculado;
    }, 100);
};

// Exportar funciones de test
window.testEndpointCoeficientes = testEndpointCoeficientes;
window.testCoeficientesCompleto = testCoeficientesCompleto;
window.testCalculoTotalPagar = testCalculoTotalPagar;
window.testEjemploTarjeta6Cuotas = testEjemploTarjeta6Cuotas;
window.testSaldoSinIntereses = testSaldoSinIntereses;
window.testCaso7500ConIntereses = testCaso7500ConIntereses;

console.log('🔧 [UNIVERSAL] Funciones exportadas globalmente:');
console.log('   - calcSaldo, checkTotales, generarCheque, limpiarCheque, eliminarCheque');
console.log('   - agregarValor, limpiarValores, eliminarValor, procesarTransaccion');
console.log('   - cargarDatosModal, debugEventListeners, verificarElementoCorrecto');
console.log('   - handlePaymentFieldChange, actualizarCoeficiente, obtenerCoeficiente');
console.log('💡 [UNIVERSAL] Pruebas disponibles en consola:');
console.log('   - window.testCoeficientes() - Test básico de coeficientes');
console.log('   - window.testCoeficientesCompleto(1, 12) - Test completo del flujo');
console.log('   - window.testCalculoTotalPagar() - Test: Saldo × Coeficiente');
console.log('   - window.testEjemploTarjeta6Cuotas() - Test escenario específico 6 cuotas');
console.log('   - window.testSaldoSinIntereses() - Verificar que saldo NO incluye intereses');
console.log('   - window.testCaso7500ConIntereses() - Test caso real: $7500 con $2500 intereses');
console.log('   - window.testEndpointCoeficientes(1, 3) - Probar solo endpoint');
console.log('   - window.actualizarTotalTarjeta() - Solo recalcular Total a pagar');
console.log('   - window.debugEventListeners() - Debug de listeners');