const debe = document.getElementById('debe');
const haber = document.getElementById('haber');

debe.addEventListener('click', ()=> {
        debe.checked = true;
        haber.checked = false;
        habilitar_pagos(false);
    }
);
haber.addEventListener('click', () => {
        haber.checked = true;        
        debe.checked = false;
        habilitar_pagos(true);
    }
);

function habilitar_pagos(habilitar) {
    
}


function checkMovCtaCte() {
    const inputFecha = document.getElementById('fecha').value;
    const fecha = new Date(inputFecha);
    const fechaControl = new Date('2024-01-01');
    const importe = parseFloat(document.getElementById('importe').value)
    
    if (((debe.checked) || (haber.checked)) && (fecha >= fechaControl) && (importe > 0)){
        return true
    }
    else{
        alert('faltan datos')
        return false;
    }
    
}

document.getElementById('movCtaCte').addEventListener('submit', function(event){
    if (checkMovCtaCte() == false){
        event.preventDefault();
    }

});

document.addEventListener("DOMContentLoaded", async function () {
  try {
    // Realizar la solicitud a la API
    const response = await fetch(`${BASE_URL}/get_punto_vta`);
    const data = await response.json(); 
    // Verificar el valor de punto_vta
    if (!data.punto_vta) {
      // Si punto_vta es null o no está definido, mostrar el modal
      const ptosVtasSucursal = await fetch(`${BASE_URL}/get_puntos_vta_sucursal`);
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
      document.getElementById("punto_vta").textContent = 'Punto de venta: ' + data.punto_vta;
    }
  } catch (error) {
    console.error("Error al obtener el punto de venta:", error);
  }
});

async function asignarPuntoVenta(idPuntoVenta) {
  try {
    // Llamar a la API para asignar el punto de venta a la sesión
    const response = await fetch(`${BASE_URL}/set_punto_vta}`, {
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
