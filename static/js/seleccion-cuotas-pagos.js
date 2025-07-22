    document.addEventListener("DOMContentLoaded", async function () {
        document.getElementById("idcliente").focus();    
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

        
    document.getElementById("idcliente").addEventListener("blur", function () {
        const idcliente = this.value;
        fetchCliente(idcliente);
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
    };

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

    function asignarCliente(cliente) {
        document.getElementById("idcliente").value = cliente.id;
        document.getElementById("cliente_nombre").value = cliente.nombre;
        cuotasPendientes(cliente.id);
    }

    function limpiarDatosCliente() {
        let idcliente = document.getElementById("idcliente");
        idcliente.value = "";
        document.getElementById("cliente_nombre").value = "";
        idcliente.focus();
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

async function cuotasPendientes(idcliente) {
    try {
        const response = await fetch(`${BASE_URL}/creditos/cuotas_pendientes/${idcliente}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                let lst_cuotas = document.getElementById("lst_cuotas");
                lst_cuotas.innerHTML = "";
                data.cuotas.forEach((cuota, index) => {
                    const cuotaOption = document.createElement("tr");
                    cuotaOption.classList.add("table");
                    cuotaOption.classList.add("table-light");
                    valorCredito = parseFloat(cuota.monto_total);
                    valorCuota = parseFloat(cuota.monto);
                    vencimiento = new Date(cuota.fecha_vencimiento);
                    cuota.fecha_vencimiento = vencimiento.toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit'
                    });
                    cuotaOption.innerHTML = `<td scope="row" name="">${cuota.id}</td>
                                            <td scope="row">$${valorCredito.toFixed(2)}</td>
                                            <td scope="row">${cuota.numero_cuota}</td>
                                            <td scope="row">${cuota.fecha_vencimiento}</td>
                                            <td scope="row">$${valorCuota.toFixed(2)}</td>
                                            <td scope="row">${cuota.dias_mora}</td>
                                            <td scope="row">$0</td>
                                            <td scope="row">$0</td>
                                            <td scope="col" onclick="calcularCuota()">
                                                <input type="checkbox" name="cuotas" value="${cuota.id}-${cuota.numero_cuota}" data-monto="${valorCuota.toFixed(2)}" onchange="calcularCuota()">
                                            </td>
                                            <td scope="row">
                                                <a href="#" class="btn btn-secundario">Ver crédito</a>
                                            </td>    
                                        `;
                    lst_cuotas.appendChild(cuotaOption);
                });
            } else {
                console.log('error');
            }
        } else {
            console.log('no ok');
        }
    } catch (error) {
        console.error("Error al obtener cuotas pendientes:", error);
        alert("Error al obtener cuotas pendientes.");
    }
}

function calcularCuota() {
    let total = 0;
    // Selecciona todos los checkboxes de cuotas
    document.querySelectorAll('input[name="cuotas"]:checked').forEach((checkbox) => {
        total += parseFloat(checkbox.getAttribute('data-monto'));
    });
    // Muestra el total donde quieras, por ejemplo en un elemento con id="total_cuotas"
    document.getElementById("total_cuotas").textContent = "$" + total.toFixed(2);
    document.getElementById("edt_total_cuotas").value = total.toFixed(2);
}

function cobrarCuotas() {
    //event.preventDefault();
    if (checkPagos() === false) {
        alert("El monto del pago es menor que el total de cuotas.");
        event.preventDefault();
        return;
    }
    else 
    {
        const checkboxes = document.querySelectorAll('input[name="cuotas"]:checked');
        if (checkboxes.length === 0) {
            alert("Por favor, seleccione al menos una cuota para cobrar.");
            event.preventDefault();
            return;
        }
        else {
            let totalCuotas = 0;
            totalCuotas = parseFloat(document.getElementById("edt_total_cuotas").value);
            let efectivo = parseFloat(document.getElementById("efectivo").value);
            let tarjeta = parseFloat(document.getElementById("tarjeta").value);
            let entidad = document.getElementById("entidad").value;
            const cuotasSeleccionadas = [];
            checkboxes.forEach((checkbox) => {
                const [idCredito, numeroCuota] = checkbox.value.split('-');
                cuotasSeleccionadas.push({ id: idCredito, numero: numeroCuota });
            });
            idCliente = document.getElementById("idcliente").value;

            // Aquí puedes enviar las cuotas seleccionadas al servidor o procesarlas como necesites
            console.log("Cuotas seleccionadas:", cuotasSeleccionadas);
            alert("Cuotas seleccionadas para cobro: " + cuotasSeleccionadas.map(c => c.numero).join(", "));
            fetch(`${BASE_URL}/creditos/cobrar_cuotas`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ cuotas: cuotasSeleccionadas, idCliente: idCliente, totalCuotas: totalCuotas, efectivo: efectivo, tarjeta: tarjeta, entidad: entidad })
            })
            return;
        }    
    }    
}    

function checkPagos() {
    let totalCuotas = 0;
    totalCuotas = parseFloat(document.getElementById("edt_total_cuotas").value);
    if (totalCuotas === 0) {
        alert("Por favor, ingrese un monto para pagar.");
        return false;
    }
    else {
        let efectivo = parseFloat(document.getElementById("efectivo").value);
        let tarjeta = parseFloat(document.getElementById("tarjeta").value);
        if (efectivo === 0 && tarjeta === 0) {
            alert("Por favor, ingrese un monto válido para pagar.");
            return false;
        }
        else {
            console.log("Total Cuotas: ", totalCuotas);
            console.log("Efectivo: ", efectivo);    
            console.log("Tarjeta: ", tarjeta);
            return totalCuotas <= (efectivo + tarjeta);
        }
    }
}

