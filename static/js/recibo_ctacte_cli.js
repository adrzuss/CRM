// Verificar que los elementos existan antes de agregar event listeners
document.addEventListener('DOMContentLoaded', function() {
    const debe = document.getElementById('debe');
    const haber = document.getElementById('haber');

    if (debe && haber) {
        debe.addEventListener('click', ()=> {
            debe.checked = true;
            haber.checked = false;
            habilitar_pagos(false);
        });
        
        haber.addEventListener('click', () => {
            haber.checked = true;        
            debe.checked = false;
            habilitar_pagos(true);
        });
    }

    // Agregar event listener al formulario si existe
    const form = document.getElementById('movCtaCte');
    if (form) {
        form.addEventListener('submit', function(event){
            if (checkMovCtaCte() == false){
                event.preventDefault();
            }
        });
    }
});

function habilitar_pagos(habilitar) {
    
}


function checkMovCtaCte() {
    const fechaInput = document.getElementById('fecha');
    const importeInput = document.getElementById('importe');
    const debe = document.getElementById('debe');
    const haber = document.getElementById('haber');
    
    // Verificar que todos los elementos existan
    if (!fechaInput || !importeInput || !debe || !haber) {
        console.error('No se encontraron todos los elementos del formulario');
        return false;
    }
    
    const inputFecha = fechaInput.value;
    const fecha = new Date(inputFecha);
    const fechaControl = new Date('2024-01-01');
    const importe = parseFloat(importeInput.value);
    
    if (((debe.checked) || (haber.checked)) && (fecha >= fechaControl) && (importe > 0)){
        return true;
    }
    else{
        mostrarAdvertencia('Faltan datos obligatorios');
        return false;
    }
}

// Este event listener se movió dentro del DOMContentLoaded arriba

// Función para manejar punto de venta (separada del DOMContentLoaded principal)
async function initializePuntoVenta() {
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
            mostrarAdvertencia("Debe seleccionar un punto de venta.");
          }
        };
        modalContent.appendChild(confirmButton);
        //---------
        $("#ptovtaModal").modal("show");
      }  
    }
    else{
      // Si punto_vta tiene un valor, asignarlo al elemento si existe
      const puntoVtaElement = document.getElementById("punto_vta");
      if (puntoVtaElement) {
        puntoVtaElement.textContent = 'Punto de venta: ' + data.punto_vta;
      }
    }
  } catch (error) {
    console.error("Error al obtener el punto de venta:", error);
  }
}

// Llamar a la función después de que el DOM esté listo
setTimeout(initializePuntoVenta, 100);

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
      const puntoVtaElement = document.getElementById("punto_vta");
      if (puntoVtaElement) {
        puntoVtaElement.textContent = 'Punto de venta: ' + idPuntoVenta;
      }
      const idclienteElement = document.getElementById("idcliente");
      if (idclienteElement) {
        idclienteElement.focus();
      }
    } else {
      mostrarError('Error al asignar el punto de venta: ' + result.message);
    }
  } catch (error) {
    console.error('Error al llamar a la API:', error);
    mostrarError('Ocurrió un error al asignar el punto de venta.');
  }
};
