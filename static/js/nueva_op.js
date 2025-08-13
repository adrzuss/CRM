isFormSubmited = false; // Variable para controlar si el formulario ha sido enviado

window.onbeforeunload = function () {
  if (!isFormSubmited) {
    return "¿Estás seguro de cerrar la Orden de pago sin guardar los cambios?";
  }
};

document.getElementById('idproveedor').focus();


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
    const movsSelect = document.getElementById("movs_select");
    movsSelect.innerHTML = `<ul class='list-group'></ul>`; // Limpiar el select de remitos
    obtener_mov_ctacte(proveedor.id);
}
  
async function obtener_mov_ctacte(idproveedor) { 
    const response = await fetch(`${BASE_URL}/proveedores/get_movs_ctacte/${idproveedor}`);
    const data = await response.json();
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
            option.innerHTML = `<input class="form-check-input me-1" type="checkbox" id="checkbox${index}" name="mov_cc[${index}][check]" onClick="calcularTotal()" >
                                <label class="form-check-label" for="firstCheckbox">${dia}/${mes}/${anio} - Comprobante: ${movs.tipo_comprobante} / ${movs.nro_comprobante} - Saldo $${saldo.toFixed(2)}</label>
                                <input type="hidden" name="mov_cc_saldo[${index}][id]" id="mov_cc_saldo[${index}][id]" value="${saldo}">
                                <input type="hidden" name="mov_cc_id[${index}][id]" value="${movs.id}">`;
            movsSelect.appendChild(option);
        });
        movsSelect.style.display = "block"; // Mostrar el select de remitos
    }
    
}

function calcularTotal(){
    const listodoMovs = document.getElementById("movs_select");
    const movs = listodoMovs.querySelectorAll("input[type=checkbox]:checked");
    if (movs.length == 0){
        document.getElementById("total_movs").textContent = 0;
        return;
    }
    let totalMovs = 0;
    movs.forEach((item) => {
        index = item.name.split('[')[1].split(']')[0];
        const saldo = document.getElementById("mov_cc_saldo[" + index + "][id]").value;
        totalMovs += parseFloat(saldo);
    });
    document.getElementById("total").value = totalMovs.toFixed(2);
    document.getElementById("total_factura").textContent = totalMovs.toFixed(2);
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
    let diferencia = (totalFac - (efectivo));
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
    const efectivo = parseFloat(document.getElementById('efectivo').value);
    const cheques = document.querySelectorAll('#cheques input[name$="[monto]"]');
    console.log(cheques);
    document.getElementById('total').value = efectivo;
    let totalCheques = 0;
    cheques.forEach((cheque) => {
        totalCheques += parseFloat(cheque.value);
    });
    console.log('Total cheques: ' + totalCheques);
    if (efectivo + totalCheques > 0){
        return true;
    }
    else{
        return false;
    }
    
}

document.getElementById('efectivo').addEventListener('input', function(event){
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
        return;
    }   
    
    if (checkTotales() == false){
        event.preventDefault();
        alert('Debe ingresar un pago válido');
        return;
    }

    if (confirm('¿Grabar Orden de pago?') == false) {
        event.preventDefault();
    }
    else{
        isFormSubmited = true;
    }
});
 
function generarCheque(){
    const banco = document.getElementById("banco").value;
    const cantCheques = parseInt(document.getElementById("cantCheques").value);
    const vtoChequeInput = document.getElementById("vtoCheque").value;
    const importeCheques = parseFloat(document.getElementById("importeCheques").value);
    const diasEntreCheques = parseInt(document.getElementById("diasCheques").value);

    if (banco == 0){
        alert("Debe seleccionar un banco");
        return;
    }
    if (!cantCheques || cantCheques == 0){
        alert("Debe ingresar cantidad de cheques");
        return;
    }
    if (!vtoChequeInput){
        alert("Debe ingresar fecha de vencimiento");
        return;
    }
    if (!importeCheques || importeCheques == 0){
        alert("Debe ingresar importe");
        return;
    }
    if (diasEntreCheques < 1){
        alert("Debe ingresar dias entre cheques");
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
