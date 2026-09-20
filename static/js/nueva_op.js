isFormSubmited = false; // Variable para controlar si el formulario ha sido enviado

document.addEventListener("DOMContentLoaded", function () {
    window.onbeforeunload = confirmarSalida;

    // Abrir modal de facturas pendientes al hacer click en el badge
    const btnFacturas = document.getElementById("btn_facturas_pendientes");
    if (btnFacturas) {
        btnFacturas.addEventListener("click", function () {
            const modal = new bootstrap.Modal(document.getElementById("facturasPendientesModal"));
            modal.show();
        });
    }

    // Botón Aceptar del modal de facturas pendientes
    const btnAceptar = document.getElementById("btn_aceptar_facturas_pend");
    if (btnAceptar) {
        btnAceptar.addEventListener("click", function () {
            calcularTotal();
            const modal = bootstrap.Modal.getInstance(document.getElementById("facturasPendientesModal"));
            if (modal) modal.hide();
        });
    }

    // Event delegation para checkboxes de facturas pendientes
    const movsSelect = document.getElementById("movs_select");
    if (movsSelect) {
        movsSelect.addEventListener("change", function (e) {
            if (e.target.type === "checkbox") {
                calcularTotal();
            }
        });
    }
});


document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("invoice_form");
  const btnGrabar = document.getElementById("grabarOp");

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
    obtener_mov_ctacte(proveedor.id);
}
  
async function obtener_mov_ctacte(idproveedor) { 
    const response = await fetch(`${BASE_URL}/proveedores/get_movs_ctacte/${idproveedor}`);
    const data = await response.json();
    const badge = document.getElementById("badge_facturas_pendientes");
    const btn = document.getElementById("btn_facturas_pendientes");
    const noFacturasMsg = document.getElementById("no-facturas-msg");
    
    if (data.length > 0) {
        const movsSelect = document.getElementById("movs_select");
        movsSelect.innerHTML = `<ul class='list-group'></ul>`; // Limpiar el select de remitos
        data.forEach((movs, index) => {
            const fecha = new Date(movs.fecha); // Convertir la fecha a un objeto Date
            const dia = String(fecha.getDate()).padStart(2, '0'); // Obtener el día con dos dígitos
            const mes = String(fecha.getMonth() + 1).padStart(2, '0'); // Obtener el mes (0-indexado, por eso +1)
            const anio = fecha.getFullYear();
            const option = document.createElement("li");
            option.className = "list-group-item ml-2"; 
            option.value = movs.id;
            const saldo = parseFloat(movs.saldo);
            option.innerHTML = `<input class="form-check-input me-1" type="checkbox" id="checkbox${index}" name="mov_cc[${index}][check]">
                                <label class="form-check-label" for="firstCheckbox">${dia}/${mes}/${anio} - Comprobante: ${movs.tipo_comprobante} / ${movs.nro_comprobante} - Saldo $${saldo.toFixed(2)}</label>
                                <input type="hidden" name="mov_cc_saldo[${index}][id]" id="mov_cc_saldo[${index}][id]" value="${saldo}">
                                <input type="hidden" name="mov_cc_id[${index}][id]" value="${movs.id}">`;
            movsSelect.appendChild(option);
        });
        
        badge.textContent = data.length;
        btn.disabled = false;
        if (noFacturasMsg) noFacturasMsg.classList.add("d-none");
    } else {
        badge.textContent = 0;
        btn.disabled = true;
        if (noFacturasMsg) noFacturasMsg.classList.remove("d-none");
    }
}

function calcularTotal(){
    const totalMovsEl = document.getElementById("total_movs");
    if (!totalMovsEl) return;
    const listodoMovs = document.getElementById("movs_select");
    const movs = listodoMovs.querySelectorAll("input[type=checkbox]:checked");
    if (movs.length == 0){
        totalMovsEl.value = 0;
        document.getElementById("total").value = "0.00";
        document.getElementById("total_factura").textContent = "0.00";
        return;
    }
    let totalMovs = 0;
    movs.forEach((item) => {
        index = item.name.split('[')[1].split(']')[0];
        const saldo = document.getElementById("mov_cc_saldo[" + index + "][id]").value;
        totalMovs += parseFloat(saldo);
    });
    totalMovsEl.value = totalMovs.toFixed(2);
    document.getElementById("total").value = totalMovs.toFixed(2);
    document.getElementById("total_factura").textContent = totalMovs.toFixed(2);
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

// Event listener movido a modal-transacciones-universal.js
// document.getElementById('efectivo').addEventListener('input', function(event){
//     calcSaldo();
// })

document.getElementById('idproveedor').addEventListener('blur', function() {
    const idproveedor = this.value;
    console.log('ID Proveedor:', idproveedor);
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
        mostrarAdvertencia('Debe ingresar un pago válido');
        return;
    }

    const confirmado = await confirmar('¿Grabar Orden de pago?');
    if (!confirmado) {
        return;
    }
    
    sinGuardar = false;
        isFormSubmited = true;
    this.submit();
});
 
function generarCheque(){
    const banco = document.getElementById("banco").value;
    const cantCheques = parseInt(document.getElementById("cantCheques").value);
    const vtoChequeInput = document.getElementById("vtoCheque").value;
    const importeCheques = parseFloat(document.getElementById("importeCheques").value);
    const diasEntreCheques = parseInt(document.getElementById("diasCheques").value);

    if (banco == 0){
        mostrarAdvertencia("Debe seleccionar un banco");
        return;
    }
    if (!cantCheques || cantCheques == 0){
        mostrarAdvertencia("Debe ingresar cantidad de cheques");
        return;
    }
    if (!vtoChequeInput){
        mostrarAdvertencia("Debe ingresar fecha de vencimiento");
        return;
    }
    if (!importeCheques || importeCheques == 0){
        mostrarAdvertencia("Debe ingresar importe");
        return;
    }
    if (diasEntreCheques < 1){
        mostrarAdvertencia("Debe ingresar dias entre cheques");
        return;
    }

    const cheques = document.getElementById("cheques");
    cheques.innerHTML = ""; // Limpiar antes de agregar

    let montoCheque = importeCheques / cantCheques;
    let redondeo = Math.round(montoCheque);
    let ultimoCheque;
        
    montoCheque = parseFloat(redondeo);
    
    ultimoCheque = parseFloat((importeCheques) - (montoCheque * cantCheques));
    
    let fechaBase = new Date(vtoChequeInput);
    let totalChequesGenerados = 0;

    for (let i = 0; i < cantCheques; i++){
        // Crear una nueva fecha sumando i meses a la fecha base
        let fechaCheque = new Date(fechaBase);
        
        fechaCheque.setDate(fechaCheque.getDate() + (i * diasEntreCheques));
        
        // Formatear la fecha a yyyy-mm-dd para el input
        let yyyy = fechaCheque.getFullYear();
        let mm = String(fechaCheque.getMonth() + 1).padStart(2, '0');
        let dd = String(fechaCheque.getDate()).padStart(2, '0');
        let fechaFormateada = `${yyyy}-${mm}-${dd}`;
        if (i == cantCheques - 1){
            montoCheque = montoCheque + ultimoCheque;
        }
        totalChequesGenerados += montoCheque;
        cheques.innerHTML += `<tr class="">
                                <td scope="row">${i+1}</td>
                                <td> 
                                  <input class="form-control" type="text" name="cheque[${i+1}][numero]" id="cheque[${i+1}][numero]" required> 
                                  <input type="number" name="cheque[${i+1}][idbanco]" id="cheque[${i+1}][idbanco]" value="${banco}" hidden> 
                                </td>
                                <td> <input class="form-control" type="date" name="cheque[${i+1}][vto]" id="cheque[${i+1}][vto]" value="${fechaFormateada}" required></td>
                                <td> <input class="form-control" type="number" name="cheque[${i+1}][monto]" id="cheque[${i+1}][monto]" step="0.01" value="${montoCheque.toFixed(2)}" required></td>
                            </tr>`;
    }

    const totalCheques = document.getElementById("totalCheques");
    totalCheques.textContent = parseFloat(totalChequesGenerados.toFixed(2));
}

function limpiarCheque(){
    const cheques = document.getElementById("cheques");
    cheques.innerHTML = "";
}
