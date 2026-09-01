/**
 * JavaScript para Dashboard Gerencial — Etapas 1-6
 * Inicialización de Chart.js 4, manejo de filtros, HTMX lifecycle,
 * drill-down, loading states, tooltips, navegación (Etapa 6)
 */
(function() {
    'use strict';

    // ─── Paleta de colores ──────────────────────────────────────────────
    const COLORES = {
        primary: '#4e73df',
        success: '#1cc88a',
        info: '#36b9cc',
        warning: '#f6c23e',
        danger: '#e74a3b',
        secondary: '#858796'
    };

    const PALETA = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
        '#858796', '#6610f2', '#fd7e14', '#20c997', '#6f42c1'
    ];

    // ─── Instancias de charts ───────────────────────────────────────────
    let chartEvolucion = null;
    let chartRubros = null;
    let chartRubrosCantidad = null;

    // ─── Helpers ────────────────────────────────────────────────────────
    function formatearMoneda(valor) {
        if (valor === null || valor === undefined) return '$ 0,00';
        return '$ ' + valor.toLocaleString('es-AR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    function formatearFecha(fecha) {
        return fecha.toISOString().split('T')[0];
    }

    function setRangoFechas(dias) {
        const hoy = new Date();
        const desde = new Date();
        desde.setDate(hoy.getDate() - dias);
        document.getElementById('desde').value = formatearFecha(desde);
        document.getElementById('hasta').value = formatearFecha(hoy);
    }

    // ─── Configuración global Chart.js ──────────────────────────────────
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Nunito', sans-serif";
        Chart.defaults.color = '#858796';
    }

    // ─── Gráfico de evolución ───────────────────────────────────────────
    function crearGraficoEvolucion(evolucion) {
        const ctx = document.getElementById('chartEvolucion');
        if (!ctx || !evolucion || !evolucion.periodos || evolucion.periodos.length === 0) return;

        if (chartEvolucion) {
            chartEvolucion.destroy();
            chartEvolucion = null;
        }

        const datasets = [{
            label: 'Ventas período actual',
            data: evolucion.totales,
            borderColor: COLORES.primary,
            backgroundColor: 'rgba(78, 115, 223, 0.08)',
            borderWidth: 2,
            fill: true,
            tension: 0.3,
            pointBackgroundColor: COLORES.primary,
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 3,
            pointHoverRadius: 5
        }];

        if (evolucion.totales_anteriores && evolucion.totales_anteriores.length > 0) {
            datasets.push({
                label: 'Período anterior',
                data: evolucion.totales_anteriores,
                borderColor: COLORES.secondary,
                backgroundColor: 'rgba(133, 135, 150, 0.05)',
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                tension: 0.3,
                pointBackgroundColor: COLORES.secondary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 5
            });
        }

        chartEvolucion = new Chart(ctx, {
            type: 'line',
            data: {
                labels: evolucion.periodos,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'index' },
                plugins: {
                    legend: { display: datasets.length > 1 },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: function(ctx) {
                                return ctx.dataset.label + ': ' + formatearMoneda(ctx.parsed.y);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { maxRotation: 45, minRotation: 0 }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(v) {
                                if (v >= 1000000) return '$' + (v / 1000000).toFixed(1) + 'M';
                                if (v >= 1000) return '$' + (v / 1000).toFixed(0) + 'K';
                                return '$' + v;
                            }
                        },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    }
                }
            }
        });
    }

    // ─── Gráfico doughnut de rubros ─────────────────────────────────────
    function crearGraficoRubros(rubros) {
        const ctx = document.getElementById('chartRubrosMonto');
        if (!ctx || !rubros || !rubros.rubros || rubros.rubros.length === 0) return;

        if (chartRubros) {
            chartRubros.destroy();
            chartRubros = null;
        }

        // Ordenar por importe de mayor a menor
        const rubrosOrdenados = rubros.rubros.slice().sort(function(a, b) { return b.importe_raw - a.importe_raw; });
        const labels = rubrosOrdenados.map(function(r) { return r.rubro; });
        const values = rubrosOrdenados.map(function(r) { return r.importe_raw; });

        chartRubros = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: PALETA.slice(0, labels.length),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 12,
                        callbacks: {
                            label: function(ctx) {
                                const total = ctx.dataset.data.reduce(function(a, b) { return a + b; }, 0);
                                const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
                                return ctx.label + ': ' + formatearMoneda(ctx.parsed) + ' (' + pct + '%)';
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    // ─── Gráfico doughnut de rubros por cantidad ──────────────────────────
    function crearGraficoRubrosCantidad(rubros) {
        const ctx = document.getElementById('chartRubrosCantidad');
        if (!ctx || !rubros || !rubros.rubros || rubros.rubros.length === 0) return;

        if (chartRubrosCantidad) {
            chartRubrosCantidad.destroy();
            chartRubrosCantidad = null;
        }

        // Ordenar por unidades de mayor a menor
        const rubrosOrdenados = rubros.rubros.slice().sort(function(a, b) { return b.unidades - a.unidades; });
        const labels = rubrosOrdenados.map(function(r) { return r.rubro; });
        const values = rubrosOrdenados.map(function(r) { return r.unidades; });
        const totalUnidades = rubros.total_unidades || 1;

        chartRubrosCantidad = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: PALETA.slice(0, labels.length),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 12,
                        callbacks: {
                            label: function(ctx) {
                                var unidades = ctx.parsed;
                                var pct = totalUnidades > 0 ? ((unidades / totalUnidades) * 100).toFixed(1) : 0;
                                return ctx.label + ': ' + unidades + ' uds (' + pct + '%)';
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    // ─── API: Actualizar sección vía HTMX ───────────────────────────────
    function actualizarSeccion(seccion) {
        var desde = document.getElementById('desde').value;
        var hasta = document.getElementById('hasta').value;
        var idSuc = document.getElementById('id_sucursal') ? document.getElementById('id_sucursal').value : '';
        var comparar = document.getElementById('comparar') && document.getElementById('comparar').checked ? '1' : '0';
        var params = 'desde=' + desde + '&hasta=' + hasta + '&comparar=' + comparar;
        if (idSuc) params += '&id_sucursal=' + idSuc;

        fetch('/api/dashboard-gerencial/' + seccion + '?' + params)
            .then(function(r) { return r.json(); })
            .then(function(json) {
                if (json.success) {
                    var target = document.getElementById('seccion-' + seccion);
                    if (target && json.data) {
                        target.dataset.json = JSON.stringify(json.data);
                    }
                }
            })
            .catch(function(e) { console.error('Error actualizando ' + seccion, e); });
    }

    // ─── Inicializar todo el dashboard ───────────────────────────────────
    window.inicializarDashboard = function(datos) {
        if (!datos) return;
        if (datos.evolucion) {
            crearGraficoEvolucion(datos.evolucion);
            configurarDrillDownLinea(chartEvolucion);
        }
        if (datos.rubros) {
            crearGraficoRubros(datos.rubros);
            crearGraficoRubrosCantidad(datos.rubros);
            configurarDrillDownDoughnut(chartRubros, '#seccion-rubros-monto');
            configurarDrillDownDoughnut(chartRubrosCantidad, '#seccion-rubros-cantidad');
        }
        inicializarCtaCte();
        inicializarBancosCaja();
        // Etapa 6
        inicializarDrillDown();
        inicializarAlertasDrillDown();
        inicializarLoadingStates();
        inicializarTooltips();
        inicializarNavegacion();
    };

    // ─── Productos sin movimiento: toggle días ───────────────────────────
    function inicializarSinMovimiento() {
        var diasBtns = document.querySelectorAll('.dias-btn');
        diasBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                // Actualizar estado activo
                diasBtns.forEach(function(b) { b.classList.remove('active'); });
                this.classList.add('active');

                var dias = this.getAttribute('data-dias');
                var idSuc = document.getElementById('id_sucursal') ? document.getElementById('id_sucursal').value : '';
                var params = '?dias=' + dias;
                if (idSuc) params += '&id_sucursal=' + idSuc;

                fetch('/api/dashboard-gerencial/stock-sin-movimiento' + params)
                    .then(function(r) { return r.json(); })
                    .then(function(json) {
                        if (json.success && json.data) {
                            renderizarSinMovimiento(json.data);
                        }
                    })
                    .catch(function(e) { console.error('Error sin movimiento:', e); });
            });
        });
    }

    function renderizarSinMovimiento(data) {
        var tbody = document.getElementById('tbody-sin-movimiento');
        if (!tbody) return;

        if (!data.productos || data.productos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-3">' +
                '<i class="fas fa-info-circle me-1"></i>No hay productos sin movimiento para este período.</td></tr>';
            return;
        }

        var html = '';
        data.productos.forEach(function(p) {
            var ventaHtml = p.ultima_venta
                ? '<span class="small">' + p.ultima_venta_display + '</span>'
                : '<span class="badge badge-stock-bajo-minimo">Sin ventas</span>';
            html += '<tr>' +
                '<td class="text-muted">' + (p.codigo || '') + '</td>' +
                '<td>' + (p.detalle || '') + '</td>' +
                '<td><span class="small text-muted">' + (p.rubro || '') + '</span></td>' +
                '<td class="text-center">' + p.stock_actual + '</td>' +
                '<td>' + ventaHtml + '</td>' +
                '</tr>';
        });
        tbody.innerHTML = html;

        // Actualizar indicador de truncación
        var card = tbody.closest('.card');
        if (card) {
            var existing = card.querySelector('.truncate-indicator');
            if (existing) existing.remove();
            if (data.tiene_mas) {
                var div = document.createElement('div');
                div.className = 'text-center text-muted small py-2 border-top truncate-indicator';
                div.innerHTML = '<i class="fas fa-info-circle me-1"></i>Mostrando ' +
                    data.mostrando + ' de ' + data.total + '+ productos';
                card.querySelector('.card-body').appendChild(div);
            }
        }
    }

    // ─── Cuentas por Cobrar / Pagar: init ───────────────────────────────
    function inicializarCtaCte() {
        // Placeholder para futuro refresh HTMX de secciones cta_cte
        // Las tablas se renderizan server-side con Jinja2
    }

    // ─── Bancos / Caja: init ────────────────────────────────────────────
    function inicializarBancosCaja() {
        // Placeholder para futuro refresh HTMX de secciones bancos/caja
        // Las tablas se renderizan server-side con Jinja2
    }

    // ─── Destruir charts (para HTMX beforeSwap) ─────────────────────────
    window.destruirCharts = function() {
        if (chartEvolucion) { chartEvolucion.destroy(); chartEvolucion = null; }
        if (chartRubros) { chartRubros.destroy(); chartRubros = null; }
        if (chartRubrosCantidad) { chartRubrosCantidad.destroy(); chartRubrosCantidad = null; }
    };

    // ─── Drill-Down: click en KPI cards ──────────────────────────────────
    function inicializarDrillDown() {
        document.addEventListener('click', function(e) {
            var target = e.target.closest('.drill-down');
            if (target) {
                var seccionId = target.getAttribute('data-target');
                if (seccionId) {
                    var seccion = document.getElementById(seccionId);
                    if (seccion) {
                        seccion.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            }
        });
    }

    // ─── Drill-Down: click en alertas ────────────────────────────────────
    function inicializarAlertasDrillDown() {
        document.addEventListener('click', function(e) {
            var alerta = e.target.closest('.dg-alerta-card');
            if (alerta) {
                var seccionId = alerta.getAttribute('data-target');
                if (seccionId) {
                    var seccion = document.getElementById(seccionId);
                    if (seccion) {
                        seccion.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            }
        });
    }

    // ─── Drill-Down: click en doughnut (rubros) ──────────────────────────
    function inicializarDrillDownRubros() {
        // Se ejecuta después de crear chartRubros
        // El handler se configura en crearGraficoRubros
    }

    // ─── Drill-Down: click en línea (evolución) ──────────────────────────
    function inicializarDrillDownEvolucion() {
        // Se ejecuta después de crear chartEvolucion
        // El handler se configura en crearGraficoEvolucion
    }

    // ─── Loading states HTMX ────────────────────────────────────────────
    function inicializarLoadingStates() {
        document.body.addEventListener('htmx:beforeRequest', function(e) {
            var elt = e.detail.elt;
            if (elt) {
                var card = elt.closest('.card');
                if (card) {
                    var spinner = document.createElement('div');
                    spinner.className = 'dg-spinner-overlay';
                    spinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div>';
                    card.style.position = 'relative';
                    card.appendChild(spinner);
                }
            }
        });

        document.body.addEventListener('htmx:afterRequest', function(e) {
            var elt = e.detail.elt;
            if (elt) {
                var card = elt.closest('.card');
                if (card) {
                    var spinner = card.querySelector('.dg-spinner-overlay');
                    if (spinner) spinner.remove();
                }
            }
        });
    }

    // ─── Tooltips Bootstrap 5 ───────────────────────────────────────────
    function inicializarTooltips() {
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function(el) {
                new bootstrap.Tooltip(el);
            });
        }
    }

    // ─── Navegación entre secciones ──────────────────────────────────────
    function inicializarNavegacion() {
        // Toggle del menú de navegación
        var navToggle = document.querySelector('.dg-nav-toggle');
        var navLinks = document.querySelector('.dg-nav-links');
        if (navToggle && navLinks) {
            navToggle.addEventListener('click', function() {
                navLinks.classList.toggle('dg-nav-links--open');
            });
        }

        // Click en links de navegación
        document.addEventListener('click', function(e) {
            var link = e.target.closest('.nav-seccion');
            if (link) {
                e.preventDefault();
                var href = link.getAttribute('href');
                if (href && href.startsWith('#')) {
                    var seccion = document.querySelector(href);
                    if (seccion) {
                        seccion.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
                // Cerrar menú en mobile
                if (navLinks) navLinks.classList.remove('dg-nav-links--open');
            }
        });
    }

    // ─── Actualizar gráfico doughnut con onClick ─────────────────────────
    function configurarDrillDownDoughnut(chart, tableSelector) {
        if (!chart) return;
        chart.options.onClick = function(evt, activeElements) {
            if (activeElements.length > 0) {
                var index = activeElements[0].index;
                var label = chart.data.labels[index];
                // Resaltar fila en tabla correspondiente
                var tabla = document.querySelector(tableSelector + ' table tbody');
                if (tabla) {
                    // Remover highlight anterior
                    tabla.querySelectorAll('tr.table-active').forEach(function(r) {
                        r.classList.remove('table-active');
                    });
                    // Buscar fila por texto del rubro
                    var filas = tabla.querySelectorAll('tr');
                    filas.forEach(function(fila) {
                        var celda = fila.querySelector('td:first-child');
                        if (celda && celda.textContent.trim() === label) {
                            fila.classList.add('table-active');
                            fila.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    });
                }
            }
        };
        chart.update();
    }

    // ─── Actualizar gráfico línea con onClick ────────────────────────────
    function configurarDrillDownLinea(chart) {
        if (!chart) return;
        chart.options.onClick = function(evt, activeElements) {
            if (activeElements.length > 0) {
                var index = activeElements[0].index;
                var label = chart.data.labels[index];
                // Mostrar badge temporal con el período
                var canvas = chart.canvas;
                var container = canvas.parentElement;
                var badge = container.querySelector('.dg-periodo-badge');
                if (!badge) {
                    badge = document.createElement('div');
                    badge.className = 'dg-periodo-badge';
                    container.appendChild(badge);
                }
                badge.textContent = label;
                badge.style.display = 'block';
                setTimeout(function() { badge.style.display = 'none'; }, 3000);
            }
        };
        chart.update();
    }

    // ─── Eventos HTMX ───────────────────────────────────────────────────
    document.body.addEventListener('htmx:beforeSwap', function() {
        window.destruirCharts();
    });

    document.body.addEventListener('htmx:afterSwap', function(evt) {
        // Re-parsear datos inline si existen
        var el = evt.detail.target || evt.detail.elt;
        if (el && el.id === 'seccion-evolucion') {
            var json = el.dataset.json;
            if (json) {
                try {
                    var data = JSON.parse(json);
                    crearGraficoEvolucion(data);
                } catch(e) {}
            }
        }
        if (el && (el.id === 'seccion-rubros-monto' || el.id === 'seccion-rubros-cantidad')) {
            var json = el.dataset.json;
            if (json) {
                try {
                    var data = JSON.parse(json);
                    crearGraficoRubros(data);
                    crearGraficoRubrosCantidad(data);
                } catch(e) {}
            }
        }
    });

    // ─── Filtros: submit del form ───────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function() {
        // Nota: los datos iniciales se pasan desde Jinja al final del archivo
        var form = document.getElementById('filtros-form');
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                var desde = document.getElementById('desde').value;
                var hasta = document.getElementById('hasta').value;
                if (desde && hasta && desde > hasta) {
                    alert('La fecha "desde" no puede ser mayor que la fecha "hasta"');
                    return;
                }
                // Actualizar secciones vía fetch y re-render
                var idSuc = document.getElementById('id_sucursal') ? document.getElementById('id_sucursal').value : '';
                var comparar = document.getElementById('comparar') && document.getElementById('comparar').checked ? '1' : '0';
                var params = '?desde=' + desde + '&hasta=' + hasta + '&comparar=' + comparar;
                if (idSuc) params += '&id_sucursal=' + idSuc;
                window.location.href = '/dashboard-gerencial' + params;
            });
        }

        // Botones de presets de fecha
        var presets = document.querySelectorAll('.preset-btn');
        presets.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var dias = parseInt(this.getAttribute('data-dias'), 10);
                setRangoFechas(dias);
                // Disparar submit
                if (form) form.dispatchEvent(new Event('submit'));
            });
        });

        // Botones de granularidad
        var granBtns = document.querySelectorAll('.granularidad-btn');
        granBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                granBtns.forEach(function(b) { b.classList.remove('active'); });
                this.classList.add('active');
                var g = this.getAttribute('data-g');
                // Actualizar evolución con granularidad
                var desde = document.getElementById('desde').value;
                var hasta = document.getElementById('hasta').value;
                var idSuc = document.getElementById('id_sucursal') ? document.getElementById('id_sucursal').value : '';
                var params = '?desde=' + desde + '&hasta=' + hasta + '&granularidad=' + g;
                if (idSuc) params += '&id_sucursal=' + idSuc;
                fetch('/api/dashboard-gerencial/evolucion' + params)
                    .then(function(r) { return r.json(); })
                    .then(function(json) {
                        if (json.success && json.data) {
                            window.destruirCharts();
                            crearGraficoEvolucion(json.data);
                            if (datosDashboard && datosDashboard.rubros) {
                                crearGraficoRubros(datosDashboard.rubros);
                                crearGraficoRubrosCantidad(datosDashboard.rubros);
                            }
                        }
                    })
                    .catch(function(e) { console.error('Error granularidad:', e); });
            });
        });

        // Botón imprimir
        var btnPrint = document.getElementById('btnImprimir');
        if (btnPrint) {
            btnPrint.addEventListener('click', function() { window.print(); });
        }

        // Atajos de teclado
        document.addEventListener('keydown', function(e) {
            if (e.altKey && e.key === 'h') { e.preventDefault(); setRangoFechas(0); form.dispatchEvent(new Event('submit')); }
            if (e.altKey && e.key === 's') { e.preventDefault(); setRangoFechas(7); form.dispatchEvent(new Event('submit')); }
            if (e.altKey && e.key === 'm') { e.preventDefault(); setRangoFechas(30); form.dispatchEvent(new Event('submit')); }
            if (e.altKey && e.key === 't') { e.preventDefault(); setRangoFechas(90); form.dispatchEvent(new Event('submit')); }
        });

        // Inicializar toggle de días para productos sin movimiento
        inicializarSinMovimiento();
    });

})();
