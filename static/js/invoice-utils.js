/**
 * invoice-utils.js
 * Utilidades compartidas para formularios de facturación, notas de crédito,
 * presupuestos, compras y remitos.
 *
 * Requiere: swal-helpers.js, universal-search-modal.js
 */

/**
 * Calcula el precio_total de una fila multiplicando precio_unitario por cantidad
 * y escribe el resultado en el campo .precio-total de la misma fila.
 * @param {Event} itemDiv - Evento del input que disparó el cálculo
 */
function updateItemTotal(itemDiv) {
  const precioUnitario = parseFloat(itemDiv.target.closest("tr").querySelector(".precio-unitario").value);
  const cantidad = parseFloat(itemDiv.target.closest("tr").querySelector(".cantidad").value);
  const precioTotal = (precioUnitario * cantidad).toFixed(2);
  if (isNaN(precioTotal)) {
    precioTotal = 0;
  }
  itemDiv.target.closest("tr").querySelector(".precio-total").value = precioTotal;
}

/**
 * Renumera los atributos `name` de los inputs en todas las filas de #items .item
 * para mantener el índice correcto después de eliminar una fila.
 */
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

/**
 * Recorre todas las filas de #tabla-items tbody y se asegura de que cada una
 * tenga los inputs hidden id_color e id_detalle. Si no existen, los crea con
 * value="0". Versión extendida con logging de diagnóstico.
 */
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

/**
 * Limpia el campo idcliente del formulario y le devuelve el foco.
 */
function limpiarDatosCliente() {
  inputIdCliente = document.getElementById("idcliente");
  inputIdCliente.value = "";
  inputIdCliente.focus();
}

/**
 * Asigna el código del artículo elegido al input .codigo-articulo de la fila
 * activa y delega en asignarArticulo() para completar el resto de campos.
 * @param {Object} articulo - Objeto artículo con al menos la propiedad `codigo`
 * @param {Event}  itemDiv  - Evento del input activo en la fila
 */
function asignarArticuloElegido(articulo, itemDiv) {
  itemDiv.target.closest("tr").querySelector(".codigo-articulo").value = articulo.codigo;
  asignarArticulo(articulo, itemDiv);
}

/**
 * Abre el modal universal de búsqueda de clientes con los datos recibidos.
 * Al seleccionar un cliente llama a asignarCliente() y enfoca el campo idcliente.
 * @param {Array} clientes - Lista de clientes a mostrar en el modal
 */
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
