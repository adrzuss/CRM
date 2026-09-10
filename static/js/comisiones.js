/**
 * JavaScript para el módulo de Comisiones — CRM SoftTech
 * Manejo de formularios dinámicos, tier management, preview AJAX,
 * confirmaciones SweetAlert2 y filtros de reportes
 */
(function() {
    'use strict';

    // ─── Helpers ──────────────────────────────────────────────────────
    function formatearMoneda(valor) {
        if (valor === null || valor === undefined) return '$ 0,00';
        return '$ ' + parseFloat(valor).toLocaleString('es-AR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    function getCsrfToken() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.getAttribute('content');
        var input = document.querySelector('input[name="csrf_token"]');
        if (input) return input.value;
        return '';
    }

    // ─── Dynamic Rule Form ────────────────────────────────────────────
    // Show/hide fields based on tipo_regla selection
    function initReglaForm() {
        var tipoReglaSelect = document.getElementById('tipo_regla');
        if (!tipoReglaSelect) return;

        function toggleFields() {
            var tipo = tipoReglaSelect.value;
            var porcentajeGroup = document.getElementById('group_porcentaje');
            var importeFijoGroup = document.getElementById('group_importe_fijo');
            var escalasGroup = document.getElementById('group_escalas');

            // Reset visibility
            if (porcentajeGroup) porcentajeGroup.style.display = 'block';
            if (importeFijoGroup) importeFijoGroup.style.display = 'block';
            if (escalasGroup) escalasGroup.style.display = 'none';

            if (tipo === 'PORCENTAJE') {
                if (importeFijoGroup) importeFijoGroup.style.display = 'none';
            } else if (tipo === 'IMPORTE_FIJO') {
                if (porcentajeGroup) porcentajeGroup.style.display = 'none';
            } else if (tipo === 'ESCALA') {
                if (escalasGroup) escalasGroup.style.display = 'block';
            }
        }

        tipoReglaSelect.addEventListener('change', toggleFields);
        toggleFields(); // Initialize on page load
    }

    // ─── Tier Management (Tramos de Escala) ───────────────────────────
    var tramoCounter = 0;

    function addTramoRow() {
        tramoCounter++;
        var container = document.getElementById('tramos-container');
        if (!container) return;

        var template = '<div class="tramo-row card mb-2" data-index="' + tramoCounter + '">' +
            '<div class="card-body py-2">' +
            '<div class="row align-items-center">' +
            '<div class="col">' +
            '<label class="form-label text-xs">Desde</label>' +
            '<input type="number" class="form-control form-control-sm" name="tramos[' + tramoCounter + '][desde]" step="0.01" min="0" required>' +
            '</div>' +
            '<div class="col">' +
            '<label class="form-label text-xs">Hasta</label>' +
            '<input type="number" class="form-control form-control-sm" name="tramos[' + tramoCounter + '][hasta]" step="0.01" min="0" required>' +
            '</div>' +
            '<div class="col">' +
            '<label class="form-label text-xs">Porcentaje (%)</label>' +
            '<input type="number" class="form-control form-control-sm tramo-porcentaje" name="tramos[' + tramoCounter + '][porcentaje]" step="0.01" min="0" max="100">' +
            '</div>' +
            '<div class="col">' +
            '<label class="form-label text-xs">Importe Fijo</label>' +
            '<input type="number" class="form-control form-control-sm tramo-importe" name="tramos[' + tramoCounter + '][importe_fijo]" step="0.01" min="0">' +
            '</div>' +
            '<div class="col-auto">' +
            '<label class="form-label text-xs">&nbsp;</label>' +
            '<button type="button" class="btn btn-danger btn-sm btn-remove-tramo" title="Eliminar">' +
            '<i class="fas fa-trash"></i>' +
            '</button>' +
            '</div>' +
            '</div></div></div>';

        container.insertAdjacentHTML('beforeend', template);
        bindTramoRemoveEvents();
    }

    function removeTramoRow(row) {
        if (row) row.remove();
    }

    function bindTramoRemoveEvents() {
        document.querySelectorAll('.btn-remove-tramo').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var row = this.closest('.tramo-row');
                removeTramoRow(row);
            });
        });
    }

    // ─── Assignment Date Validation (no overlap) ──────────────────────
    function initAsignacionValidation() {
        var form = document.getElementById('formAsignacion');
        if (!form) return;

        form.addEventListener('submit', function(e) {
            var desde = form.querySelector('[name="fecha_desde"]');
            var hasta = form.querySelector('[name="fecha_hasta"]');
            var usuarioId = form.querySelector('[name="usuario_id"]');

            if (desde && hasta && hasta.value && desde.value > hasta.value) {
                e.preventDefault();
                Swal.fire({
                    icon: 'error',
                    title: 'Fechas inválidas',
                    text: 'La fecha desde no puede ser posterior a la fecha hasta',
                    confirmButtonColor: '#4e73df'
                });
                return false;
            }
        });
    }

    // ─── Preview Calculation (AJAX) ──────────────────────────────────
    function initPreviewCalculo() {
        var form = document.getElementById('formCalculoPreview');
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault();

            var formData = new FormData(form);
            var btnSubmit = form.querySelector('button[type="submit"]');
            var originalText = btnSubmit.innerHTML;

            // Loading state
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Calculando...';

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = originalText;

                if (data.success) {
                    // Reload page with results
                    window.location.reload();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error en el cálculo',
                        text: data.message || 'No se pudieron calcular las comisiones',
                        confirmButtonColor: '#4e73df'
                    });
                }
            })
            .catch(function(error) {
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = originalText;
                Swal.fire({
                    icon: 'error',
                    title: 'Error de conexión',
                    text: 'No se pudo conectar con el servidor',
                    confirmButtonColor: '#4e73df'
                });
            });
        });
    }

    // ─── Confirm Liquidation (SweetAlert2) ────────────────────────────
    function initConfirmarLiquidacion() {
        document.querySelectorAll('.btn-confirmar-liquidacion').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                var form = this.closest('form');

                Swal.fire({
                    title: '¿Confirmar liquidación?',
                    text: 'Se creará la liquidación de comisiones. Esta acción no se puede deshacer.',
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: '#1cc88a',
                    cancelButtonColor: '#858796',
                    confirmButtonText: 'Sí, confirmar',
                    cancelButtonText: 'Cancelar'
                }).then(function(result) {
                    if (result.isConfirmed) {
                        form.submit();
                    }
                });
            });
        });
    }

    // ─── Anular Liquidation (SweetAlert2) ─────────────────────────────
    function initAnularLiquidacion() {
        document.querySelectorAll('.btn-anular-liquidacion').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                var form = this.closest('form');

                Swal.fire({
                    title: '¿Anular liquidación?',
                    text: 'Se anulará esta liquidación de comisiones.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#e74a3b',
                    cancelButtonColor: '#858796',
                    confirmButtonText: 'Sí, anular',
                    cancelButtonText: 'Cancelar',
                    input: 'textarea',
                    inputPlaceholder: 'Motivo de anulación (opcional)',
                    inputAttributes: {
                        'aria-label': 'Motivo'
                    }
                }).then(function(result) {
                    if (result.isConfirmed) {
                        // Add motivo to form if provided
                        if (result.value) {
                            var input = document.createElement('input');
                            input.type = 'hidden';
                            input.name = 'observaciones';
                            input.value = result.value;
                            form.appendChild(input);
                        }
                        form.submit();
                    }
                });
            });
        });
    }

    // ─── Delete Confirmation (Regla, Tramo, Asignación) ───────────────
    function initDeleteConfirmations() {
        document.querySelectorAll('.btn-delete-confirm').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                var form = this.closest('form');
                var itemName = this.getAttribute('data-name') || 'este elemento';

                Swal.fire({
                    title: '¿Eliminar ' + itemName + '?',
                    text: 'Esta acción no se puede deshacer.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#e74a3b',
                    cancelButtonColor: '#858796',
                    confirmButtonText: 'Sí, eliminar',
                    cancelButtonText: 'Cancelar'
                }).then(function(result) {
                    if (result.isConfirmed) {
                        form.submit();
                    }
                });
            });
        });
    }

    // ─── Toggle Plan Active/Inactive ──────────────────────────────────
    function initTogglePlan() {
        document.querySelectorAll('.btn-toggle-plan').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                var form = this.closest('form');
                var isActive = this.getAttribute('data-active') === '1';
                var action = isActive ? 'desactivar' : 'activar';

                Swal.fire({
                    title: '¿' + (isActive ? 'Desactivar' : 'Activar') + ' plan?',
                    text: 'El plan será ' + (isActive ? 'desactivado' : 'activado') + '.',
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: '#f6c23e',
                    cancelButtonColor: '#858796',
                    confirmButtonText: 'Sí, ' + action,
                    cancelButtonText: 'Cancelar'
                }).then(function(result) {
                    if (result.isConfirmed) {
                        form.submit();
                    }
                });
            });
        });
    }

    // ─── Report Filters ───────────────────────────────────────────────
    function initReportFilters() {
        var filterForm = document.getElementById('formFiltrosReporte');
        if (!filterForm) return;

        // Preset date range buttons
        document.querySelectorAll('.preset-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var dias = parseInt(this.getAttribute('data-dias'), 10);
                var hoy = new Date();
                var desde = new Date();
                desde.setDate(hoy.getDate() - dias);

                var desdeInput = filterForm.querySelector('[name="desde"]');
                var hastaInput = filterForm.querySelector('[name="hasta"]');

                if (desdeInput) desdeInput.value = desde.toISOString().split('T')[0];
                if (hastaInput) hastaInput.value = hoy.toISOString().split('T')[0];
            });
        });

        // Export buttons
        document.querySelectorAll('.btn-export').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                var format = this.getAttribute('data-format');
                var url = this.getAttribute('data-url');
                var formData = new FormData(filterForm);
                formData.append('formato', format);

                // Build query string from form
                var params = new URLSearchParams(formData);
                window.open(url + '?' + params.toString(), '_blank');
            });
        });
    }

    // ─── Duplicate Plan Form ──────────────────────────────────────────
    function initDuplicatePlan() {
        var dupForm = document.getElementById('formDuplicarPlan');
        if (!dupForm) return;

        dupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            var nuevoNombre = this.querySelector('[name="nuevo_nombre"]').value.trim();

            if (!nuevoNombre) {
                Swal.fire({
                    icon: 'error',
                    title: 'Nombre requerido',
                    text: 'Ingrese un nombre para el nuevo plan',
                    confirmButtonColor: '#4e73df'
                });
                return;
            }

            Swal.fire({
                title: '¿Duplicar plan?',
                text: 'Se creará un nuevo plan con el nombre: ' + nuevoNombre,
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#1cc88a',
                cancelButtonColor: '#858796',
                confirmButtonText: 'Sí, duplicar',
                cancelButtonText: 'Cancelar'
            }).then(function(result) {
                if (result.isConfirmed) {
                    dupForm.submit();
                }
            });
        });
    }

    // ─── Table Sort (simple) ──────────────────────────────────────────
    function initTableSort() {
        document.querySelectorAll('.sortable-table thead th[data-sort]').forEach(function(th) {
            th.style.cursor = 'pointer';
            th.addEventListener('click', function() {
                var table = this.closest('table');
                var tbody = table.querySelector('tbody');
                var rows = Array.from(tbody.querySelectorAll('tr'));
                var colIndex = Array.from(this.parentNode.children).indexOf(this);
                var sortKey = this.getAttribute('data-sort');
                var isAsc = this.classList.contains('sort-asc');

                // Remove sort classes from all headers
                this.parentNode.querySelectorAll('th').forEach(function(h) {
                    h.classList.remove('sort-asc', 'sort-desc');
                });

                // Sort rows
                rows.sort(function(a, b) {
                    var aVal = a.children[colIndex] ? a.children[colIndex].textContent.trim() : '';
                    var bVal = b.children[colIndex] ? b.children[colIndex].textContent.trim() : '';

                    // Try numeric comparison
                    var aNum = parseFloat(aVal.replace(/[$,.\s]/g, '').replace(',', '.'));
                    var bNum = parseFloat(bVal.replace(/[$,.\s]/g, '').replace(',', '.'));

                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        return isAsc ? bNum - aNum : aNum - bNum;
                    }
                    return isAsc ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
                });

                // Apply sort class
                this.classList.add(isAsc ? 'sort-desc' : 'sort-asc');

                // Re-render rows
                rows.forEach(function(row) { tbody.appendChild(row); });
            });
        });
    }

    // ─── Initialize on DOM Ready ──────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function() {
        initReglaForm();
        bindTramoRemoveEvents();
        initAsignacionValidation();
        initPreviewCalculo();
        initConfirmarLiquidacion();
        initAnularLiquidacion();
        initDeleteConfirmations();
        initTogglePlan();
        initReportFilters();
        initDuplicatePlan();
        initTableSort();
    });

    // ─── Public API (for inline scripts) ──────────────────────────────
    window.Comisiones = {
        addTramoRow: addTramoRow,
        removeTramoRow: removeTramoRow,
        formatearMoneda: formatearMoneda
    };

})();
