// ✅ VERSION ACTUALIZADA - Nueva Venta JS v2.0 - Fix label-ctacte
import InvoiceHandler from './invoice_handler.js';

console.log("🚀 Nueva Venta JS cargado - Versión corregida 2.0");

let isFormSubmited = false;
let contadorFilas = 0;
let articulosFacturados = [];
let ofertasDeCierre = [];

window.onbeforeunload = function () {
  if (!isFormSubmited) {
    return "¿Estás seguro de cerrar la venta sin guardar los cambios?";
  }
};

// Función para asegurar que todas las filas tengan campos de color y detalle
function ensureColorDetalleFields() {
  const rows = document.querySelectorAll("#tabla-items tbody tr");
  console.log('🔍 [ensureColorDetalleFields] Verificando campos en', rows.length, 'filas');
  
  rows.forEach((row, index) => {
    const firstCell = row.querySelector("td.id-articulo");
    if (firstCell) {
      // Verificar si ya tiene los campos
      let colorInput = row.querySelector('[name*="id_color"]');
      let detalleInput = row.querySelector('[name*="id_detalle"]');
      
      console.log(`📋 Fila ${index} - Color input existe:`, !!colorInput, 'Detalle input existe:', !!detalleInput);
      
      if (!colorInput) {
        colorInput = document.createElement('input');
        colorInput.type = 'hidden';
        colorInput.name = `items[${index}][id_color]`;
        colorInput.value = '0';
        colorInput.setAttribute('data-debug', 'auto-created-color');
        colorInput.setAttribute('data-row', index.toString());
        firstCell.appendChild(colorInput);
        console.log('✅ Campo id_color agregado a fila', index, 'con nombre:', colorInput.name);
        
        // Verificar que realmente se agregó
        const verificacion = row.querySelector('[name*="id_color"]');
        console.log('🔬 Verificación inmediata - Campo agregado:', !!verificacion);
      } else {
        console.log('✨ Campo color existe con nombre:', colorInput.name, 'y valor:', colorInput.value);
      }
      
      if (!detalleInput) {
        detalleInput = document.createElement('input');
        detalleInput.type = 'hidden';
        detalleInput.name = `items[${index}][id_detalle]`;
        detalleInput.value = '0';
        detalleInput.setAttribute('data-debug', 'auto-created-detalle');
        detalleInput.setAttribute('data-row', index.toString());
        firstCell.appendChild(detalleInput);
        console.log('✅ Campo id_detalle agregado a fila', index, 'con nombre:', detalleInput.name);
        
        // Verificar que realmente se agregó
        const verificacion = row.querySelector('[name*="id_detalle"]');
        console.log('🔬 Verificación inmediata - Campo agregado:', !!verificacion);
      } else {
        console.log('✨ Campo detalle existe con nombre:', detalleInput.name, 'y valor:', detalleInput.value);
      }
    }
  });
  
  // Verificación final con más detalle
  const allColorInputs = document.querySelectorAll('[name*="id_color"]');
  const allDetalleInputs = document.querySelectorAll('[name*="id_detalle"]');
  console.log('📊 Total campos color encontrados:', allColorInputs.length);
  console.log('📊 Total campos detalle encontrados:', allDetalleInputs.length);
  
  // Debug adicional: mostrar todos los campos encontrados
  allColorInputs.forEach((input, i) => {
    console.log(`  🎨 Color ${i}: name="${input.name}" value="${input.value}" data-debug="${input.getAttribute('data-debug')}"`);
  });
  allDetalleInputs.forEach((input, i) => {
    console.log(`  📝 Detalle ${i}: name="${input.name}" value="${input.value}" data-debug="${input.getAttribute('data-debug')}"`);
  });
}

document.addEventListener("DOMContentLoaded", async function () {
  document.getElementById('idcliente').focus();
  try {
    // Realizar la solicitud a la API
    const response = await fetch(`${BASE_URL}/ventas/get_punto_vta`);	
    const data = await response.json(); 
    // Verificar el valor de punto_vta
    if (data.success == false) {
      console.log("Error al obtener el punto de venta:", data.message);
      return;
    }  
    if (!data.punto_vta || data.punto_vta == 0) {
      // Si punto_vta es null o no está definido, mostrar el modal
      const ptosVtasSucursal = await fetch(`${BASE_URL}/ventas/get_puntos_vta_sucursal`);
      const datos = await ptosVtasSucursal.json(); 
      if (datos.length == 1) {
        asignarPuntoVenta(datos[0].id);
      }
      else{
        saleccionarPtoVta(datos);
      }  
    }
    else{
      // Si punto_vta tiene un valor, asignarlo al input
      document.getElementById("punto_vta").textContent = 'Punto de venta: ' + data.punto_vta;
      document.getElementById("ptovta_seleccionado").value = data.punto_vta;
      document.getElementById("fac_electronica").value = data.fac_electronica ? 'true' : 'false';
      document.getElementById("pos_printer").value = data.pos_printer || '';
    }
  } catch (error) {
    console.log("Error al obtener el punto de venta:", error);
  }

  // Si hay datos de presupuesto, precargar
  if (window.PRESUPUESTO) {
    // Cargar cabecera
    let cabecera = document.getElementById("cabecera");
    if (!cabecera.querySelector("#idPresupuestoContainer")) {
      cabecera.innerHTML += `<div class="m-2 col-2" id="idPresupuestoContainer">
                                <h4 class="idPresupuestoLabel" >#Presupuesto: ${window.PRESUPUESTO.id} </h4>
                                <input class="form-control" type="number" name="idPresupuesto" id="idPresupuesto" value="${window.PRESUPUESTO.id}" hidden>
                              </div>`;

    }
    else {
      let idPresupuestoLabel = document.getElementById("idPresupuestoLabel");
      idPresupuestoLabel.innerText = 'Presupuesto: ' + window.PRESUPUESTO.id;
      let idPresupuesto = document.getElementById("idPresupuesto");
      idPresupuesto.value = window.PRESUPUESTO.id;
    }
    document.getElementById("idcliente").value = window.PRESUPUESTO.idcliente;
    document.getElementById("totalFactura").value = window.PRESUPUESTO.total;
    
    // Podés llamar a fetchCliente para completar el resto de los datos del cliente
    fetchCliente(window.PRESUPUESTO.idcliente);

    // Cargar artículos
    window.PRESUPUESTO.articulos.forEach(art => {
      // Simular click en "Agregar artículo"
      document.getElementById("agregarArticulo").click();
      // Buscar la última fila agregada
      const fila = tablaItems.querySelector("tr:last-child");
      fila.querySelector(".id-articulo").textContent = art.idarticulo;
      fila.querySelector(".codigo-articulo").value = art.codigo;
      fila.querySelector(".precio-unitario").value = art.precio_unitario;
      fila.querySelector(".cantidad").value = art.cantidad;
      // Calcular el total
      fila.querySelector(".precio-total").value = (art.precio_unitario * art.cantidad).toFixed(2);
    });
    updateTotalFactura();
    
    // Asegurar que todas las filas tengan campos de color/detalle
    setTimeout(ensureColorDetalleFields, 100);
  }

  // Si hay datos de remito, precargar
  if (window.REMITO) {
    // Cargar cabecera
    let cabecera = document.getElementById("cabecera");
    if (!cabecera.querySelector("#idRemitoContainer")) {
      cabecera.innerHTML += `<div class="m-2 col-2" id="idRemitoContainer">
                                <h4 class="idRemitoLabel" >#Remito: ${window.REMITO.id} </h4>
                                <input class="form-control" type="number" name="idRemito" id="idRemito" value="${window.REMITO.id}" hidden>
                              </div>`;

    }
    else {
      let idRemitoLabel = document.getElementById("idRemitoLabel");
      idRemitoLabel.innerText = 'Remito: ' + window.REMITO.id;
      let idRemito = document.getElementById("idRemito");
      idRemito.value = window.REMITO.id;
    }
    document.getElementById("idcliente").value = window.REMITO.idcliente;
    document.getElementById("totalFactura").value = window.REMITO.total;
    
    // Podés llamar a fetchCliente para completar el resto de los datos del cliente
    fetchCliente(window.REMITO.idcliente);

    // Cargar artículos
    window.REMITO.articulos.forEach(art => {
      // Simular click en "Agregar artículo"
      document.getElementById("agregarArticulo").click();
      // Buscar la última fila agregada
      const fila = tablaItems.querySelector("tr:last-child");
      fila.querySelector(".id-articulo").textContent = art.idarticulo;
      fila.querySelector(".codigo-articulo").value = art.codigo;
      fila.querySelector(".precio-unitario").value = art.precio_unitario;
      fila.querySelector(".cantidad").value = art.cantidad;
      // Calcular el total
      fila.querySelector(".precio-total").value = (art.precio_unitario * art.cantidad).toFixed(2);
    });
    updateTotalFactura();
  }
});

document.getElementById("cambiar_pto_vta").addEventListener("click", async function () {
  const ptosVtasSucursal = await fetch(`${BASE_URL}/ventas/get_puntos_vta_sucursal`);
  const datos = await ptosVtasSucursal.json(); 
  if (datos.length == 1) {
    asignarPuntoVenta(datos[0].id);
  }
  else{
    saleccionarPtoVta(datos);
  }    
});

function saleccionarPtoVta(datos) {
  const modalContent = document.getElementById("modalContentPtoVta");
        
  const listaPtosVtasSucursal = document.createElement("select");
  listaPtosVtasSucursal.classList.add("form-select"); // Agregar clases de Bootstrap
  listaPtosVtasSucursal.id = "selectPtoVta"; // Asignar un ID para referencia futura
  
  // Agregar una opción por defecto
  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "Seleccione un punto de venta";
  defaultOption.disabled = true;
  defaultOption.selected = true;
  listaPtosVtasSucursal.appendChild(defaultOption);

  // Recorrer los puntos de venta y agregarlos como opciones
  datos.forEach((ptovta) => {
    const ptoVtaOption = document.createElement("option");
    ptoVtaOption.value = ptovta.id; // Asignar el ID como valor
    ptoVtaOption.textContent = "Punto de venta: " + ptovta.puntoVta + " - Fac. Electrónica: " + ptovta.facElectronica; // Mostrar el nombre del punto de venta
    listaPtosVtasSucursal.appendChild(ptoVtaOption);
    
  });
  
  // Agregar el <select> al modal
  modalContent.appendChild(listaPtosVtasSucursal);

  // Agregar un botón para confirmar la selección
  const confirmButton = document.createElement("button");
  confirmButton.classList.add("btn", "btn-primary", "mt-3");
  confirmButton.textContent = "Confirmar";
  confirmButton.onclick = async function () {
    const selectedPtoVta = listaPtosVtasSucursal.value;
    if (selectedPtoVta) {
      asignarPuntoVenta(selectedPtoVta);
    } else {
      alert("Debe seleccionar un punto de venta.");
    }
  };
  modalContent.appendChild(confirmButton);
  //---------
  $("#ptovtaModal").modal("show");
}

function abrirModalPagos(){
  //Calcular ofertas de cierre
  calcularOfetasDeCierre();
  
  // Configurar total antes de abrir modal
  const totalElement = document.getElementById('totalFactura');
  const totalFactura = totalElement ? (totalElement.value || totalElement.textContent) : '0';
  
  // Usar la función universal cargarDatosModal
  if (window.cargarDatosModal) {
    window.cargarDatosModal(parseFloat(totalFactura) || 0);
  } else {
    console.error('❌ cargarDatosModal no está disponible');
  }
  
  $("#transaccionesModal").modal("show");
  
  // Cuando el modal se haya mostrado completamente
  document.getElementById('transaccionesModal').addEventListener('shown.bs.modal', function () {
    // Aplicar crédito pendiente si existe
    if (window.creditoPendienteAplicar) {
      console.log('💳 Aplicando crédito pendiente al modal de pagos...');
      setTimeout(() => {
        const aplicado = aplicarCreditoEnModal();
        if (aplicado) {
          console.log('✅ Crédito aplicado automáticamente en el modal');
        }
      }, 200); // Pequeño delay para asegurar que el DOM esté listo
    }
    
    // Enfocar el input apropiado
    const primerInput = document.querySelector('#transaccionesModal input:not([readonly]):not([type="hidden"])');
    if (primerInput && !window.creditoPendienteAplicar) {
      primerInput.focus();
    } else if (window.creditoPendienteAplicar) {
      // Si hay crédito aplicado, enfocar el campo de efectivo o el siguiente disponible
      const efectivoInput = document.querySelector('#efectivo, [name="efectivo"]');
      if (efectivoInput) {
        setTimeout(() => efectivoInput.focus(), 300);
      }
    }
  }, { once: true });

  // Asegurar que todas las filas existentes tengan campos de color/detalle
  setTimeout(ensureColorDetalleFields, 500);
}

// Hacer funciones disponibles globalmente
window.abrirModalPagos = abrirModalPagos;
window.procesarTransaccion = procesarTransaccion;

// Función personalizada para procesar transacción en nueva venta
function procesarTransaccion() {
    console.log('procesarTransaccion() llamada para nueva venta');
    
    // Usar la validación del modal universal
    if (!checkTotales()) {
        const diferencia = calcSaldo();
        const mensaje = diferencia > 0 ? 
            `Falta pagar $${diferencia.toFixed(2)}` : 
            `Sobra $${Math.abs(diferencia).toFixed(2)}`;
        
        if (!confirm(`${mensaje}. ¿Desea continuar de todas formas?`)) {
            return false;
        }
    }
    
    console.log('Cerrando modal y grabando venta...');
    
    // Cerrar modal
    $('#transaccionesModal').modal('hide');
    
    // Enviar formulario via AJAX para grabar la venta
    console.log('Enviando formulario de venta via AJAX...');
    const form = document.getElementById('invoice_form');
    if (!form) {
        console.error('Formulario invoice_form no encontrado');
        alert('Error: No se pudo grabar la venta. Formulario no encontrado.');
        return false;
    }
    
    // Preparar datos del formulario
    const formData = new FormData(form);
    
    // Mostrar loading
    const originalText = 'Grabando venta...';
    
    let url = form.action || window.location.href;
    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
        
        if (data.success) {
            // Verificar si tiene facturación electrónica e impresora POS
            const tieneFacElectronica = document.getElementById('fac_electronica')?.value === 'true';
            const posPrinter = document.getElementById('pos_printer')?.value || '';
            const facturaId = data.id;
            const ptoVta = document.getElementById('ptovta_seleccionado')?.value || '1';
            
            // Mostrar modal de confirmación de impresión (siempre)
            document.getElementById('facturaIdConfirmacion').textContent = facturaId;
            
            const modalConfirmar = new bootstrap.Modal(document.getElementById('modalConfirmarImpresion'));
            modalConfirmar.show();
            
            // Bandera para controlar si ya se procesó con un botón
            let botonProcesado = false;
            
            // Manejar botón de imprimir
            document.getElementById('btnSiImprimir').onclick = async function() {
                botonProcesado = true;
                modalConfirmar.hide();
                // Mostrar spinner mientras se procesa
                document.getElementById('spinner').style.display = 'flex';
                
                try {
                    if (tieneFacElectronica) {
                        // Solo llamar a facturar_venta si tiene facturación electrónica
                        const response = await fetch(`${BASE_URL}/ventas/facturar_venta/${ptoVta}/${facturaId}`);
                        const result = await response.json().catch(() => null);
                        
                        if (!result || !result.success) {
                            console.warn('Advertencia al facturar electrónicamente:', result?.message || 'Error desconocido');
                        }
                    }
                    
                    // Imprimir según el tipo de impresora
                    if (posPrinter) {
                        // Usar impresora POS (formato ticket térmico via navegador)
                        console.log('-----------------------------------------------');
                        console.log('Intentando imprimir factura en POS para factura ID:', facturaId, 'en punto de venta:', ptoVta);
                        console.log('-----------------------------------------------');
                        const invoiceHandler = new InvoiceHandler();
                        console.log('Se creo el objeto de impresion');
                        invoiceHandler.setPrinterType('pos');
                        console.log('Se seteo el tipo de impresora a POS');
                        const printResult = await invoiceHandler.printInvoice(facturaId);
                        console.log('Se envió la factura a imprimir en POS, resultado:', printResult);
                        console.log('-----------------------------------------------');
                        if (!printResult || !printResult.success) {
                            console.warn('Error en impresión POS:', printResult?.error || 'Error desconocido');
                            // Fallback a PDF
                            window.open(`${BASE_URL}/ventas/imprimir_factura_vta/${facturaId}`, '_blank');
                        }
                    } else {
                        // Abrir el PDF de la factura en nueva pestaña
                        window.open(`${BASE_URL}/ventas/imprimir_factura_vta/${facturaId}`, '_blank');
                    }
                } catch (error) {
                    console.error('Error al procesar:', error);
                    // Intentar abrir PDF de todas formas
                    window.open(`${BASE_URL}/ventas/imprimir_factura_vta/${facturaId}`, '_blank');
                } finally {
                    document.getElementById('spinner').style.display = 'none';
                }
                
                limpiarFormularioVenta();
            }

            // Manejar botón de no imprimir
            document.getElementById('btnNoImprimir').onclick = function() {
              botonProcesado = true;
              console.log('Usuario optó por no imprimir. Limpiando formulario...');
              modalConfirmar.hide();
              imprimirRemitoVenta(facturaId);
            }
                    
                        
            // Solo ejecutar si se cerró con X o click fuera (no con los botones)
            document.getElementById('modalConfirmarImpresion').addEventListener('hidden.bs.modal', function () {
                if (!botonProcesado) {
                    console.log('Modal cerrado con X o click fuera. Limpiando formulario...');
                    imprimirRemitoVenta(facturaId);
                }
            }, { once: true });
            
        } else {
            alert(`❌ Error: ${data.message || 'No se pudo grabar la venta'}`);
        }
    })
    .catch(error => {
        console.error('Error al grabar venta:', error);
        alert('❌ Error de conexión al grabar la venta (Mensaje' + error.message + ' - Detalle: ' + error.error_detalle + '). URL: ' + url);
        
    });
    
    return true;
}

/**
 * Función para imprimir el remito de la venta
**/

async function imprimirRemitoVenta(facturaId) {
  console.log('-----------------------------------------------');
  console.log('Intentando imprimir remito para factura ID:', facturaId);
  console.log('-----------------------------------------------');
  if (posPrinter) {
    // Usar impresora POS (formato ticket térmico via navegador)
    const invoiceHandler = new InvoiceHandler();
    invoiceHandler.setPrinterType('pos');
    const printResult = await invoiceHandler.printDelivery(facturaId);
    
    if (!printResult || !printResult.success) {
        console.warn('Error en impresión POS:', printResult?.error || 'Error desconocido');
        // Fallback a PDF
        window.open(`${BASE_URL}/ventas/imprimir_factura_vta/${facturaId}`, '_blank');
    }
  } else {
    // Abrir el PDF de la factura en nueva pestaña
    window.open(`${BASE_URL}/ventas/imprimir_factura_vta/${facturaId}`, '_blank');
  }
  limpiarFormularioVenta();
}              

/**
 * Limpia el formulario de venta para preparar una nueva operación
 */
function limpiarFormularioVenta() {
    const form = document.getElementById('invoice_form');
    if (form) {
        form.reset();
    }
    
    // Limpiar tabla de artículos
    const tbody = document.querySelector('#tabla-items tbody');
    if (tbody) {
        tbody.innerHTML = '';
    }
    
    // Resetear total
    const totalFactura = document.getElementById('totalFactura');
    if (totalFactura) {
        totalFactura.value = '0';
    }
    
    // Resetear total visual si existe
    const totalVisual = document.getElementById('total-factura-visual');
    if (totalVisual) {
        totalVisual.textContent = '$0.00';
    }
    
    // Limpiar cliente
    const idcliente = document.getElementById('idcliente');
    if (idcliente) {
        idcliente.value = '';
    }
    
    const idInput = document.getElementById('id');
    if (idInput) {
        idInput.value = '';
    }
}

async function calcularOfetasDeCierre(){
  articulosFacturados = [];
  const filas = document.querySelectorAll("#tabla-items tbody tr");
  let totalFactura = 0;
  filas.forEach((fila) => {
    const idofertaInput = fila.querySelector(".idoferta").value;
    const idoferta = parseInt(idofertaInput);
    if (idoferta === 0) {
      const precio = fila.querySelector(".precio-unitario");
      const idArticulo = fila.querySelector(".id-articulo").textContent;
      const idMarca = fila.querySelector(".id-marca").textContent;
      const idRubro = fila.querySelector(".id-rubro").textContent;
      const cantidadInput = fila.querySelector(".cantidad").value;
      const cantidad = parseInt(cantidadInput);
      
      articulosFacturados.push({id: idArticulo, idmarca: idMarca, idrubro: idRubro, cantidad: cantidad, precio: precio.value});
    }  
  });
  try{                                                
    const response = await fetch(`${BASE_URL}/ofertas/calcular_ofertas_de_cierre`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ articulos: articulosFacturados })
    });
    if (response.ok){
      const data = await response.json();
      let totalOfeta = 0.0;
      ofertasDeCierre = []
      for (const oferta of data) {
        totalOfeta += parseFloat(oferta.precio);
        //arma el arreglo de ofertas para cargarlo a la venta
        ofertasDeCierre.push(oferta);
      }
      document.getElementById("ofertas_especiales").value = totalOfeta.toFixed(2);
    }else{
      console.error("Error al calcular ofertas de cierre:", response.statusText);
    }
  }
  catch(error){ 
    console.error("Error al calcular ofertas de cierre:", error);
  }

}

async function asignarPuntoVenta(idPuntoVenta) {
  try {
    // Llamar a la API para asignar el punto de venta a la sesión
    const response = await fetch(`${BASE_URL}/ventas/set_punto_vta`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ punto_vta_id: idPuntoVenta}),
    });

    const result = await response.json();
    if (result.success) {
      $("#ptovtaModal").modal("hide");
      // Actualizar el texto en la página con el punto de venta seleccionado
      document.getElementById("punto_vta").textContent = 'Punto de venta: ' + idPuntoVenta;
      document.getElementById("posPrinter").textContent = 'Pos: ' + result.posPrinter;
      document.getElementById("facElectronica").textContent = 'Fac. Electrónica: ' + (result.facElectronica ? 'Sí' : 'No');
      // Guardar el ID del punto de venta en el input hidden
      document.getElementById("ptovta_seleccionado").value = idPuntoVenta;
      // Guardar si tiene facturación electrónica
      document.getElementById("fac_electronica").value = result.facElectronica ? 'true' : 'false';
      // Guardar la impresora POS si existe
      document.getElementById("pos_printer").value = result.posPrinter || '';
      document.getElementById("idcliente").focus();
    } else {
      alert('Error al asignar el punto de venta: ' + result.message);
    }
  } catch (error) {
    console.error('Error al llamar a la API:', error);
    alert('Ocurrió un error al asignar el punto de venta.');
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("invoice_form");
  const btnAgregar = document.getElementById("agregarArticulo");
  const btnGrabar = document.getElementById("grabarVenta");

  // Detectar tecla Enter en los inputs del formulario
  form.addEventListener("keydown", async function (event) {
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
    // Asignar tecla F4 para agregar un nuevo artículo
    if (event.key === "F4") {
      event.preventDefault(); // Evita la recarga de página con F5
      btnAgregar.click(); // Simula un click en el botón "Agregar Artículo"
    }
    // F8: Abrir modal de pagos
    if (event.key === "F8") {
      event.preventDefault();
      // Si el elemento activo es un input codigo-articulo
      if (document.activeElement.classList.contains("codigo-articulo")) {
        // Esperar a que se complete el blur antes de abrir el modal
        await handleArticuloBlur({target: document.activeElement});
      }
      abrirModalPagos();
    }

    // Atajos de teclado en modal de formas de pago
    // Verifica si la modal está visible
    if (document.getElementById('transaccionesModal').classList.contains('show')) {
        // Alt + E para Efectivo
        if (event.altKey && event.key.toLowerCase() === 'e') {
            event.preventDefault();
            const efectivoTab = document.querySelector('[data-bs-target="#pago-efectivo"]');
            //const efectivoTab = document.getElementById('efectivo-tab');
            const tab = new bootstrap.Tab(efectivoTab);
            tab.show();
            activarDatosTab('pago-efectivo');
            document.getElementById('efectivo').focus();
        }
        // Alt + T para Tarjetas
        if (event.altKey && event.key.toLowerCase() === 't') {
            event.preventDefault();
            const tarjetasTab = document.querySelector('[data-bs-target="#pago-tarjetas"]');
            //const tarjetasTab = document.getElementById('tarjetas-tab');
            const tab = new bootstrap.Tab(tarjetasTab);
            tab.show();
            activarDatosTab('pago-tarjetas');
            document.getElementById('entidad').focus();
        }
        // Alt + C para Cuenta corriente
        if (event.altKey && event.key.toLowerCase() === 'c') {
            event.preventDefault();
            const ctacteTab = document.querySelector('[data-bs-target="#pago-ctacte"]');
            //const ctacteTab = document.getElementById('ctacte-tab');
            const tab = new bootstrap.Tab(ctacteTab);
            tab.show();
            activarDatosTab('pago-ctacte');
            document.getElementById('ctacte').focus();
        }
        // Alt + R para Creditos
        if (event.altKey && event.key.toLowerCase() === 'r') {
            event.preventDefault();
            const creditoTab = document.querySelector('[data-bs-target="#pago-credito"]');
            //const creditoTab = document.getElementById('credito-tab');
            const tab = new bootstrap.Tab(creditoTab);
            tab.show();
            activarDatosTab('pago-credito');
            document.getElementById('idcredito').focus();
        }
        // Alt + B para Bonificacion
        if (event.altKey && event.key.toLowerCase() === 'b') {
            event.preventDefault();
            const bonificacionTab = document.querySelector('[data-bs-target="#pago-bonificacion"]');
            //const bonificacionTab = document.getElementById('bonificacion-tab');
            const tab = new bootstrap.Tab(bonificacionTab);
            tab.show();
            activarDatosTab('pago-bonificacion');
            document.getElementById('bonificacion').focus();
        }
        // Puedes agregar más atajos siguiendo el mismo patrón
    }
    
  });
});


document.querySelector('[data-bs-target="#pago-efectivo"]').addEventListener('click', function() {
  document.getElementById('efectivo').focus();
});

document.querySelector('[data-bs-target="#pago-tarjetas"]').addEventListener('click', function() {
  document.getElementById('entidad').focus();
});

document.querySelector('[data-bs-target="#pago-ctacte"]').addEventListener('click', function() {
  document.getElementById('ctacte').focus();
});

document.querySelector('[data-bs-target="#pago-credito"]').addEventListener('click', function() {
  document.getElementById('idcredito').focus();
});

document.querySelector('[data-bs-target="#pago-bonificacion"]').addEventListener('click', function() {
  document.getElementById('bonificacion').focus();
});


function activarDatosTab(tabClass){
  const tabs = document.querySelectorAll(".tab-pane");
  tabs.forEach(t => {
    t.classList.remove('show')
    t.classList.remove('active');
  });
  document.getElementById(tabClass).classList.add('show');
  document.getElementById(tabClass).classList.add('active');
}

function limpiarDatosCliente() {
  inputIdCliente = document.getElementById("idcliente");
  inputIdCliente.value = "";
  inputIdCliente.focus();
}

async function fetchCliente(input) {
  let response;

  // Determinar si la entrada es un ID numérico o un nombre
  if (input != ""){
    if (!isNaN(input)) {
      // Si es un número, buscar por ID
      response = await fetch(`${BASE_URL}/clientes/get_cliente/${input}/${1}`); //1 venta
    } else {
      // Si es un nombre parcial, buscar por nombre
      response = await fetch(`${BASE_URL}/clientes/get_clientes?nombre=${input}&&tipo_operacion=${1}`);
    }

    if (!response.ok) {
      console.error("Error en la búsqueda del cliente");
      return;
    }
    const data = await response.json();

    if (data.success) {
      if (data.cliente) {
        // Si se encuentra un cliente por ID, asignarlo directamente
        if (data.cliente.baja == true) {
          limpiarDatosCliente();
          alert("Cliente dado de baja. No puedes facturar a este cliente.");
          return;
        }
        asignarCliente(data.cliente);
      } else {
        alert("No se encontraron clientes con ese ID.");
      }
    } else {
      if (data.length > 1) {
        // Si hay más de un resultado, mostrar un modal para seleccionar
        mostrarModalSeleccionClientes(data);
      } else if (data.length === 1) {
        // Si hay un solo resultado, asignar directamente
        asignarCliente(data[0]);
      } else {
        limpiarDatosCliente
        alert("No se encontraron clientes con ese nombre.");
      }
    }
  }  
}

function mostrarModalSeleccionClientes(clientes) {
  // Usar el sistema universal de modal de búsqueda
  const callback = (cliente) => {
    asignarCliente(cliente);
    // Enfocar el nuevo input de código
    const clienteInput = document.getElementById("idcliente");
    if (clienteInput) clienteInput.focus();
  };
  
  // Mostrar modal con los datos
  window.universalSearchModal.show('clientes', clientes || [], callback);
}

function asignarCliente(cliente) {
  console.log("🎯 Asignando cliente:", cliente);
  
  // Función auxiliar para actualizar elementos de forma segura
  const updateElement = (id, property, value) => {
    const element = document.getElementById(id);
    if (element) {
      element[property] = value;
    } else {
      console.warn(`⚠️ Elemento '${id}' no encontrado en el DOM`);
    }
  };

  // Actualizar campos del cliente con validación
  updateElement("idcliente", "value", cliente.id);
  updateElement("cliente_nombre", "value", cliente.nombre);
  updateElement("id", "value", cliente.id);
  updateElement("id_tipo_comprobante", "value", cliente.id_tipo_comprobante);
  
  // Manejar campo ctacte con validación
  const ctacteElement = document.getElementById("ctacte");
  if (ctacteElement) {
    ctacteElement.readOnly = cliente.ctacte == 0;
  }
  
  // Manejar tipo de comprobante con validación
  const tipoComprobanteElement = document.getElementById("tipo_comprobante");
  if (tipoComprobanteElement) {
    tipoComprobanteElement.innerText = "Tipo de factura: " + cliente.tipo_comprobante;
  }
  
  // Actualizar label de cuenta corriente con validación de seguridad
  const labelCtacte = document.getElementById("label-ctacte");
  if (labelCtacte) {
    if (cliente.ctacte == 0) {
      labelCtacte.innerText = "Cta. Cte. - Cliente sin cta. cte.";
    } else {
      labelCtacte.innerText = "Cta. Cte.";
    }
  }
  
  // Verificar si el cliente tiene crédito disponible
  console.log("🔍 Verificando crédito para cliente:", cliente.id);
  try {
    hayCredito(cliente.id);
  } catch (error) {
    console.error("❌ Error al verificar crédito:", error);
  }
}

async function fetchArticulo(id, idlista, itemDiv) {
  let response;
  if (!isNaN(id)) {
    response = await fetch(`${BASE_URL}/articulos/articulo/${id}/${idlista}`);
  } else {
    response = await fetch(`${BASE_URL}/articulos/articulo/${id}/${idlista}`);
    if (!response.ok) {
        response = await fetch(`${BASE_URL}/articulos/get_articulos?detalle=${id}&idlista=${idlista}`);
    }    
  }
  
  if ((!response.ok)&&(id!="")) {
    const nuevoInputCodigo = tablaItems.querySelector(`tr:last-child .codigo-articulo`);
    nuevoInputCodigo.value = "";
    nuevoInputCodigo.focus();
    alert("Error en la búsqueda de artículos");
    return;
  }
  //const data = await response.json();
  const data = await response.json();
  
  if (data.success) {
    if (data.articulo && data.articulo.baja == true) {
      // Artículo dado de baja
      alert("El artículo está dado de baja.");
      return;
    }

    if (data.articulo) {
      asignarArticulo(data.articulo, itemDiv);
    } else {
      alert("No se encontraron articulos con ese ID.");
    }
  } else {
    if (data.length > 1) {
      // Si hay más de un resultado, mostrar un modal para seleccionar
      mostrarModalSeleccionArticulos(data, idlista, itemDiv);
    } else if (data.length === 1) {
      // Si hay un solo resultado, asignar directamente
      response = await fetch(`${BASE_URL}/articulos/articulo/${data[0].codigo}/${idlista}`);
      if (response.ok) {
        result = await response.json();
        asignarArticulo(result.articulo, itemDiv);
        
      } else {
        response.catch((err) => {
          console.error("Error al buscar artículo:", err);
        });
      }
        
      //asignarArticuloElegido(data[0], itemDiv);
    } else {
      alert("No se encontraron articulos con ese detalle.");
    }
  }
}

function asignarArticuloElegido(articulo, itemDiv) {
  itemDiv.target.closest("tr").querySelector(".codigo-articulo").value = articulo.codigo;
  asignarArticulo(articulo, itemDiv);
}

function asignarArticulo(articulo, itemDiv) {
  const row = itemDiv.target.closest("tr");
  
  row.querySelector(".id-articulo").textContent = articulo.id;
  row.querySelector(".id-marca").textContent = articulo.idmarca;
  row.querySelector(".id-rubro").textContent = articulo.idrubro;
  row.querySelector(".codigo-articulo").value = articulo.codigo;
  row.querySelector(".idoferta").value = articulo.idoferta;
  row.querySelector(".descripcion-articulo").textContent = articulo.detalle;
  
  // Activar modal de color/detalle si está disponible
  function tryShowModal() {
    if (window.modalColorDetalleManager && articulo.id) {
      const rowIndex = Array.from(tablaItems.querySelectorAll('tr')).indexOf(row);
      
      window.modalColorDetalleManager.mostrarModal(
        articulo.id,
        rowIndex,
        articulo.detalle,
        function(seleccion) {
          // Asegurar que existan los campos hidden
          ensureColorDetalleFields();
          
          // Buscar campos hidden
          let colorInput = row.querySelector('input[name*="id_color"]');
          let detalleInput = row.querySelector('input[name*="id_detalle"]');
          
          // Si no se encuentran, crearlos
          if (!colorInput || !detalleInput) {
            const firstCell = row.querySelector("td.id-articulo");
            if (firstCell) {
              if (!colorInput) {
                colorInput = document.createElement('input');
                colorInput.type = 'hidden';
                colorInput.name = `items[${seleccion.rowIndex}][id_color]`;
                colorInput.value = '0';
                firstCell.appendChild(colorInput);
              }
              
              if (!detalleInput) {
                detalleInput = document.createElement('input');
                detalleInput.type = 'hidden';
                detalleInput.name = `items[${seleccion.rowIndex}][id_detalle]`;
                detalleInput.value = '0';
                firstCell.appendChild(detalleInput);
              }
            }
          }
          
          // Asignar valores seleccionados
          if (colorInput && seleccion.colorId) {
            colorInput.value = seleccion.colorId;
          }
          
          if (detalleInput && seleccion.detalleId) {
            detalleInput.value = seleccion.detalleId;
          }
          
          if (colorInput) {
            colorInput.value = seleccion.colorId || '';
            console.log('Color asignado:', colorInput.name, '=', colorInput.value);
          }
          
          if (detalleInput) {
            detalleInput.value = seleccion.detalleId || '';
            console.log('Detalle asignado:', detalleInput.name, '=', detalleInput.value);
          }
        }
      );
    } else if (window.modalColorDetalleManager === undefined) {
      // Reintentar después de un breve retraso si el manager no está disponible
      setTimeout(tryShowModal, 50);
    }
    // Si modalColorDetalleManager existe pero articulo.id no, no hacer nada
  }
  
  // Intentar mostrar el modal después de un pequeño retraso para asegurar que esté listo
  setTimeout(tryShowModal, 100);
  if ((itemDiv.target.closest("tr").querySelector(".precio-unitario").value === null) || (itemDiv.target.closest("tr").querySelector(".precio-unitario").value == 0)) {
    const precioUnitario = parseFloat(articulo.precio);
    const inputPrecio = itemDiv.target.closest("tr").querySelector(".precio-unitario")
    inputPrecio.value = precioUnitario.toFixed(2);
    if (articulo.oferta == true){
      inputPrecio.className = inputPrecio.className + " precio-destacado";
    }
    else{
      inputPrecio.className = inputPrecio.className + " precio-normal";
    }  
  } 
  // Establezco que inputs son editables en base a la propiedad pedirEnVentas del articulo  
  if (articulo.pedirEnVentas === "PRECIO"){
    const precioUnitario = itemDiv.target.closest("tr").querySelector(".precio-unitario");
    precioUnitario.removeAttribute("readonly")
    const cantidad = itemDiv.target.closest("tr").querySelector(".cantidad");
    cantidad.value = 1;
    cantidad.setAttribute("readonly", "readonly");
    precioUnitario.focus();
  }else{
    if (articulo.pedirEnVentas === "CANTIDAD_PRECIO"){
      const precioUnitario = itemDiv.target.closest("tr").querySelector(".precio-unitario");
      precioUnitario.removeAttribute("readonly", true);
      const cantidad = itemDiv.target.closest("tr").querySelector(".cantidad");
      cantidad.removeAttribute("readonly");
      precioUnitario.focus();
    }else{
      const precioUnitario = itemDiv.target.closest("tr").querySelector(".precio-unitario");
      precioUnitario.setAttribute("readonly", "readonly");
      const cantidad = itemDiv.target.closest("tr").querySelector(".cantidad");
      cantidad.removeAttribute("readonly");
    }
  }
  updateItemTotal(itemDiv);
  updateTotalFactura();
}

function mostrarModalSeleccionArticulos(articulos, idlista, itemDiv) {
  // Usar el sistema universal de modal de búsqueda
  const callback = async (articulo) => {
    try {
      const response = await fetch(`${BASE_URL}/articulos/articulo/${articulo.codigo}/${idlista}`);
      if (response.ok) {
        const data = await response.json();
        asignarArticuloElegido(data.articulo, itemDiv);
      }
    } catch (error) {
      console.error('Error al obtener artículo:', error);
      // Fallback: usar el artículo directamente
      asignarArticuloElegido(articulo, itemDiv);
    }
    
    // Enfocar el nuevo input de código
    const nuevoInputCodigo = tablaItems.querySelector(`tr:last-child .codigo-articulo`);
    if (nuevoInputCodigo) nuevoInputCodigo.focus();
  };
  
  // Mostrar modal con los datos
  window.universalSearchModal.show('articulos', articulos || [], callback);
}

function updateItemTotal(itemDiv) {
  const precioUnitario = parseFloat(itemDiv.target.closest("tr").querySelector(".precio-unitario").value);
  const cantidad = parseFloat(itemDiv.target.closest("tr").querySelector(".cantidad").value);
  const precioTotal = (precioUnitario * cantidad).toFixed(2);
  if (isNaN(precioTotal)) {
    precioTotal = 0;
  }
  itemDiv.target.closest("tr").querySelector(".precio-total").value = precioTotal;
}

function updateTotalFactura() {
  const filas = document.querySelectorAll("#tabla-items tbody tr");
  let totalFactura = 0;
  filas.forEach((fila) => {
    const precioTotalInput = fila.querySelector(".precio-total");
    if (precioTotalInput) {
      const precioTotal = parseFloat(precioTotalInput.value) || 0;
      totalFactura += precioTotal;
    }
  });
  document.getElementById("totalFactura").value = totalFactura.toFixed(2);
  
  // Solo llamar calcSaldo si el modal está abierto y las funciones universales están disponibles
  const modal = document.getElementById('transaccionesModal');
  if (modal && modal.classList.contains('show') && window.calcSaldo) {
    window.calcSaldo();
  }
}

function removeItem(itemDiv) {
  itemDiv.remove();
  updateTotalFactura();
  renumberItems();
}

function renumberItems() {
  const itemDivs = document.querySelectorAll("#items .item");
  itemDivs.forEach((itemDiv, index) => {
    itemDiv
      .querySelector(".idarticulo")
      .setAttribute("name", `items[${index}][idarticulo]`);
    itemDiv
      .querySelector(".cantidad")
      .setAttribute("name", `items[${index}][cantidad]`);
    itemDiv
      .querySelector(".precio_articulo")
      .setAttribute("name", `items[${index}][cantidad]`);
  });
}

function checkDatosTarjeta() {
  const totTarjeta = parseFloat(document.getElementById("tarjeta").value);
  const entidad = parseInt(document.getElementById("entidad").value);
  if (totTarjeta > 0) {
    if (entidad <= 0 || isNaN(entidad)) {
      alert("Debe completar correctamente los datos de tarjeta");
      return false;
    }
    return true;
  } else {
    if ((totTarjeta > 0) || (entidad > 0)) {
      alert("Debe completar correctamente los datos de tarjeta");
      return false;
    }else{
      return true;
    }      
  }
}
/*FIXIT
        controlar valores nulos NaN*/
// Funciones calcSaldo() y checkTotales() movidas a modal-transacciones-universal.js
// para evitar conflictos con el modal universal

// Event listeners movidos a modal-transacciones-universal.js
// Mantener solo el de cliente que es específico de esta página

document.getElementById("idcliente").addEventListener("blur", function () {
  const idcliente = this.value;
  fetchCliente(idcliente);
});

document.getElementById("tabla-items").addEventListener("input", function (e) {
  if (
    e.target.classList.contains("idarticulo") ||
    e.target.classList.contains("cantidad") ||
    e.target.classList.contains("precio-unitario")
  ) {
    updateItemTotal(e);
    updateTotalFactura();
  }
});

const tablaItems = document.querySelector("#tabla-items tbody");

// Agregar nueva fila
document.getElementById("agregarArticulo").addEventListener("click", () => {
  const nuevaFila = `
                <tr class="items">
                    <td class="id-articulo" name="items[${contadorFilas}][idarticulo]">- 
                        <input type="hidden" name="items[${contadorFilas}][idrubro]">
                        <input type="hidden" name="items[${contadorFilas}][idmarca]">
                        <input type="hidden" name="items[${contadorFilas}][id_color]" value="0">
                        <input type="hidden" name="items[${contadorFilas}][id_detalle]" value="0">
                    </td>                    <td class="id-marca" name="items[${contadorFilas}][idmarca]" hidden> </td>
                    <td class="id-rubro" name="items[${contadorFilas}][idrubro]" hidden> </td>

                    <td><input type="text" class="form-control codigo-articulo" name="items[${contadorFilas}][codigo]" required onfocus="this.select()"></td>
                    <td class="descripcion-articulo">-</td>
                    <td><input type="number" class="form-control precio-unitario" name="items[${contadorFilas}][precio_unitario]" readonly onfocus="this.select()"></td>
                    <td><input type="number" class="form-control cantidad" name="items[${contadorFilas}][cantidad]" value="1" step="0.01" min="0.01" required onfocus="this.select()"></td> 
                    <td><input type="number" class="form-control precio-total" name="items[${contadorFilas}][precio_total]" readonly></td>
                    <td hidden><input type="number" class="idoferta" name="items[${contadorFilas}][idoferta]" value="0"></td> 
                    <td><button type="button" class="btn btn-danger btn-eliminar">Eliminar</button></td>
                </tr>`;
  tablaItems.insertAdjacentHTML("beforeend", nuevaFila);
  contadorFilas++;
  
  // Asegurar que la nueva fila tenga los campos necesarios
  setTimeout(() => {
    ensureColorDetalleFields();
  }, 10);
  
  // Enfocar el nuevo input de código
  const nuevoInputCodigo = tablaItems.querySelector(`tr:last-child .codigo-articulo`);
  nuevoInputCodigo.focus();
});

async function handleArticuloBlur(itemDiv) {
  if (itemDiv.target.classList.contains("codigo-articulo")) {
    const codigo = itemDiv.target.value;
    const idlista = document.getElementById("idlista").value;
    const precioUnitario = itemDiv.target.closest("tr").querySelector(".precio-unitario");
    if (precioUnitario){
      precioUnitario.value = 0;
    }
    await fetchArticulo(codigo, idlista, itemDiv);
  }
}

tablaItems.addEventListener("blur", handleArticuloBlur, true);

// Eliminar fila
tablaItems.addEventListener("click", (itemDiv) => {
  if (itemDiv.target.classList.contains("btn-eliminar")) {
    itemDiv.target.closest("tr").remove();
  }
});

document.getElementById("invoice_form").addEventListener("submit", async function (event) {
    event.preventDefault();

    if (document.querySelectorAll("#tabla-items tbody tr").length === 0) {
        alert("Debe agregar al menos un item a la factura");
        return false;
    }
    if (checkDatosTarjeta() === false) {
        return false;
    }
    if (!window.checkTotales || !window.checkTotales()) {
        alert(
            'El total debe ser mayor a cero y/o la suma de "Efectivo" + "Tarjeta" + "Cta. cte." + "Crédito" debe ser igual al total de la factura'
        );
        return false;
    }
    if (confirm("¿Grabar la factura?") === false) {
        return false;
    }

    // Asegurar que los campos color/detalle estén presentes antes del envío
    ensureColorDetalleFields();
    
    // 👉 Mostrar spinner
    document.getElementById("spinner").style.display = "block";

    // Cargargres el arreglo de ofertas de cierre
    if (ofertasDeCierre.length > 0) {
      ofertasDeCierre.forEach(art => {
        // Simular click en "Agregar artículo"
        document.getElementById("agregarArticulo").click();
        // Buscar la última fila agregada
        const fila = tablaItems.querySelector("tr:last-child");
        fila.querySelector(".id-articulo").textContent = art.id;
        fila.querySelector(".codigo-articulo").value = art.codigo;
        fila.querySelector(".precio-unitario").value = art.precio;
        fila.querySelector(".cantidad").value = -art.cantidad;
        fila.querySelector(".idoferta").value = art.idoferta;
        // Calcular el total
        fila.querySelector(".precio-total").value = -(art.precio * art.cantidad).toFixed(2);
      });
    }  
    updateTotalFactura();

    isFormSubmited = true;
    try {
        const formData = new FormData(this);
        const response = await fetch(`${BASE_URL}/ventas/nueva_venta`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {

            // Imprimir factura
            posPrinter = document.getElementById("posPrinter").value;
            if (posPrinter != ""){
              try {
                  alert('voy a imprimir la factura');
                  await imprimirFactura(result.id);
              } catch (error) {
                  console.error('Error al imprimir la factura:', error);
              }
            }

            window.location.href = `${BASE_URL}/ventas/nueva_venta`;
        } else {
            alert(result.message);
            window.location.href = `${BASE_URL}/ventas/nueva_venta`;
        }
    }
    catch (error) {
        console.error(error);
        alert('Error al procesar la venta');
        window.location.href = `${BASE_URL}/ventas/nueva_venta`;
    }
});


// Variable global para almacenar los datos del crédito
let creditoDisponible = null;

async function hayCredito(idcliente) {
  console.log(`🔍 Verificando crédito para cliente: ${idcliente}`);
  
  try {
    const response = await fetch(`${BASE_URL}/creditos/hay_credito/${idcliente}`);
    
    if (response.ok) {
      const data = await response.json();
      console.log('📊 Respuesta del servidor:', data);
      
      if (data.success) {
        if (data.credito.idcredito != 0) {
          console.log('💳 Cliente tiene crédito disponible');
          
          // Guardar los datos del crédito globalmente
          creditoDisponible = {
            idcredito: data.credito.idcredito,
            estado: data.credito.estado,
            monto_credito: parseFloat(data.credito.monto_credito),
            cuotas: data.credito.cuotas
          };
          
          console.log('💾 Datos del crédito guardados:', creditoDisponible);
          
          // Mostrar modal de confirmación
          mostrarModalCreditoDisponible(creditoDisponible);
        } else {
          console.log('❌ Cliente no tiene crédito disponible');
          // No hay crédito disponible - limpiar campos
          limpiarCamposCredito();
        }
      } else {
        console.error('❌ Error en la respuesta del servidor:', data);
        limpiarCamposCredito();
      }
    } else {
      console.error(`❌ Error HTTP ${response.status}: ${response.statusText}`);
      limpiarCamposCredito();
    }
  } catch (error) {
    console.error('❌ Error al verificar crédito:', error);
    limpiarCamposCredito();
  }
}

function mostrarModalCreditoDisponible(credito) {
  console.log('Mostrando modal de crédito disponible:', credito);
  
  // Llenar los datos en la modal
  document.getElementById('credito-id').textContent = credito.idcredito;
  document.getElementById('credito-estado').textContent = getEstadoCredito(credito.estado);
  document.getElementById('credito-monto').textContent = `$ ${credito.monto_credito.toLocaleString('es-AR', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })}`;
  document.getElementById('credito-cuotas').textContent = credito.cuotas;
  
  // Mostrar la modal (usando both jQuery and vanilla JS for compatibility)
  const modal = document.getElementById('creditoDisponibleModal');
  if (modal) {
    $('#creditoDisponibleModal').modal({
      backdrop: 'static',  // Prevent closing by clicking outside
      keyboard: false      // Prevent closing with ESC key  
    }).modal('show');
  } else {
    console.error('Modal creditoDisponibleModal no encontrada');
  }
}

function getEstadoCredito(estado) {
  const estados = {
    1: 'Nuevo',
    2: 'Pendiente',
    3: 'Aprobado',
    4: 'Rechazado',
    5: 'Cancelado',
    6: 'Finalizado',
    7: 'Actualizar datos'
  };
  return estados[estado] || 'Desconocido';
}

function aplicarCredito() {
  if (creditoDisponible) {
    console.log('✅ Aplicando crédito:', creditoDisponible);
    
    // Guardar el crédito para aplicar cuando se abra el modal de pagos
    window.creditoPendienteAplicar = {
      monto: creditoDisponible.monto_credito,
      idcredito: creditoDisponible.idcredito
    };
    
    console.log('💾 Crédito guardado para aplicar:', window.creditoPendienteAplicar);
    
    // Mostrar notificación de éxito ANTES de aplicar (para evitar que se limpie la variable)
    mostrarNotificacionCredito(window.creditoPendienteAplicar.monto);
    
    // Intentar aplicar inmediatamente si el modal de pagos ya está disponible
    aplicarCreditoEnModal();
    
    // Cerrar modal
    $('#creditoDisponibleModal').modal('hide');
  } else {
    console.error('❌ No hay datos de crédito disponibles para aplicar');
  }
}

function aplicarCreditoEnModal() {
  if (!window.creditoPendienteAplicar) return;
  
  console.log('🔄 Intentando aplicar crédito en modal de pagos...');
  
  // Buscar campos de crédito en el modal de pagos con múltiples selectores
  const posiblesSelectores = [
    '#credito',
    '#monto_credito', 
    '[name="credito"]',
    '[name="monto_credito"]',
    '#pago-credito input[type="number"]',
    '.tab-pane#pago-credito input'
  ];
  
  let montoCreditoField = null;
  let idCreditoField = null;
  
  // Buscar el campo de monto de crédito
  for (const selector of posiblesSelectores) {
    montoCreditoField = document.querySelector(selector);
    if (montoCreditoField) {
      console.log(`✅ Campo de crédito encontrado con selector: ${selector}`);
      break;
    }
  }
  
  // Buscar el campo de ID de crédito
  const posiblesIdSelectores = [
    '#idcredito',
    '[name="idcredito"]',
    '#pago-credito input[name="idcredito"]'
  ];
  
  for (const selector of posiblesIdSelectores) {
    idCreditoField = document.querySelector(selector);
    if (idCreditoField) {
      console.log(`✅ Campo ID crédito encontrado con selector: ${selector}`);
      break;
    }
  }
  
  if (montoCreditoField) {
    montoCreditoField.disabled = false;
    montoCreditoField.value = window.creditoPendienteAplicar.monto.toFixed(2);
    
    if (idCreditoField) {
      idCreditoField.value = window.creditoPendienteAplicar.idcredito;
      console.log('✅ ID de crédito establecido:', window.creditoPendienteAplicar.idcredito);
    }
    
    // NO activar automáticamente la pestaña de crédito
    // El usuario puede cambiar manualmente si lo desea
    // El tab de efectivo siempre queda activo por defecto
    console.log('✅ Valores de crédito cargados (tab efectivo permanece activo)');
    
    // Recalcular saldo usando función universal
    if (window.calcSaldo) {
      setTimeout(() => {
        window.calcSaldo();
      }, 100);
    }
    
    // Mostrar feedback visual
    montoCreditoField.style.backgroundColor = '#d4edda';
    montoCreditoField.style.border = '2px solid #28a745';
    setTimeout(() => {
      montoCreditoField.style.backgroundColor = '';
      montoCreditoField.style.border = '';
    }, 3000);
    
    console.log('✅ Crédito aplicado exitosamente en el modal de pagos');
    
    // Limpiar el crédito pendiente DESPUÉS de aplicarlo exitosamente
    window.creditoPendienteAplicar = null;
    
    return true;
  } else {
    console.warn('⚠️ Campos de crédito no encontrados en el modal de pagos');
    return false;
  }
}

function mostrarNotificacionCredito(monto) {
  // Usar el monto pasado como parámetro
  const montoCredito = monto || (window.creditoPendienteAplicar ? window.creditoPendienteAplicar.monto : 0);
  
  if (montoCredito <= 0) {
    console.warn('⚠️ No se puede mostrar notificación: monto inválido');
    return;
  }
  
  // Crear notificación temporal
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    z-index: 10000;
    font-weight: 600;
    animation: slideIn 0.3s ease-out;
  `;
  notification.innerHTML = `
    <i class="fas fa-check-circle"></i>
    Crédito de $${montoCredito.toLocaleString('es-AR', {minimumFractionDigits: 2})} listo para usar
  `;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    if (notification && notification.parentNode) {
      notification.remove();
    }
  }, 4000);
}

// Asegurar que las funciones estén en el scope global
window.aplicarCredito = aplicarCredito;

function rechazarCredito() {
  console.log('🚫 Usuario rechazó aplicar el crédito');
  
  // No aplicar el crédito - limpiar campos y variables
  limpiarCamposCredito();
  
  // Limpiar crédito pendiente
  window.creditoPendienteAplicar = null;
  
  // Cerrar modal
  $('#creditoDisponibleModal').modal('hide');
  
  console.log('✅ Crédito rechazado - campos y variables limpiados');
}

// Event listeners para los botones del modal de crédito
document.addEventListener('DOMContentLoaded', function() {
  // Botón rechazar crédito
  const btnRechazarCredito = document.querySelector('#creditoDisponibleModal .btn-secondary');
  if (btnRechazarCredito) {
    btnRechazarCredito.addEventListener('click', rechazarCredito);
    console.log('✅ Event listener para rechazar crédito configurado');
  }
  
  // Botón aplicar crédito  
  const btnAplicarCredito = document.querySelector('#creditoDisponibleModal .btn-success');
  if (btnAplicarCredito) {
    btnAplicarCredito.addEventListener('click', aplicarCredito);
    console.log('✅ Event listener para aplicar crédito configurado');
  }
});

// También asegurar que estén en el scope global para compatibilidad
window.rechazarCredito = rechazarCredito;

function limpiarCamposCredito() {
  console.log('🧹 Limpiando campos de crédito');
  
  const idCreditoField = document.getElementById("idcredito");
  const montoCreditoField = document.getElementById("monto_credito");
  
  if (idCreditoField && montoCreditoField) {
    idCreditoField.disabled = true;
    idCreditoField.value = '';
    montoCreditoField.disabled = true;
    montoCreditoField.value = 0;
    
    // Remover cualquier estilo de feedback visual
    montoCreditoField.style.backgroundColor = '';
    
    console.log('✅ Campos de crédito limpiados');
  } else {
    console.warn('⚠️ No se encontraron los campos de crédito para limpiar');
  }
  
  // Limpiar variable global
  creditoDisponible = null;
}  


async function imprimirFactura(id) {
    try {
        // Construir la URL completa para debugging
        const url = `${BASE_URL}/ventas/imprimir_factura_vta_pos/${id}`;

        const response = await fetch(url);
        
        // Si la respuesta no es ok, lanzar error con más detalles
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.message || 'Error desconocido en la impresión');
        }

        return true;
    } catch (error) {
        console.error('Error detallado:', error);
        console.error('Stack trace:', error.stack);
        alert(`Error al imprimir la factura: ${error.message}`);
        return false;
    }
}

async function coefCuotas(tarjeta, cuotas) {
  if (cuotas === 0) return 0;
  const url = `${BASE_URL}/entidades/coeficiente_cuotas/${tarjeta}/${cuotas}`;
  response = await fetch(url);
  if (response.ok) {
    const data = await response.json();
    return data.coeficiente;
  }  
}

// Event listener para cuotas movido a modal-transacciones-universal.js
// para usar la implementación universal que maneja todos los campos correctamente