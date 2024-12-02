document.getElementById('costo').addEventListener('input', function(e) {
    const costo = parseFloat(document.getElementById('costo').value);
    const itemDivs = document.querySelectorAll('.precios #precio');
    itemDivs.forEach((itemDiv, index) => {
        const markup = parseFloat(itemDiv.querySelector('.markup').value);
        itemDiv.querySelector('.precio').value = (markup.toFixed(2) * costo.toFixed(2)).toFixed(2);
    });
    
});

async function checkArt(e){
    e.preventDefault();
    const codigo = document.getElementById('codigo').value;
    const respuesta = await fetch(`/articulo/${codigo}/0`);
    const data = await respuesta.json();
    if ((data.error = 'Artículo no encontrado') || (data.success == false)){
        form_articulos.removeEventListener('submit', checkArt)
        form_articulos.submit();
    }
    else{
        alert(`El código: ${codigo} ya figura en otro artículo: ${data.articulo.id}: ${data.articulo.detalle}`);
    }
}

