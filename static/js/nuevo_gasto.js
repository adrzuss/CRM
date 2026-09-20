isFormSubmited = false; // Variable para controlar si el formulario ha sido enviado

document.addEventListener("DOMContentLoaded", function () {
  window.onbeforeunload = confirmarSalida;
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

  document.getElementById('idproveedor').addEventListener('blur', function() {
      const idproveedor = this.value;
      fetchProveedor(idproveedor);
  });

  document.getElementById('invoice_form').addEventListener('submit', async function(event) {
      event.preventDefault();
      
      const totalFac = parseFloat(document.getElementById('total').value);
      if (totalFac <= 0) {
          mostrarAdvertencia('El total debe ser mayor a 0');
          return;
      }   
      
      if (checkTotales() == false){
          mostrarAdvertencia('La suma de "Efectivo" + "Cta. cte." debe ser igual al total de la factura');
          return;
      }    
      
      const confirmado = await confirmar('¿Grabar la factura?');
      if (!confirmado) {
          return;
      }
      
      sinGuardar = false;
          isFormSubmited = true;
      this.submit();
  });
});

async function fetchProveedor(input) {
    let response;
    if (!isNaN(input)) {
      // Si es un número, buscar por ID
      response = await fetch(`${BASE_URL}/proveedores/get_proveedor/${input}`); //1 venta
    } else {
      // Si es un nombre parcial, buscar por nombre
      response = await fetch(`${BASE_URL}/proveedores/get_proveedores?nombre=${input}&&tipo_operacion=${1}`);
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
        mostrarInfo("No se encontraron proveedores con ese nombre.");
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
    const response = await fetch(`${BASE_URL}/proveedores/get_remitos/${idproveedor}`);
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
  const callback = (proveedor) => {
    asignarProveedor(proveedor);
    // Enfocar el nuevo input de código
    const proveedorInput = document.getElementById("idproveedor");
    if (proveedorInput) proveedorInput.focus();
  };
  
  // Mostrar modal con los datos
  window.universalSearchModal.show('proveedores', proveedores || [], callback);
} 
  
// calcSaldo() y checkTotales() están definidos en modal-transacciones-universal.js
// NO definirlos aquí — sombrean las funciones universales del modal de pagos

// Event listeners movidos a modal-transacciones-universal.js
// document.getElementById('efectivo').addEventListener('input', function(event){
//     calcSaldo();
// })

// document.getElementById('ctacte').addEventListener('input', function(event){
//     calcSaldo();
// })
