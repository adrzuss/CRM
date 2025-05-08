
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
    const btnGrabar = document.getElementById('grabarRemSucursales');

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

async function fetchArticulo(id, idlista, itemDiv) {
    let response;
    if (!isNaN(id)){
        response = await fetch(`/articulo/${id}/${idlista}`);
    }
    else{
        response = await fetch(`/articulo/${id}/${idlista}`);
        if (!response.ok) {
            response = await fetch(`/get_articulos?detalle=${id}&idlista=${idlista}`);
        }    
        //response = await fetch(`/get_articulos?detalle=${id}&idlista=${idlista}`);
    }    
    if (!response.ok) {
        console.error("Error en la búsqueda de artículos");
        return;
    }
    //const data = await response.json();
    const data = await response.json();

    if (data.success) {
        if (data.articulo) {
            // Si se encuentra un cliente por ID, asignarlo directamente
            asignarArticulo(data.articulo, itemDiv);
        } else {
            alert("No se encontraron articulos con ese ID.");
        }
    } else {
        if (data.length > 1) {
            // Si hay más de un resultado, mostrar un modal para seleccionar
            mostrarModalSeleccionArticulos(data, itemDiv);
        } else if (data.length === 1) {
            // Si hay un solo resultado, asignar directamente
            asignarArticuloElegido(data[0], itemDiv);
        } else {
            alert("No se encontraron articulos con ese detalle.");
        }
    }
}

function asignarArticuloElegido(articulo, itemDiv) {
    itemDiv.target.closest("tr").querySelector(".codigo-articulo").value = articulo.codigo;
    asignarArticulo(articulo, itemDiv);; 
}

function asignarArticulo(articulo, itemDiv) {
    itemDiv.target.closest("tr").querySelector(".id-articulo").textContent = articulo.id;
    itemDiv.target.closest("tr").querySelector(".descripcion-articulo").textContent = articulo.detalle;
    
}

function mostrarModalSeleccionArticulos(articulos, itemDiv) {
    // Crear el contenido del modal con las opciones de cliente
    const tituloModal = document.getElementById('clienteModalLabel'); 
    tituloModal.textContent = 'Seleccione un Artículo';
    const modalContent = document.getElementById('modalContent');
    modalContent.innerHTML = '';
    const listaArticulos = document.createElement('ul');
    listaArticulos.classList.add('list-group')
    modalContent.appendChild(listaArticulos)
    
    articulos.forEach(articulo => {
        const articuloOption = document.createElement('li');
        articuloOption.classList.add('cliente-option');
        articuloOption.classList.add('list-group-item');
        articuloOption.innerHTML = `<strong>${articulo.detalle}</strong> - <span class="precio-normal">$${parseFloat(articulo.precio).toFixed(2).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>`;
        articuloOption.onclick = () => {
            asignarArticuloElegido(articulo, itemDiv);
            $('#clienteModal').modal('hide');
        };
        listaArticulos.appendChild(articuloOption);
    });

    // Mostrar el modal
    $('#clienteModal').modal('show');
}
        
function removeItem(itemDiv) {
    itemDiv.remove();
    renumberItems();
}

function renumberItems() {
    const itemDivs = document.querySelectorAll('#items .item');
    itemDivs.forEach((itemDiv, index) => {
        itemDiv.querySelector('.idarticulo').setAttribute('name', `items[${index}][idarticulo]`);
        itemDiv.querySelector('.cantidad').setAttribute('name', `items[${index}][cantidad]`);
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
        const idlista = 0;
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
        alert('Debe agregar al menos un item al remito');
        event.preventDefault();
        return false;
    } 
    const idDestino = document.getElementById('iddestino').value;
    const idSucursal = document.getElementById('id_sucursal').value;
    if (idDestino == idSucursal){
        alert('El destino y la sucursal no pueden ser la misma');
        event.preventDefault();
        return false;
    }

    if (confirm('¿Grabar el remito a sucursal?') == false) {
        event.preventDefault();
    }
    else{
        isFormSubmited = true;
    }
});

        