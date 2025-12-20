/**
 * Sistema Universal de Modal de Búsqueda
 * Reemplaza todas las funciones mostrarModalSeleccion*
 * Diseño moderno y funcionalidad unificada
 */

class UniversalSearchModal {
    constructor() {
        this.modal = null;
        this.currentType = null;
        this.currentData = [];
        this.filteredData = [];
        this.selectedIndex = -1;
        this.callback = null;
        this.searchTimeout = null;
        this.currentQuery = '';
        
        this.init();
    }

    init() {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupModal());
        } else {
            this.setupModal();
        }
    }

    setupModal() {
        this.modal = document.getElementById('universalSearchModal');
        if (!this.modal) {
            console.warn('Modal universalSearchModal no encontrada');
            return;
        }

        this.setupEventListeners();
    }

    setupEventListeners() {
        const searchInput = document.getElementById('universalSearchInput');
        const modal = this.modal;

        // Búsqueda en tiempo real
        searchInput?.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        // Mostrar todos los resultados al enfocar si está vacío
        searchInput?.addEventListener('focus', (e) => {
            if (!e.target.value || e.target.value.trim() === '') {
                this.filteredData = this.currentData;
                this.renderResults();
                if (this.currentData && this.currentData.length > 0) {
                    this.showSearchState('results');
                }
            }
        });

        // Navegación con teclado
        searchInput?.addEventListener('keydown', (e) => {
            this.handleKeyNavigation(e);
        });

        // Limpiar al cerrar modal
        $(modal).on('hidden.bs.modal', () => {
            this.cleanup();
        });

        // Enfocar input al abrir
        $(modal).on('shown.bs.modal', () => {
            searchInput?.focus();
        });
    }

    /**
     * Mostrar modal de búsqueda
     * @param {string} type - Tipo: 'clientes', 'articulos', 'proveedores', 'garantes'
     * @param {Array} data - Array de datos para buscar
     * @param {Function} callback - Función callback al seleccionar
     * @param {Object} options - Opciones adicionales
     */
    show(type, data, callback, options = {}) {
        console.log(`🔍 Mostrando modal de búsqueda: ${type}`, { data: data.length, options });
        
        this.currentType = type;
        this.currentData = data;
        this.filteredData = data;
        this.callback = callback;
        this.selectedIndex = -1;
        this.currentQuery = '';

        this.setupModalForType(type, options);
        this.renderResults();
        
        // Mostrar el estado correcto según si hay datos o no
        if (data && data.length > 0) {
            this.showSearchState('results');
        } else {
            this.showSearchState('initial');
        }
        
        $('#universalSearchModal').modal('show');
    }

    setupModalForType(type, options) {
        const config = this.getTypeConfig(type);
        
        // Configurar header
        document.getElementById('universalSearchModalLabel').textContent = config.title;
        document.getElementById('searchTypeText').textContent = config.typeName;
        document.getElementById('searchTypeIcon').className = config.icon;
        
        // Configurar placeholder del input
        const searchInput = document.getElementById('universalSearchInput');
        if (searchInput) {
            searchInput.placeholder = `Buscar ${config.typeName.toLowerCase()}...`;
            searchInput.value = '';
        }

        // Configurar badge de tipo
        const badge = document.getElementById('searchTypeBadge');
        if (badge) {
            badge.className = `search-type-badge ${config.badgeClass}`;
        }

        // Mostrar estadísticas
        this.updateStats();
    }

    getTypeConfig(type) {
        const configs = {
            clientes: {
                title: 'Seleccionar Cliente',
                typeName: 'Clientes',
                icon: 'fas fa-user',
                badgeClass: 'badge-cliente',
                searchFields: ['nombre', 'telefono', 'email', 'documento'],
                displayTemplate: (item) => `
                    <div class="result-card cliente-card">
                        <div class="result-header">
                            <div class="result-icon">
                                <i class="fas fa-user"></i>
                            </div>
                            <div class="result-info">
                                <h6 class="result-title">${item.nombre}</h6>
                                <p class="result-subtitle">
                                    <i class="fas fa-phone"></i>
                                    ${item.telefono || 'Sin teléfono'}
                                </p>
                            </div>
                        </div>
                        <div class="result-details">
                            ${item.email ? `<span class="detail-item"><i class="fas fa-envelope"></i>${item.email}</span>` : ''}
                            ${item.documento ? `<span class="detail-item"><i class="fas fa-id-card"></i>${item.documento}</span>` : ''}
                        </div>
                    </div>`
            },
            articulos: {
                title: 'Seleccionar Artículo',
                typeName: 'Artículos',
                icon: 'fas fa-box',
                badgeClass: 'badge-articulo',
                searchFields: ['detalle', 'marca', 'codigo', 'categoria'],
                displayTemplate: (item) => {
                    const precio = parseFloat(item.precio || item.costo || 0);
                    const priceClass = item.oferta ? 'precio-oferta' : 'precio-normal';
                    
                    return `
                    <div class="result-card articulo-card">
                        <div class="result-header">
                            <div class="result-icon">
                                <i class="fas fa-box"></i>
                            </div>
                            <div class="result-info">
                                <h6 class="result-title">${item.detalle}</h6>
                                <p class="result-subtitle">
                                    <i class="fas fa-tag"></i>
                                    ${item.marca || 'Sin marca'}
                                </p>
                            </div>
                            <div class="result-price">
                                <span class="price ${priceClass}">
                                    $${precio.toLocaleString('es-AR', { 
                                        minimumFractionDigits: 2, 
                                        maximumFractionDigits: 2 
                                    })}
                                </span>
                                ${item.oferta ? '<span class="oferta-badge">OFERTA</span>' : ''}
                            </div>
                        </div>
                        <div class="result-details">
                            ${item.codigo ? `<span class="detail-item"><i class="fas fa-barcode"></i>${item.codigo}</span>` : ''}
                            ${item.categoria ? `<span class="detail-item"><i class="fas fa-folder"></i>${item.categoria}</span>` : ''}
                        </div>
                    </div>`
                }
            },
            proveedores: {
                title: 'Seleccionar Proveedor',
                typeName: 'Proveedores',
                icon: 'fas fa-truck',
                badgeClass: 'badge-proveedor',
                searchFields: ['nombre', 'telefono', 'email', 'cuit'],
                displayTemplate: (item) => `
                    <div class="result-card proveedor-card">
                        <div class="result-header">
                            <div class="result-icon">
                                <i class="fas fa-truck"></i>
                            </div>
                            <div class="result-info">
                                <h6 class="result-title">${item.nombre}</h6>
                                <p class="result-subtitle">
                                    <i class="fas fa-phone"></i>
                                    ${item.telefono || 'Sin teléfono'}
                                </p>
                            </div>
                        </div>
                        <div class="result-details">
                            ${item.email ? `<span class="detail-item"><i class="fas fa-envelope"></i>${item.email}</span>` : ''}
                            ${item.cuit ? `<span class="detail-item"><i class="fas fa-file-alt"></i>CUIT: ${item.cuit}</span>` : ''}
                        </div>
                    </div>`
            },
            garantes: {
                title: 'Seleccionar Garante',
                typeName: 'Garantes',
                icon: 'fas fa-user-shield',
                badgeClass: 'badge-garante',
                searchFields: ['nombre', 'telefono', 'email', 'documento'],
                displayTemplate: (item) => `
                    <div class="result-card garante-card">
                        <div class="result-header">
                            <div class="result-icon">
                                <i class="fas fa-user-shield"></i>
                            </div>
                            <div class="result-info">
                                <h6 class="result-title">${item.nombre}</h6>
                                <p class="result-subtitle">
                                    <i class="fas fa-phone"></i>
                                    ${item.telefono || 'Sin teléfono'}
                                </p>
                            </div>
                        </div>
                        <div class="result-details">
                            ${item.email ? `<span class="detail-item"><i class="fas fa-envelope"></i>${item.email}</span>` : ''}
                            ${item.documento ? `<span class="detail-item"><i class="fas fa-id-card"></i>${item.documento}</span>` : ''}
                        </div>
                    </div>`
            }
        };

        return configs[type] || configs.clientes;
    }

    handleSearch(query) {
        this.currentQuery = query;
        
        // Limpiar timeout anterior
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        // Mostrar loading si hay query suficiente, sino mostrar todos los resultados
        if (query.length >= 2) {
            this.showSearchState('loading');
            // Debounce búsqueda
            this.searchTimeout = setTimeout(() => {
                this.performSearch(query);
            }, 300);
        } else {
            // Mostrar todos los resultados cuando no hay query suficiente
            this.filteredData = this.currentData;
            this.renderResults();
            if (this.currentData && this.currentData.length > 0) {
                this.showSearchState('results');
            } else {
                this.showSearchState('initial');
            }
        }
    }

    performSearch(query) {
        console.log(`🔍 Buscando: "${query}" en ${this.currentType}`);
        const startTime = performance.now();
        
        if (!query || query.length < 2) {
            this.filteredData = this.currentData;
            this.renderResults();
            if (this.currentData && this.currentData.length > 0) {
                this.showSearchState('results');
            } else {
                this.showSearchState('initial');
            }
            return;
        }

        const config = this.getTypeConfig(this.currentType);
        const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);
        
        this.filteredData = this.currentData.filter(item => {
            return searchTerms.every(term => {
                return config.searchFields.some(field => {
                    const fieldValue = item[field];
                    if (!fieldValue) return false;
                    return fieldValue.toString().toLowerCase().includes(term);
                });
            });
        });

        const endTime = performance.now();
        const searchTime = Math.round(endTime - startTime);
        
        console.log(`📊 Búsqueda completada: ${this.filteredData.length}/${this.currentData.length} resultados en ${searchTime}ms`);
        
        this.updateStats(searchTime);
        
        if (this.filteredData.length === 0) {
            this.showSearchState('noResults');
        } else {
            this.showSearchState('results');
            this.renderResults();
        }
    }

    renderResults() {
        const container = document.getElementById('searchResults');
        if (!container) return;

        const config = this.getTypeConfig(this.currentType);
        
        container.innerHTML = this.filteredData.map((item, index) => {
            const isSelected = index === this.selectedIndex;
            const selectedClass = isSelected ? 'selected' : '';
            
            return `
                <div class="result-item ${selectedClass}" 
                     data-index="${index}" 
                     onclick="window.universalSearchModal.selectItem(${index})"
                     onmouseover="window.universalSearchModal.hoverItem(${index})">
                    ${config.displayTemplate(item)}
                </div>
            `;
        }).join('');

        // Scroll al item seleccionado si es necesario
        if (this.selectedIndex >= 0) {
            this.scrollToSelected();
        }
    }

    showSearchState(state) {
        const states = {
            initial: document.getElementById('initialState'),
            loading: document.getElementById('loadingState'),
            noResults: document.getElementById('noResultsState'),
            results: document.getElementById('searchResults')
        };

        // Ocultar todos los estados
        Object.values(states).forEach(el => {
            if (el) el.style.display = 'none';
        });

        // Mostrar el estado actual
        if (states[state]) {
            states[state].style.display = state === 'results' ? 'block' : 'flex';
        }

        // Ocultar/mostrar estadísticas
        const statsEl = document.getElementById('searchStats');
        if (statsEl) {
            statsEl.style.display = state === 'results' ? 'flex' : 'none';
        }
    }

    updateStats(searchTime = 0) {
        document.getElementById('totalResults').textContent = this.currentData.length;
        document.getElementById('filteredResults').textContent = this.filteredData.length;
        document.getElementById('searchTime').textContent = `${searchTime}ms`;
    }

    selectItem(index) {
        if (index < 0 || index >= this.filteredData.length) return;
        
        const selectedItem = this.filteredData[index];
        console.log(`✅ Item seleccionado:`, selectedItem);
        
        // Ejecutar callback
        if (this.callback && typeof this.callback === 'function') {
            this.callback(selectedItem);
        }
        
        // Cerrar modal
        $('#universalSearchModal').modal('hide');
    }

    hoverItem(index) {
        this.selectedIndex = index;
        this.updateSelectedVisual();
    }

    handleKeyNavigation(e) {
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.filteredData.length - 1);
                this.updateSelectedVisual();
                this.scrollToSelected();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelectedVisual();
                this.scrollToSelected();
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectItem(this.selectedIndex);
                }
                break;
                
            case 'Escape':
                e.preventDefault();
                $('#universalSearchModal').modal('hide');
                break;
        }
    }

    updateSelectedVisual() {
        const items = document.querySelectorAll('.result-item');
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === this.selectedIndex);
        });
    }

    scrollToSelected() {
        if (this.selectedIndex < 0) return;
        
        const selectedItem = document.querySelector(`.result-item[data-index="${this.selectedIndex}"]`);
        if (selectedItem) {
            selectedItem.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }
    }

    cleanup() {
        console.log('🧹 Limpiando modal de búsqueda');
        
        this.currentType = null;
        this.currentData = [];
        this.filteredData = [];
        this.selectedIndex = -1;
        this.callback = null;
        this.currentQuery = '';
        
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = null;
        }
        
        // Limpiar input
        const searchInput = document.getElementById('universalSearchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        
        // Mostrar estado inicial
        this.showSearchState('initial');
    }
}

// Inicializar instancia global
window.universalSearchModal = new UniversalSearchModal();

// Funciones de compatibilidad para reemplazar las existentes
window.mostrarModalSeleccionClientes = function(clientes, callback) {
    if (!callback) {
        // Si no hay callback, usar el comportamiento original
        callback = function(cliente) {
            if (typeof asignarCliente === 'function') {
                asignarCliente(cliente);
            }
            
            // Enfocar campo cliente si existe
            const clienteInput = document.getElementById("idcliente");
            if (clienteInput) clienteInput.focus();
        };
    }
    
    window.universalSearchModal.show('clientes', clientes, callback);
};

window.mostrarModalSeleccionArticulos = function(articulos, idlista, itemDiv, callback) {
    if (!callback) {
        callback = function(articulo) {
            if (typeof asignarArticuloElegido === 'function' && itemDiv) {
                asignarArticuloElegido(articulo, itemDiv);
            } else if (typeof asignarArticulo === 'function' && itemDiv) {
                asignarArticulo(articulo, itemDiv);
            }
            
            // Enfocar próximo input si existe
            const nuevoInputCodigo = document.querySelector(`#tabla-items tr:last-child .codigo-articulo`);
            if (nuevoInputCodigo) nuevoInputCodigo.focus();
        };
    }
    
    window.universalSearchModal.show('articulos', articulos, callback);
};

window.mostrarModalSeleccionProveedores = function(proveedores, callback) {
    if (!callback) {
        callback = function(proveedor) {
            if (typeof asignarProveedor === 'function') {
                asignarProveedor(proveedor);
            }
            
            // Enfocar campo proveedor si existe
            const proveedorInput = document.getElementById("idproveedor");
            if (proveedorInput) proveedorInput.focus();
        };
    }
    
    window.universalSearchModal.show('proveedores', proveedores, callback);
};

window.mostrarModalSeleccionGarantes = function(garantes, input, callback) {
    if (!callback) {
        callback = function(garante) {
            if (input && typeof asignarGarante === 'function') {
                asignarGarante(garante, input);
            }
        };
    }
    
    window.universalSearchModal.show('garantes', garantes, callback);
};

console.log('✅ Sistema Universal de Modal de Búsqueda inicializado');