let isFormSubmited = false;
let contadorFilas = 0;

// Función para asegurar que existan campos hidden de color/detalle
function ensureColorDetalleFields() {
  const rows = document.querySelectorAll("#tabla-items tbody tr");
  
  rows.forEach((row, index) => {
    const firstCell = row.querySelector("td.id-articulo");
    if (firstCell) {
      // Verificar si ya tiene los campos
      let colorInput = row.querySelector('[name*="id_color"]');
      let detalleInput = row.querySelector('[name*="id_detalle"]');
      
      if (!colorInput) {
        colorInput = document.createElement('input');
        colorInput.type = 'hidden';
        colorInput.name = `items[${index}][id_color]`;
        colorInput.value = '0';
        firstCell.appendChild(colorInput);
      }
      
      if (!detalleInput) {
        detalleInput = document.createElement('input');
        detalleInput.type = 'hidden';
        detalleInput.name = `items[${index}][id_detalle]`;
        detalleInput.value = '0';
        firstCell.appendChild(detalleInput);
      }
    }
  });
}

window.onbeforeunload = function () {
  if (!isFormSubmited) {
    return "¿Estás seguro de cerrar la compra sin guardar los cambios?";
  }
};

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("invoice_form");
  const btnAgregar = document.getElementById("agregarArticulo");
  const btnGrabar = document.getElementById("grabarCompra");

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

    // Asignar tecla F5 para agregar un nuevo artículo
    if (event.key === "F4") {
      event.preventDefault(); // Evita la recarga de página con F5
      btnAgregar.click(); // Simula un click en el botón "Agregar Artículo"
    }
  });
});


function asignarProveedor(proveedor) {
  document.getElementById("idproveedor").value = proveedor.id;
  document.getElementById("proveedor_nombre").value = proveedor.nombre;
  obtener_remitos(proveedor.id); // Llamar a la función para obtener remitos
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

function limpiarDatosProveedor() {
  inputIdProveedor = document.getElementById("idproveedor");
  inputIdProveedor.value = "";
  inputIdProveedor.focus();
}


async function fetchProveedor(input) {
  let response;
  if (!isNaN(input)) {
    // Si es un número, buscar por ID
    response = await fetch(`${BASE_URL}/proveedores/get_proveedor/${input}`); //1 venta
  } else {
    // Si es un nombre parcial, buscar por nombre
    response = await fetch(`${BASE_URL}/proveedores/get_proveedores?nombre=${input}`);
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


async function fetchArticulo(id, idlista, itemDiv) {
  let response;
  if (!isNaN(id)) {
    response = await fetch(`${BASE_URL}/articulos/articulo/${id}/${idlista}`);
  } else {
    response = await fetch(`${BASE_URL}/articulos/get_articulos?detalle=${id}&idlista=${idlista}`);
  }

  if (!response.ok) {
    console.error("Error en la búsqueda de artículos");
    return;
  }
  //const data = await response.json();
  const data = await response.json();

  if (data.success) {
    if (data.articulo) {
      // Si se encuentra un articulo por ID, asignarlo directamente
      asignarArticulo(data.articulo, itemDiv);
      
    } else {
      alert("No se encontraron articulos con ese ID.");
    }
  } else {
    if (data.length > 1) {
      // Si hay más de un resultado, mostrar un modal para seleccionar
      mostrarModalSeleccionArticulos(data, itemDiv);
    } else if (data.length === 1) {
      // Si hay un solo resultado, asignar directamente
      asignarArticuloElegido(data[0], itemDiv);
      
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
  const tablaItems = document.getElementById("tabla-items").querySelector("tbody");
  
  row.querySelector(".id-articulo").textContent = articulo.id;
  row.querySelector(".descripcion-articulo").textContent = articulo.detalle;
  const precioUnitario = parseFloat(articulo.precio);
  const edtPrecio = row.querySelector(".precio-unitario");
  edtPrecio.value = precioUnitario.toFixed(2);
  
  // Asegurar que existan campos hidden antes de intentar mostrar modal
  ensureColorDetalleFields();
  
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
              }
          );
      } else if (window.modalColorDetalleManager === undefined) {
          // Reintentar después de un breve retraso si el manager no está disponible
          setTimeout(tryShowModal, 50);
      }
  }
  
  // Intentar mostrar el modal después de un pequeño retraso
  setTimeout(tryShowModal, 100);
  
  updateItemTotal(itemDiv);
  updateTotalFactura();
  edtPrecio.focus();
}

function mostrarModalSeleccionArticulos(articulos, itemDiv) {
  // Callback para manejar la selección del artículo
  const callback = (articulo) => {
    asignarArticuloElegido(articulo, itemDiv);
  };
  
  // Usar el modal universal para mostrar los artículos
  window.universalSearchModal.show('articulos', articulos, callback);
}

function updateItemTotal(itemDiv) {
  const precioUnitario = parseFloat(
    itemDiv.target.closest("tr").querySelector(".precio-unitario").value
  );
  const cantidad = parseFloat(
    itemDiv.target.closest("tr").querySelector(".cantidad").value
  );
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

// Funciones calcSaldo() y checkTotales() movidas a modal-transacciones-universal.js
// para usar la implementación universal que funciona correctamente

// Event listeners para campos de pago movidos a modal-transacciones-universal.js
// para evitar duplicación y usar la funcionalidad universal

document.getElementById("idproveedor").addEventListener("blur", function () {
  const idproveedor = this.value;
  fetchProveedor(idproveedor);
});

document.getElementById("tabla-items").addEventListener("input", function (e) {
  if (
    e.target.classList.contains("idarticulo") ||
    e.target.classList.contains("cantidad")
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
            <td class="id-articulo" name="items[${contadorFilas}][idarticulo]">-</td>
            <td><input type="text" class="form-control codigo-articulo" name="items[${contadorFilas}][codigo]" required></td>
            <td class="descripcion-articulo">-</td>
            <td><input type="number" class="form-control precio-unitario" name="items[${contadorFilas}][precio_unitario]" value="0.00" step="0.01" min="0.01" onfocus="this.select()" required></td>
            <td><input type="number" class="form-control cantidad" name="items[${contadorFilas}][cantidad]" value="1" step="0.01" min="0.01" onfocus="this.select()" required></td> 
            <td><input type="number" class="form-control precio-total" name="items[${contadorFilas}][precio_total]" readonly></td>
            <td><button type="button" class="btn btn-danger btn-eliminar">Eliminar</button></td>
        </tr>`;
  tablaItems.insertAdjacentHTML("beforeend", nuevaFila);
  contadorFilas++;
  // Enfocar el nuevo input de código
  const nuevoInputCodigo = tablaItems.querySelector(`tr:last-child .codigo-articulo`);
  nuevoInputCodigo.focus();
});

tablaItems.addEventListener(
  "blur",
  (itemDiv) => {
    if (itemDiv.target.classList.contains("codigo-articulo")) {
      const codigo = itemDiv.target.value;
      const idlista = 0; //idlista = 0 toma valores de costo

      // Simulación de una búsqueda (deberías usar una API aquí)
      fetchArticulo(codigo, idlista, itemDiv);
    }
  },
  true
);

// Eliminar fila
tablaItems.addEventListener("click", (itemDiv) => {
  if (itemDiv.target.classList.contains("btn-eliminar")) {
    itemDiv.target.closest("tr").remove();
  }
});

document
  .getElementById("invoice_form")
  .addEventListener("submit", function (event) {
    if (document.querySelectorAll("#tabla-items tbody").length === 0) {
      event.preventDefault();
      alert("Debe agregar al menos un item a la factura");
      event.preventDefault();
      return false;
    }

    if (checkTotales() === false) {
      event.preventDefault();
      alert(
        'El total debe ser mayor a cera y/o la suma de "Efectivo" + "Tarjeta" + "Cta. cte." debe ser igual al total de la factura'
      );
      event.preventDefault();
      return false;
    }
    if (confirm("¿Grabar la factura?") === false) {
      event.preventDefault();
    } else {
      isFormSubmited = true;
    }
  });

// ================================================================
//                    FUNCIONES DE MODAL DE PAGOS
// ================================================================

function abrirModalPagos() {
    // Configurar total antes de abrir modal
    const totalElement = document.getElementById('totalFactura');
    const totalFactura = totalElement ? (totalElement.value || totalElement.textContent) : '0';
    
    console.log('🚚 [COMPRAS] abrirModalPagos() - Total obtenido:', totalFactura, typeof totalFactura);
    
    // Verificar que la función universal esté disponible
    if (window.cargarDatosModal) {
        console.log('✅ [COMPRAS] cargarDatosModal está disponible');
        window.cargarDatosModal(parseFloat(totalFactura) || 0);
    } else {
        console.error('❌ [COMPRAS] cargarDatosModal no está disponible');
        console.log('🔍 [COMPRAS] window.cargarDatosModal:', typeof window.cargarDatosModal);
    }
    
    $('#transaccionesModal').modal('show');
    
    // Cuando el modal se haya mostrado, hacer debug adicional
    document.getElementById('transaccionesModal').addEventListener('shown.bs.modal', function () {
        console.log('📋 [COMPRAS] Modal mostrado, verificando campos...');
        
        // Verificar campos de pago
        const paymentFields = ['efectivo', 'tarjeta', 'ctacte', 'credito', 'bonificacion'];
        paymentFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            console.log(`🔍 [COMPRAS] Campo ${fieldId}:`, field ? 'EXISTE' : 'NO EXISTE', field?.value || 'sin valor');
        });
        
        // Verificar elemento total
        const totalFacElement = document.getElementById('modal_total_factura');
        console.log('💰 [COMPRAS] modal_total_factura:', totalFacElement ? 'EXISTE' : 'NO EXISTE', totalFacElement?.textContent || 'sin valor');
        
        // Enfocar primer input
        const primerInput = document.querySelector('#transaccionesModal input:not([readonly]):not([type="hidden"])');
        if (primerInput) {
            primerInput.focus();
            console.log('👆 [COMPRAS] Enfocando:', primerInput.id);
        }
        
        // LISTENERS REMOVIDOS: Ahora se manejan exclusivamente en modal-transacciones-universal.js
        // para evitar duplicaciones y conflictos
        
        // Agregar función de test para verificar funcionamiento
        window.testCambiarEfectivo = function(valor) {
            console.log('🧪 [TEST] Cambiando efectivo a:', valor);
            const efectivo = document.getElementById('efectivo');
            if (efectivo) {
                const valorAnterior = efectivo.value;
                efectivo.value = valor;
                console.log(`🧪 [TEST] Valor cambiado de "${valorAnterior}" a "${valor}"`);
                
                // Disparar evento
                const evento = new Event('input', { bubbles: true });
                efectivo.dispatchEvent(evento);
                console.log('🧪 [TEST] Evento input disparado');
                
                // Verificar listeners
                console.log('🧪 [TEST] Verificando listeners en el elemento:', efectivo);
                
                // Verificar funciones globales
                console.log('🧪 [TEST] window.calcSaldo disponible:', typeof window.calcSaldo);
                console.log('🧪 [TEST] calcSaldo local disponible:', typeof calcSaldo);
                
            } else {
                console.error('🧪 [TEST] Campo efectivo no encontrado');
            }
        };
        
        window.testCambiarCredito = function(valor) {
            console.log('🧪 [TEST CREDITO] Cambiando credito a:', valor);
            const credito = document.getElementById('credito');
            if (credito) {
                credito.value = valor;
                credito.dispatchEvent(new Event('input', { bubbles: true }));
                console.log('🧪 [TEST CREDITO] Evento disparado');
            }
        };
        
        console.log('🧪 [COMPRAS] Funciones de test disponibles:');
        console.log('   - testCambiarEfectivo(1000)');
        console.log('   - testCambiarCredito(500)');
        
    }, { once: true });
}

// Personalizar procesamiento para compras
function procesarTransaccion() {
    console.log('🚚 [COMPRAS] procesarTransaccion() llamada');
    
    // Usar las funciones universales para verificar totales
    if (!window.checkTotales || !window.checkTotales()) {
        const diferencia = window.calcSaldo ? window.calcSaldo() : 0;
        const mensaje = diferencia > 0 ? 
            `Falta pagar $${diferencia.toFixed(2)}` : 
            `Sobra $${Math.abs(diferencia).toFixed(2)}`;
        
        if (!confirm(`${mensaje}. ¿Desea continuar de todas formas?`)) {
            return false;
        }
    }
    
    // Confirmar grabado
    if (!confirm('¿Grabar la compra?')) {
        return false;
    }
    
    console.log('✅ [COMPRAS] Usuario confirmó grabado, cerrando modal...');
    
    // Cerrar modal
    $('#transaccionesModal').modal('hide');
    
    // Usar el comportamiento tradicional del formulario en lugar de AJAX
    console.log('📋 [COMPRAS] Enviando formulario tradicional...');
    
    // Obtener formulario
    const form = document.querySelector('form#invoice_form');
    if (!form) {
        console.error('❌ [COMPRAS] Formulario no encontrado');
        alert('Error: No se pudo grabar la compra. Formulario no encontrado.');
        return false;
    }
    
    // Validar campos required antes de enviar
    if (!form.checkValidity()) {
        console.warn('⚠️ [COMPRAS] Formulario no válido, mostrando errores...');
        form.reportValidity();
        return false;
    }
    
    // Marcar que el formulario está siendo enviado para evitar el warning de beforeunload
    isFormSubmited = true;
    
    // Enviar formulario de la manera tradicional (sin AJAX)
    form.submit();
    
    return true;
}

// Atajos de teclado
document.addEventListener('keydown', function(e) {
    if (e.key === 'F8') {
        e.preventDefault();
        abrirModalPagos();
    }
});

// Hacer funciones disponibles globalmente
window.abrirModalPagos = abrirModalPagos;
window.procesarTransaccion = procesarTransaccion;
