document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los inputs con la clase 'precio'
    var precios = document.querySelectorAll('.precio');
    precios.forEach(function(input) {
        formatDecimal(input);
    });
});

function formatDecimal(input) {
    let value = parseFloat(input.value);
    if (!isNaN(value)) {
        input.value = value.toFixed(2);
    }
}

