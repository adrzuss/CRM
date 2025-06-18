async function getVentasSucursales(desde, hasta){
    const response = await fetch(`${BASE_URL}/ventas/get_vta_sucursales/${desde}/${hasta}`);
    const data = await response.json();
    return data;
}
    
document.getElementById('calcular_sucs').addEventListener('click', async function() {
    let desde = document.getElementById('desde_sucs').value;
    let hasta = document.getElementById('hasta_sucs').value;
    const data = await getVentasSucursales(desde, hasta);
    if (data.success == false){
        alert('Error al obtener ventas');
    }
    else{
        let tbody = document.getElementById('tablaVtaSucursales').getElementsByTagName('tbody')[0];
        tbody.innerHTML = '';  // Limpiar la tabla existente

        data.ventas.forEach(function(venta) {
            var row = tbody.insertRow();
            var cell1 = row.insertCell(0);
            var cell2 = row.insertCell(1);
            var cell3 = row.insertCell(2);
            var cell4 = row.insertCell(3);
            cell1.textContent = venta.sucursal;
            cell2.textContent = venta.total;
            cell3.textContent = venta.cantidad;
            cell4.textContent = venta.tktProm;
        });
    }    
});

async function getVentasVendedores(desde, hasta){
    const response = await fetch(`${BASE_URL}/ventas/get_vta_vendedores/${desde}/${hasta}`);
    const data = await response.json();
    return data;
}
    
document.getElementById('calcular_vend').addEventListener('click', async function() {
    let desde = document.getElementById('desde_vend').value;
    let hasta = document.getElementById('hasta_vend').value;
    const data = await getVentasVendedores(desde, hasta);
    if (data.success == false){
        alert('Error al obtener ventas');
    }
    else{
        let tbody = document.getElementById('tablaVtaVendedores').getElementsByTagName('tbody')[0];
        tbody.innerHTML = '';  // Limpiar la tabla existente

        data.ventas.forEach(function(venta) {
            var row = tbody.insertRow();
            var cell1 = row.insertCell(0);
            var cell2 = row.insertCell(1);
            var cell3 = row.insertCell(2);
            var cell4 = row.insertCell(3);
            cell1.textContent = venta.vendedor;
            cell2.textContent = venta.total;
            cell3.textContent = venta.cantidad;
            cell4.textContent = venta.tktProm;
        });
    }    
});