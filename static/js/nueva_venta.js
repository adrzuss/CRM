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
            itemDiv.target.closest("tr").querySelector(".codigo-articulo").value = articulo.codigo;
            asignarArticulo(articulo, itemDiv);; 
        }

        function asignarArticulo(articulo, itemDiv) {
            itemDiv.target.closest("tr").querySelector(".id-articulo").textContent = articulo.id;
            itemDiv.target.closest("tr").querySelector(".descripcion-articulo").textContent = articulo.detalle;
            const precioUnitario = parseFloat(articulo.precio);
            itemDiv.target.closest("tr").querySelector(".precio-unitario").value = (precioUnitario).toFixed(2);
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

        function updateItemTotal(itemDiv) {
            const precioUnitario = parseFloat(itemDiv.target.closest("tr").querySelector(".precio-unitario").value);
            const cantidad = parseFloat(itemDiv.target.closest("tr").querySelector(".cantidad").value);
            const precioTotal = (precioUnitario * cantidad).toFixed(2);
            if (isNaN(precioTotal)){
                precioTotal = 0;
            }
            itemDiv.target.closest("tr").querySelector(".precio-total").value = precioTotal;
        }

        function updateTotalFactura() {
            const filas = document.querySelectorAll('#tabla-items tbody tr');
            let totalFactura = 0;
            filas.forEach(fila => {
                const precioTotalInput = fila.querySelector('.precio-total');
                if (precioTotalInput) {
                    const precioTotal = parseFloat(precioTotalInput.value) || 0;
                    totalFactura += precioTotal;
                }
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
            const totTarjeta = parseFloat(document.getElementById('tarjeta').value);
            if (totTarjeta > 0){
                const entidad = parseInt(document.getElementById('entidad').value);
                if ((entidad <= 0) || (isNaN(entidad))){
                    alert('Debe completar correctamente los datos de tarjeta');
                    return false;
                }
                alert('Datos de tarjeta correctos');
                return true;
            }
            else{
                alert('Debe completar correctamente los datos de tarjeta'); 
                return false;
            }
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
            lblSaldo.textContent = (diferencia).toFixed(2);
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

        document.getElementById('efectivo').addEventListener('blur', function(event){
            calcSaldo();
        }
        )

        document.getElementById('tarjeta').addEventListener('blur', function(event){
            calcSaldo();
        }
        )

        document.getElementById('ctacte').addEventListener('blur', function(event){
            calcSaldo();
        }
        )

        document.getElementById('idcliente').addEventListener('blur', function() {
            const idcliente = this.value;
            fetchCliente(idcliente);
        });

        document.getElementById('tabla-items').addEventListener('input', function(e) {
            if (e.target.classList.contains('idarticulo') || e.target.classList.contains('cantidad')) {
                updateItemTotal(e);
                updateTotalFactura();
            }
        });

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
                    <td><input type="number" class="form-control precio-total" name="items[${contadorFilas}][precio_total]" readonly></td>
                    <td><button type="button" class="btn btn-danger btn-eliminar">Eliminar</button></td>
                </tr>`;
            tablaItems.insertAdjacentHTML("beforeend", nuevaFila);
            contadorFilas++;
        });

        tablaItems.addEventListener("blur", (itemDiv) => {
            if (itemDiv.target.classList.contains("codigo-articulo")) {
                const codigo = itemDiv.target.value;
                const idlista = document.getElementById('idlista').value;
    
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
                alert('Debe agregar al menos un item a la factura');
                event.preventDefault();
                return false;
            } 
            console.log('vamos a la tarjeta')
            if (checkDatosTarjeta() === false){
                event.preventDefault();
                return false;
            }

            if (checkTotales() === false){
                event.preventDefault();
                alert('El total debe ser mayor a cera y/o la suma de "Efectivo" + "Tarjeta" + "Cta. cte." debe ser igual al total de la factura');
                event.preventDefault();
                return false;
            }    
            if (confirm('¿Grabar la factura?') === false) {
                event.preventDefault();
            }
            else{
                isFormSubmited = true;
            }
        });