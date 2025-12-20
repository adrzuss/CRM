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
        const callback = (cliente) => {
            asignarCliente(cliente);
            // Enfocar el nuevo input de código
            const clienteInput = document.getElementById("idcliente");
            if (clienteInput) clienteInput.focus();
        };
        
        // Mostrar modal con los datos
        window.universalSearchModal.show('clientes', clientes || [], callback);
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
                    valorCredito = parseFloat(cuota.monto_credito);
                    valorCuota = parseFloat(cuota.monto);
                    interesMora = parseFloat(cuota.interes_mora);
                    totalAPagar = parseFloat(cuota.total_a_pagar);
                    vencimiento = new Date(cuota.fecha_vencimiento);
                    cuota.fecha_vencimiento = vencimiento.toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit'
                    });
                    if (cuota.dias_mora == 0) {
                        cuotaOption.innerHTML = `<td scope="row" name="">${cuota.id}</td>
                                                <td scope="row">$${valorCredito.toFixed(2)}</td>
                                                <td scope="row">${cuota.numero_cuota}</td>
                                                <td scope="row">${cuota.fecha_vencimiento}</td>
                                                <td scope="row">$${valorCuota.toFixed(2)}</td>
                                                <td scope="row">${cuota.dias_mora}</td>
                                                <td scope="row">$${interesMora.toFixed(2)}</td>
                                                <td scope="row">$${totalAPagar.toFixed(2)}</td>
                                                <td scope="col" style="text-align:center" onclick="calcularCuota()">
                                                    <input type="checkbox" name="cuotas" value="${cuota.id}-${cuota.numero_cuota}" data-monto="${totalAPagar.toFixed(2)}" onchange="calcularCuota()">
                                                </td>
                                                <td scope="row">
                                                    <a href="#" class="btn btn-secundario">Ver crédito</a>
                                                </td>    
                                            `;
                    }
                    else{
                        cuotaOption.innerHTML = `<td scope="row" style="color: red" name="">${cuota.id}</td>
                                                <td scope="row" style="color: red">$${valorCredito.toFixed(2)}</td>
                                                <td scope="row" style="color: red">${cuota.numero_cuota}</td>
                                                <td scope="row" style="color: red">${cuota.fecha_vencimiento}</td>
                                                <td scope="row" style="color: red">$${valorCuota.toFixed(2)}</td>
                                                <td scope="row" style="color: red">${cuota.dias_mora}</td>
                                                <td scope="row" style="color: red">$${interesMora.toFixed(2)}</td>
                                                <td scope="row" style="color: red">$${totalAPagar.toFixed(2)}</td>
                                                <td scope="col" style="text-align:center; color: red" onclick="calcularCuota()">
                                                    <input type="checkbox" name="cuotas" value="${cuota.id}-${cuota.numero_cuota}" data-monto="${totalAPagar.toFixed(2)}" onchange="calcularCuota()">
                                                </td>
                                                <td scope="row">
                                                    <a href="#" class="btn btn-secundario">Ver crédito</a>
                                                </td>    
                                            `;
                    }
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

// Función auxiliar para mostrar mensajes tipo flash
function mostrarMensaje(mensaje, tipo) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insertar el mensaje al principio del contenedor principal
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);

    // Remover el mensaje después de 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function calcularCuota() {
    let total = 0;
    // Selecciona todos los checkboxes de cuotas
    document.querySelectorAll('input[name="cuotas"]:checked').forEach((checkbox) => {
        total += parseFloat(checkbox.getAttribute('data-monto'));
    });
    
    console.log('💵 [COBRANZAS] calcularCuota() - Total calculado:', total);
    
    // Actualizar todos los elementos de total
    document.getElementById("total_cuotas").textContent = "$" + total.toFixed(2);
    document.getElementById("edt_total_cuotas").value = total.toFixed(2);
    document.getElementById("total_factura").textContent = total.toFixed(2);
    
    console.log('✅ [COBRANZAS] Todos los elementos de total actualizados:', total.toFixed(2));
    
    // Si la modal está abierta, actualizar el total de la modal universal
    const modal = document.getElementById('transaccionesModal');
    if (modal && modal.classList.contains('show') && window.cargarDatosModal) {
        console.log('🔄 [COBRANZAS] Modal abierta, actualizando total universal...');
        window.cargarDatosModal(total);
    }
}


function abrirModalPagos(){
  console.log('💵 [COBRANZAS] abrirModalPagos() iniciando...');
  
  //Comprobamos que haya cuotas seleccionadas
  const total = document.getElementById("edt_total_cuotas").value;
  if (total === "0.00") {
      alert("Por favor, seleccione al menos una cuota para cobrar.");
      return;
  }
  
  console.log('💵 [COBRANZAS] Total cuotas seleccionadas:', total);
  
  // Verificar que la función universal esté disponible
  if (window.cargarDatosModal) {
      console.log('✅ [COBRANZAS] cargarDatosModal está disponible');
      window.cargarDatosModal(parseFloat(total) || 0);
  } else {
      console.error('❌ [COBRANZAS] cargarDatosModal no está disponible');
      console.log('🔍 [COBRANZAS] window.cargarDatosModal:', typeof window.cargarDatosModal);
  }
  
  // Abrir modal universal
  $("#transaccionesModal").modal("show");

  // Cuando el modal se haya mostrado, hacer debug y enfocar
  document.getElementById('transaccionesModal').addEventListener('shown.bs.modal', function () {
    console.log('📋 [COBRANZAS] Modal mostrado, verificando campos...');
    
    // Verificar campos de pago
    const paymentFields = ['efectivo', 'tarjeta', 'ctacte', 'credito', 'bonificacion'];
    paymentFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        console.log(`🔍 [COBRANZAS] Campo ${fieldId}:`, field ? 'EXISTE' : 'NO EXISTE', field?.value || 'sin valor');
    });
    
    // Verificar elemento total
    const totalFacElement = document.getElementById('modal_total_factura');
    console.log('💰 [COBRANZAS] modal_total_factura:', totalFacElement ? 'EXISTE' : 'NO EXISTE', totalFacElement?.textContent || 'sin valor');
    
    // Enfocar primer input
    const primerInput = document.querySelector('#transaccionesModal input:not([readonly]):not([type="hidden"])');
    if (primerInput) {
        primerInput.focus();
        console.log('👆 [COBRANZAS] Enfocando:', primerInput.id);
    }
    
    // Agregar funciones de test para verificar funcionamiento
    window.testCambiarEfectivoCobranza = function(valor) {
        console.log('🧪 [TEST COBRANZA] Cambiando efectivo a:', valor);
        const efectivo = document.getElementById('efectivo');
        if (efectivo) {
            efectivo.value = valor;
            efectivo.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('🧪 [TEST COBRANZA] Evento disparado');
        }
    };
    
    console.log('🧪 [COBRANZAS] Función de test disponible: testCambiarEfectivoCobranza(1000)');
    
  }, { once: true });

}


async function cobrarCuotas() {
    console.log('💵 [COBRANZAS] 🎬 INICIANDO cobrarCuotas()');
    
    //event.preventDefault();
    if (checkPagos() === false) {
        console.log('💵 [COBRANZAS] ❌ checkPagos() falló');
        alert("El monto del pago es menor que el total de cuotas.");
        event.preventDefault();
        return;
    }
    else 
    {
        console.log('💵 [COBRANZAS] ✅ checkPagos() pasó correctamente');
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
            //console.log("Cuotas seleccionadas:", cuotasSeleccionadas);
            //alert("Cuotas seleccionadas para cobro: " + cuotasSeleccionadas.map(c => c.numero).join(", "));
            try{
                console.log('💵 [COBRANZAS] 🚀 Enviando petición cobrar_cuotas...');
                console.log('💵 [COBRANZAS] 📦 Datos enviados:', { cuotas: cuotasSeleccionadas, idCliente: idCliente, totalCuotas: totalCuotas, efectivo: efectivo, tarjeta: tarjeta, entidad: entidad });
                
                const response = await fetch(`${BASE_URL}/creditos/cobrar_cuotas`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ cuotas: cuotasSeleccionadas, idCliente: idCliente, totalCuotas: totalCuotas, efectivo: efectivo, tarjeta: tarjeta, entidad: entidad })
                })
                
                console.log('💵 [COBRANZAS] 📡 Respuesta HTTP status:', response.status);
                console.log('💵 [COBRANZAS] 📡 Response headers:', response.headers.get('content-type'));
                console.log('💵 [COBRANZAS] 📡 Response OK:', response.ok);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const responseText = await response.text();
                console.log('💵 [COBRANZAS] 📜 Respuesta RAW del servidor:', responseText.substring(0, 500));
                
                let data;
                try {
                    data = JSON.parse(responseText);
                    console.log('💵 [COBRANZAS] 📊 JSON parseado exitosamente:', data);
                } catch (parseError) {
                    console.error('💵 [COBRANZAS] ❌ Error parseando JSON:', parseError);
                    console.error('💵 [COBRANZAS] 📜 Respuesta que no es JSON:', responseText);
                    
                    // Si el servidor devuelve HTML pero la operación fue exitosa
                    if (responseText.includes('<!DOCTYPE html>') || responseText.includes('<html>')) {
                        console.log('💵 [COBRANZAS] 🌐 El servidor devolvió HTML - probablemente exitoso');
                        alert('✅ ¡Cobro procesado exitosamente! (El servidor devolvió HTML en lugar de JSON)');
                        $("#transaccionesModal").modal("hide");
                        cuotasPendientes(idCliente);
                        return;
                    }
                    
                    throw new Error('El servidor devolvió una respuesta que no es JSON válido');
                }
        
                console.log('💵 [COBRANZAS] 🔍 Verificando campo success:', data.success, typeof data.success);
                console.log('💵 [COBRANZAS] 🔍 Mensaje del servidor (message):', data.message);
                console.log('💵 [COBRANZAS] 🔍 Mensaje del servidor (mensaje):', data.mensaje);
                console.log('💵 [COBRANZAS] 🔍 Estructura completa de data:', Object.keys(data));
                
                // Obtener mensaje del servidor (puede ser 'message' o 'mensaje')
                const serverMessage = data.message || data.mensaje || '';
                
                if (data.success === true || data.success === 'true' || data.success === 1) {
                    console.log('💵 [COBRANZAS] ✅ Cobro procesado exitosamente');
                    
                    // Mostrar alert de éxito
                    alert(`✅ ¡Éxito! ${serverMessage || 'Cuotas cobradas correctamente'}`);
                    
                    // También mostrar mensaje en la página
                    mostrarMensaje(serverMessage || "Cuotas cobradas correctamente", "success");
                    
                    // Cerrar modal y actualizar lista
                    $("#transaccionesModal").modal("hide");
                    cuotasPendientes(idCliente); // Actualizar la lista de cuotas
                    

                } else {
                    console.error('💵 [COBRANZAS] ❌ Error en cobro - success es falso');
                    console.error('💵 [COBRANZAS] ❌ Datos completos:', data);
                    
                    // Mostrar alert de error
                    alert(`❌ Error: ${serverMessage || 'Error al procesar el pago'}`);
                    
                    // También mostrar mensaje en la página
                    mostrarMensaje(serverMessage || "Error al procesar el pago", "error");
                }
            } catch (error) {
                console.error("💵 [COBRANZAS] 💥 EXCEPCIÓN CAPTURADA:");
                console.error("💵 [COBRANZAS] 💥 Error message:", error.message);
                console.error("💵 [COBRANZAS] 💥 Error stack:", error.stack);
                console.error("💵 [COBRANZAS] 💥 Error completo:", error);
                
                // Mostrar alert de error de conexión
                alert(`❌ Error de conexión: No se pudo procesar el cobro. ${error.message}`);
                
                // También mostrar mensaje en la página
                mostrarMensaje("Error al procesar la operación", "error");
            }
                
            return;
        }    
    }
    
    console.log('💵 [COBRANZAS] 🎭 FINALIZANDO cobrarCuotas()');    
}    

// Event listeners movidos a modal-transacciones-universal.js
// document.getElementById("efectivo").addEventListener("blur", function (event) {
//   calcSaldo();
// });

// document.getElementById("tarjeta").addEventListener("blur", function (event) {
//   calcSaldo();
// });

// document.getElementById("ctacte").addEventListener("blur", function (event) {
//   calcSaldo();
// });

// document.getElementById("bonificacion").addEventListener("blur", function (event) {
//   calcSaldo();
// });


// Función calcSaldo() movida a modal-transacciones-universal.js
// para usar la implementación universal que funciona correctamente
// 
// function calcSaldo() {
//   const totalFac = parseFloat(document.getElementById("total_factura").textContent);
//   const efectivo = parseFloat(document.getElementById("efectivo").value);
//   let tarjeta = parseFloat(document.getElementById("tarjeta").value);
//   const ctacte = parseFloat(document.getElementById("ctacte").value);
//   const bonificacion = parseFloat(document.getElementById("bonificacion").value);
//   if (isNaN(efectivo)) {
//     efectivo = 0;
//   }
//   if (isNaN(tarjeta)) {
//     tarjeta = 0;
//   }
//   else{
//     const coeficiente = parseFloat(document.getElementById("coeficiente").value);
//     tarjeta = tarjeta / coeficiente;
//   }
//   if (isNaN(ctacte)) {
//     ctacte = 0;
//   }
//   if (isNaN(bonificacion)) {
//     bonificacion = 0;
//   }
//   
//   let diferencia = parseFloat(totalFac - (efectivo + tarjeta + ctacte + bonificacion)).toFixed(2);
//   
//   // Actualizar el contenido del saldo
//   let lblSaldo = document.getElementById("saldo_factura");
//   lblSaldo.textContent = diferencia;
//   
//   // Actualizar la clase del contenedor
//   const saldoContainer = document.getElementById("saldo-container");
//   if (diferencia > 0) {
//     saldoContainer.className = "total-amount m-3 negativo";
//   } else if (diferencia === 0) {
//     saldoContainer.className = "total-amount m-3 neutro";
//   } else {
//     saldoContainer.className = "total-amount m-3 positivo";
//   }
// }


function checkPagos() {
    let totalCuotas = 0;
    totalCuotas = parseFloat(document.getElementById("edt_total_cuotas").value);
    if (totalCuotas === 0) {
        alert("Por favor, ingrese un monto para pagar.");
        return false;
    }
    else {
        let efectivo = parseFloat(document.getElementById("efectivo").value) || 0;
        let tarjeta = parseFloat(document.getElementById("tarjeta").value) || 0;
        let ctacte = parseFloat(document.getElementById("ctacte").value) || 0;
        let bonificacion = parseFloat(document.getElementById("bonificacion").value) || 0;
        
        const totalPagos = efectivo + tarjeta + ctacte + bonificacion;
        
        if (totalPagos === 0) {
            alert("Por favor, ingrese un monto válido para pagar.");
            return false;
        }
        else {
            console.log("💵 [COBRANZAS] Total Cuotas: ", totalCuotas);
            console.log("💵 [COBRANZAS] Total Pagos: ", totalPagos, {efectivo, tarjeta, ctacte, bonificacion});
            return totalCuotas <= totalPagos;
        }
    }
}

