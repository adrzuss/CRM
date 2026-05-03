/* =============================================================================
   PERMISOS DE MENÚ - JavaScript
   ============================================================================= */

(function() {
    'use strict';

    // Seleccionar/Deseleccionar todos los permisos de una categoría
    window.toggleCategoria = function(categoria, checkbox) {
        console.log('toggleCategoria called:', categoria, checkbox.checked);
        var checkboxes = document.querySelectorAll('input[data-categoria="' + categoria + '"]');
        checkboxes.forEach(function(cb) {
            cb.checked = checkbox.checked;
        });
        actualizarContador();
    };

    // Seleccionar todos los permisos
    window.seleccionarTodos = function() {
        console.log('seleccionarTodos called');
        var checkboxes = document.querySelectorAll('#contenedor-permisos input[type="checkbox"][name="permisos"]');
        checkboxes.forEach(function(cb) {
            cb.checked = true;
        });
        actualizarContador();
    };

    // Deseleccionar todos los permisos
    window.deseleccionarTodos = function() {
        console.log('deseleccionarTodos called');
        var checkboxes = document.querySelectorAll('#contenedor-permisos input[type="checkbox"][name="permisos"]');
        checkboxes.forEach(function(cb) {
            cb.checked = false;
        });
        actualizarContador();
    };

    // Actualizar contador de permisos seleccionados
    function actualizarContador() {
        var total = document.querySelectorAll('#contenedor-permisos input[type="checkbox"][name="permisos"]').length;
        var seleccionados = document.querySelectorAll('#contenedor-permisos input[type="checkbox"][name="permisos"]:checked').length;
        var contador = document.getElementById('contador-permisos');
        console.log('actualizarContador:', seleccionados, 'de', total);
        if (contador) {
            contador.textContent = seleccionados + ' de ' + total + ' permisos';
        }
    }

    // Exponer también actualizarContador globalmente
    window.actualizarContador = actualizarContador;

    // Inicializar cuando el DOM esté listo
    function init() {
        console.log('permisos-menu.js initialized');

        // Escuchar cambios en checkboxes (delegación de eventos)
        document.addEventListener('change', function(e) {
            if (e.target.matches('input[type="checkbox"][name="permisos"]')) {
                actualizarContador();
            }
        });

        // Escuchar evento HTMX después de cargar contenido
        document.body.addEventListener('htmx:afterSwap', function(e) {
            console.log('htmx:afterSwap fired, target:', e.detail.target.id);
            if (e.detail.target.id === 'contenedor-permisos') {
                actualizarContador();
            }
        });

        // Escuchar evento HTMX después de procesar (como alternativa)
        document.body.addEventListener('htmx:afterSettle', function(e) {
            if (e.detail.target.id === 'contenedor-permisos') {
                console.log('htmx:afterSettle fired');
                actualizarContador();
            }
        });
    }

    // Ejecutar init cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
