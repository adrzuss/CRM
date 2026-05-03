document.addEventListener('DOMContentLoaded', () => {
    const h6 = document.getElementById('vencimiento-plan');
    if (!h6) return; // Seguridad por si el elemento no existe

    // Leer el valor del atributo data-dias
    const dias = parseInt(h6.dataset.dias, 10);
    

    // Limpiar clases previas para evitar conflictos
    h6.classList.remove('badge-plan-vencimiento-ok', 'badge-plan-vencimiento-proximo', 'badge-plan-vencimiento-vencido');

    // Aplicar lógica condicional
    
    if (dias >= 15) {
        h6.classList.add('badge-plan-vencimiento-ok');
    } else if (dias < 15 && dias > -15) {
        h6.classList.add('badge-plan-vencimiento-proximo');
    } else {
        h6.classList.add('badge-plan-vencimiento-vencido');
    }
});
