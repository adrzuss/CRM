/**
 * Modal Color Detalle Manager
 * Sistema para selección modal de colores y detalles en transacciones
 */
class ModalColorDetalleManager {
    constructor() {
        this.modal = null;
        this.currentArticleId = null;
        this.currentRowIndex = null;
        this.selectedColorId = null;
        this.selectedDetalleId = null;
        this.requiredColor = false;
        this.requiredDetalle = false;
        this.callback = null;
        this.isReady = false;
        
        this.init();
    }
    
    init() {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initWhenReady());
        } else {
            this.initWhenReady();
        }
    }
    
    initWhenReady() {
        // Esperar a que Bootstrap esté disponible
        this.waitForBootstrap().then(() => {
            this.initModal();
            this.bindEvents();
            this.isReady = true;
        });
    }
    
    waitForBootstrap() {
        return new Promise((resolve) => {
            const checkBootstrap = () => {
                // Priorizar jQuery ya que Bootstrap 4 depende de él
                if (typeof $ !== 'undefined' && $.fn.modal) {
                    resolve();
                } else if (typeof bootstrap !== 'undefined') {
                    resolve();
                } else {
                    setTimeout(checkBootstrap, 50);
                }
            };
            checkBootstrap();
        });
    }

    initModal() {
        // Detectar qué versión de Bootstrap está disponible
        this.modalElement = document.getElementById('modalColorDetalle');
        
        if (!this.modalElement) {
            console.error('Error: No se encontró el elemento #modalColorDetalle');
            return;
        }
        
        // Priorizar jQuery/Bootstrap 4 ya que es lo que realmente se usa en el proyecto
        if (typeof $ !== 'undefined' && $.fn.modal) {
            // Bootstrap 4 con jQuery
            this.modal = {
                show: () => {
                    $(this.modalElement).modal({
                        backdrop: 'static',
                        keyboard: false,
                        show: true
                    });
                },
                hide: () => {
                    $(this.modalElement).modal('hide');
                }
            };
            this.isBootstrap4 = true;
            

        } else if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            // Bootstrap 5+ (por si acaso)
            this.modal = new bootstrap.Modal(this.modalElement);
            this.isBootstrap4 = false;
        } else {
            // Fallback manual
            this.modal = {
                show: () => {
                    this.modalElement.style.display = 'block';
                    this.modalElement.classList.add('show');
                    document.body.classList.add('modal-open');
                },
                hide: () => {
                    this.modalElement.style.display = 'none';
                    this.modalElement.classList.remove('show');
                    document.body.classList.remove('modal-open');
                }
            };
            this.isBootstrap4 = false;
        }
        
        // Referencias a elementos DOM
        this.seccionColores = document.getElementById('seccion-colores');
        this.seccionDetalles = document.getElementById('seccion-detalles');
        this.sinOpciones = document.getElementById('sin-opciones');
        this.coloresGrid = this.modalElement.querySelector('.colores-grid-modal');
        this.detallesGrid = this.modalElement.querySelector('.detalles-grid-modal');
        this.articuloInfo = document.getElementById('modal-articulo-info');
        this.btnConfirmar = document.getElementById('btn-confirmar-seleccion');
        this.colorInfo = this.modalElement.querySelector('.color-selection-info');
        this.detalleInfo = this.modalElement.querySelector('.detalle-selection-info');
    }

    bindEvents() {
        // Evento para confirmar selección
        this.btnConfirmar.addEventListener('click', () => {
            this.confirmarSeleccion();
        });

        // Evento al cerrar modal - limpiar estado
        if (typeof $ !== 'undefined' && $.fn.modal) {
            // Bootstrap 4 con jQuery (priorizar esto)
            $(this.modalElement).on('hidden.bs.modal', () => {
                this.limpiarEstado();
            });
        } else if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            // Bootstrap 5+
            this.modalElement.addEventListener('hidden.bs.modal', () => {
                this.limpiarEstado();
            });
        } else {
            // Fallback manual - detectar clicks en backdrop o botón cerrar
            this.modalElement.addEventListener('click', (e) => {
                if (e.target === this.modalElement || 
                    e.target.classList.contains('btn-close') || 
                    e.target.classList.contains('close') ||
                    e.target.closest('.close')) {
                    this.modal.hide();
                    this.limpiarEstado();
                }
            });
        }
    }

    /**
     * Mostrar modal para selección de color/detalle
     * @param {number} articleId - ID del artículo
     * @param {number} rowIndex - Índice de la fila en la transacción
     * @param {string} articleName - Nombre del artículo
     * @param {function} callback - Función callback con los datos seleccionados
     */
    async mostrarModal(articleId, rowIndex, articleName, callback) {
        // Esperar a que el modal esté listo
        if (!this.isReady) {
            return new Promise((resolve) => {
                const waitForReady = () => {
                    if (this.isReady) {
                        this.mostrarModal(articleId, rowIndex, articleName, callback).then(resolve);
                    } else {
                        setTimeout(waitForReady, 50);
                    }
                };
                waitForReady();
            });
        }
        
        this.currentArticleId = articleId;
        this.currentRowIndex = rowIndex;
        this.callback = callback;

        // Mostrar información del artículo
        this.articuloInfo.textContent = articleName;

        try {
            // Obtener colores y detalles disponibles
            const response = await fetch(`${BASE_URL}/articulos/api/${articleId}/colores-detalles`);
            const data = await response.json();

            if (data.success) {
                const tieneColores = data.colores && data.colores.length > 0;
                const tieneDetalles = data.detalles && data.detalles.length > 0;
                
                // Solo mostrar modal si tiene colores o detalles
                if (tieneColores || tieneDetalles) {
                    this.configurarModal(data.colores, data.detalles);
                    
                    // Remover aria-hidden antes de mostrar y configurar correctamente
                    this.modalElement.removeAttribute('aria-hidden');
                    this.modalElement.setAttribute('aria-modal', 'true');
                    
                    // Mostrar el modal
                    this.modal.show();
                    
                    // Fallback para asegurar visibilidad
                    setTimeout(() => {
                        const isVisible = getComputedStyle(this.modalElement).display !== 'none' && 
                                         getComputedStyle(this.modalElement).visibility !== 'hidden' &&
                                         parseFloat(getComputedStyle(this.modalElement).opacity) > 0;
                        
                        if (!isVisible) {
                            // Aplicar estilos CSS directamente
                            this.modalElement.style.display = 'block';
                            this.modalElement.style.visibility = 'visible';
                            this.modalElement.style.opacity = '1';
                            this.modalElement.style.zIndex = '1055';
                            this.modalElement.style.position = 'fixed';
                            this.modalElement.style.top = '0';
                            this.modalElement.style.left = '0';
                            this.modalElement.style.width = '100%';
                            this.modalElement.style.height = '100%';
                            
                            // Agregar clases de Bootstrap
                            this.modalElement.classList.add('show');
                            this.modalElement.classList.remove('fade');
                            
                            // Crear backdrop manual si no existe
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (!backdrop) {
                                const manualBackdrop = document.createElement('div');
                                manualBackdrop.className = 'modal-backdrop show';
                                manualBackdrop.style.zIndex = '1050';
                                document.body.appendChild(manualBackdrop);
                            }
                        }
                    }, 100);
                } else {
                    console.log('❌ [mostrarModal] No hay colores ni detalles, ejecutando callback con valores vacíos');
                    // No tiene colores ni detalles, ejecutar callback con valores vacíos
                    if (this.callback) {
                        this.callback({
                            colorId: null,
                            detalleId: null,
                            rowIndex: this.currentRowIndex
                        });
                    }
                }
            } else {
                console.error('Error al obtener colores y detalles:', data.message);
                mostrarError('No se pudieron cargar los colores y detalles');
            }
        } catch (error) {
            console.error('Error en la petición:', error);
            mostrarError('Error de conexión');
        }
    }

    configurarModal(colores, detalles) {
        // Ocultar todas las secciones inicialmente
        this.seccionColores.style.display = 'none';
        this.seccionDetalles.style.display = 'none';
        this.sinOpciones.style.display = 'none';

        const tieneColores = colores && colores.length > 0;
        const tieneDetalles = detalles && detalles.length > 0;

        // Reset de selecciones previas
        this.selectedColorId = null;
        this.selectedDetalleId = null;

        // Asegurar que los requerimientos se setean correctamente
        this.requiredColor = false;
        this.requiredDetalle = false;

        if (!tieneColores && !tieneDetalles) {
            // No hay colores ni detalles - esto no debería ocurrir ya que 
            // verificamos antes de mostrar el modal
            this.sinOpciones.style.display = 'block';
        } else {
            // Configurar colores
            if (tieneColores) {
                this.seccionColores.style.display = 'block';
                this.renderColores(colores);
                this.requiredColor = true;
            }

            // Configurar detalles
            if (tieneDetalles) {
                this.seccionDetalles.style.display = 'block';
                this.renderDetalles(detalles);
                this.requiredDetalle = true;
            }

            // Ajustar el ancho de las columnas
            if (tieneColores && tieneDetalles) {
                this.seccionColores.className = 'col-md-6';
                this.seccionDetalles.className = 'col-md-6';
            } else {
                if (tieneColores) this.seccionColores.className = 'col-12';
                if (tieneDetalles) this.seccionDetalles.className = 'col-12';
            }
        }

        this.actualizarEstadoConfirmar();

        // Habilitar cierre/cancelación manual
        if (this.modalElement) {
            const closeBtns = this.modalElement.querySelectorAll('.btn-close, .btn-cancelar, .close');
            closeBtns.forEach(btn => {
                btn.onclick = () => {
                    this.modal.hide();
                    this.limpiarEstado();
                };
            });
        }
    }

    renderColores(colores) {
        this.coloresGrid.innerHTML = '';
        
        colores.forEach(color => {
            const colorElement = document.createElement('div');
            colorElement.className = 'color-option-modal';
            colorElement.dataset.colorId = color.id;
            colorElement.innerHTML = `
                <div class="color-circle" style="background-color: ${color.color || '#ccc'}"></div>
                <span class="color-name">${color.nombre}</span>
            `;
            
            colorElement.addEventListener('click', () => {
                this.seleccionarColor(color.id, colorElement);
            });
            
            this.coloresGrid.appendChild(colorElement);
        });
    }

    renderDetalles(detalles) {
        this.detallesGrid.innerHTML = '';
        
        detalles.forEach(detalle => {
            const detalleElement = document.createElement('div');
            detalleElement.className = 'detalle-option-modal';
            detalleElement.dataset.detalleId = detalle.id;
            detalleElement.innerHTML = `
                <i class="fa fa-tag"></i>
                <span class="detalle-name">${detalle.nombre}</span>
            `;
            
            detalleElement.addEventListener('click', () => {
                this.seleccionarDetalle(detalle.id, detalleElement);
            });
            
            this.detallesGrid.appendChild(detalleElement);
        });
    }

    seleccionarColor(colorId, element) {
        // Quitar selección anterior
        this.coloresGrid.querySelectorAll('.color-option-modal').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Seleccionar nuevo color
        element.classList.add('selected');
        this.selectedColorId = colorId;
        
        this.colorInfo.textContent = 'Color seleccionado';
        this.actualizarEstadoConfirmar();
    }

    seleccionarDetalle(detalleId, element) {
        // Quitar selección anterior
        this.detallesGrid.querySelectorAll('.detalle-option-modal').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Seleccionar nuevo detalle
        element.classList.add('selected');
        this.selectedDetalleId = detalleId;
        
        this.detalleInfo.textContent = 'Detalle seleccionado';
        this.actualizarEstadoConfirmar();
    }

    actualizarEstadoConfirmar() {
        const colorCompleto = !this.requiredColor || this.selectedColorId;
        const detalleCompleto = !this.requiredDetalle || this.selectedDetalleId;
        const shouldEnable = colorCompleto && detalleCompleto;
        
        this.btnConfirmar.disabled = !shouldEnable;
    }

    confirmarSeleccion() {
        console.log('🎯 [confirmarSeleccion] Iniciando confirmación...');
        console.log('🎯 [confirmarSeleccion] Selección actual:', {
            colorId: this.selectedColorId,
            detalleId: this.selectedDetalleId,
            rowIndex: this.currentRowIndex,
            callbackExists: !!this.callback
        });
        
        if (this.callback) {
            const seleccion = {
                colorId: this.selectedColorId,
                detalleId: this.selectedDetalleId,
                rowIndex: this.currentRowIndex
            };
            
            console.log('📞 [confirmarSeleccion] Ejecutando callback con selección:', seleccion);
            this.callback(seleccion);
            console.log('✅ [confirmarSeleccion] Callback ejecutado');
        }
        
        console.log('🚪 [confirmarSeleccion] Cerrando modal...');
        
        // Método mejorado para cerrar el modal
        try {
            // Restaurar aria-hidden antes de cerrar
            this.modalElement.setAttribute('aria-hidden', 'true');
            
            // Intentar cerrar con Bootstrap primero
            if (this.modal && this.modal.hide) {
                this.modal.hide();
                console.log('✅ [confirmarSeleccion] Modal.hide() ejecutado');
            }
            
            // Fallback: cerrar manualmente si no funciona
            setTimeout(() => {
                if (this.modalElement.style.display !== 'none') {
                    console.log('⚠️ [confirmarSeleccion] Fallback: cerrando manualmente...');
                    this.modalElement.style.display = 'none';
                    this.modalElement.classList.remove('show');
                    
                    // Remover backdrop manual si existe
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    
                    // Restaurar scroll del body
                    document.body.classList.remove('modal-open');
                    document.body.style.paddingRight = '';
                    
                    console.log('✅ [confirmarSeleccion] Modal cerrado manualmente');
                }
            }, 100);
            
        } catch (error) {
            console.error('❌ [confirmarSeleccion] Error cerrando modal:', error);
        }
    }

    limpiarEstado() {
        this.currentArticleId = null;
        this.currentRowIndex = null;
        this.selectedColorId = null;
        this.selectedDetalleId = null;
        this.requiredColor = false;
        this.requiredDetalle = false;
        this.callback = null;
        
        this.coloresGrid.innerHTML = '';
        this.detallesGrid.innerHTML = '';
        this.articuloInfo.textContent = '-';
        this.colorInfo.textContent = 'Selecciona un color';
        this.detalleInfo.textContent = 'Selecciona un detalle';
        this.btnConfirmar.disabled = true;
    }
}

// CSS dinámico para el modal
const modalStyles = `
<style>
.colores-grid-modal, .detalles-grid-modal {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
    max-height: 250px;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    background-color: #fafafa;
}

.color-option-modal, .detalle-option-modal {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px;
    border: 2px solid #ddd;
    border-radius: 8px;
    background-color: white;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
}

.color-option-modal:hover, .detalle-option-modal:hover {
    border-color: #007bff;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,123,255,0.3);
}

.color-option-modal.selected, .detalle-option-modal.selected {
    border-color: #28a745;
    background-color: #f8fff9;
    box-shadow: 0 0 10px rgba(40,167,69,0.4);
}

.color-circle {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: 2px solid #fff;
    box-shadow: 0 0 5px rgba(0,0,0,0.2);
    margin-bottom: 5px;
}

.color-name, .detalle-name {
    font-size: 11px;
    font-weight: 500;
    color: #333;
    word-break: break-word;
}

.detalle-option-modal i {
    font-size: 20px;
    color: #6c757d;
    margin-bottom: 5px;
}

#modalColorDetalle .modal-dialog {
    max-width: 800px;
}

#modalColorDetalle .modal-body {
    min-height: 200px;
}
</style>
`;

// Insertar estilos en el documento
document.head.insertAdjacentHTML('beforeend', modalStyles);

// Inicializar manager global
window.modalColorDetalleManager = new ModalColorDetalleManager();