// JavaScript para manejar la interacción
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('form-cambio-precios');
    const btnAgregar = document.getElementById('agregar-item');
    const btnGrabar = document.getElementById('guardar-cambio');

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

let contadorFilas = 0;

document.addEventListener("DOMContentLoaded", () => {
    const tablaItems = document.querySelector("#tabla-items tbody");

    // Agregar nueva fila
    document.querySelector("#agregar-item").addEventListener("click", () => {
        const nuevaFila = `
            <tr>
                <td><input type="text" class="form-control codigo-articulo" name="items[${contadorFilas}][codigo]" required></td>
                <td class="descripcion-articulo">-</td>
                <td><input type="number" class="form-control precio-actual" name="items[${contadorFilas}][precio_actual]" readonly></td>
                <td><input type="number" class="form-control precio-nuevo" name="items[${contadorFilas}][precio_nuevo]" step="0.01" min="0" required></td>
                <td><button type="button" class="btn btn-danger btn-eliminar">Eliminar</button></td>
            </tr>`;
        tablaItems.insertAdjacentHTML("beforeend", nuevaFila);
        contadorFilas++;
    });

    // Eliminar fila
    tablaItems.addEventListener("click", (itemDiv) => {
        if (itemDiv.target.classList.contains("btn-eliminar")) {
            itemDiv.target.closest("tr").remove();
        }
    });

    // Validar y guardar
    document.querySelector("#guardar-cambio").addEventListener("click", () => {
        if (tablaItems.children.length === 0) {
            alert("Debe agregar al menos un artículo.");
            return;
        }

        if (confirm("¿Está seguro de guardar los cambios?")) {
            console.log("voy a grabar");
            document.querySelector("#form-cambio-precios").submit();
        }
    });

    // Validar salida sin guardar
    
    window.addEventListener("beforeunload", (e) => {
        e.preventDefault();
        e.returnValue = "Tiene cambios sin guardar. ¿Está seguro de salir?";
    });
    
    // Cargar artículos en tabla de acuerdo a los filtros
    document.querySelector('#cargarRubroMarca').addEventListener('click', async (e) => {
        e.preventDefault();
        console.log('click cargar');
        const marca = document.getElementById('marca').value;
        const rubro = document.getElementById('rubro').value;
        const listaPrecio = document.getElementById('lista_precio').value;
        const porcentaje = document.getElementById('porcentaje').value;
        console.log('click cargar 2');
        if (!listaPrecio) {
            alert('Seleccione una lista de precios');
            return;
        }
    
        try {
            let response;
            response = await fetch(`/filtrar_articulos/${marca}/${rubro}/${listaPrecio}/${porcentaje}`);
            console.log('ya tengo la respuesta:', response);
            if (!response.ok) throw new Error('Error al cargar los artículos');
            console.log('voy a cargar los datos de los articulos');
            const data = await response.json();
            if (data.success) {
                console.log('data', data);
                cargarArticulosEnTabla(data.articulos);
            }
            else {
                alert('Ocurrió un error al cargar los productos ' + data.error);
            }
        } catch (error) {
            console.error(error);
            alert('Ocurrió un error al cargar los productos');
        }
    });
    
    function cargarArticulosEnTabla(articulos) {
        const tablaItems = document.querySelector("#tabla-items tbody");
        tablaItems.innerHTML = ''; // Limpiar tabla
    
        articulos.forEach((articulo) => {
            console.log('articulo', articulo);
            const nuevaFila = `
                <tr>
                    <td>${articulo.codigo}</td>
                    <td>${articulo.descripcion}</td>
                    <td><input type="number" class="form-control precio-actual" value="${articulo.precio_actual}" readonly></td>
                    <td><input type="number" class="form-control precio-nuevo" value="${articulo.precio_nuevo}"></td>
                    <td><button type="button" class="btn btn-danger btn-eliminar">Eliminar</button></td>
                </tr>`;
            tablaItems.insertAdjacentHTML('beforeend', nuevaFila);
        });
    }

    // Buscar descripción y precio actual (simulado)
    async function fetchArticulo(id, idlista, itemDiv) {
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
            articuloOption.innerHTML = `<strong>${articulo.detalle}</strong> - <span class="precio-normal">$${articulo.precio.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>`;
            articuloOption.onclick = () => {
                asignarArticuloElegido(articulo, itemDiv);
                $('#clienteModal').modal('hide');
            };
            listaArticulos.appendChild(articuloOption);
        });
    
        // Mostrar el modal
        $('#clienteModal').modal('show');
    }

    function asignarArticuloElegido(articulo, itemDiv) {
        itemDiv.target.closest("tr").querySelector(".codigo-articulo").value = articulo.codigo;
        asignarArticulo(articulo, itemDiv); 
    }

    function asignarArticulo(articulo, itemDiv) {
        itemDiv.target.closest("tr").querySelector(".descripcion-articulo").textContent = articulo.detalle;
        itemDiv.target.closest("tr").querySelector(".precio-actual").value = articulo.precio;
    }


    tablaItems.addEventListener("blur", (itemDiv) => {
        if (itemDiv.target.classList.contains("codigo-articulo")) {
            const codigo = itemDiv.target.value;
            const idlista = document.getElementById('lista_precio').value;

            // Simulación de una búsqueda (deberías usar una API aquí)
            fetchArticulo(codigo, idlista, itemDiv)
            
        }
    }, true);
});