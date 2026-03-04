// Manejo de acciones en el listado de remitos
document.addEventListener('DOMContentLoaded', function() {
    const modalDetalle = new bootstrap.Modal(document.getElementById('modalDetalleRemito'));
    
    // Ver detalle del remito
    document.querySelectorAll('.ver-detalle').forEach(btn => {
        btn.addEventListener('click', async function() {
            const idRemito = this.dataset.id;
            const contenedor = document.getElementById('contenidoDetalleRemito');
            
            // Mostrar spinner
            contenedor.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                </div>
            `;
            
            modalDetalle.show();
            
            try {
                const response = await fetch(`${BASE_URL}/articulos/detalle_remito_sucursal/${idRemito}`);
                const data = await response.json();
                
                if (data.success) {
                    const remito = data.remito;
                    let estadoBadge = '';
                    
                    if (remito.estado_key === 'PENDIENTE') {
                        estadoBadge = '<span class="badge bg-warning text-dark">Pendiente</span>';
                    } else if (remito.estado_key === 'ENVIADO') {
                        estadoBadge = '<span class="badge bg-info text-dark">Enviado</span>';
                    } else if (remito.estado_key === 'RECIBIDO') {
                        estadoBadge = '<span class="badge bg-success">Recibido</span>';
                    }
                    
                    let html = `
                        <div class="mb-3">
                            <h6>Información del Remito</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Remito #:</strong></td>
                                    <td>${remito.id}</td>
                                </tr>
                                <tr>
                                    <td><strong>Fecha:</strong></td>
                                    <td>${remito.fecha}</td>
                                </tr>
                                <tr>
                                    <td><strong>Origen:</strong></td>
                                    <td>${remito.origen}</td>
                                </tr>
                                <tr>
                                    <td><strong>Destino:</strong></td>
                                    <td>${remito.destino}</td>
                                </tr>
                                <tr>
                                    <td><strong>Estado:</strong></td>
                                    <td>${estadoBadge}</td>
                                </tr>
                                <tr>
                                    <td><strong>Usuario:</strong></td>
                                    <td>${remito.usuario}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div>
                            <h6>Artículos</h6>
                            <table class="table table-striped table-sm">
                                <thead>
                                    <tr>
                                        <th>Código</th>
                                        <th>Descripción</th>
                                        <th>Cantidad</th>
                                        <th>Color</th>
                                        <th>Detalle</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    remito.items.forEach(item => {
                        html += `
                            <tr>
                                <td>${item.codigo}</td>
                                <td>${item.detalle}</td>
                                <td>${item.cantidad}</td>
                                <td>${item.color || '-'}</td>
                                <td>${item.detalle_art || '-'}</td>
                            </tr>
                        `;
                    });
                    
                    html += `
                                </tbody>
                            </table>
                        </div>
                    `;
                    
                    contenedor.innerHTML = html;
                } else {
                    contenedor.innerHTML = `
                        <div class="alert alert-danger">
                            Error: ${data.message}
                        </div>
                    `;
                }
            } catch (error) {
                contenedor.innerHTML = `
                    <div class="alert alert-danger">
                        Error al cargar el detalle del remito
                    </div>
                `;
                console.error('Error:', error);
            }
        });
    });
    
    // Enviar remito
    document.querySelectorAll('.enviar-remito').forEach(btn => {
        btn.addEventListener('click', async function() {
            const idRemito = this.dataset.id;
            
            if (!confirm('¿Está seguro de enviar este remito? Se descontará del stock actual de esta sucursal.')) {
                return;
            }
            
            try {
                const response = await fetch(`${BASE_URL}/articulos/enviar_remito_sucursal/${idRemito}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            } catch (error) {
                alert('Error al enviar el remito');
                console.error('Error:', error);
            }
        });
    });
    
    // Controlar/Recibir remito
    document.querySelectorAll('.controlar-remito').forEach(btn => {
        btn.addEventListener('click', async function() {
            const idRemito = this.dataset.id;
            
            if (!confirm('¿Está seguro de controlar y recibir este remito? Los artículos se agregarán al stock actual.')) {
                return;
            }
            
            try {
                const response = await fetch(`${BASE_URL}/articulos/recibir_remito_sucursal/${idRemito}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            } catch (error) {
                alert('Error al controlar el remito');
                console.error('Error:', error);
            }
        });
    });
});
