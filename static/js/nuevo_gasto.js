isFormSubmited = false; // Variable para controlar si el formulario ha sido enviado

window.onbeforeunload = function () {
  if (!isFormSubmited) {
    return "¿Estás seguro de cerrar la venta sin guardar los cambios?";
  }
};

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("invoice_form");
  const btnGrabar = document.getElementById("grabarGasto");

  // Detectar tecla Enter en los inputs del formulario
  form.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault(); // Evita que se envíe el formulario

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
    if (event.key === "F9") {
      event.preventDefault(); // Evita el comportamiento por defecto de la tecla
      btnGrabar.click(); // Simula un click en el botón "Grabar Venta"
    }

  });
});

async function fetchProveedor(input) {
    let response;
    if (!isNaN(input)) {
      // Si es un número, buscar por ID
      response = await fetch(`/get_proveedor/${input}`); //1 venta
    } else {
      // Si es un nombre parcial, buscar por nombre
      response = await fetch(
        `/get_proveedores?nombre=${input}`
      );
    }
  
    if (!response.ok) {
      limpiarDatosProveedor();
      console.error("Error en la búsqueda del proveedor");
      return;
    }
    const data = await response.json();
    if (data.success) {
      asignarProveedor(data.proveedor);
    } else {
      if (data.length > 1) {
        // Si hay más de un resultado, mostrar un modal para seleccionar
        mostrarModalSeleccionProveedores(data);
      } else if (data.length === 1) {
        // Si hay un solo resultado, asignar directamente
        asignarProveedor(data[0]);
      } else {
        limpiarDatosProveedor();
        alert("No se encontraron proveedores con ese nombre.");
      }
      //document.getElementById("proveedor_nombre").value = "Proveedor no encontrado";
    }
  }

function limpiarDatosProveedor() {
    inputIdProveedor = document.getElementById("idproveedor");
    inputIdProveedor.value = "";
    inputIdProveedor.focus();
}

function asignarProveedor(proveedor) {
    document.getElementById("idproveedor").value = proveedor.id;
    document.getElementById("proveedor_nombre").value = proveedor.nombre;
    obtener_remitos(proveedor.id);
}
  
async function obtener_remitos(idproveedor) {
    const response = await fetch(`/get_remitos/${idproveedor}`);
    const data = await response.json();
    if (data.length > 0) {
        const remitosSelect = document.getElementById("remitos_select");
        remitosSelect.innerHTML = `<ul class='list-group'></ul>`; // Limpiar el select de remitos
        data.forEach((remito, index) => {
            const fecha = new Date(remito.fecha); // Convertir la fecha a un objeto Date
            const dia = String(fecha.getDate()).padStart(2, '0'); // Obtener el día con dos dígitos
            const mes = String(fecha.getMonth() + 1).padStart(2, '0'); // Obtener el mes (0-indexado, por eso +1)
            const anio = fecha.getFullYear();
            const option = document.createElement("li");
            option.className = "list-group-item ml-2"; 
            option.value = remito.id;
            option.innerHTML = `<input class="form-check-input me-1" type="checkbox" id="checkbox${index}" name="remito[${index}][check]">
                                <label class="form-check-label" for="firstCheckbox">${dia}/${mes}/${anio} - ${remito.nro_comprobante}</label>
                                <input type="hidden" name="remito[${index}][id]" value="${remito.id}">`;
            remitosSelect.appendChild(option);
        });
        remitosSelect.style.display = "block"; // Mostrar el select de remitos
    }
    
}

function mostrarModalSeleccionProveedores(proveedores) {
    // Crear el contenido del modal con las opciones de proveedor
    const tituloModal = document.getElementById("clienteModalLabel");
    tituloModal.textContent = "Seleccione un Proveedor";
    const modalContent = document.getElementById("modalContent");
    modalContent.innerHTML = "";
    const listaClientes = document.createElement("ul");
    listaClientes.classList.add("list-group");
    modalContent.appendChild(listaClientes);
  
    proveedores.forEach((proveedor) => {
      const clienteOption = document.createElement("li");
      clienteOption.classList.add("cliente-option");
      clienteOption.classList.add("list-group-item");
      clienteOption.textContent = `${proveedor.nombre} - Tel/Cel: ${proveedor.telefono}`;
      clienteOption.onclick = () => {
        asignarProveedor(proveedor);
        $("#clienteModal").modal("hide");
        // Enfocar el nuevo input de código
        const proveedorInput = document.getElementById("idproveedor");
        proveedorInput.focus();
      };
      listaClientes.appendChild(clienteOption);
    });
  
    // Mostrar el modal
    $("#clienteModal").modal("show");
} 
  
function calcSaldo(){
    const totalFac = parseFloat(document.getElementById('total').value);
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
    const totalFac = parseFloat(document.getElementById('total').value);
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

document.getElementById('invoice_form').addEventListener('submit', function(event) {
    const totalFac = parseFloat(document.getElementById('total').value);
    if (totalFac <= 0) {
        event.preventDefault();
        alert('El total debe ser mayor a 0');
    }   
    
    if (checkTotales() == false){
        event.preventDefault();
        alert('La suma de "Efectivo" + "Cta. cte." debe ser igual al total de la factura');
    }    
    if (confirm('¿Grabar la factura?') == false) {
        event.preventDefault();
    }
    else{
        isFormSubmited = true;
    }
});
 