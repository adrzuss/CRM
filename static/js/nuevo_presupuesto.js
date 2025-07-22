let isFormSubmited = false;
let contadorFilas = 0;


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
      document.getElementById("punto_vta").textContent = 'Punto de venta: ' + data.punto_vta;
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
      alert("Debe seleccionar un punto de venta.");
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
          alert("Cliente dado de baja. No puedes presupuestar a este cliente.");
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
  // Crear el contenido del modal con las opciones de cliente
  const tituloModal = document.getElementById("clienteModalLabel");
  tituloModal.textContent = "Seleccione un Cliente";
  const modalContent = document.getElementById("modalContent");
  modalContent.innerHTML = "";
  const listaClientes = document.createElement("ul");
  listaClientes.classList.add("list-group");
  modalContent.appendChild(listaClientes);

  clientes.forEach((cliente) => {
    const clienteOption = document.createElement("li");
    clienteOption.classList.add("cliente-option");
    clienteOption.classList.add("list-group-item");
    clienteOption.textContent = `${cliente.nombre} - Tel/Cel: ${cliente.telefono}`;
    clienteOption.onclick = () => {
      asignarCliente(cliente);
      $("#clienteModal").modal("hide");
      // Enfocar el nuevo input de código
      const clienteInput = document.getElementById("idcliente");
      clienteInput.focus();
    };
    listaClientes.appendChild(clienteOption);
  });

  // Mostrar el modal
  $("#clienteModal").modal("show");
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
    alert("Error en la búsqueda de artículos");
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
  itemDiv.target.closest("tr").querySelector(".codigo-articulo").value = articulo.codigo;
  asignarArticulo(articulo, itemDiv);
}

function asignarArticulo(articulo, itemDiv) {
  itemDiv.target.closest("tr").querySelector(".id-articulo").textContent = articulo.id;
  itemDiv.target
    .closest("tr")
    .querySelector(".descripcion-articulo").textContent = articulo.detalle;
  const precioUnitario = parseFloat(articulo.precio);
  itemDiv.target.closest("tr").querySelector(".precio-unitario").value = precioUnitario.toFixed(2);
  updateItemTotal(itemDiv);
  updateTotalFactura();
}

function mostrarModalSeleccionArticulos(articulos, itemDiv) {
  // Crear el contenido del modal con las opciones de cliente
  const tituloModal = document.getElementById("clienteModalLabel");
  tituloModal.textContent = "Seleccione un Artículo";
  const modalContent = document.getElementById("modalContent");
  modalContent.innerHTML = "";
  const listaArticulos = document.createElement("ul");
  listaArticulos.classList.add("list-group");
  modalContent.appendChild(listaArticulos);

  articulos.forEach((articulo) => {
    const articuloOption = document.createElement("li");
    articuloOption.classList.add("cliente-option");
    articuloOption.classList.add("list-group-item");
    articuloOption.innerHTML = `<strong>${articulo.marca} ${articulo.detalle}</strong> - <span class="precio-normal">$${parseFloat(articulo.precio)
      .toFixed(2)
      .toLocaleString("es-AR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}</span>`;
    articuloOption.onclick = () => {
      asignarArticuloElegido(articulo, itemDiv);
      $("#clienteModal").modal("hide");
      // Enfocar el nuevo input de código
      const nuevoInputCodigo = tablaItems.querySelector(`tr:last-child .codigo-articulo`);
      nuevoInputCodigo.focus();
    };
    listaArticulos.appendChild(articuloOption);
  });

  // Mostrar el modal
  $("#clienteModal").modal("show");
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

// Agregar nueva fila
document.getElementById("agregarArticulo").addEventListener("click", () => {
  const nuevaFila = `
                <tr class="items">
                    <td class="id-articulo" name="items[${contadorFilas}][idarticulo]">-</td>
                    <td><input type="text" class="form-control codigo-articulo" name="items[${contadorFilas}][codigo]" required></td>
                    <td class="descripcion-articulo">-</td>
                    <td><input type="number" class="form-control precio-unitario" name="items[${contadorFilas}][precio_unitario]" value="0" step="0.1" min="0.1" required></td>
                    <td><input type="number" class="form-control cantidad" name="items[${contadorFilas}][cantidad]" value="1" step="0.1" min="0.1" required></td> 
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
      const idlista = document.getElementById("idlista").value;

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

document.getElementById("invoice_form").addEventListener("submit", function (event) {
    if (document.querySelectorAll("#tabla-items tbody").length === 0) {
      event.preventDefault();
      alert("Debe agregar al menos un item al presupuesto");
      event.preventDefault();
      return false;
    }
    
    if (confirm("¿Grabar el presupuesto?") === false) {
      event.preventDefault();
    } else {
      isFormSubmited = true;
    }
  });
