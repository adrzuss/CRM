    var datos_plan = [];
    document.getElementById("idcliente").addEventListener("blur", function () {
        const idcliente = this.value;
        fetchCliente(idcliente);
    });

    document.getElementById("idplan").addEventListener("change", function (event) {
        const idPlan = event.target.value;
        if (idPlan != null) {
            setPlanValues(idPlan);
            createPlanDocuments(idPlan);
            createGarantes();
        }
        
    });

    document.getElementById("generar").addEventListener("click", async () => {
        
        const cuotas = document.getElementById("cuotas").value;
        const tasa_interes = document.getElementById("tasa_interes").value;
        const monto_total = document.getElementById("monto_total").value;
        if (cuotas === null || cuotas === "" || tasa_interes === null || tasa_interes === "" || monto_total === null || monto_total === "") {
            alert("Faltan datos obligatorios");
            return;
        }
        response = await fetch(`${BASE_URL}/creditos/generar_cuotas?cuotas=${cuotas}&&tasa_interes=${tasa_interes}&&monto_total=${monto_total}`);
        
        const data = await response.json();
        
        if (response.ok) {
            
            const cronograma = data.cronograma;
            const cuota = data.cuota;
            
            let monto_cuota = document.getElementById("monto_cuota");
            monto_cuota.innerHTML = `Monto cuota: ${cuota}`;
            let cuota_credito = document.getElementById("cuota_credito");
            cuota_credito.value = cuota;
            let lst_cuotas = document.getElementById("lst_cuotas");
            lst_cuotas.innerHTML = "";
            cronograma.forEach((cuota) => {
                const cuotaOption = document.createElement("tr");
                cuotaOption.classList.add("table");
                cuotaOption.classList.add("table-light");
                cuotaOption.innerHTML = `<td scope="row">${cuota.nro_cuota}</td>
                                        <td scope="row">${cuota.cuota}</td>
                                        <td scope="row">${cuota.interes}</td>
                                        <td scope="row">${cuota.capital}</td>
                                        <td scope="row">${cuota.saldo}</td>`;
                lst_cuotas.appendChild(cuotaOption);
            });
        } else {
            console.log('error');
        }
    });

    document.getElementById("otorgamiento_form").addEventListener("submit", function (event) {
        let idCliente = document.getElementById("idcliente").value;
        let idPlan = document.getElementById("idplan").value;
        let cuotas = document.getElementById("cuotas").value;
        let montoTotal = document.getElementById("monto_total").value;
        let tasa_interes = document.getElementById("tasa_interes").value;
        let fecha_solicitud = document.getElementById("fecha_solicitud").value;
        
        if (confirm("¿Grabar los datos del crédito?") === false) {
            event.preventDefault();
        }
    });

    function setPlanValues(idPlan) {
        if (idPlan && datos_plan.length > 0) {
            let planSelecionado = 0;
            for (let i = 0; i < datos_plan.length; i++) {
                if (datos_plan[i].id == idPlan) {
                    planSelecionado = i;
                    break;
                }
            }
            let cuotas = datos_plan[planSelecionado].cuotas;
            let inputCuotas = document.getElementById("cuotas")
            inputCuotas.value = cuotas;
            inputCuotas.max = cuotas;
            let tasa_interes = datos_plan[planSelecionado].tasa_interes;
            let inputTasa_interes = document.getElementById("tasa_interes")
            inputTasa_interes.value = tasa_interes;
            let anticipo = document.getElementById("anticipo");
            anticipo.checked = datos_plan[planSelecionado].anticipo;
            let garantes = document.getElementById("garantes");
            garantes.value = datos_plan[planSelecionado].garantes;
            
        }
    };        

    async function createPlanDocuments(idPlan) {
        response = await fetch(`${BASE_URL}/creditos/get_documentos_por_plan/${idPlan}`);
        if (response.ok) {
            const data = await response.json();
            if (data.documentos.length > 0) {
                let documentosPlan = document.getElementById("documentos_plan");
                documentosPlan.innerHTML = "";
                data.documentos.forEach((documento, indice) => {
                    if (documento.idDocCred != null) {
                        let documentDiv = document.createElement("div");
                        documentDiv.classList.add("row");
                        documentDiv.classList.add("mb-3");
                        documentDiv.innerHTML = `<div class="col-10"> 
                                                <label for="documento${indice+1}">${documento.documento}</label>
                                                <input class="form-control" type="file" name="documento${indice+1}" id="documento${indice+1}" placeholder="Documento" value="${documento.documento}" required>
                                                <input class="form-control" type="number" name="idDocumento${indice+1}" id="idDocumento${indice+1}" value="${documento.idDoc}" hidden>
                                            </div>`;
                        documentosPlan.appendChild(documentDiv);
                    }    
                });
            } else {
                alert("No se encontraron documentos para este plan");
            }    
        }    
    };

    function createGarantes() {
        let garantes = document.getElementById("datos_garantes");
        garantes.innerHTML = "";
        cantGarantes = document.getElementById("garantes").value;
        if (cantGarantes != null) {
            for (let i = 0; i < cantGarantes; i++) {
                garantes.innerHTML += ` <div class="row">
                                            <div class="col-2">
                                                <label for="garante_id_${i+1}"># Garante ${i+1}</label>
                                                <input class="form-control" type="text" name="garante_id_${i+1}" id="garante_id_${i+1}" placeholder="Numero del garante">
                                            </div>
                                            <div class="col-5">
                                                <label for="garante_nombre_${i+1}"># Nombre garante ${i+1}</label>
                                                <input class="form-control" type="text" name="garante_nombre_${i+1}" id="garante_nombre_${i+1}" placeholder="Nombre del garante">
                                            </div>
                                        </div>
                                        `;
            }
            document.querySelectorAll('input[name^="garante_id_"]').forEach(input => {
                input.addEventListener("blur", function () {
                fetchGarante(this);
                });
            });
        } else {
            console.log('error');
        }
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
        document.getElementById("cliente_categoria").value = cliente.categoria;
        planesParaCliente(cliente.idcategoria);
    }

    function limpiarDatosCliente() {
        let idcliente = document.getElementById("idcliente");
        idcliente.value = "";
        document.getElementById("cliente_nombre").value = "";
        document.getElementById("cliente_categoria").value = "";
        document.getElementById("idplan").value = "";
        document.getElementById("cuotas").value = "";
        document.getElementById("tasa_interes").value = "";
        document.getElementById("monto_total").value = "";
        document.getElementById("fecha_solicitud").value = "";
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

    async function fetchGarante(input) {
        const valor = input.value;
        // Aquí puedes guardar el valor anterior si lo necesitas
        // Por ejemplo: input.dataset.valorAnterior = valor;

        if (valor !== "") {
            let response;
            if (!isNaN(valor)) {
                response = await fetch(`${BASE_URL}/clientes/get_cliente/${valor}/1`);
            } else {
                response = await fetch(`${BASE_URL}/clientes/get_clientes?nombre=${valor}&&tipo_operacion=1`);
            }

            if (!response.ok) {
                limpiarDatosGarante(input);
                alert("Error en la búsqueda del garante");
                return;
            }
            const data = await response.json();

            if (data.success && data.cliente) {
                if (data.cliente.baja == true) {
                    limpiarDatosGarante(input);
                    alert("Garante dado de baja.");
                    return;
                }
                asignarGarante(input, data.cliente);
            } else if (data.length === 1) {
                asignarGarante(input, data[0]);
            } else {
                if (data.length > 1) {
                    // Si hay más de un resultado, mostrar un modal para seleccionar
                    mostrarModalSeleccionGarantes(data, input);
                } else 
                {
                    limpiarDatosGarante(input);
                    alert("No se encontró garante.");
                }    
            }
        } else {
            limpiarDatosGarante(input);
        }
    }

    function asignarGarante(input, garante) {
        idCliente = document.getElementById("idcliente").value;
        if ( idCliente === input.value )  {
            limpiarDatosGarante(input);
            alert("No puedes asignar como garante al mismo cliente.");
            input.focus();
            return;
        }
        input.value = garante.id;
        // Buscar el input de nombre relacionado y asignar el nombre
        const row = input.closest('.row');
        if (row) {
            const nombreInput = row.querySelector('input[name^="garante_nombre"]');
            if (nombreInput) {
                nombreInput.value = garante.nombre;
            }
        }
    }

    function limpiarDatosGarante(input) {
        input.value = "";
        const row = input.closest('.row');
        if (row) {
            const nombreInput = row.querySelector('input[name^="garante_nombre"]');
            if (nombreInput) {
                nombreInput.value = "";
            }
        }
    }

    function mostrarModalSeleccionGarantes(garantes, input) {
    // Crear el contenido del modal con las opciones de cliente
    const tituloModal = document.getElementById("clienteModalLabel");
    tituloModal.textContent = "Seleccione un Cliente";
    const modalContent = document.getElementById("modalContent");
    modalContent.innerHTML = "";
    const listaClientes = document.createElement("ul");
    listaClientes.classList.add("list-group");
    modalContent.appendChild(listaClientes);

    garantes.forEach((garante) => {
        const clienteOption = document.createElement("li");
        clienteOption.classList.add("cliente-option");
        clienteOption.classList.add("list-group-item");
        clienteOption.textContent = `${garante.nombre} - Tel/Cel: ${garante.telefono}`;
        clienteOption.onclick = () => {
        asignarGarante(input,garante);
        $("#clienteModal").modal("hide");
        // Enfocar el nuevo input de código
        input.focus();
        };
        listaClientes.appendChild(clienteOption);
    });

    // Mostrar el modal
    $("#clienteModal").modal("show");
    }

    async function planesParaCliente(categoria) {
        const response = await fetch(`${BASE_URL}/creditos/planes_para_cliente/${categoria}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                datos_plan = data.planes;
                let planes = data.planes;
                let planesSeleccionados = document.getElementById("idplan");
                planesSeleccionados.innerHTML = "";
                if (planes.length > 0) {
                    const planesOption = document.createElement("option");
                    planesOption.textContent = 'Seleccione un plan';
                    planesSeleccionados.appendChild(planesOption);
                    planes.forEach((plane) => {
                        const planesOption = document.createElement("option");
                        planesOption.value = plane.id;
                        planesOption.textContent = plane.nombre;
                        planesSeleccionados.appendChild(planesOption);
                    });
                } else {
                    alert("No se encontraron planes para este cliente");
                    limpiarDatosCliente();
                }
            } else {
                console.log('error');
            }
        } else {
            console.log('no ok');
        }
    }
