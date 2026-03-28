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

// Seleccionar todos los botones con la clase 'eliminarCompuesto'
document.querySelectorAll('.eliminarCompuesto').forEach(function(boton) {
    boton.addEventListener('click', async function(event) {
        event.preventDefault(); // Prevenir la acción por defecto del enlace

        // Obtener los atributos únicos del botón
        const idArticulo = this.dataset.idarticulo;
        const idArtComp = this.dataset.idart_comp;

        // Pedir confirmación
        const confirmado = await confirmarEliminar(`¿Estás seguro de que quieres eliminar el compuesto con ID ${idArticulo} y Compuesto ID ${idArtComp}?`);

        if (confirmado) {
            // Redirigir al enlace original
            window.location.href = this.href;
        }
    });
});

async function fetchArticulo(idart_org, id, idlista) {
    let response;
    if (!isNaN(id)){
        response = await fetch(`${BASE_URL}/articulos/articulo/${id}/${idlista}`);
        
    }
    else{
        response = await fetch(`${BASE_URL}/get_articulos?detalle=${id}&idlista=${idlista}`);
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
                mostrarAdvertencia('No se puede componer un artículo con el mismo');
            }
            else{
                asignarArticulo(data.articulo);
            }
        } else {
            mostrarInfo('No se encontraron artículos con ese ID', 'Sin resultados');
        }
    } else {
        if (data.length > 1) {
            // Si hay más de un resultado, mostrar un modal para seleccionar
            mostrarModalSeleccionArticulos(data);
        } else if (data.length === 1) {
            // Si hay un solo resultado, asignar directamente
            if (idart_org == data[0].id){
                limpiarDatos();
                mostrarAdvertencia('No se puede componer un artículo con el mismo');
            }
            else{
                asignarArticuloElegido(data[0]);
            }
        } else {
            mostrarInfo('No se encontraron artículos con ese detalle', 'Sin resultados');
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
    const callback = (articulo) => {
        asignarArticuloElegido(articulo);
    };
    
    // Mostrar modal con los datos
    window.universalSearchModal.show('articulos', articulos || [], callback);
}

