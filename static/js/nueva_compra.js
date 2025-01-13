let isFormSubmited = false;
let contadorFilas = 0;

async function fetchProveedor(id) {
    const response = await fetch(`/proveedor/${id}`);
    const data = await response.json();
    if (data.success) {
        document.getElementById('proveedor_nombre').value = data.proveedor.nombre;
    } else {
        document.getElementById('proveedor_nombre').value = 'Proveedor no encontrado';
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
            // Si se encuentra un articulo por ID, asignarlo directamente
            asignarArticulo(data.articulo, itemDiv);
        } else {
            alert("No se encontraron articulos con ese ID.");
        }
    } else {
        console.log(data);
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

function calcSaldo(){
    const totalFac = parseFloat(document.getElementById('total_factura').textContent);
    const efectivo = parseFloat(document.getElementById('efectivo').value);
    const ctacte = parseFloat(document.getElementById('ctacte').value);
    let diferencia = (totalFac - (efectivo + ctacte));
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
    let HayDiferencia = (totalFac == (efectivo + ctacte));
    return HayDiferencia;
}

document.getElementById('efectivo').addEventListener('input', function(event){
    calcSaldo();
}
)

document.getElementById('ctacte').addEventListener('input', function(event){
    calcSaldo();
}
)

document.getElementById('idproveedor').addEventListener('blur', function() {
    const idproveedor = this.value;
    fetchProveedor(idproveedor);
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
        const idlista = 0; //idlista = 0 toma valores de costo 

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