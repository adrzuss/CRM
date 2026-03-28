/**
 * SweetAlert2 Helper Functions
 * Funciones utilitarias para mostrar alertas elegantes en toda la aplicación
 */

const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer);
        toast.addEventListener('mouseleave', Swal.resumeTimer);
    }
});

/**
 * Muestra un mensaje de advertencia
 * @param {string} mensaje - El mensaje a mostrar
 * @param {string} titulo - Título opcional (default: 'Atención')
 */
function mostrarAdvertencia(mensaje, titulo = 'Atención') {
    return Swal.fire({
        icon: 'warning',
        title: titulo,
        text: mensaje,
        confirmButtonColor: '#3085d6'
    });
}

/**
 * Muestra un mensaje de error
 * @param {string} mensaje - El mensaje de error
 * @param {string} titulo - Título opcional (default: 'Error')
 */
function mostrarError(mensaje, titulo = 'Error') {
    return Swal.fire({
        icon: 'error',
        title: titulo,
        text: mensaje,
        confirmButtonColor: '#d33'
    });
}

/**
 * Muestra un mensaje de éxito
 * @param {string} mensaje - El mensaje de éxito
 * @param {string} titulo - Título opcional (default: '¡Éxito!')
 * @param {boolean} autoClose - Si se cierra automáticamente (default: true)
 */
function mostrarExito(mensaje, titulo = '¡Éxito!', autoClose = true) {
    const config = {
        icon: 'success',
        title: titulo,
        text: mensaje,
        confirmButtonColor: '#28a745'
    };
    
    if (autoClose) {
        config.timer = 2500;
        config.showConfirmButton = false;
    }
    
    return Swal.fire(config);
}

/**
 * Muestra un mensaje informativo
 * @param {string} mensaje - El mensaje informativo
 * @param {string} titulo - Título opcional (default: 'Información')
 */
function mostrarInfo(mensaje, titulo = 'Información') {
    return Swal.fire({
        icon: 'info',
        title: titulo,
        text: mensaje,
        confirmButtonColor: '#3085d6'
    });
}

/**
 * Muestra un diálogo de confirmación
 * @param {string} mensaje - El mensaje de confirmación
 * @param {string} titulo - Título opcional (default: '¿Está seguro?')
 * @param {string} btnConfirmar - Texto del botón confirmar (default: 'Sí, confirmar')
 * @param {string} btnCancelar - Texto del botón cancelar (default: 'Cancelar')
 * @returns {Promise<boolean>} - true si confirmó, false si canceló
 */
async function confirmar(mensaje, titulo = '¿Está seguro?', btnConfirmar = 'Sí, confirmar', btnCancelar = 'Cancelar') {
    const result = await Swal.fire({
        icon: 'question',
        title: titulo,
        text: mensaje,
        showCancelButton: true,
        confirmButtonText: btnConfirmar,
        cancelButtonText: btnCancelar,
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d',
        reverseButtons: true
    });
    
    return result.isConfirmed;
}

/**
 * Muestra un diálogo de confirmación para eliminar
 * @param {string} mensaje - El mensaje de confirmación
 * @param {string} titulo - Título opcional (default: '¿Eliminar?')
 * @returns {Promise<boolean>} - true si confirmó, false si canceló
 */
async function confirmarEliminar(mensaje, titulo = '¿Eliminar?') {
    const result = await Swal.fire({
        icon: 'warning',
        title: titulo,
        text: mensaje,
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        reverseButtons: true
    });
    
    return result.isConfirmed;
}

/**
 * Muestra un toast de éxito (notificación pequeña)
 * @param {string} mensaje - El mensaje
 */
function toastExito(mensaje) {
    Toast.fire({
        icon: 'success',
        title: mensaje
    });
}

/**
 * Muestra un toast de error (notificación pequeña)
 * @param {string} mensaje - El mensaje
 */
function toastError(mensaje) {
    Toast.fire({
        icon: 'error',
        title: mensaje
    });
}

/**
 * Muestra un toast informativo (notificación pequeña)
 * @param {string} mensaje - El mensaje
 */
function toastInfo(mensaje) {
    Toast.fire({
        icon: 'info',
        title: mensaje
    });
}

/**
 * Muestra un toast de advertencia (notificación pequeña)
 * @param {string} mensaje - El mensaje
 */
function toastAdvertencia(mensaje) {
    Toast.fire({
        icon: 'warning',
        title: mensaje
    });
}
