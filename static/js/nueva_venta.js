let isFormSubmited = false;
let contadorFilas = 0;
let articulosFacturados = [];
let ofertasDeCierre = [];

window.onbeforeunload = function () {
  if (!isFormSubmited) {
    return "¿Estás seguro de cerrar la venta sin guardar los cambios?";
  }
};

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
    document.getElementById("total_factura").textContent = window.PRESUPUESTO.total;
    document.getElementById("totalFactura").textContent = window.PRESUPUESTO.total;
    
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
    document.getElementById("total_factura").textContent = window.REMITO.total;
    document.getElementById("totalFactura").textContent = window.REMITO.total;
    
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
  // Enfocar el primer campo de pago
  $("#pagosModal").modal("show");

  // Cuando el modal se haya mostrado, enfocar el input
    document.getElementById('pagosModal').addEventListener('shown.bs.modal', function () {
      document.getElementById("efectivo").focus();
    }, { once: true }); // once=true para que no se dispare más de una vez

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
    // Asignar tecla F8 para mostra formas de pago
    if (event.key === "F8") {
      event.preventDefault(); // Evita el comportamiento por defecto de la tecla
      // Si el elemento activo es un input codigo-articulo
      if (document.activeElement.classList.contains("codigo-articulo")) {
        // Esperar a que se complete el blur antes de abrir el modal
        await handleArticuloBlur({target: document.activeElement});
      }
      abrirModalPagos(); // Simula un click en el botón "Grabar Venta"
    }

    // Asignar tecla F9 para grabar venta
    if (event.key === "F9") {
      event.preventDefault(); // Evita el comportamiento por defecto de la tecla
      btnGrabar.click(); // Simula un click en el botón "Grabar Venta"
    }

    // Atajos de teclado en modal de formas de pago
    // Verifica si la modal está visible
    if (document.getElementById('pagosModal').classList.contains('show')) {
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
  document.getElementById("ctacte").readOnly = cliente.ctacte == 0;
  document.getElementById("tipo_comprobante").innerText = "Tipo de factura: " + cliente.tipo_comprobante;
  document.getElementById("id_tipo_comprobante").value = cliente.id_tipo_comprobante;
  if (cliente.ctacte == 0) {
    document.getElementById("label-ctacte").innerText =
      "Cta. Cte. - Cliente sin cta. cte.";
  } else {
    document.getElementById("label-ctacte").innerText = "Cta. Cte.";
  }
  hayCredito(cliente.id);
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
  itemDiv.target.closest("tr").querySelector(".id-articulo").textContent = articulo.id;
  itemDiv.target.closest("tr").querySelector(".id-marca").textContent = articulo.idmarca;
  itemDiv.target.closest("tr").querySelector(".id-rubro").textContent = articulo.idrubro;
  itemDiv.target.closest("tr").querySelector(".codigo-articulo").value = articulo.codigo;
  itemDiv.target.closest("tr").querySelector(".idoferta").value = articulo.idoferta;
  itemDiv.target.closest("tr").querySelector(".descripcion-articulo").textContent = articulo.detalle;
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
    articuloOption.onclick = async() => {
      response = await fetch(`${BASE_URL}/articulos/articulo/${articulo.codigo}/${idlista}`);
      if (response.ok) {
        const data = await response.json();
        //asignarArticulo(data.articulo, itemDiv);
        asignarArticuloElegido(data.articulo, itemDiv);
      }
      //asignarArticuloElegido(articulo, itemDiv);
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
  document.getElementById("total_factura").textContent = totalFactura.toFixed(2);
  document.getElementById("totalFactura").value = totalFactura.toFixed(2);
  calcSaldo();
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
function calcSaldo() {
  const totalFac = parseFloat(document.getElementById("total_factura").textContent);
  const efectivo = parseFloat(document.getElementById("efectivo").value);
  let tarjeta = parseFloat(document.getElementById("tarjeta").value);
  const ctacte = parseFloat(document.getElementById("ctacte").value);
  const bonificacion = parseFloat(document.getElementById("bonificacion").value);
  const monto_credito = parseFloat(document.getElementById("monto_credito").value);
  const ofertas_especiales = parseFloat(document.getElementById("ofertas_especiales").value);
  if (isNaN(efectivo)) {
    efectivo = 0;
  }
  if (isNaN(tarjeta)) {
    tarjeta = 0;
  }
  else{
    const coeficiente = parseFloat(document.getElementById("coeficiente").value);
    tarjeta = tarjeta / coeficiente;
  }
  if (isNaN(ctacte)) {
    ctacte = 0;
  }
  if (isNaN(bonificacion)) {
    bonificacion = 0;
  }
  if (isNaN(monto_credito)) {
    monto_credito = 0;
  }
  if (isNaN(ofertas_especiales)) {
    ofertas_especiales = 0;
  }
  let diferencia = parseFloat(totalFac - (efectivo + tarjeta + ctacte + bonificacion + monto_credito + ofertas_especiales)).toFixed(2);
  let lblSaldo = document.getElementById("saldo_factura");
  lblSaldo.textContent = diferencia;
  if (diferencia > 0) {
    lblSaldo.className = "negativo";
  } else if (diferencia === 0) {
    lblSaldo.className = "neutro";
  } else {
    lblSaldo.className = "positivo";
  }
}

function checkTotales() {
  const totalFac = parseFloat(document.getElementById("total_factura").textContent);
  const efectivo = parseFloat(document.getElementById("efectivo").value);
  const ctacte = parseFloat(document.getElementById("ctacte").value);
  let tarjeta = parseFloat(document.getElementById("tarjeta").value);
  const bonificacion = parseFloat(document.getElementById("bonificacion").value);
  const monto_credito = parseFloat(document.getElementById("monto_credito").value);
  const ofertas_especiales = parseFloat(document.getElementById("ofertas_especiales").value);
  if (isNaN(efectivo)) {
    efectivo = 0;
  }
  if (isNaN(tarjeta)) {
    tarjeta = 0;
  }
  else{
    const coeficiente = parseFloat(document.getElementById("coeficiente").value);
    tarjeta = tarjeta / coeficiente;
  }

  if (isNaN(ctacte)) {
    ctacte = 0;
  }
  if (isNaN(bonificacion)) {
    bonificacion = 0;
  }
  if (isNaN(monto_credito)) {
    monto_credito = 0;
  }
  if (isNaN(ofertas_especiales)) {
    ofertas_especiales = 0;
  }
  let HayDiferencia;
  if (efectivo > 0) {
     HayDiferencia = totalFac.toFixed(2) > 0 && (totalFac <= (efectivo + tarjeta + ctacte + bonificacion + monto_credito + ofertas_especiales).toFixed(2));
  }
  else{
    HayDiferencia = totalFac.toFixed(2) > 0 && (totalFac.toFixed(2) === (tarjeta + ctacte + bonificacion + monto_credito + ofertas_especiales).toFixed(2));
  }  
  return HayDiferencia;
}

document.getElementById("efectivo").addEventListener("blur", function (event) {
  calcSaldo();
});

document.getElementById("tarjeta").addEventListener("blur", function (event) {
  calcSaldo();
});

document.getElementById("ctacte").addEventListener("blur", function (event) {
  calcSaldo();
});

document.getElementById("bonificacion").addEventListener("blur", function (event) {
  calcSaldo();
});

document.getElementById("monto_credito").addEventListener("blur", function (event) {
  calcSaldo();
});

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
                    <td class="id-articulo" name="items[${contadorFilas}][idarticulo]">- <input type="number" name="items[${contadorFilas}][idrubro]" hidden> <input type="number" name="items[${contadorFilas}][idmarca]" hidden> </td>

                    <td class="id-marca" name="items[${contadorFilas}][idmarca]" hidden> </td>
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
    if (checkTotales() === false) {
        alert(
            'El total debe ser mayor a cero y/o la suma de "Efectivo" + "Tarjeta" + "Cta. cte." + "Crédito" debe ser igual al total de la factura'
        );
        return false;
    }
    if (confirm("¿Grabar la factura?") === false) {
        return false;
    }

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


async function hayCredito(idcliente) {
  response = await fetch(`${BASE_URL}/creditos/hay_credito/${idcliente}`)
  if (response.ok) {
    const data = await response.json();
    if (data.success) {
      if (data.credito.idcredito != 0) {
        document.getElementById("monto_credito").disabled = false;
        let monto_credito = parseFloat(data.credito.monto_credito);
        document.getElementById("monto_credito").value = monto_credito.toFixed(2);
        document.getElementById("idcredito").value = data.credito.idcredito;
      } else {
        document.getElementById("idcredito").disabled = true;
        document.getElementById("idcredito").value = '';
        document.getElementById("monto_credito").disabled = true;
        document.getElementById("monto_credito").value = 0;
      }
    } else {
      console.log('error');
    }
  }
  else {
    console.log('Error al consultar créditos');
  } 
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

document.getElementById('cuotas').addEventListener('input', async function() {
    const cuotas = this.value;
    const tarjeta = document.getElementById('entidad').value;
    const coeficienteCuotas = await coefCuotas(tarjeta, cuotas);
    document.getElementById('coeficiente').value = coeficienteCuotas;
    const saldo = parseFloat(document.getElementById("saldo_factura").innerHTML);
    document.getElementById('total_tarjeta').value = parseFloat(saldo * coeficienteCuotas).toFixed(2);
    //document.getElementById('total').innerText = total.toFixed(2);
});