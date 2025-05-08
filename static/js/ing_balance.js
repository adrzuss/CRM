import { fetchArticulo } from './utilidades.js';

let isFormSubmited = false;
let contadorFilas = 0;

window.onbeforeunload = function() {
    if (!isFormSubmited) {
        return '¿Estás seguro de cerrar la venta sin guardar los cambios?';
    }
};        
        

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('invoice_form');
    const btnAgregar = document.getElementById('agregarArticulo');
    const btnGrabar = document.getElementById('grabarBalance');

    // Detectar tecla Enter en los inputs del formulario
    form.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();  // Evita que se envíe el formulario

            // Obtener todos los inputs del formulario
            let inputs = Array.from(form.elements);
            
            // Encontrar el input actual
            let currentIndex = inputs.indexOf(event.target);
            
            // Buscar el siguiente input que no sea readonly
            let nextIndex = currentIndex + 1;
            while (nextIndex < inputs.length && inputs[nextIndex].readOnly) {
                nextIndex++;
            }
            
            // Si existe un siguiente input no readonly, enfocarlo
            if (nextIndex < inputs.length) {
                inputs[nextIndex].focus();
            }
        }

        // Asignar tecla F9 para grabar venta
        if (event.key === 'F9') {
            event.preventDefault();  // Evita el comportamiento por defecto de la tecla
            btnGrabar.click();  // Simula un click en el botón "Grabar Venta"
        }

        // Asignar tecla F4 para agregar un nuevo artículo
        if (event.key === 'F4') {
            event.preventDefault();  // Evita la recarga de página con F5
            btnAgregar.click();  // Simula un click en el botón "Agregar Artículo"
        }
    });
});        

//aca estaba el codigo de la funcion fetchArticulo
        
function removeItem(itemDiv) {
    itemDiv.remove();
    renumberItems();
}

function renumberItems() {
    const itemDivs = document.querySelectorAll('#items .item');
    itemDivs.forEach((itemDiv, index) => {
        itemDiv.querySelector('.idarticulo').setAttribute('name', `items[${index}][idarticulo]`);
        itemDiv.querySelector('.cantidad').setAttribute('name', `items[${index}][cantidad]`);
        itemDiv.querySelector('.precio_articulo').setAttribute('name', `items[${index}][cantidad]`);
    });
}

const tablaItems = document.querySelector("#tabla-items tbody");

// Agregar nueva fila
document.getElementById('agregarArticulo').addEventListener("click", () => {
    const nuevaFila = `
        <tr class="items">
            <td class="id-articulo" name="items[${contadorFilas}][idarticulo]">-</td>
            <td><input type="text" class="form-control codigo-articulo" name="items[${contadorFilas}][codigo]" required></td>
            <td class="descripcion-articulo">-</td>
            <td><input type="number" class="form-control precio-unitario" name="items[${contadorFilas}][precio_unitario]" readonly></td>
            <td><input type="number" class="form-control cantidad" name="items[${contadorFilas}][cantidad]" value="1" step="0.01" min="0.01" required></td> 
            <td><button type="button" class="btn btn-danger btn-eliminar">Eliminar</button></td>
        </tr>`;
    tablaItems.insertAdjacentHTML("beforeend", nuevaFila);
    contadorFilas++;
    // Enfocar el nuevo input de código
    const nuevoInputCodigo = tablaItems.querySelector(`tr:last-child .codigo-articulo`);
    nuevoInputCodigo.focus();
});

tablaItems.addEventListener("blur", (itemDiv) => {
    if (itemDiv.target.classList.contains("codigo-articulo")) {
        const codigo = itemDiv.target.value;
        const idlista = 1;

        // Simulación de una búsqueda (deberías usar una API aquí)
        fetchArticulo(codigo, idlista, itemDiv)
        
    }
    
}, true);

// Eliminar fila
tablaItems.addEventListener("click", (itemDiv) => {
    if (itemDiv.target.classList.contains("btn-eliminar")) {
        itemDiv.target.closest("tr").remove();
    }
});

document.getElementById('invoice_form').addEventListener('submit', function(event) {
    if (document.querySelectorAll('#tabla-items tbody').length === 0) {
        event.preventDefault();
        alert('Debe agregar al menos un item al ingreso de balance');
        event.preventDefault();
        return false;
    } 
    
    if (confirm('¿Grabar el ingreso de balance?') == false) {
        event.preventDefault();
    }
    else{
        isFormSubmited = true;
    }
});
        