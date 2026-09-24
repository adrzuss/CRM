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

  // ---- Impuestos del gasto: filas bracket impuesto[i] + totales ----
  const netoInput = document.getElementById('neto');
  if (netoInput) {
    netoInput.addEventListener('input', recalcularTotales);
  }
  const btnAgregarImpuesto = document.getElementById('btnAgregarImpuesto');
  if (btnAgregarImpuesto) {
    btnAgregarImpuesto.addEventListener('click', agregarImpuestoFila);
  }
  // Alta/baja delegadas en el contenedor (las filas se crean y borran en runtime)
  const contenedorImpuestos = document.getElementById('impuestos_rows');
  if (contenedorImpuestos) {
    contenedorImpuestos.addEventListener('click', function (event) {
      const btnQuitar = event.target.closest('[data-quitar-impuesto]');
      if (btnQuitar) {
        btnQuitar.closest('.impuesto-fila').remove();
        renumerarFilasImpuesto();
        recalcularTotales();
      }
    });
  }
  // Estado inicial: #total y #total_factura sincronizados con neto=0
  recalcularTotales();

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

// ---- Impuestos del gasto: alta de filas, renumeración y totales ----
function agregarImpuestoFila() {
  const select = document.getElementById('select_impuesto');
  const contenedor = document.getElementById('impuestos_rows');
  if (!select || !contenedor || !select.value) return;

  const opcion = select.selectedOptions[0];
  const idimpuesto = select.value;
  const alicuota = parseFloat(opcion.dataset.alicuota) || 0;
  const indice = contenedor.querySelectorAll('.impuesto-fila').length;

  const fila = document.createElement('div');
  fila.className = 'impuesto-fila input-group mb-2';
  fila.innerHTML =
    `<span class="input-group-text">${opcion.text}</span>` +
    `<input type="hidden" name="impuesto[${indice}][idimpuesto]" value="${idimpuesto}">` +
    `<input type="hidden" name="impuesto[${indice}][alicuota]" value="${alicuota}">` +
    `<input class="form-control" type="text" name="impuesto[${indice}][importe]" value="0.00" readonly>` +
    `<button class="btn btn-outline-danger" type="button" data-quitar-impuesto title="Quitar impuesto">` +
    `<i class="fas fa-times"></i></button>`;

  contenedor.appendChild(fila);
  select.value = '';
  renumerarFilasImpuesto();
  recalcularTotales();
}

// Reordena los nombres impuesto[i][...] tras altas/bajas, para que el
// servidor reciba índices contiguos 0..n-1
function renumerarFilasImpuesto() {
  document.querySelectorAll('#impuestos_rows .impuesto-fila').forEach((fila, indice) => {
    fila.querySelectorAll('[name]').forEach((campo) => {
      campo.name = campo.name.replace(/\[\d+\]/, `[${indice}]`);
    });
  });
}

// Recalcula importes (neto * alicuota / 100) y sincroniza #total + #total_factura
// El total del cliente es solo visual: el servidor recalcula con la misma fórmula
function recalcularTotales() {
  const netoInput = document.getElementById('neto');
  const totalInput = document.getElementById('total');
  if (!netoInput || !totalInput) return;

  const redondear = (valor) => Math.round(valor * 100) / 100;
  const neto = parseFloat(netoInput.value) || 0;
  let total = neto;

  document.querySelectorAll('#impuestos_rows .impuesto-fila').forEach((fila) => {
    const alicuota = parseFloat(fila.querySelector('input[name$="[alicuota]"]').value) || 0;
    const importe = redondear((neto * alicuota) / 100);
    fila.querySelector('input[name$="[importe]"]').value = importe.toFixed(2);
    total += importe;
  });

  total = redondear(total);
  totalInput.value = total.toFixed(2);
  const totalFactura = document.getElementById('total_factura');
  if (totalFactura) totalFactura.textContent = total.toFixed(2);
}


// Event listeners movidos a modal-transacciones-universal.js
// document.getElementById('efectivo').addEventListener('input', function(event){
//     calcSaldo();
// })

// document.getElementById('ctacte').addEventListener('input', function(event){
//     calcSaldo();
// })
