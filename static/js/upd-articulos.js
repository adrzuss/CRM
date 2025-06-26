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
    const respuesta = await fetch(`${BASE_URL}/articulos/articulo/${codigo}/0`);
    const data = await respuesta.json();
    if (data.success == false){
        form_articulos.removeEventListener('submit', checkArt)
        form_articulos.submit();
    }
    else{
        if (data.articulo.id != id){
            alert('El código ya figura en otro artículo')
            preventDefault();
            return false;
        }
        else{
            form_articulos.removeEventListener('submit', checkArt)
            form_articulos.submit();
        }
        
    }
}

let form_articulos = document.getElementById('articulo_form');
form_articulos.addEventListener('submit', checkArt);
