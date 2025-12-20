/**
 * Gestor de colores para artículos desde base de datos
 * Maneja la selección de colores predefinidos
 */

class ColorManager {
    constructor() {
        this.selectedColors = [];
        this.init();
    }

    init() {
        this.loadSelectedColors();
        this.bindEvents();
        this.updateHiddenInput();
    }

    /**
     * Carga los colores seleccionados desde el input hidden o inicializa vacío
     */
    loadSelectedColors() {
        const hiddenInput = document.getElementById('colores-seleccionados');
        if (hiddenInput && hiddenInput.value) {
            try {
                this.selectedColors = JSON.parse(hiddenInput.value);
                this.updateVisualSelection();
            } catch (e) {
                console.warn('Error parsing selected colors:', e);
                this.selectedColors = [];
            }
        }
    }

    /**
     * Vincula eventos del DOM
     */
    bindEvents() {
        // Eventos de toggle color (delegación)
        const grid = document.querySelector('.colores-grid');
        if (grid) {
            grid.addEventListener('click', (e) => {
                if (e.target.closest('.btn-toggle-color')) {
                    const colorItem = e.target.closest('.color-item');
                    this.toggleColor(colorItem);
                }
                
                // También permitir click en el elemento completo para toggle
                if (e.target.closest('.color-item') && !e.target.closest('.btn-toggle-color')) {
                    const colorItem = e.target.closest('.color-item');
                    this.toggleColor(colorItem);
                }
            });
        }
    }

    /**
     * Alterna la selección de un color
     */
    toggleColor(colorItem) {
        if (!colorItem) return;

        const colorId = parseInt(colorItem.dataset.id);
        const colorValue = colorItem.dataset.color;
        const colorName = colorItem.querySelector('.color-name').textContent;

        const isSelected = colorItem.classList.contains('selected');

        if (isSelected) {
            // Deseleccionar
            colorItem.classList.remove('selected');
            this.selectedColors = this.selectedColors.filter(c => c.id !== colorId);
        } else {
            // Seleccionar
            colorItem.classList.add('selected');
            this.selectedColors.push({
                id: colorId,
                color: colorValue,
                name: colorName
            });
        }

        this.updateHiddenInput();
        this.dispatchColorEvent('colorToggled', { 
            colorId, 
            colorValue, 
            colorName, 
            selected: !isSelected 
        });
    }

    /**
     * Actualiza la visualización de la selección
     */
    updateVisualSelection() {
        const colorItems = document.querySelectorAll('.color-item');
        
        colorItems.forEach(item => {
            const colorId = parseInt(item.dataset.id);
            const isSelected = this.selectedColors.some(c => c.id === colorId);
            
            if (isSelected) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    /**
     * Actualiza el input hidden con los colores seleccionados
     */
    updateHiddenInput() {
        const hiddenInput = document.getElementById('colores-seleccionados');
        if (hiddenInput) {
            hiddenInput.value = JSON.stringify(this.selectedColors);
            console.log('DEBUG - Colores actualizados en input hidden:', this.selectedColors);
        }
    }

    /**
     * Selecciona colores por sus IDs (útil para cargar selecciones existentes)
     */
    selectColorsByIds(colorIds) {
        if (!Array.isArray(colorIds)) return;

        // Limpiar selección actual
        this.selectedColors = [];

        // Seleccionar cada color por ID
        colorIds.forEach(id => {
            const colorItem = document.querySelector(`.color-item[data-id="${id}"]`);
            if (colorItem) {
                const colorValue = colorItem.dataset.color;
                const colorName = colorItem.querySelector('.color-name').textContent;
                
                colorItem.classList.add('selected');
                this.selectedColors.push({
                    id: parseInt(id),
                    color: colorValue,
                    name: colorName
                });
            }
        });

        this.updateHiddenInput();
    }

    /**
     * Limpia toda la selección
     */
    clearSelection() {
        const colorItems = document.querySelectorAll('.color-item');
        colorItems.forEach(item => item.classList.remove('selected'));
        
        this.selectedColors = [];
        this.updateHiddenInput();
    }

    /**
     * Dispara eventos personalizados
     */
    dispatchColorEvent(eventName, detail) {
        const event = new CustomEvent(eventName, { detail });
        document.dispatchEvent(event);
    }

    /**
     * Obtiene los colores seleccionados
     */
    getSelectedColors() {
        return [...this.selectedColors];
    }

    /**
     * Obtiene los colores en formato para envío al servidor
     */
    getColorsForSubmit() {
        return this.selectedColors.map(color => color.id);
    }

    /**
     * Obtiene el número de colores seleccionados
     */
    getSelectedCount() {
        return this.selectedColors.length;
    }

    /**
     * Verifica si un color específico está seleccionado
     */
    isColorSelected(colorId) {
        return this.selectedColors.some(c => c.id === colorId);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.colorManager = new ColorManager();

    // Eventos opcionales para debugging y feedback
    document.addEventListener('colorToggled', function(e) {
        console.log('Color toggled:', e.detail);
        
        // Mostrar feedback visual
        const count = window.colorManager.getSelectedCount();
        const info = document.querySelector('.selected-colors-info small');
        if (info) {
            if (count > 0) {
                info.innerHTML = `<i class="fa fa-check-circle text-success"></i> ${count} color${count > 1 ? 'es' : ''} seleccionado${count > 1 ? 's' : ''}`;
            } else {
                info.innerHTML = `<i class="fa fa-info-circle"></i> Haz clic en los colores para seleccionar/deseleccionar para este artículo`;
            }
        }
    });
});