let articuloSeleccionTipo = null; // 'origen' o 'destino'

document.addEventListener('DOMContentLoaded', function() {

    
    const condicionesContainer = document.getElementById('condiciones-container');
    console.log('obtengo el tipo de oferta');
    const tipoOferta = document.getElementById('tipo_oferta');
    console.log('El tipo de oferta es: ', tipoOferta.value);    
    const seccionVinculada = document.getElementById('seccion-vinculada');
    const seccionRegla = document.getElementById('seccion-regla');
    const seccionNormal = document.getElementById('seccion-normal');

    // Función para manejar cambio de tipo de condición
    function handleTipoCondicionChange(condicionItem) {
        console.log('change condicion');
        const tipoSelect = condicionItem.querySelector('.tipo-condicion');
        const selectContainer = condicionItem.querySelector('.select-container');
        const articuloContainer = condicionItem.querySelector('.articulo-container');
        const referenciaSelect = condicionItem.querySelector('.referencia');
        const idArticuloInput = articuloContainer.querySelector('.id-articulo');
        
        // Verificar que el select tenga una opción seleccionada
        //bbbbbbbbbbbb
        if (tipoSelect.selectedIndex >= 0) {
            const tipoSeleccionado = tipoSelect.options[tipoSelect.selectedIndex].text.toLowerCase();
            console.log("Tipo condición seleccionado: ", tipoSeleccionado);
            if (tipoSeleccionado === 'articulo') {
                // Configuración para artículos
                selectContainer.style.display = 'none';
                articuloContainer.style.display = 'block';
                
                // Deshabilitar y quitar name del select
                referenciaSelect.removeAttribute('required');
                referenciaSelect.setAttribute('disabled', 'disabled');
                referenciaSelect.name = '';  // Importante: quitar el name
                
                // Habilitar y agregar name al input de artículo
                idArticuloInput.name = 'referencia[]';
                articuloContainer.querySelector('.codigo-articulo').setAttribute('required', 'required');
            } else {
                // Configuración para otros tipos (marca, rubro, etc)
                selectContainer.style.display = 'block';
                articuloContainer.style.display = 'none';
                
                // Habilitar y agregar name al select
                referenciaSelect.setAttribute('required', 'required');
                referenciaSelect.removeAttribute('disabled');
                referenciaSelect.name = 'referencia[]';
                
                // Deshabilitar y quitar name del input de artículo
                idArticuloInput.name = '';
                articuloContainer.querySelector('.codigo-articulo').removeAttribute('required');
            }
        }
        // Mostrar secciones según tipo de oferta inicial
        const tipoInicial = tipoOferta.value;
        console.log("Tipo de oferta inicial: ", tipoInicial);
        setTipoOfertaOptions(tipoInicial);
    }

    // Cargar datos iniciales de artículos vinculados
    async function cargarDatosArticulos() {
        if ('{{ vinculos }}' !== 'None') {
            if ('{{ vinculos.id_articulo_origen }}') {
                console.log('3');
                const responseOrigen = await fetch(`${BASE_URL}/articulos/articulo_id/{{ vinculos.id_articulo_origen }}`);
                const dataOrigen = await responseOrigen.json();
                if (dataOrigen.success) {
                    asignarArticulo('origen', dataOrigen.articulo);
                }
            }
            if ('{{ vinculos.id_articulo_destino }}') {
                console.log('4');
                const responseDestino = await fetch(`${BASE_URL}/articulos/articulo_id/{{ vinculos.id_articulo_destino }}`);
                const dataDestino = await responseDestino.json();
                if (dataDestino.success) {
                    asignarArticulo('destino', dataDestino.articulo);
                }
            }
        }
    }

    async function cargarReferenciasIniciales() {
        console.log('Cargando referencias iniciales...');
        const condiciones = document.querySelectorAll('.condicion-item');
        if (condiciones.length > 0) {
            console.log('Tengo condiciones');
                for (let condicion of condiciones) {
                    const tipoSelect = condicion.querySelector('.tipo-condicion');
                    console.log('Tipo de condicion: ', tipoSelect.options[tipoSelect.selectedIndex].text);
                    // Leer el valor de referencia desde el input hidden .id-articulo si existe, si no desde el select
                    let idReferencia = condicion.querySelector('.id-articulo')?.value;
                    if ((!idReferencia) && (typeof referenciaSelect !== 'undefined')) {

                        idReferencia = referenciaSelect.value;
                    }
                    else{
                        if (typeof referenciaSelect !== 'undefined'){
                            ///ccccccccccccc
                        }
                    }
                if (tipoSelect && tipoSelect.selectedIndex >= 0) {
                    const referenciaSelect = condicion.querySelector('.referencia');
                    const tipoSeleccionado = tipoSelect.options[tipoSelect.selectedIndex].text.toLowerCase();
                    const idReferencia = condicion.querySelector('.id-articulo')?.value || 
                                    referenciaSelect.getAttribute('data-id-referencia');

                    if (tipoSeleccionado === 'articulo') {
                        console.log('Datos de articulo');
                        if (idReferencia) {
                            const response = await fetch(`${BASE_URL}/articulos/articulo_id/${idReferencia}`);
                            const data = await response.json();
                            if (data.success) {
                                asignarArticuloCondicion(condicion.querySelector('.articulo-container'), data.articulo);
                            }
                        }
                    } else if (tipoSelect.value) {
                        const response = await fetch(`${BASE_URL}/ofertas/get_referencias/${tipoSelect.value}`);
                        const data = await response.json();
                        
                        referenciaSelect.innerHTML = '<option value="">Seleccione una opción</option>';
                        data.forEach(item => {
                            const option = document.createElement('option');
                            option.value = item.id;
                            option.textContent = item.nombre;
                            if (item.id == idReferencia) {
                                option.selected = true;
                            }
                            referenciaSelect.appendChild(option);
                        });
                        referenciaSelect.disabled = false;
                    }
                }
            }
        }
    }


    // Cargar datos de artículos en condiciones
    async function cargarDatosCondiciones() {
        const condiciones = document.querySelectorAll('.condicion-item');
        if (condiciones.length > 0) {
            for (let condicion of condiciones) {
                const tipoSelect = condicion.querySelector('.tipo-condicion');
                if (tipoSelect && tipoSelect.selectedIndex >= 0 && 
                    tipoSelect.options[tipoSelect.selectedIndex].text.toLowerCase() === 'articulo') {
                    const articuloContainer = condicion.querySelector('.articulo-container');
                    const idArticulo = articuloContainer.querySelector('.id-articulo').value;
                    if (idArticulo) {
                        const response = await fetch(`${BASE_URL}/articulos/articulo_id/${idArticulo}`);
                        const data = await response.json();
                        if (data.success) {
                            asignarArticuloCondicion(articuloContainer, data.articulo);
                        }
                    }
                }
            }
        }
    }

    // Ejecutar carga inicial
    console.log('Cargando...')
    cargarDatosArticulos();
    cargarDatosCondiciones();
    cargarReferenciasIniciales();
  
    // Cargar artículos para ofertas vinculadas
    async function buscarArticulo(tipo, codigo) {
        try {
            const idlista = 1;
            let response; 
            console.log('7');
            response = await fetch(`${BASE_URL}/articulos/articulo/${codigo}/${idlista}`);
            //const response = await fetch(`/articulos/buscar/${codigo}`);
            if (!response.ok) {
                response = await fetch(`${BASE_URL}/articulos/get_articulos?detalle=${codigo}&idlista=${idlista}`);
            }
            if (!response.ok) {
                console.error('Error en la búsqueda del artículo:', response.statusText);
                throw new Error('Error en la búsqueda del artículo');
            }
            const data = await response.json();
            if (data.success) {
                // Si solo hay un artículo, seleccionarlo directamente
                asignarArticulo(tipo, data.articulo);
            } else if (data.length > 1) {
                // Si hay múltiples artículos, mostrar modal
                articuloSeleccionTipo = tipo;
                mostrarModalArticulos(data);
            } else {
                // No se encontraron artículos
                limpiarArticulo(tipo);
                alert('No se encontró ningún artículo');
            }
        } catch (error) {
            console.error('Error buscando artículo:', error);
            alert('Error al buscar artículo');
        }
    }

    function mostrarModalArticulos(articulos, container = null) {
        const tbody = document.getElementById('tablaArticulos');
        tbody.innerHTML = '';
        
        articulos.forEach(art => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${art.codigo}</td>
                <td>${art.detalle}</td>
                <td>${art.marca}</td>
                <td>${art.precio}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-primary seleccionar-articulo" 
                        data-id="${art.id}"
                        data-codigo="${art.codigo}"
                        data-detalle="${art.detalle}"
                        data-marca="${art.marca}">
                        Seleccionar
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Agregar event listeners a los botones
        tbody.querySelectorAll('.seleccionar-articulo').forEach(boton => {
            boton.addEventListener('click', function() {
                const articulo = {
                    id: this.dataset.id,
                    codigo: this.dataset.codigo,
                    detalle: this.dataset.detalle,
                    marca: this.dataset.marca
                };
                
                if (container) {
                    asignarArticuloCondicion(container, articulo);
                } else {
                    asignarArticulo(articuloSeleccionTipo, articulo);
                }
                
                $('#modalArticulos').modal('hide');
            });
        });
        
        $('#modalArticulos').modal('show');
    }

    // Agregar event listeners para los inputs de artículos
    document.getElementById('codigo_articulo_origen').addEventListener('blur', function() {
        if (this.value) buscarArticulo('origen', this.value);
    });

    document.getElementById('codigo_articulo_destino').addEventListener('blur', function() {
        if (this.value) buscarArticulo('destino', this.value);
    });

    // Mostrar/ocultar secciones según tipo de oferta
    tipoOferta.addEventListener('change', function() {
        //aaaaaaaaaaaa
        setTipoOfertaOptions(this.value);
    });
        
    condicionesContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('remover-condicion') || 
            e.target.closest('.remover-condicion')) {
            const condicionItem = e.target.closest('.condicion-item');
            if (condicionesContainer.querySelectorAll('.condicion-item').length > 1) {
                condicionItem.remove();
            }
        }
    });

    condicionesContainer.addEventListener('change', async function(e) {
        console.log('Cambio de condiciones')
        if (e.target.classList.contains('tipo-condicion')) {
            const condicionItem = e.target.closest('.condicion-item');
            handleTipoCondicionChange(condicionItem);
            const selectContainer = condicionItem.querySelector('.select-container');
            const articuloContainer = condicionItem.querySelector('.articulo-container');
            const referenciaSelect = condicionItem.querySelector('.referencia');
            const idArticulo = articuloContainer.querySelector('.id-articulo');

            const tipoSeleccionado = e.target.options[e.target.selectedIndex].text.toLowerCase();
            if (tipoSeleccionado === 'articulo') { 
                selectContainer.style.display = 'none';
                articuloContainer.style.display = 'block';
                referenciaSelect.removeAttribute('required');
                articuloContainer.querySelector('.codigo-articulo').setAttribute('required', 'required');

                // Si hay un ID de artículo, cargar sus datos
                if (idArticulo.value) {
                    console.log('1');
                    const response = await fetch(`${BASE_URL}/articulos/articulo/${idArticulo.value}/1`);
                    const data = await response.json();
                    if (data.success) {
                        asignarArticuloCondicion(articuloContainer, data.articulo);
                    }
                }
                
                // Inicializar el input de artículo
                const codigoInput = articuloContainer.querySelector('.codigo-articulo');
                codigoInput.addEventListener('blur', async function() {
                    if (this.value) {
                        try {
                            const idlista = 1;
                            console.log('2');
                            let response = await fetch(`${BASE_URL}/articulos/articulo/${this.value}/${idlista}`);
                            
                            if (!response.ok) {
                                response = await fetch(`${BASE_URL}/articulos/get_articulos?detalle=${this.value}&idlista=${idlista}`);
                            }
                            
                            if (!response.ok) {
                                throw new Error('Error en la búsqueda del artículo');
                            }

                            const data = await response.json();
                            
                            if (data.success) {
                                // Un solo artículo encontrado
                                asignarArticuloCondicion(articuloContainer, data.articulo);
                            } else if (data.length > 1) {
                                // Múltiples artículos encontrados
                                articuloSeleccionTipo = 'condicion';
                                mostrarModalArticulos(data, articuloContainer);
                            } else {
                                alert('No se encontró ningún artículo');
                            }
                        } catch (error) {
                            console.error('Error:', error);
                            alert('Error al buscar artículo');
                        }
                    }
                });
            } else {
                // Mostrar select normal
                selectContainer.style.display = 'block';
                articuloContainer.style.display = 'none';
                
                // Cargar referencias normales
                referenciaSelect.disabled = true;
                referenciaSelect.innerHTML = '<option value="">Cargando...</option>';

                try {
                    const response = await fetch(`${BASE_URL}/ofertas/get_referencias/${e.target.value}`);
                    const data = await response.json();
                    
                    referenciaSelect.innerHTML = '<option value="">Seleccione una opción</option>';
                    data.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item.id;
                        option.textContent = item.nombre;
                        referenciaSelect.appendChild(option);
                    });
                    referenciaSelect.disabled = false;
                } catch (error) {
                    console.error('Error cargando referencias:', error);
                    referenciaSelect.innerHTML = '<option value="">Error al cargar</option>';
                }
            }
        }
    });

    document.querySelectorAll('.condicion-item').forEach(condicionItem => {
        handleTipoCondicionChange(condicionItem);
    });

    document.getElementById('agregar-condicion').addEventListener('click', function() {
        // Obtener la primera condición como template
        const templateCondicion = document.querySelector('.condicion-item');
        if (!templateCondicion) return;
        
        // Clonar el template
        const nuevaCondicion = templateCondicion.cloneNode(true);
        
        // Limpiar valores
        const selects = nuevaCondicion.querySelectorAll('select');
        
        selects.forEach(select => {
            select.value = '';
            if (select.classList.contains('referencia')) {
                select.innerHTML = '<option value="">Primero seleccione un tipo</option>';
            }
        });

        // Limpiar contenedores de artículos
        const articuloContainer = nuevaCondicion.querySelector('.articulo-container');
        if (articuloContainer) {
            articuloContainer.querySelector('.id-articulo').value = '';
            articuloContainer.querySelector('.codigo-articulo').value = '';
            articuloContainer.querySelector('.desc-articulo').textContent = '';
            articuloContainer.style.display = 'none';
        }

        // Mostrar el select container
        const selectContainer = nuevaCondicion.querySelector('.select-container');
        if (selectContainer) {
            selectContainer.style.display = 'block';
        }

        // Agregar la nueva condición al contenedor
        document.getElementById('condiciones-container').appendChild(nuevaCondicion);
    });

    function setTipoOfertaOptions(tipo) {
        console.log('change tipo oferta: ', tipo);
        seccionVinculada.style.display = 'none';
        seccionRegla.style.display = 'none';
        seccionNormal.style.display = 'none';
        const tipoCondicion = document.querySelector('.tipo-condicion');
        const referencia = document.querySelector('.referencia');
        switch(tipo) {
            case 'vinculada':
                seccionVinculada.style.display = 'block';
                seccionRegla.style.display = 'none';
                cargarDatosArticulos();
                tipoCondicion.removeAttribute('required');
                referencia.removeAttribute('required');
                break;
            case 'mayor_menor_valor':
                seccionRegla.style.display = 'block';
                seccionNormal.style.display = 'block';
                tipoCondicion.setAttribute('required', 'required');
                referencia.setAttribute('required', 'required');
                break;
            default:
                seccionNormal.style.display = 'block';
                tipoCondicion.setAttribute('required', 'required');
                referencia.setAttribute('required', 'required');
        }
    }    

    function seleccionarArticulo(tipo, boton) {
        const articulo = {
            id: boton.dataset.id,
            codigo: boton.dataset.codigo,
            detalle: boton.dataset.detalle,
            marca: boton.dataset.marca
        };
        asignarArticulo(tipo, articulo);
        $('#modalArticulos').modal('hide');
}

    function asignarArticulo(tipo, articulo) {
            document.getElementById(`id_articulo_${tipo}`).value = articulo.id;
            document.getElementById(`codigo_articulo_${tipo}`).value = articulo.codigo;
            document.getElementById(`desc_articulo_${tipo}`).textContent = `${articulo.marca} - ${articulo.detalle}`;
    }

    function limpiarArticulo(tipo) {
        document.getElementById(`id_articulo_${tipo}`).value = '';
        document.getElementById(`codigo_articulo_${tipo}`).value = '';
        document.getElementById(`desc_articulo_${tipo}`).textContent = '';
    }

    // Función para asignar artículo en condiciones
    function asignarArticuloCondicion(container, articulo) {
        console.log('articulo: ', articulo);
        if (articulo != null) {
            container.querySelector('.id-articulo').value = articulo.id;
            container.querySelector('.codigo-articulo').value = articulo.codigo;
            container.querySelector('.desc-articulo').textContent = `${articulo.marca} - ${articulo.detalle}`;
        }    
    }

});