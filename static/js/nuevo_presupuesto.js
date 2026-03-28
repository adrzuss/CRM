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
    return "¿Estás seguro de cerrar la venta sin guardar los cambios?";
  }
};

document.addEventListener("DOMContentLoaded", async function () {
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
      const ptoVtaElement = document.getElementById("punto_vta");
      ptoVtaElement.innerHTML = `<i class="fas fa-store me-1"></i>Punto de venta: ${data.punto_vta}`;
    }
  } catch (error) {
    console.log("Error al obtener el punto de venta:", error);
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

async function asignarPuntoVenta(idPuntoVenta) {
  try {
    // Llamar a la API para asignar el punto de venta a la sesión
    const response = await fetch(`${BASE_URL}/ventas/set_punto_vta`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ punto_vta_id: idPuntoVenta }),
    });

    const result = await response.json();
    if (result.success) {
      $("#ptovtaModal").modal("hide");
      // Actualizar el texto en la página con el punto de venta seleccionado
      const ptoVtaElement = document.getElementById("punto_vta");
      ptoVtaElement.innerHTML = `<i class="fas fa-store me-1"></i>Punto de venta: ${idPuntoVenta}`;
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
  const btnGrabar = document.getElementById("grabarPresupuesto");

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

    // Asignar tecla F9 para grabar presupuesto
    if (event.key === "F9") {
      event.preventDefault(); // Evita el comportamiento por defecto de la tecla
      btnGrabar.click(); // Simula un click en el botón "Grabar Presupuesto"
    }

    // Asignar tecla F5 para agregar un nuevo artículo
    if (event.key === "F4") {
      event.preventDefault(); // Evita la recarga de página con F5
      btnAgregar.click(); // Simula un click en el botón "Agregar Artículo"
    }
  });
});

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
      response = await fetch(`${BASE_URL}/clientes/get_cliente/${input}/${7}`); //7 Presupueto
    } else {
      // Si es un nombre parcial, buscar por nombre
      response = await fetch(`${BASE_URL}/clientes/get_clientes?nombre=${input}&&tipo_operacion=${7}`);
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
          mostrarAdvertencia("Cliente dado de baja. No puedes presupuestar a este cliente.");
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
  document.getElementById("idcliente").value = cliente.id;
  document.getElementById("cliente_nombre").value = cliente.nombre;
  document.getElementById("id").value = cliente.id;
  document.getElementById("tipo_comprobante").innerText = "Tipo de presupuesto: " + cliente.tipo_comprobante;
  document.getElementById("id_tipo_comprobante").value = cliente.id_tipo_comprobante;
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
    mostrarError("Error en la búsqueda de artículos");
    return;
  }
  //const data = await response.json();
  const data = await response.json();

  if (data.success) {
    if (data.articulo) {
      // Si se encuentra un cliente por ID, asignarlo directamente
      asignarArticulo(data.articulo, itemDiv);
    } else {
      mostrarInfo("No se encontraron articulos con ese ID.");
    }
  } else {
    if (data.length > 1) {
      // Si hay más de un resultado, mostrar un modal para seleccionar
      mostrarModalSeleccionArticulos(data, itemDiv);
    } else if (data.length === 1) {
      // Si hay un solo resultado, asignar directamente
      asignarArticuloElegido(data[0], itemDiv);
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
  const tablaItems = document.getElementById("tabla-items").querySelector("tbody");
  
  row.querySelector(".id-articulo").textContent = articulo.id;
  row.querySelector(".descripcion-articulo").textContent = articulo.detalle;
  const precioUnitario = parseFloat(articulo.precio);
  row.querySelector(".precio-unitario").value = precioUnitario.toFixed(2);
  
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
}

function mostrarModalSeleccionArticulos(articulos, itemDiv) {
  const callback = (articulo) => {
    asignarArticuloElegido(articulo, itemDiv);
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
  itemDiv.target.closest("tr").querySelector(".precio-total").value =
    precioTotal;
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
  document.getElementById("total_factura").textContent =
    totalFactura.toFixed(2);
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

// Event listeners para cliente
document.getElementById("idcliente").addEventListener("blur", function () {
  const idcliente = this.value;
  fetchCliente(idcliente);
});

// Botón buscar cliente
document.getElementById("buscarCliente").addEventListener("click", function() {
  const nombreCliente = document.getElementById("idcliente").value.trim();
  if (nombreCliente) {
    fetchCliente(nombreCliente);
  } else {
    // Mostrar modal de búsqueda vacío para explorar todos los clientes
    window.universalSearchModal.show('clientes', [], (cliente) => {
      asignarCliente(cliente);
    });
  }
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
                    <td class="id-articulo text-center" name="items[${contadorFilas}][idarticulo]">-</td>
                    <td class="text-center">
                        <input type="text" class="form-control form-control-sm codigo-articulo text-center" 
                               name="items[${contadorFilas}][codigo]" 
                               placeholder="Código" required>
                    </td>
                    <td class="descripcion-articulo text-muted">Busque por código...</td>
                    <td class="text-center">
                        <input type="number" class="form-control form-control-sm precio-unitario text-end" 
                               name="items[${contadorFilas}][precio_unitario]" 
                               value="0" step="0.01" min="0" required>
                    </td>
                    <td class="text-center">
                        <input type="number" class="form-control form-control-sm cantidad text-center" 
                               name="items[${contadorFilas}][cantidad]" 
                               value="1" step="0.01" min="0.01" required>
                    </td> 
                    <td class="text-center">
                        <input type="number" class="form-control form-control-sm precio-total text-end" 
                               name="items[${contadorFilas}][precio_total]" readonly>
                    </td>
                    <td class="text-center">
                        <button type="button" class="btn btn-outline-danger btn-sm btn-eliminar" title="Eliminar artículo">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>`;
  tablaItems.insertAdjacentHTML("beforeend", nuevaFila);
  contadorFilas++;
  
  // Ocultar estado vacío y enfocar el nuevo input
  const emptyState = document.getElementById('empty-state');
  if (emptyState) emptyState.style.display = 'none';
  
  const nuevoInputCodigo = tablaItems.querySelector(`tr:last-child .codigo-articulo`);
  if (nuevoInputCodigo) nuevoInputCodigo.focus();
  
  updateTotalFactura();
});

tablaItems.addEventListener(
  "blur",
  (itemDiv) => {
    if (itemDiv.target.classList.contains("codigo-articulo")) {
      const codigo = itemDiv.target.value;
      const idlista = document.getElementById("idlista").value;

      // Simulación de una búsqueda (deberías usar una API aquí)
      fetchArticulo(codigo, idlista, itemDiv);
    }
  },
  true
);

// Eliminar fila
tablaItems.addEventListener("click", async (itemDiv) => {
  if (itemDiv.target.classList.contains("btn-eliminar") || itemDiv.target.closest('.btn-eliminar')) {
    const confirmado = await confirmar('¿Está seguro de eliminar este artículo?');
    if (confirmado) {
      itemDiv.target.closest("tr").remove();
      updateTotalFactura();
      
      // Mostrar estado vacío si no hay filas
      const remainingRows = tablaItems.querySelectorAll('tr');
      if (remainingRows.length === 0) {
        const emptyState = document.getElementById('empty-state');
        if (emptyState) emptyState.style.display = 'block';
      }
    }
  }
});

document.getElementById("invoice_form").addEventListener("submit", async function (event) {
    event.preventDefault();
    
    const itemsRows = document.querySelectorAll("#tabla-items tbody tr");
    
    if (itemsRows.length === 0) {
      mostrarAdvertencia("Debe agregar al menos un artículo al presupuesto");
      document.getElementById("agregarArticulo").focus();
      return false;
    }
    
    // Validar que todos los artículos tengan datos completos
    let hasInvalidItems = false;
    itemsRows.forEach(row => {
      const codigo = row.querySelector('.codigo-articulo').value.trim();
      const descripcion = row.querySelector('.descripcion-articulo').textContent.trim();
      const precio = parseFloat(row.querySelector('.precio-unitario').value);
      const cantidad = parseFloat(row.querySelector('.cantidad').value);
      
      if (!codigo || descripcion === '-' || descripcion === 'Busque por código...' || precio <= 0 || cantidad <= 0) {
        hasInvalidItems = true;
      }
    });
    
    if (hasInvalidItems) {
      mostrarAdvertencia("Hay artículos con datos incompletos. Por favor complete toda la información antes de guardar.");
      return false;
    }
    
    // Confirmar guardado
    const confirmado = await confirmar("¿Confirma que desea guardar este presupuesto?");
    if (confirmado) {
      isFormSubmited = true;
      // Mostrar indicador de carga
      const submitBtn = document.getElementById("grabarPresupuesto");
      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Guardando...';
      submitBtn.disabled = true;
      
      // Restaurar botón en caso de error (después de 5 segundos)
      setTimeout(() => {
        if (!isFormSubmited) {
          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;
        }
      }, 5000);
      
      this.submit();
    }
  });

// Inicialización adicional al cargar el DOM
document.addEventListener('DOMContentLoaded', function() {
  // Mostrar estado vacío inicialmente
  setTimeout(() => {
    const tbody = document.querySelector('#tabla-items tbody');
    const emptyState = document.getElementById('empty-state');
    
    if (tbody && emptyState && tbody.children.length === 0) {
      emptyState.style.display = 'block';
    }
    
    // Auto-focus en el campo cliente
    const clienteInput = document.getElementById('idcliente');
    if (clienteInput) {
      clienteInput.focus();
    }
  }, 100);
  
  // Configurar validez por defecto (15 días)
  const fechaActual = new Date();
  const fechaValidez = new Date(fechaActual);
  fechaValidez.setDate(fechaActual.getDate() + 15);
  
  const validezInput = document.querySelector('input[name="validez"]');
  if (validezInput && !validezInput.value) {
    validezInput.value = fechaValidez.toISOString().split('T')[0];
  }
});
