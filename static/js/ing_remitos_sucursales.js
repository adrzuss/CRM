let isFormSubmited = false;

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

        function asignarArticuloElegido(articulo, itemDiv) {
            itemDiv.querySelector('.idarticulo').value = articulo.codigo;
            asignarArticulo(articulo, itemDiv); 
        }

        function asignarArticulo(articulo, itemDiv) {
            itemDiv.querySelector('.articulo_detalle').textContent = articulo.detalle;
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
                articuloOption.innerHTML = `<strong>${articulo.detalle}</strong> - <span class="precio-normal">$${articulo.precio}</span>`;
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


        document.getElementById('agregarArticulo').addEventListener('click', function() {
            const itemsDiv = document.getElementById('items');
            const itemCount = itemsDiv.children.length;

            const newItem = document.createElement('div');
            newItem.classList.add('item');

            newItem.innerHTML = `
                <div class="row m-3">
                    <div class="col-2">
                        <label for="idarticulo">Cod artículo:</label>
                        <input type="text" name="items[${itemCount}][idarticulo]" class="form-control idarticulo" required>
                    </div>    
                    <div class="col-6">
                        <label for="articulo_detalle">Detalle:</label>
                        <span class="articulo_detalle text-uno-bold"></span>
                    </div>    
                    <div class="col-2">
                        <label for="cantidad">Cantidad:</label>
                        <input type="number" name="items[${itemCount}][cantidad]" class="cantidad form-control"  step="0.01" min="0.01" value='1' required>
                    </div>    
                    <div class="col-2">
                        <button type="button" class="remove_item btn btn-danger">Eliminar</button>
                    </div>
                </div>    
            `;

            itemsDiv.appendChild(newItem);

            // Dar foco al input de idarticulo
            const idArticuloInput = newItem.querySelector('.idarticulo');
            idArticuloInput.focus();

            newItem.querySelector('.idarticulo').addEventListener('blur', function() {
                const idarticulo = this.value;
                const idlista = 1
                fetchArticulo(idarticulo, idlista, newItem);
            });

            newItem.querySelector('.remove_item').addEventListener('click', function() {
                removeItem(newItem);
            });

        });

        document.getElementById('invoice_form').addEventListener('submit', function(event) {
            if (document.getElementById('iddestino').value === document.getElementById('id_sucursal').value){
                alert('No puede enviar el remito a la misma sucursal');
                event.preventDefault();
                return false;
            }

            if (document.querySelectorAll('#items .item').length === 0) {
                event.preventDefault();
                alert('Debe agregar al menos un item al remito a sucursales');
                event.preventDefault();
                return false;
            } 
            
            if (confirm('¿Grabar el ingreso de remito a sucursales?') == false) {
                event.preventDefault();
            }
            else{
                isFormSubmited = true;
            }
        });