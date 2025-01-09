document.getElementById('costo').addEventListener('input', function(e) {
    const costo = parseFloat(document.getElementById('costo').value);
    const itemDivs = document.querySelectorAll('.precios #precio');
    itemDivs.forEach((itemDiv, index) => {
        const markup = parseFloat(itemDiv.querySelector('.markup').value);
        itemDiv.querySelector('.precio').value = markup.toFixed(2) * costo.toFixed(2);
    });
    
});

async function checkArt(e){
    e.preventDefault();
    const codigo = document.getElementById('codigo').value;
    const respuesta = await fetch(`/articulo/${codigo}/0`);
    const data = await respuesta.json();
    if (data.success == false){
        form_articulos.removeEventListener('submit', checkArt)
        form_articulos.submit();
    }
    else{
        alert('El código ya figura en otro artículo')
    }
}

let form_articulos = document.getElementById('articulo_form');
form_articulos.addEventListener('submit', checkArt);