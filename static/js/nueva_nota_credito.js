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
      mostrarAdvertencia("Debe seleccionar un punto de venta.");
    }
  };
  modalContent.appendChild(confirmButton);
  //---------
  $("#ptovtaModal").modal("show");
}

function abrirModalPagos(){
  // Validar datos requeridos antes de abrir el modal de pagos
  const idcliente = document.getElementById('idcliente')?.value;
  const idlista = document.getElementById('idlista')?.value;
  const cantidadProductos = document.querySelectorAll("#tabla-items tbody tr").length;
  
  // Verificar cliente cargado
  if (!idcliente || idcliente === '' || idcliente === '0') {
    mostrarAdvertencia("Debe seleccionar un cliente antes de continuar con el pago.");
    document.getElementById('idcliente')?.focus();
    return;
  }
  
  // Verificar lista de precios
  if (!idlista || idlista === '' || idlista === '0') {
    mostrarAdvertencia("Debe seleccionar una lista de precios antes de continuar con el pago.");
    return;
  }
  
  // Verificar al menos un producto
  if (cantidadProductos === 0) {
    mostrarAdvertencia("Debe agregar al menos un producto antes de continuar con el pago.");
    document.getElementById('agregarArticulo')?.focus();
    return;
  }
  
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
    // Enfocar el input apropiado
    const primerInput = document.querySelector('#transaccionesModal input:not([readonly]):not([type="hidden"])');
    if (primerInput) {
      primerInput.focus();
    };
  }, { once: true });

  // Asegurar que todas las filas existentes tengan campos de color/detalle
  setTimeout(ensureColorDetalleFields, 500);
}

// Hacer funciones disponibles globalmente
window.abrirModalPagos = abrirModalPagos;
window.procesarTransaccion = procesarTransaccion;
window.grabarNotaCredito = grabarNotaCredito;

/**
 * Función para grabar la nota de crédito directamente sin modal de pagos
 * El pago se registra automáticamente como nota_credito (idpago=20)
 */
async function grabarNotaCredito() {
    console.log('grabarNotaCredito() llamada');
    
    // Validar que hay un comprobante original seleccionado
    const idComprobanteOriginal = document.getElementById('id_comprobante_original')?.value;
    if (!idComprobanteOriginal || idComprobanteOriginal === '') {
        mostrarAdvertencia('Debe seleccionar un comprobante original antes de grabar la nota de crédito.');
        return false;
    }
    
    // Validar que hay items en la tabla
    const filas = document.querySelectorAll("#tabla-items tbody tr:not(#no-items-row)");
    if (filas.length === 0) {
        mostrarAdvertencia('Debe agregar al menos un artículo a la nota de crédito.');
        return false;
    }
    
    // Validar cliente
    const idcliente = document.getElementById('idcliente')?.value;
    if (!idcliente || idcliente === '' || idcliente === '0') {
        mostrarAdvertencia('Debe tener un cliente asignado para grabar la nota de crédito.');
        return false;
    }
    
    // Obtener el total de la factura
    const totalFacturaElement = document.getElementById('totalFactura');
    const total = parseFloat(totalFacturaElement?.value || 0);
    
    if (total <= 0) {
        mostrarAdvertencia('El total de la nota de crédito debe ser mayor a cero.');
        return false;
    }
    
    // Establecer el valor del campo hidden nota_credito con el total
    const notaCreditoField = document.getElementById('nota_credito');
    if (notaCreditoField) {
        notaCreditoField.value = total.toFixed(2);
        console.log('Campo nota_credito establecido en:', total.toFixed(2));
    } else {
        console.error('Campo nota_credito no encontrado');
        mostrarError('Error interno: campo nota_credito no encontrado');
        return false;
    }
    
    // Confirmar antes de grabar
    const confirmado = await confirmar('¿Confirma que desea grabar la Nota de Crédito?');
    if (!confirmado) {
        return false;
    }
    
    // Enviar formulario via AJAX
    console.log('Enviando formulario de nota de crédito via AJAX...');
    const form = document.getElementById('invoice_form');
    if (!form) {
        console.error('Formulario invoice_form no encontrado');
        mostrarError('No se pudo grabar la nota de crédito. Formulario no encontrado.');
        return false;
    }
    
    // Preparar datos del formulario
    const formData = new FormData(form);
    
    // Mostrar spinner de carga
    const spinner = document.getElementById('spinner');
    if (spinner) spinner.style.display = 'flex';
    
    let url = form.action || window.location.href;
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        console.log('Respuesta del servidor:', data);
        
        if (data.success) {
            toastExito(`Nota de Crédito ${data.nro_comprobante || data.id} grabada exitosamente`);
            
            // Verificar si tiene facturación electrónica
            const tieneFacElectronica = document.getElementById('fac_electronica')?.value === 'true';
            const facturaId = data.id;
            const ptoVta = document.getElementById('ptovta_seleccionado')?.value || '1';
            
            try {
                if (tieneFacElectronica) {
                    try {
                        const facResponse = await fetch(`${BASE_URL}/ventas/facturar_venta/${ptoVta}/${facturaId}`);
                        const facResult = await facResponse.json().catch(() => null);
                        
                        if (facResult && facResult.success) {
                            toastExito(`CAE: ${facResult.cae}`);
                        } else {
                            console.warn('Advertencia al facturar electrónicamente:', facResult?.message || 'Error desconocido');
                            toastAdvertencia('Error en facturación electrónica. Verifique el CAE.');
                        }
                    } catch (facError) {
                        console.error('Error al facturar electrónicamente:', facError);
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
            
            // Limpiar formulario
            limpiarFormularioVenta();
            
        } else {
            mostrarError(`${data.message || 'No se pudo grabar la nota de crédito'}`);
        }
    } catch (error) {
        console.error('Error al grabar nota de crédito:', error);
        mostrarError('Error de conexión al grabar la nota de crédito. URL: ' + url);
    } finally {
        if (spinner) spinner.style.display = 'none';
    }
    
    return true;
}

// Función personalizada para procesar transacción en nueva venta
async function procesarTransaccion() {
    console.log('procesarTransaccion() llamada para nueva venta');
    
    // Usar la validación del modal universal
    if (!checkTotales()) {
        const diferencia = calcSaldo();
        const mensaje = diferencia > 0 ? 
            `Falta pagar $${diferencia.toFixed(2)}` : 
            `Sobra $${Math.abs(diferencia).toFixed(2)}`;
        
        const continuar = await confirmar(`${mensaje}. ¿Desea continuar de todas formas?`);
        if (!continuar) {
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
        mostrarError('No se pudo grabar la venta. Formulario no encontrado.');
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
            // Mostrar mensaje de éxito con el número de comprobante
            toastExito(`Factura ${data.nro_comprobante || data.id} grabada exitosamente`);
            
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
                        
                        if (result && result.success) {
                            toastExito(`CAE: ${result.cae}`);
                        } else {
                            console.warn('Advertencia al facturar electrónicamente:', result?.message || 'Error desconocido');
                            toastAdvertencia('Error en facturación electrónica. Verifique el CAE.');
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
            mostrarError(`${data.message || 'No se pudo grabar la venta'}`);
        }
    })
    .catch(error => {
        console.error('Error al grabar venta:', error);
        mostrarError('Error de conexión al grabar la venta (Mensaje' + error.message + ' - Detalle: ' + error.error_detalle + '). URL: ' + url);
        
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
      mostrarError('Error al asignar el punto de venta: ' + result.message);
    }
  } catch (error) {
    console.error('Error al llamar a la API:', error);
    mostrarError('Ocurrió un error al asignar el punto de venta.');
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
    
    // F8: Grabar nota de crédito
    
    if (event.key === "F8") {
      event.preventDefault();
      // Si el elemento activo es un input codigo-articulo
      if (document.activeElement.classList.contains("codigo-articulo")) {
        // Esperar a que se complete el blur antes de grabar
        await handleArticuloBlur({target: document.activeElement});
      }
      grabarNotaCredito();
    }
    
  });
});

// Nota: Los listeners de pago-efectivo, pago-tarjetas, etc. fueron removidos
// porque la Nota de Crédito no usa el modal de pagos

// Event listeners para cambios de cantidad


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
      response = await fetch(`${BASE_URL}/clientes/get_cliente/${input}/${3}`); //3 nota de crédito
    } else {
      // Si es un nombre parcial, buscar por nombre
      response = await fetch(`${BASE_URL}/clientes/get_clientes?nombre=${input}&&tipo_operacion=${3}`);
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
          mostrarAdvertencia("Cliente dado de baja. No puedes facturar a este cliente.");
          return;
        }
        asignarCliente(data.cliente);
      } else {
        mostrarInfo("No se encontraron clientes con ese ID.");
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
        mostrarInfo("No se encontraron clientes con ese nombre.");
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
  console.log("Cliente asignado con ID:", cliente.id, "y nombre:", cliente.nombre, " - Tipo comprobante ID:", cliente.id_tipo_comprobante);
  
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
  
  
}

async function fetchArticulo(id, idlista, itemDiv) {
  let response;
  console.log("🔍 Buscando artículo con ID o detalle:", id, "en lista de precios ID:", idlista);
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
    mostrarError("Error en la búsqueda de artículos");
    return;
  }
  //const data = await response.json();
  const data = await response.json();
  
  if (data.success) {
    if (data.articulo && data.articulo.baja == true) {
      // Artículo dado de baja
      mostrarAdvertencia("El artículo está dado de baja.");
      return;
    }

    if (data.articulo) {
      asignarArticulo(data.articulo, itemDiv);
    } else {
      mostrarInfo("No se encontraron articulos con ese ID.");
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
      mostrarInfo("No se encontraron articulos con ese detalle.");
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
      mostrarAdvertencia("Debe completar correctamente los datos de tarjeta");
      return false;
    }
    return true;
  } else {
    if ((totTarjeta > 0) || (entidad > 0)) {
      mostrarAdvertencia("Debe completar correctamente los datos de tarjeta");
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

// Event listener para cambio de lista de precios
// Variable para guardar la lista de precios anterior
let listaAnterior = null;

// Guardar valor anterior al hacer focus en el select
document.getElementById("idlista").addEventListener("focus", function () {
  listaAnterior = this.value;
});

document.getElementById("idlista").addEventListener("change", async function () {
  await recalcularPreciosPorLista(this);
});

/**
 * Recalcula los precios de todos los productos según la nueva lista de precios
 */
async function recalcularPreciosPorLista(selectElement) {
  const filas = document.querySelectorAll("#tabla-items tbody tr");
  
  // Si no hay productos, no hacer nada (y actualizar listaAnterior)
  if (filas.length === 0) {
    listaAnterior = selectElement.value;
    return;
  }
  
  const idlista = selectElement.value;
  
  // Pedir confirmación
  const confirmado = await confirmar(`¿Desea actualizar los precios de ${filas.length} producto(s) con la nueva lista de precios?`);
  if (!confirmado) {
    // Restaurar la lista anterior
    if (listaAnterior !== null) {
      selectElement.value = listaAnterior;
    }
    return;
  }
  
  // Actualizar listaAnterior con el nuevo valor confirmado
  listaAnterior = idlista;
  
  let productosActualizados = 0;
  let productosSinPrecio = [];
  
  // Recorrer cada fila y actualizar precio
  for (const fila of filas) {
    const codigo = fila.querySelector(".codigo-articulo")?.value;
    
    if (!codigo || codigo === '') {
      continue;
    }
    
    try {
      const response = await fetch(`${BASE_URL}/articulos/articulo/${codigo}/${idlista}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.success && data.articulo) {
          const precioUnitario = parseFloat(data.articulo.precio);
          const cantidad = parseFloat(fila.querySelector(".cantidad").value) || 1;
          const inputPrecio = fila.querySelector(".precio-unitario");
          
          if (!isNaN(precioUnitario) && precioUnitario > 0) {
            inputPrecio.value = precioUnitario.toFixed(2);
            
            // Actualizar clase de oferta
            inputPrecio.classList.remove("precio-destacado", "precio-normal");
            inputPrecio.classList.add(data.articulo.oferta ? "precio-destacado" : "precio-normal");
            
            // Actualizar precio total de la línea
            fila.querySelector(".precio-total").value = (precioUnitario * cantidad).toFixed(2);
            
            productosActualizados++;
          } else {
            productosSinPrecio.push(codigo);
          }
        } else {
          productosSinPrecio.push(codigo);
        }
      } else {
        productosSinPrecio.push(codigo);
      }
    } catch (error) {
      console.error(`Error al obtener precio para artículo ${codigo}:`, error);
      productosSinPrecio.push(codigo);
    }
  }
  
  // Actualizar total de la factura
  updateTotalFactura();
  
  // Mostrar resultado
  if (productosSinPrecio.length > 0) {
    mostrarAdvertencia(`Se actualizaron ${productosActualizados} productos. Los siguientes artículos no tienen precio en la nueva lista: ${productosSinPrecio.join(', ')}`);
  } else if (productosActualizados > 0) {
    toastExito(`Se actualizaron los precios de ${productosActualizados} producto(s)`);
  }
}

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
        mostrarAdvertencia("Debe agregar al menos un item a la factura");
        return false;
    }
    if (checkDatosTarjeta() === false) {
        return false;
    }
    if (!window.checkTotales || !window.checkTotales()) {
        mostrarAdvertencia(
            'El total debe ser mayor a cero y/o la suma de "Efectivo" + "Tarjeta" + "Cta. cte." + "Crédito" debe ser igual al total de la factura'
        );
        return false;
    }
    
    const confirmado = await confirmar("¿Grabar la factura?");
    if (!confirmado) {
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
                  console.log('Imprimiendo factura...');
                  await imprimirFactura(result.id);
              } catch (error) {
                  console.error('Error al imprimir la factura:', error);
              }
            }

            window.location.href = `${BASE_URL}/ventas/nueva_venta`;
        } else {
            mostrarError(result.message);
            window.location.href = `${BASE_URL}/ventas/nueva_venta`;
        }
    }
    catch (error) {
        console.error(error);
        mostrarError('Error al procesar la venta');
        window.location.href = `${BASE_URL}/ventas/nueva_venta`;
    }
});

// ==================== BÚSQUEDA DE COMPROBANTES PARA NOTA DE CRÉDITO ====================

/**
 * Busca comprobantes disponibles para generar nota de crédito
 * Llama al endpoint /ventas/buscar_comprobantes_nc con la fecha y número de comprobante
 */
async function buscarComprobantesParaNC() {
  const fechaInput = document.querySelector('[name="fecha_comprobante_original"]');
  const nroCompInput = document.getElementById('nro_comp_original');
  
  if (!fechaInput || !fechaInput.value) {
    mostrarAdvertencia('Debe ingresar una fecha para buscar comprobantes');
    fechaInput?.focus();
    return;
  }
  
  const fecha = fechaInput.value;
  const nroComprobante = nroCompInput?.value || '';
  
  console.log(`🔍 Buscando comprobantes - Fecha: ${fecha}, Nro: ${nroComprobante}`);
  
  try {
    const response = await fetch(`${BASE_URL}/ventas/buscar_comprobantes_nc`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        fecha: fecha,
        nro_comprobante: nroComprobante
      })
    });
    
    const data = await response.json();
    
    if (!data.success) {
      mostrarError(data.message || 'Error al buscar comprobantes');
      return;
    }
    
    const comprobantes = data.comprobantes || [];
    
    if (comprobantes.length === 0) {
      mostrarAdvertencia('No se encontraron comprobantes para los criterios ingresados');
      return;
    }
    
    if (comprobantes.length === 1) {
      // Si solo hay un resultado, asignarlo directamente
      asignarComprobanteOriginal(comprobantes[0]);
    } else {
      // Si hay múltiples resultados, mostrar el modal de selección
      mostrarModalSeleccionComprobantes(comprobantes, asignarComprobanteOriginal);
    }
    
  } catch (error) {
    console.error('Error al buscar comprobantes:', error);
    mostrarError('Error al conectar con el servidor');
  }
}

/**
 * Asigna los datos del comprobante seleccionado a los campos del formulario
 * @param {Object} comprobante - Objeto con los datos del comprobante
 */
async function asignarComprobanteOriginal(comprobante) {
  console.log('📄 Asignando comprobante original:', comprobante);
  
  // Asignar ID del comprobante original
  const idCompOriginal = document.getElementById('id_comprobante_original');
  const idLista = document.getElementById('idlista');
  
  if (idCompOriginal) {
    idCompOriginal.value = comprobante.id;
  }
  if (idLista && comprobante.idlista) {
    idLista.value = comprobante.idlista;
  }
  
  
  // Asignar total del comprobante original
  const totalCompOriginal = document.getElementById('total_comp_original');
  if (totalCompOriginal) {
    totalCompOriginal.value = comprobante.total.toLocaleString('es-AR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }
  
  // Asignar nombre del cliente
  const clienteNombre = document.getElementById('cliente_nombre');
  if (clienteNombre) {
    clienteNombre.value = comprobante.cliente;
  }
  
  // Asignar ID del cliente (si existe el campo)
  const idCliente = document.getElementById('idcliente');
  if (idCliente && comprobante.idcliente) {
    idCliente.value = comprobante.idcliente;
    // Disparar evento para que se carguen los datos del cliente si es necesario
    idCliente.dispatchEvent(new Event('blur'));
  }
  
  // Asignar tipo de comprobante original
  const idTipoCompOriginal = document.getElementById('id_tipo_comprobante_original');
  if (idTipoCompOriginal) {
    idTipoCompOriginal.value = comprobante.idtipocomp;
  }
  
  // Actualizar badge de tipo de comprobante
  const tipoCompBadge = document.getElementById('tipo_comprobante_original');
  if (tipoCompBadge) {
    tipoCompBadge.innerHTML = `<i class="fas fa-file-invoice"></i> Tipo: ${comprobante.tipo_comp}`;
  }
  
  // Cargar los items del comprobante
  await cargarItemsComprobante(comprobante.id);
  
  console.log('✅ Comprobante original asignado correctamente');
  
  // Mostrar mensaje de éxito
  if (typeof toastExito === 'function') {
    toastExito(`Comprobante #${comprobante.id} seleccionado con ${document.querySelectorAll('#tabla-items tbody tr.items').length} artículos`);
  }
}

/**
 * Carga los items de un comprobante de venta en la tabla
 * @param {number} idComprobante - ID del comprobante
 */
async function cargarItemsComprobante(idComprobante) {
  console.log(`🔄 Cargando items del comprobante ${idComprobante}...`);
  
  try {
    const response = await fetch(`${BASE_URL}/ventas/get_items_comprobante/${idComprobante}`);
    const data = await response.json();
    
    if (!data.success) {
      console.error('Error al cargar items:', data.message);
      mostrarError(data.message || 'Error al cargar los artículos del comprobante');
      return;
    }
    
    const items = data.items || [];
    console.log(`📦 ${items.length} items encontrados`);
    
    // Vaciar la tabla actual
    vaciarTablaItems();
    
    // Agregar cada item a la tabla
    items.forEach((item, index) => {
      agregarItemATabla(item, index);
    });
    
    // Actualizar el contador de filas
    contadorFilas = items.length;
    
    // Actualizar el total de la factura
    updateTotalFactura();
    
    // Sincronizar el total visual
    if (typeof sincronizarTotal === 'function') {
      sincronizarTotal();
    }
    
    console.log('✅ Items cargados correctamente');
    
  } catch (error) {
    console.error('Error al cargar items:', error);
    mostrarError('Error al conectar con el servidor');
  }
}

/**
 * Vacía la tabla de items
 */
function vaciarTablaItems() {
  const tbody = document.querySelector('#tabla-items tbody');
  if (tbody) {
    // Remover todas las filas excepto la fila "no-items-row" si existe
    const filas = tbody.querySelectorAll('tr.items');
    filas.forEach(fila => fila.remove());
    
    // Ocultar la fila de "no hay items" si existe
    const noItemsRow = document.getElementById('no-items-row');
    if (noItemsRow) {
      noItemsRow.style.display = 'none';
    }
  }
  
  // Resetear contador
  contadorFilas = 0;
}

/**
 * Agrega un item a la tabla de artículos
 * @param {Object} item - Objeto con los datos del item
 * @param {number} index - Índice del item
 */
function agregarItemATabla(item, index) {
  const tbody = document.querySelector('#tabla-items tbody');
  if (!tbody) return;
  
  const precioTotal = (item.cantidad * item.precio_unitario).toFixed(2);
  
  const nuevaFila = `
    <tr class="items">
      <td class="id-articulo" name="items[${index}][idarticulo]">${item.idarticulo}
        <input type="hidden" name="items[${index}][idrubro]" value="">
        <input type="hidden" name="items[${index}][idmarca]" value="">
        <input type="hidden" name="items[${index}][id_color]" value="${item.idcolor || 0}">
        <input type="hidden" name="items[${index}][id_detalle]" value="${item.iddetalle || 0}">
      </td>
      <td class="id-marca" name="items[${index}][idmarca]" hidden></td>
      <td class="id-rubro" name="items[${index}][idrubro]" hidden></td>
      <td><input type="text" class="form-control codigo-articulo" name="items[${index}][codigo]" value="${item.codigo || ''}" readonly onfocus="this.select()"></td>
      <td class="descripcion-articulo">${item.descripcion || '-'}</td>
      <td><input type="number" class="form-control precio-unitario" name="items[${index}][precio_unitario]" value="${item.precio_unitario}" readonly onfocus="this.select()"></td>
      <td><input type="number" class="form-control cantidad" name="items[${index}][cantidad]" value="${item.cantidad}" step="0.01" min="0.01" required onfocus="this.select()"></td>
      <td><input type="number" class="form-control precio-total" name="items[${index}][precio_total]" value="${precioTotal}" readonly></td>
      <td hidden><input type="number" class="idoferta" name="items[${index}][idoferta]" value="0"></td>
      <td><button type="button" class="btn btn-danger btn-eliminar">Eliminar</button></td>
    </tr>`;
  
  tbody.insertAdjacentHTML('beforeend', nuevaFila);
}

// Event listener para el botón de buscar comprobante original
// Nota: Como el script es type="module", se ejecuta después de que el DOM está listo
// por lo que no necesitamos DOMContentLoaded
(function initBuscarComprobante() {
  const btnBuscarCompOriginal = document.getElementById('buscar_comprobante_original');
  if (btnBuscarCompOriginal) {
    btnBuscarCompOriginal.addEventListener('click', function(e) {
      e.preventDefault();
      buscarComprobantesParaNC();
    });
    console.log('✅ Event listener para buscar comprobante original configurado');
  } else {
    console.warn('⚠️ Botón buscar_comprobante_original no encontrado');
  }
})();

// Exponer funciones globalmente
window.buscarComprobantesParaNC = buscarComprobantesParaNC;
window.asignarComprobanteOriginal = asignarComprobanteOriginal;
window.cargarItemsComprobante = cargarItemsComprobante;
window.vaciarTablaItems = vaciarTablaItems;
window.agregarItemATabla = agregarItemATabla;


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
        mostrarError(`Error al imprimir la factura: ${error.message}`);
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