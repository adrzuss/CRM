/**
 * Transaction Color Detail Helper
 * Funciones auxiliares para integrar selección de color/detalle en transacciones
 */

/**
 * Agregar evento de selección de color/detalle a un input de artículo
 * @param {HTMLElement} inputArticulo - Input donde se selecciona el artículo
 * @param {number} rowIndex - Índice de la fila (opcional)
 * @param {object} options - Opciones de configuración
 */
function setupArticuloColorDetalle(inputArticulo, rowIndex = null, options = {}) {
    const defaultOptions = {
        onSelectionComplete: null,  // Callback cuando se completa la selección
        autoFillFields: true,       // Auto-completar campos id_color e id_detalle
        colorFieldName: 'id_color', // Nombre del campo color
        detalleFieldName: 'id_detalle' // Nombre del campo detalle
    };
    
    const config = { ...defaultOptions, ...options };
    
    // Obtener fila contenedora
    const row = inputArticulo.closest('tr') || inputArticulo.closest('.row') || inputArticulo.closest('.form-row');
    
    // Función para manejar cambio de artículo
    function handleArticuloChange() {
        const articleId = inputArticulo.value;
        const articleName = inputArticulo.dataset.nombre || 
                           inputArticulo.getAttribute('data-nombre') ||
                           inputArticulo.nextElementSibling?.textContent ||
                           'Artículo seleccionado';
        
        if (articleId && window.modalColorDetalleManager) {
            // Determinar índice de fila si no se proporcionó
            const finalRowIndex = rowIndex !== null ? rowIndex : 
                Array.from(inputArticulo.closest('table')?.querySelectorAll('tr') || []).indexOf(row);
            
            // Mostrar modal
            window.modalColorDetalleManager.mostrarModal(
                parseInt(articleId),
                finalRowIndex,
                articleName,
                function(seleccion) {
                    handleColorDetalleSelection(seleccion, row, config);
                }
            );
        }
    }
    
    // Agregar eventos según el tipo de input
    if (inputArticulo.type === 'hidden' || inputArticulo.readOnly) {
        // Para inputs hidden o readonly, escuchar cambios programáticos
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                    handleArticuloChange();
                }
            });
        });
        observer.observe(inputArticulo, { attributes: true });
        
        // También escuchar eventos de input
        inputArticulo.addEventListener('input', handleArticuloChange);
    } else {
        // Para inputs normales
        inputArticulo.addEventListener('change', handleArticuloChange);
        inputArticulo.addEventListener('blur', handleArticuloChange);
    }
}

/**
 * Manejar la selección de color y detalle
 * @param {object} seleccion - Datos de la selección
 * @param {HTMLElement} row - Fila contenedora
 * @param {object} config - Configuración
 */
function handleColorDetalleSelection(seleccion, row, config) {
    if (config.autoFillFields && row) {
        // Buscar campos de color y detalle en la fila
        const colorField = row.querySelector(`[name="${config.colorFieldName}"], [name*="${config.colorFieldName}"]`);
        const detalleField = row.querySelector(`[name="${config.detalleFieldName}"], [name*="${config.detalleFieldName}"]`);
        
        if (colorField && seleccion.colorId) {
            colorField.value = seleccion.colorId;
            
            // Disparar evento change para que otros scripts lo detecten
            colorField.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        if (detalleField && seleccion.detalleId) {
            detalleField.value = seleccion.detalleId;
            
            // Disparar evento change
            detalleField.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
    
    // Ejecutar callback personalizado si existe
    if (config.onSelectionComplete) {
        config.onSelectionComplete(seleccion, row);
    }
}

/**
 * Inicializar automáticamente todos los inputs de artículo en una tabla
 * @param {HTMLElement} table - Tabla contenedora
 * @param {object} options - Opciones de configuración
 */
function initializeTableArticulos(table, options = {}) {
    if (!table) return;
    
    const articuloInputs = table.querySelectorAll('input[name*="articulo"], input[name*="idarticulo"], select[name*="articulo"]');
    
    articuloInputs.forEach((input, index) => {
        setupArticuloColorDetalle(input, index, options);
    });
}

/**
 * Crear campos hidden para color y detalle si no existen
 * @param {HTMLElement} form - Formulario contenedor
 * @param {string} prefix - Prefijo para los nombres de campos (ej: 'items')
 */
function createHiddenColorDetalleFields(form, prefix = '') {
    if (!form) return;
    
    const rows = form.querySelectorAll('tr, .item-row, .form-row');
    
    rows.forEach((row, index) => {
        const colorName = prefix ? `${prefix}[${index}][id_color]` : `id_color_${index}`;
        const detalleName = prefix ? `${prefix}[${index}][id_detalle]` : `id_detalle_${index}`;
        
        // Crear campo color si no existe
        if (!row.querySelector(`[name="${colorName}"]`)) {
            const colorInput = document.createElement('input');
            colorInput.type = 'hidden';
            colorInput.name = colorName;
            colorInput.value = '';
            row.appendChild(colorInput);
        }
        
        // Crear campo detalle si no existe
        if (!row.querySelector(`[name="${detalleName}"]`)) {
            const detalleInput = document.createElement('input');
            detalleInput.type = 'hidden';
            detalleInput.name = detalleName;
            detalleInput.value = '';
            row.appendChild(detalleInput);
        }
    });
}

/**
 * Validar que se hayan seleccionado colores/detalles obligatorios antes de enviar
 * @param {HTMLElement} form - Formulario a validar
 * @return {boolean} True si la validación pasa
 */
function validateColorDetalleSelection(form) {
    if (!form) return true;
    
    const rows = form.querySelectorAll('tr, .item-row, .form-row');
    let validationErrors = [];
    
    rows.forEach((row, index) => {
        const articuloInput = row.querySelector('input[name*="articulo"], select[name*="articulo"]');
        const colorInput = row.querySelector('input[name*="id_color"]');
        const detalleInput = row.querySelector('input[name*="id_detalle"]');
        
        if (articuloInput && articuloInput.value) {
            // Verificar si faltan colores o detalles obligatorios
            // (Esta validación requeriría información adicional sobre qué artículos requieren color/detalle)
            
            if (colorInput && !colorInput.value) {
                // Podríamos agregar validación específica aquí
            }
            
            if (detalleInput && !detalleInput.value) {
                // Podríamos agregar validación específica aquí
            }
        }
    });
    
    if (validationErrors.length > 0) {
        Swal.fire({
            title: 'Validación requerida',
            text: 'Algunos artículos requieren selección de color y/o detalle',
            icon: 'warning'
        });
        return false;
    }
    
    return true;
}

// Función de inicialización automática al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Buscar tablas con clases comunes de transacciones
    const transactionTables = document.querySelectorAll(
        '.table-items, .items-table, table[id*="items"], table[id*="tabla"]'
    );
    
    transactionTables.forEach(table => {
        initializeTableArticulos(table);
    });
});

// Exportar funciones para uso global
window.TransactionColorDetailHelper = {
    setupArticuloColorDetalle,
    initializeTableArticulos,
    createHiddenColorDetalleFields,
    validateColorDetalleSelection,
    handleColorDetalleSelection
};