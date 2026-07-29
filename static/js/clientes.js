/**
 * clientes.js
 * Lógica de la página de gestión de clientes.
 * Requiere: base.html (BASE_URL, swal-helpers.js, jQuery)
 *           vendor/datatable/datatables.js
 */

document.getElementById("provincia").addEventListener("change", function() {
    const provinciaId = this.value;
    fetch(`${BASE_URL}/clientes/localidades/${provinciaId}`)
        .then(response => response.json())
        .then(data => {
            const localidadSelect = document.getElementById("localidad");
            localidadSelect.innerHTML = '';
            data.localidades.forEach(localidad => {
                const option = document.createElement("option");
                option.value = localidad.id;
                option.textContent = localidad.localidad;
                localidadSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching localidades:', error));
});

document.getElementById("documento").addEventListener("blur", function() {
    checkCuit();
});

async function checkCuit() {
    const cuit = document.getElementById("documento").value;
    const tipoDoc = document.getElementById("tipo_doc").value;

    const response = await fetch(`${BASE_URL}/checkCuit/${cuit}/${tipoDoc}`);
    const data = await response.json();

    if (!data.cuitValido) {
        mostrarAdvertencia("El CUIT ingresado no es válido");
    }
}

new DataTable('#dataTable', {
    iDisplayLength: 50,
    language: {
        entries: {
            _: "entradas",
            1: "entrada"
        },
        sInfo: "Mostrando _START_ de _END_ de un total de _TOTAL_ _ENTRIES-TOTAL_",
        sInfoEmpty: "Mostrando 0 de 0 de 0 _ENTRIES-TOTAL_",
        sInfoFiltered: "(Filtrando _MAX_ de un total de _ENTRIES-MAX_)",
        sLengthMenu: "_MENU_ _ENTRIES_ por página",
        sSearch: 'Buscar',
        sSearchPlaceholder: 'Buscar registros'
    }
});
