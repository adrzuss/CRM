
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

export async function fetchArticulo(id, idlista, itemDiv) {
    let response;
    if (!isNaN(id)){
        response = await fetch(`/articulo/${id}/${idlista}`);
    }
    else{
        response = await fetch(`/get_articulos?detalle=${id}&idlista=${idlista}`);
    }    

    if (!response.ok) {
        console.error("Error en la búsqueda de artículos");
        return;
    }
    //const data = await response.json();
    const data = await response.json();

    if (data.success) {
        if (data.articulo) {
            // Si se encuentra un articulo por ID, asignarlo directamente
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
    const precioUnitario = parseFloat(articulo.precio);
    itemDiv.target.closest("tr").querySelector(".precio-unitario").value = (precioUnitario).toFixed(2);
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
        articuloOption.innerHTML = `<strong>${articulo.marca} ${articulo.detalle}</strong> - <span class="precio-normal">$${parseFloat(articulo.precio).toFixed(2).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>`;
        articuloOption.onclick = () => {
            asignarArticuloElegido(articulo, itemDiv);
            $('#clienteModal').modal('hide');
        };
        listaArticulos.appendChild(articuloOption);
    });

    // Mostrar el modal
    $('#clienteModal').modal('show');
}