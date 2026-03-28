window.abrirModalMovArticulos = abrirModalMovArticulos;

window.abrirModalMovArticulosDetalle = abrirModalMovArticulosDetalle;

document.getElementById('costo').addEventListener('input', function(e) {
    calcularPrecio();
});

document.getElementById('exento').addEventListener('input', function(e) {
    calcularPrecio();
});

document.getElementById('impint').addEventListener('input', function(e) {
    calcularPrecio();
});

document.getElementById('idiva').addEventListener('change', function(e) {
    calcularPrecio();
});

document.getElementById('con_talles').addEventListener('change', function(e) {
    const con_talles = document.getElementById('con_talles').checked;
    const cardTalles = document.querySelector('.card-talles');
    if (con_talles) {
        cardTalles.style.display = 'block';
    } else {
        cardTalles.style.display = 'none';
    }
});

document.getElementById('con_colores').addEventListener('change', function(e) {
    const con_colores = document.getElementById('con_colores').checked;
    const cardColores = document.querySelector('.card-colores');
    if (con_colores) {
        cardColores.style.display = 'block';
    } else {
        cardColores.style.display = 'none';
    }
});


async function calcularPrecio() {
    const costo = parseFloat(document.getElementById('costo').value);
    const idiva = document.getElementById('idiva').value;
    const exento = parseFloat(document.getElementById('exento').value);
    const impInt = parseFloat(document.getElementById('impint').value);
 
         
    const response = await fetch(`${BASE_URL}/articulos/api/precioVP/${costo}/${impInt}/${exento}/${idiva}`);
    
    const data = await response.json();
    
    
    let costoTotal = 0.0;
    if (data.success) {
        costoTotal = parseFloat(data.precio);
        const costo_total = document.getElementById('costo_total');
        costo_total.value = parseFloat(costoTotal);
    }
    
    const itemDivs = document.querySelectorAll('.precios #precio');
    itemDivs.forEach((itemDiv, index) => {
        const markup = parseFloat(itemDiv.querySelector('.markup').value);
        let precioVP = itemDiv.querySelector('.precio');
        precioVP.value = (markup.toFixed(2) * costoTotal.toFixed(2)).toFixed(2);
    });
}

async function checkArt(e){
    e.preventDefault();
    const id = document.getElementById('id').value;
    const codigo = document.getElementById('codigo').value;
    
    if (codigo != ''){
        const respuesta = await fetch(`${BASE_URL}/articulos/articulo/${codigo}/0`);
        const data = await respuesta.json();
        if (data.success == false){
            form_articulos.removeEventListener('submit', checkArt)
            form_articulos.submit();
        }
        else{
            if (data.articulo.id != id){
                mostrarAdvertencia('El código ya figura en otro artículo');
                e.preventDefault();
                return false;
            }
            else{
                form_articulos.removeEventListener('submit', checkArt)
                form_articulos.submit();
            }
            
        }
    }
    else{
        form_articulos.removeEventListener('submit', checkArt)
        form_articulos.submit();
    } 
}

let form_articulos = document.getElementById('articulo_form');
form_articulos.addEventListener('submit', checkArt);



    const con_talles = document.getElementById('con_talles').checked;
    const cardTalles = document.querySelector('.card-talles');
    if (con_talles) {
        cardTalles.style.display = 'block';
    } else {
        cardTalles.style.display = 'none';
    }



    const con_colores = document.getElementById('con_colores').checked;
    const cardColores = document.querySelector('.card-colores');
    if (con_colores) {
        cardColores.style.display = 'block';
    } else {
        cardColores.style.display = 'none';
    }


async function abrirModalMovArticulos(idArticulo){
  try{
    const data = await fetch(`${BASE_URL}/articulos/detalle_articulo/${idArticulo}`);
    const response = await data.json();
    if (!response.success) {
        mostrarAdvertencia('No se pudo cargar el detalle del artículo. Intente nuevamente.');
        return;
    }
    
    const articulo = response.articulo;
    const modalContent = document.getElementById('modalArticuloContent');
    modalContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <i class="fa fa-shopping-cart"></i> <strong>Compras</strong>
                    </div>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Remitos compras
                            <span class="badge badge-primary badge-pill">${articulo.remitos_compras}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Compras
                            <span class="badge badge-primary badge-pill">${articulo.compras}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Entradas de sucursales
                            <span class="badge badge-info badge-pill">${articulo.entradas_de_sucursales}</span>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <i class="fa fa-cash-register"></i> <strong>Ventas</strong>
                    </div>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Remitos ventas
                            <span class="badge badge-success badge-pill">${articulo.remitos_ventas}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Ventas
                            <span class="badge badge-success badge-pill">${articulo.ventas}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Notas de crédito
                            <span class="badge badge-success badge-pill">${articulo.credito_ventas}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Salidas a sucursales
                            <span class="badge badge-warning badge-pill">${articulo.salidas_a_sucursales}</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4 text-center">
                                <small class="text-muted">Fecha de alta</small>
                                <h6><i class="fa fa-calendar-plus"></i> ${articulo.alta}</h6>
                            </div>
                            <div class="col-md-4 text-center">
                                <small class="text-muted">Balance</small>
                                <h6><i class="fa fa-balance-scale"></i> ${articulo.balance}</h6>
                            </div>
                            <div class="col-md-4 text-center">
                                <small class="text-muted">Stock actual</small>
                                <h4 class="text-primary"><i class="fa fa-boxes"></i> <strong>${articulo.stock_actual}</strong></h4>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `

    // Abrir modal usando Bootstrap 5
    const modalElement = document.getElementById('articuloMovimientosModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    
  }
  catch(error){
    console.error('Error al obtener el detalle del artículo:', error);
    mostrarAdvertencia('No se pudo cargar el detalle del artículo. Intente nuevamente.' + error.message);  
  };
}


async function abrirModalMovArticulosDetalle(idArticulo){
  try{
    const data = await fetch(`${BASE_URL}/articulos/detalle_full_articulo/${idArticulo}`);
    const response = await data.json();
    if (!response.success) {
        mostrarAdvertencia('No se pudo cargar el detalle del artículo. Intente nuevamente.');
        return;
    }
    
    const movimientos = response.articulo.movimientos;
    const modalContent = document.getElementById('modalArticuloContent');
    
    // Función para asignar badge según tipo de movimiento
    const getBadgeClass = (tipo) => {
        console.log('Tipo de movimiento:', tipo);
        const tipoLower = tipo.toLowerCase();
        if (tipoLower.includes('compras') || tipoLower.includes('entrada')) return 'bg-primary';
        if (tipoLower.includes('ventas') || tipoLower.includes('salida')) return 'bg-success';
        if (tipoLower.includes('remito')) return 'bg-info';
        if (tipoLower.includes('balance')) return 'bg-warning text-dark';
        return 'bg-secondary';
    };

    // Función para formatear cantidad con signo y color
    const formatCantidad = (cantidad) => {
        const num = parseFloat(cantidad);
        if (num > 0) return `<span class="text-success fw-bold">+${num}</span>`;
        if (num < 0) return `<span class="text-danger fw-bold">${num}</span>`;
        return `<span class="text-muted">${num}</span>`;
    };

    let tablaHTML = '';
    
    let stock = 0; // Variable para calcular el stock resultante
    if (movimientos && movimientos.length > 0) {
        tablaHTML = `
            <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                <table class="table table-striped table-hover table-sm">
                    <thead class="table-dark sticky-top">
                        <tr>
                            <th><i class="fa fa-calendar"></i> Fecha</th>
                            <th><i class="fa fa-tag"></i> Tipo</th>
                            <th><i class="fa fa-file-alt"></i> Nrp. comp.</th>
                            <th class="text-end"><i class="fa fa-sort-numeric-up"></i> Entradas</th>
                            <th class="text-end"><i class="fa fa-boxes"></i> Salidas</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${movimientos.map(mov => `
                            <tr>
                                <td>${mov.fecha || '-'}</td>
                                <td><span class="badge ${getBadgeClass(mov.tipo_movimiento)}">${mov.tipo_movimiento}</span></td>
                                <td>${mov.nro_comp || '-'}</td>
                                <td class="text-end">${formatCantidad(mov.entradas)}</td>
                                <td class="text-end fw-bold">${formatCantidad(mov.salidas)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <div class="mt-3 p-2 bg-light rounded d-flex justify-content-between">
                <span><i class="fa fa-list"></i> Total de movimientos: <strong>${movimientos.length}</strong></span>
                <span><i class="fa fa-boxes"></i> Stock actual: <strong class="text-primary">${movimientos.length > 0 ? movimientos.map(mov => parseFloat(mov.entradas) - parseFloat(mov.salidas)).reduce((acc, curr) => acc + curr, 0) : 0}</strong></span>
            </div>
        `;
    } else {
        tablaHTML = `
            <div class="alert alert-info">
                <i class="fa fa-info-circle"></i> No se encontraron movimientos para este artículo.
            </div>
        `;
    }
    
    modalContent.innerHTML = tablaHTML;

    // Abrir modal usando Bootstrap 5
    const modalElement = document.getElementById('articuloMovimientosModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    
  }
  catch(error){
    console.error('Error al obtener el detalle del artículo:', error);
    mostrarAdvertencia('No se pudo cargar el detalle del artículo. Intente nuevamente.' + error.message);  
  };
}
