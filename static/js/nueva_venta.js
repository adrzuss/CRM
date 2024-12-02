let isFormSubmited = false;

        window.onbeforeunload = function() {
            if (!isFormSubmited) {
                return '¿Estás seguro de cerrar la venta sin guardar los cambios?';
            }
        };
        

        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('invoice_form');
            const btnAgregar = document.getElementById('agregarArticulo');
            const btnGrabar = document.getElementById('grabarVenta');
        
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

                // Asignar tecla F5 para agregar un nuevo artículo
                if (event.key === 'F4') {
                    event.preventDefault();  // Evita la recarga de página con F5
                    btnAgregar.click();  // Simula un click en el botón "Agregar Artículo"
                }
            });
        });

        async function fetchCliente(input) {
            let response;
        
            // Determinar si la entrada es un ID numérico o un nombre
            if (!isNaN(input)) {
                // Si es un número, buscar por ID
                response = await fetch(`/get_cliente/${input}/${1}`); //1 venta
            } else {
                // Si es un nombre parcial, buscar por nombre
                response = await fetch(`/get_clientes?nombre=${input}&&tipo_operacion=${1}`);
            }
        
            if (!response.ok) {
                console.error("Error en la búsqueda del cliente");
                return;
            }
        
            const data = await response.json();

            if (data.success) {
                if (data.cliente) {
                    // Si se encuentra un cliente por ID, asignarlo directamente
                    asignarCliente(data.cliente);
                } else {
                    alert("No se encontraron clientes con ese ID.");
                }
            } else {
                if (data.length > 1) {
                    // Si hay más de un resultado, mostrar un modal para seleccionar
                    mostrarModalSeleccionClientes(data);
                } else if (data.length === 1) {
                    // Si hay un solo resultado, asignar directamente
                    asignarCliente(data[0]);
                } else {
                    alert("No se encontraron clientes con ese nombre.");
                }
            }
        }
        
        function mostrarModalSeleccionClientes(clientes) {
            // Crear el contenido del modal con las opciones de cliente
            const tituloModal = document.getElementById('clienteModalLabel'); 
            tituloModal.textContent = 'Seleccione un Cliente';
            const modalContent = document.getElementById('modalContent');
            modalContent.innerHTML = '';
            const listaClientes = document.createElement('ul');
            listaClientes.classList.add('list-group')
            modalContent.appendChild(listaClientes)
            
            clientes.forEach(cliente => {
                const clienteOption = document.createElement('li');
                clienteOption.classList.add('cliente-option');
                clienteOption.classList.add('list-group-item');
                clienteOption.textContent = `${cliente.nombre} - Tel/Cel: ${cliente.telefono}`;
                clienteOption.onclick = () => {
                    asignarCliente(cliente);
                    $('#clienteModal').modal('hide');
                };
                listaClientes.appendChild(clienteOption);
            });
        
            // Mostrar el modal
            $('#clienteModal').modal('show');
        }
        
        function asignarCliente(cliente) {
            document.getElementById('idcliente').value = cliente.id;
            document.getElementById('cliente_nombre').value = cliente.nombre;
            document.getElementById('id').value = cliente.id;
            document.getElementById('ctacte').readOnly = cliente.ctacte == 0;
            document.getElementById('tipo_comprobante').innerText = 'Tipo de factura: ' + cliente.tipo_comprobante;
            document.getElementById('id_tipo_comprobante').value = cliente.id_tipo_comprobante;
            if (cliente.ctacte == 0){
                document.getElementById('label-ctacte').innerText = 'Cta. Cte. - Cliente sin cta. cte.'
            }
            else{
                document.getElementById('label-ctacte').innerText = 'Cta. Cte.'
            }
        }



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
            itemDiv.querySelector('.articulo_precio').value = articulo.precio;
            updateItemTotal(itemDiv);
            updateTotalFactura();
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

        function updateItemTotal(itemDiv) {
            const precioUnitario = parseFloat(itemDiv.querySelector('.articulo_precio').value);
            const cantidad = parseFloat(itemDiv.querySelector('.cantidad').value);
            const precioTotal = (precioUnitario * cantidad).toFixed(2);
            if (isNaN(precioTotal)){
                precioTotal = 0;
            }
            itemDiv.querySelector('.precio_total').value = precioTotal;
        }

        function updateTotalFactura() {
            const itemDivs = document.querySelectorAll('#items .item');
            let totalFactura = 0;
            itemDivs.forEach(itemDiv => {
                const precioTotal = parseFloat(itemDiv.querySelector('.precio_total').value);
                totalFactura += precioTotal;
            });
            document.getElementById('total_factura').textContent = totalFactura.toFixed(2);
            calcSaldo();
        }

        function removeItem(itemDiv) {
            itemDiv.remove();
            updateTotalFactura();
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

        function checkDatosTarjeta(){
            const tarjeta = parseFloat(document.getElementById('tarjeta').value);
            if (tarjeta > 0){
                const entidad = document.getElementById('entidad').value;
             
                if (entidad <= 0){
                    return false;
                }
                return true;
            }
            return true;
        }
        /*FIXIT
        controlar valores nulos NaN*/
        function calcSaldo(){
            const totalFac = parseFloat(document.getElementById('total_factura').textContent);
            const efectivo = parseFloat(document.getElementById('efectivo').value);
            const tarjeta = parseFloat(document.getElementById('tarjeta').value);
            const ctacte = parseFloat(document.getElementById('ctacte').value);
            if (isNaN(efectivo)){
                efectivo = 0;    
            }
            if (isNaN(tarjeta)){
                tarjeta = 0;
            }
            if (isNaN(ctacte)){
                ctacte = 0;
            }
            let diferencia = (totalFac - (efectivo + tarjeta + ctacte));
            let lblSaldo = document.getElementById('saldo_factura');
            lblSaldo.textContent = diferencia;
            if (diferencia > 0){
                lblSaldo.className = 'negativo';
            }
            else if (diferencia === 0){
                lblSaldo.className = 'neutro';
            }
            else{
                lblSaldo.className = 'positivo';
            }
        }

        function checkTotales() {
            const totalFac = parseFloat(document.getElementById('total_factura').textContent);
            const efectivo = parseFloat(document.getElementById('efectivo').value);
            const ctacte = parseFloat(document.getElementById('ctacte').value);
            const tarjeta = parseFloat(document.getElementById('tarjeta').value);
            if (isNaN(efectivo)){
                efectivo = 0;    
            }
            if (isNaN(tarjeta)){
                tarjeta = 0;
            }
            if (isNaN(ctacte)){
                ctacte = 0;
            }
            let HayDiferencia = (totalFac > 0) && (totalFac == (efectivo + tarjeta + ctacte));
            
            return HayDiferencia;
        }

        document.getElementById('efectivo').addEventListener('input', function(event){
            calcSaldo();
        }
        )

        document.getElementById('tarjeta').addEventListener('input', function(event){
            calcSaldo();
        }
        )

        document.getElementById('ctacte').addEventListener('input', function(event){
            calcSaldo();
        }
        )

        document.getElementById('idcliente').addEventListener('blur', function() {
            const idcliente = this.value;
            fetchCliente(idcliente);
        });

        document.getElementById('items').addEventListener('input', function(e) {
            if (e.target.classList.contains('idarticulo') || e.target.classList.contains('cantidad')) {
                const itemDiv = e.target.closest('.item');
                updateItemTotal(itemDiv);
                updateTotalFactura();
            }
        });

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
                    <div class="col-3">
                        <label for="articulo_detalle">Detalle:</label>
                        <span class="articulo_detalle text-uno-bold"></span>
                    </div>    
                    <div class="col-2">
                        <label for="articulo_precio">Precio Unitario:</label>
                        <input type="number" name="items[${itemCount}][articulo_precio]" class="form-control articulo_precio" readonly>
                    </div>    
                    <div class="col-1">
                        <label for="cantidad">Cantidad:</label>
                        <input type="number" name="items[${itemCount}][cantidad]" class="cantidad form-control" min="1" value='1' required>
                    </div>    

                    <div class="col-2">
                        <label for="precio_total">Precio Total:</label>
                        <input type="text" name="precio_total" id="precio_total" class="precio_total form-control" value="0.00" readonly>
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
                const idlista = document.getElementById('idlista').value
                fetchArticulo(idarticulo, idlista, newItem);
            });

            newItem.querySelector('.remove_item').addEventListener('click', function() {
                removeItem(newItem);
            });

        });

        document.getElementById('invoice_form').addEventListener('submit', function(event) {
            if (document.querySelectorAll('#items .item').length === 0) {
                event.preventDefault();
                alert('Debe agregar al menos un item a la factura');
                event.preventDefault();
                return false;
            } 
            if (checkDatosTarjeta() == false){
                event.preventDefault();
                alert('Debe completar correctamente los datos de tarjeta');
                event.preventDefault();
                return false;
            }

            if (checkTotales() == false){
                event.preventDefault();
                alert('El total debe ser mayor a cera y/o la suma de "Efectivo" + "Tarjeta" + "Cta. cte." debe ser igual al total de la factura');
                event.preventDefault();
                return false;
            }    
            if (confirm('¿Grabar la factura?') == false) {
                event.preventDefault();
            }
            else{
                isFormSubmited = true;
            }
        });