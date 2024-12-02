/*
let form_articulos = document.getElementById('composicion_form');
form_articulos.addEventListener('submit', checkArt);
*/

let codigo = document.getElementById('codigo');
codigo.addEventListener('blur', function() {
    const idarticulo = this.value;
    const idlista = 1
    const idart_org = document.getElementById('idarticulo').value;
    fetchArticulo(idart_org, idarticulo, idlista);
});

async function fetchArticulo(idart_org, id, idlista) {
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
            // Si se encuentra un cliente por ID, asignarlo directamente
            if (idart_org == data.articulo.id){
                limpiarDatos();
                alert('No se puede componer un artículo con el mismo');
            }
            else{
                asignarArticulo(data.articulo);
            }
        } else {
            alert("No se encontraron articulos con ese ID.");
        }
    } else {
        if (data.length > 1) {
            // Si hay más de un resultado, mostrar un modal para seleccionar
            mostrarModalSeleccionArticulos(data);
        } else if (data.length === 1) {
            // Si hay un solo resultado, asignar directamente
            if (idart_org == data[0].id){
                limpiarDatos();
                alert('No se puede componer un artículo con el mismo');
            }
            else{
                asignarArticuloElegido(data[0]);
            }
        } else {
            alert("No se encontraron articulos con ese detalle.");
        }
    }
}

function asignarArticuloElegido(articulo) {
    asignarArticulo(articulo); 
}

function limpiarDatos(){
    document.getElementById('codigo').value = '';
    document.getElementById('detalle').value = '';
    document.getElementById('cantidad').value = '';
}


function asignarArticulo(articulo) {
    document.getElementById('codigo').value = articulo.codigo;
    document.getElementById('detalle').value = articulo.detalle;
    document.getElementById('cantidad').value = 1;
}

function mostrarModalSeleccionArticulos(articulos) {
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
        articuloOption.innerHTML = `<strong>${articulo.detalle}</strong> - <span class="precio-normal">$${articulo.precio}</span>`;
        articuloOption.onclick = () => {
            asignarArticuloElegido(articulo);
            $('#clienteModal').modal('hide');
        };
        listaArticulos.appendChild(articuloOption);
    });

    // Mostrar el modal
    $('#clienteModal').modal('show');
}

