/**
 * Gestor de detalles para artículos desde base de datos
 * Maneja la selección de detalles predefinidos
 */

class DetailManager {
    constructor() {
        this.selectedDetails = [];
        this.init();
    }

    init() {
        this.loadSelectedDetails();
        this.bindEvents();
        this.updateHiddenInput();
    }

    /**
     * Carga los detalles seleccionados desde el input hidden o inicializa vacío
     */
    loadSelectedDetails() {
        const hiddenInput = document.getElementById('detalles-seleccionados');
        if (hiddenInput && hiddenInput.value) {
            try {
                this.selectedDetails = JSON.parse(hiddenInput.value);
                this.updateVisualSelection();
            } catch (e) {
                console.warn('Error parsing selected details:', e);
                this.selectedDetails = [];
            }
        }
    }

    /**
     * Vincula eventos del DOM
     */
    bindEvents() {
        // Eventos de toggle detalle (delegación)
        const grid = document.querySelector('.detalles-grid');
        if (grid) {
            grid.addEventListener('click', (e) => {
                if (e.target.closest('.btn-toggle-detalle')) {
                    const detailItem = e.target.closest('.detalle-item');
                    this.toggleDetail(detailItem);
                }
                
                // También permitir click en el elemento completo para toggle
                if (e.target.closest('.detalle-item') && !e.target.closest('.btn-toggle-detalle')) {
                    const detailItem = e.target.closest('.detalle-item');
                    this.toggleDetail(detailItem);
                }
            });
        }
    }

    /**
     * Alterna la selección de un detalle
     */
    toggleDetail(detailItem) {
        if (!detailItem) return;

        const detailId = parseInt(detailItem.dataset.id);
        const detailName = detailItem.querySelector('.detalle-name').textContent;

        const isSelected = detailItem.classList.contains('selected');

        if (isSelected) {
            // Deseleccionar
            detailItem.classList.remove('selected');
            this.selectedDetails = this.selectedDetails.filter(d => d.id !== detailId);
        } else {
            // Seleccionar
            detailItem.classList.add('selected');
            this.selectedDetails.push({
                id: detailId,
                name: detailName
            });
        }

        this.updateHiddenInput();
        this.dispatchDetailEvent('detailToggled', { 
            detailId, 
            detailName, 
            selected: !isSelected 
        });
    }

    /**
     * Actualiza la visualización de la selección
     */
    updateVisualSelection() {
        const detailItems = document.querySelectorAll('.detalle-item');
        
        detailItems.forEach(item => {
            const detailId = parseInt(item.dataset.id);
            const isSelected = this.selectedDetails.some(d => d.id === detailId);
            
            if (isSelected) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    /**
     * Actualiza el input hidden con los detalles seleccionados
     */
    updateHiddenInput() {
        const hiddenInput = document.getElementById('detalles-seleccionados');
        if (hiddenInput) {
            hiddenInput.value = JSON.stringify(this.selectedDetails);
            console.log('DEBUG - Detalles actualizados en input hidden:', this.selectedDetails);
        }
    }

    /**
     * Selecciona detalles por sus IDs (útil para cargar selecciones existentes)
     */
    selectDetailsByIds(detailIds) {
        if (!Array.isArray(detailIds)) return;

        // Limpiar selección actual
        this.selectedDetails = [];

        // Seleccionar cada detalle por ID
        detailIds.forEach(id => {
            const detailItem = document.querySelector(`.detalle-item[data-id="${id}"]`);
            if (detailItem) {
                const detailName = detailItem.querySelector('.detalle-name').textContent;
                
                detailItem.classList.add('selected');
                this.selectedDetails.push({
                    id: parseInt(id),
                    name: detailName
                });
            }
        });

        this.updateHiddenInput();
    }

    /**
     * Limpia toda la selección
     */
    clearSelection() {
        const detailItems = document.querySelectorAll('.detalle-item');
        detailItems.forEach(item => item.classList.remove('selected'));
        
        this.selectedDetails = [];
        this.updateHiddenInput();
    }

    /**
     * Dispara eventos personalizados
     */
    dispatchDetailEvent(eventName, detail) {
        const event = new CustomEvent(eventName, { detail });
        document.dispatchEvent(event);
    }

    /**
     * Obtiene los detalles seleccionados
     */
    getSelectedDetails() {
        return [...this.selectedDetails];
    }

    /**
     * Obtiene los detalles en formato para envío al servidor
     */
    getDetailsForSubmit() {
        return this.selectedDetails.map(detail => detail.id);
    }

    /**
     * Obtiene el número de detalles seleccionados
     */
    getSelectedCount() {
        return this.selectedDetails.length;
    }

    /**
     * Verifica si un detalle específico está seleccionado
     */
    isDetailSelected(detailId) {
        return this.selectedDetails.some(d => d.id === detailId);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.detailManager = new DetailManager();

    // Eventos opcionales para debugging y feedback
    document.addEventListener('detailToggled', function(e) {
        console.log('Detail toggled:', e.detail);
        
        // Mostrar feedback visual
        const count = window.detailManager.getSelectedCount();
        const info = document.querySelector('.selected-detalles-info small');
        if (info) {
            if (count > 0) {
                info.innerHTML = `<i class="fa fa-check-circle text-success"></i> ${count} detalle${count > 1 ? 's' : ''} seleccionado${count > 1 ? 's' : ''}`;
            } else {
                info.innerHTML = `<i class="fa fa-info-circle"></i> Haz clic en los detalles para seleccionar/deseleccionar para este artículo`;
            }
        }
    });
});