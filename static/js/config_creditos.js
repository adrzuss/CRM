
async function get_documentos_plan(idplan) {
  try {
    const response = await fetch(`${BASE_URL}/creditos/get_documentos_por_plan/${idplan}`);
    if (response.ok != true) {
        alert("Error al obtener los documentos para el plan.");
        return;
    }
    const data = await response.json();
    if (data) {
      document.getElementById("documentos_plan").innerHTML = "";
      data.documentos.forEach((documento) => {
        const item = document.createElement("li");
        item.innerText = documento.documento;
        const input = document.createElement("input");
        input.classList.add("form-check-input");
        input.classList.add("ml-2");
        input.type = "checkbox";
        input.name = "documentos";
        input.id = "documentos";
        input.checked = (documento.idDocCred != null);
          
        input.value = documento.idDoc;
        item.appendChild(input);
        document.getElementById("documentos_plan").appendChild(item);
      });
    } else {
      alert("Error al obtener los documentos para el plan: " + data.message);
    }
  } catch (error) {
    console.error("Error al obtener los documentos para el plan:", error);
    alert("Error al obtener los documentos para el plan.");
  }
}

document.getElementById("idplandoc").addEventListener("change", function (event) {
  get_documentos_plan(this.value);
});

async function get_categorias_plan(idplan) {
  try {
    const response = await fetch(`${BASE_URL}/creditos/get_categorias_por_plan/${idplan}`);
    if (response.ok != true) {
        alert("Error al obtener los documentos para el plan.");
        return;
    }
    const data = await response.json();
    if (data) {
      document.getElementById("categorias_plan").innerHTML = "";
      data.categorias.forEach((categoria) => {
        const item = document.createElement("li");
        item.innerText = categoria.nombre;
        const input = document.createElement("input");
        input.classList.add("form-check-input");
        input.classList.add("ml-2");
        input.type = "checkbox";
        input.name = "categorias";
        input.id = "categorias";
        input.checked = (categoria.idplan != null);
          
        input.value = categoria.id;
        item.appendChild(input);
        document.getElementById("categorias_plan").appendChild(item);
      });
    } else {
      alert("Error al obtener las categorias para el plan: " + data.message);
    }
  } catch (error) {
    console.error("Error al obtener las categorias para el plan:", error);
    alert("Error al obtener las categorias para el plan.");
  }
}

document.getElementById("idplancategoria").addEventListener("change", function (event) {
  get_categorias_plan(this.value);
});