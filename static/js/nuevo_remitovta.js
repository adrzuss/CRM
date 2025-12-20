let isFormSubmited = false;
let contadorFilas = 0;

window.onbeforeunload = function () {
  if (!isFormSubmited) {
    return "¿Estás seguro de cerrar la venta sin guardar los cambios?";
  }
};

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

document.addEventListener("DOMContentLoaded", async function () {
  // Configurar atajos de teclado
  setupKeyboardShortcuts();
  
  try {
    // Realizar la solicitud a la API
    const response = await fetch(`${BASE_URL}/ventas/get_punto_vta`);	
    const data = await response.json(); 
    // Verificar el valor de punto_vta
    if (!data.punto_vta) {
      // Si punto_vta es null o no está definido, mostrar el modal
      const ptosVtasSucursal = await fetch(`${BASE_URL}/ventas/get_puntos_vta_sucursal`);
      const datos = await ptosVtasSucursal.json(); 
      
      if (datos.length == 1) {
      
        asignarPuntoVenta(datos[0].id);
      }
      else{
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
          ptoVtaOption.textContent = "Punto de venta:" + ptovta.puntoVta; // Mostrar el nombre del punto de venta
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
    }
    else{
      // Si punto_vta tiene un valor, asignarlo al input
      console.log("punto_vta:", data.punto_vta);
      document.getElementById("punto_vta").textContent = 'Punto de venta: ' + data.punto_vta;
    }
  } catch (error) {
    console.error("Error al obtener el punto de venta:", error);
  }
});

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
      document.getElementById("punto_vta").textContent = 'Punto de venta: ' + idPuntoVenta;
      document.getElementById("idcliente").focus();
    } else {
      alert('Error al asignar el punto de venta: ' + result.message);
    }
  } catch (error) {
    console.error('Error al llamar a la API:', error);
    alert('Ocurrió un error al asignar el punto de venta.');
  }
}

// Función global para manejar atajos de teclado
function setupKeyboardShortcuts() {
  const form = document.getElementById("invoice_form");
  const btnAgregar = document.getElementById("agregarArticulo");
  const btnGrabar = document.getElementById("grabarVenta");

  if (!form || !btnAgregar || !btnGrabar) {
    console.warn('No se encontraron todos los elementos para configurar atajos');
    return;
  }

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
  });

  // Atajos globales de teclado
  document.addEventListener("keydown", function (event) {
    // Asignar tecla F9 para grabar venta
    if (event.key === "F9") {
      event.preventDefault();
      btnGrabar.click();
    }

    // Asignar tecla F4 para agregar un nuevo artículo
    if (event.key === "F4") {
      event.preventDefault();
      btnAgregar.click();
    }
  });
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
      response = await fetch(`${BASE_URL}/clientes/get_cliente/${input}/${5}`); //5 remito
    } else {
      // Si es un nombre parcial, buscar por nombre
      response = await fetch(`${BASE_URL}/clientes/get_clientes?nombre=${input}&&tipo_operacion=${5}`);
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
          alert("Cliente dado de baja. No puedes remitir a este cliente.");
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
  document.getElementById("tipo_comprobante").innerText = "Tipo de comprobante: " + cliente.tipo_comprobante;
  document.getElementById("id_tipo_comprobante").value = cliente.id_tipo_comprobante;
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
      // Si se encuentra un cliente por ID, asignarlo directamente
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
  itemDiv.target.closest("tr").querySelector(".codigo-articulo").value =
    articulo.codigo;
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

document.getElementById("idcliente").addEventListener("blur", function () {
  const idcliente = this.value;
  fetchCliente(idcliente);
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

// Función para agregar nueva fila
function agregarNuevaFila() {
  const nuevaFila = `
                <tr class="items">
                    <td class="id-articulo text-center" name="items[${contadorFilas}][idarticulo]">-</td>
                    <td class="text-center"><input type="text" class="form-control codigo-articulo" name="items[${contadorFilas}][codigo]" required></td>
                    <td class="descripcion-articulo">-</td>
                    <td class="text-center"><input type="number" class="form-control precio-unitario" name="items[${contadorFilas}][precio_unitario]" readonly></td>
                    <td class="text-center"><input type="number" class="form-control cantidad" name="items[${contadorFilas}][cantidad]" value="1" step="0.01" min="0.01" required></td> 
                    <td class="text-center"><input type="number" class="form-control precio-total" name="items[${contadorFilas}][precio_total]" readonly></td>
                    <td class="text-center"><button type="button" class="btn btn-outline-danger btn-sm btn-eliminar"><i class="fas fa-trash"></i></button></td>
                </tr>`;
  tablaItems.insertAdjacentHTML("beforeend", nuevaFila);
  contadorFilas++;
  
  // Ocultar estado vacío
  const emptyState = document.getElementById('empty-state');
  if (emptyState) emptyState.style.display = 'none';
  
  // Asegurar que la nueva fila tenga los campos necesarios
  setTimeout(() => {
    ensureColorDetalleFields();
  }, 10);
  
  // Enfocar el nuevo input de código
  const nuevoInputCodigo = tablaItems.querySelector(`tr:last-child .codigo-articulo`);
  if (nuevoInputCodigo) nuevoInputCodigo.focus();
}

// Event listener para el botón agregar artículo
document.getElementById("agregarArticulo").addEventListener("click", agregarNuevaFila);

tablaItems.addEventListener(
  "blur",
  (itemDiv) => {
    if (itemDiv.target.classList.contains("codigo-articulo")) {
      const codigo = itemDiv.target.value;

      // Simulación de una búsqueda (deberías usar una API aquí)
      fetchArticulo(codigo, 0, itemDiv);
    }
  },
  true
);

// Eliminar fila
tablaItems.addEventListener("click", (itemDiv) => {
  if (itemDiv.target.classList.contains("btn-eliminar") || itemDiv.target.closest('.btn-eliminar')) {
    if (confirm('¿Está seguro de eliminar este artículo?')) {
      itemDiv.target.closest("tr").remove();
      updateTotalFactura();
      
      // Mostrar estado vacío si no hay más artículos
      const tbody = document.getElementById("tabla-items").querySelector("tbody");
      const emptyState = document.getElementById('empty-state');
      if (tbody.children.length === 0 && emptyState) {
        emptyState.style.display = 'block';
      }
    }
  }
});

document.getElementById("invoice_form").addEventListener("submit", function (event) {
    if (document.querySelectorAll("#tabla-items tbody").length === 0) {
      event.preventDefault();
      alert("Debe agregar al menos un item al remito");
      event.preventDefault();
      return false;
    }
    
    if (confirm("¿Grabar el remito?") === false) {
      event.preventDefault();
    } else {
      // Asegurar que los campos color/detalle estén presentes antes del envío
      ensureColorDetalleFields();
      isFormSubmited = true;
    }
  });
