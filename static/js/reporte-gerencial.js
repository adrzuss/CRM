/**
 * JavaScript para Reporte Gerencial
 * Sistema CRM - SoftTech
 * Gestión de gráficos con Chart.js
 */

// Paleta de colores consistente
const COLORES = {
    primary: '#4e73df',
    success: '#1cc88a',
    info: '#36b9cc',
    warning: '#f6c23e',
    danger: '#e74a3b',
    secondary: '#858796',
    light: '#f8f9fc',
    dark: '#5a5c69'
};

const PALETA_GRAFICOS = [
    '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
    '#858796', '#6610f2', '#fd7e14', '#20c997', '#6f42c1'
];

// Configuración global de Chart.js
Chart.defaults.font.family = "'Nunito', sans-serif";
Chart.defaults.color = '#858796';

/**
 * Inicializa todos los gráficos del reporte
 * @param {Object} datos - Datos del reporte pasados desde el servidor
 */
function inicializarGraficos(datos) {
    crearGraficoEvolucion(datos.evolucion);
    crearGraficoMediosPago(datos.mediosPago);
    crearGraficoSucursales(datos.sucursales);
    crearGraficoBurbujasSecciones('chartBurbujasCantidadSeccion', datos.secciones, 'cantidad');
    crearGraficoBurbujasSecciones('chartBurbujasImporteSeccion', datos.secciones, 'importe');
}

/**
 * Gráfico de evolución de ventas (línea/área)
 */
function crearGraficoEvolucion(datos) {
    const ctx = document.getElementById('chartEvolucionVentas');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: datos.periodos,
            datasets: [{
                label: 'Ventas',
                data: datos.totales,
                borderColor: COLORES.primary,
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3,
                pointBackgroundColor: COLORES.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return 'Ventas: ' + formatearMoneda(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return formatearMonedaCorta(value);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Gráfico de medios de pago (dona)
 */
function crearGraficoMediosPago(datos) {
    const ctx = document.getElementById('chartMediosPago');
    if (!ctx || !datos.nombres.length) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: datos.nombres,
            datasets: [{
                data: datos.totales,
                backgroundColor: PALETA_GRAFICOS.slice(0, datos.nombres.length),
                borderColor: '#fff',
                borderWidth: 2,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const porcentaje = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + formatearMoneda(context.parsed) + ' (' + porcentaje + '%)';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Gráfico de ventas por sucursal (pie)
 */
function crearGraficoSucursales(datos) {
    const ctx = document.getElementById('chartSucursales');
    if (!ctx || !datos.nombres.length) return;

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: datos.nombres,
            datasets: [{
                data: datos.ventas,
                backgroundColor: PALETA_GRAFICOS.slice(0, datos.nombres.length),
                borderColor: '#fff',
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 10,
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const porcentaje = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + formatearMoneda(context.parsed) + ' (' + porcentaje + '%)';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Gráfico de burbujas por sección/rubro.
 * Eje X = días de inventario, eje Y = cantidad o importe vendido, radio = stock actual.
 */
function crearGraficoBurbujasSecciones(canvasId, secciones, modo) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !secciones || !secciones.length) return;

    const datos = secciones.map((seccion, index) => {
        const radioBase = Math.max(seccion.stock_actual || 0, 1);
        const radio = Math.max(6, Math.min(28, Math.sqrt(radioBase) * 1.8));

        return {
            x: seccion.dias_inventario,
            y: modo === 'cantidad' ? seccion.unidades_vendidas : seccion.monto_raw,
            r: radio,
            nombre: seccion.nombre,
            stock: seccion.stock_actual,
            rotacion: seccion.rotacion,
            unidades: seccion.unidades_vendidas,
            monto: seccion.monto_raw,
            color: PALETA_GRAFICOS[index % PALETA_GRAFICOS.length]
        };
    });

    new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: [{
                data: datos,
                backgroundColor: datos.map((item) => `${item.color}99`),
                borderColor: datos.map((item) => item.color),
                borderWidth: 1.5,
                hoverBorderWidth: 2.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.82)',
                    displayColors: false,
                    callbacks: {
                        title: function(context) {
                            return context[0].raw.nombre;
                        },
                        label: function(context) {
                            const item = context.raw;
                            const valorPrincipal = modo === 'cantidad'
                                ? `Unidades vendidas: ${item.unidades}`
                                : `Importe vendido: ${formatearMoneda(item.monto)}`;

                            return [
                                valorPrincipal,
                                `Dias de inventario: ${item.x}`,
                                `Stock actual: ${item.stock}`,
                                `Rotacion: ${item.rotacion}x`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Dias de inventario'
                    },
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: modo === 'cantidad' ? 'Unidades vendidas' : 'Importe vendido'
                    },
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return modo === 'cantidad' ? value : formatearMonedaCorta(value);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Formatea un número como moneda argentina
 */
function formatearMoneda(valor) {
    if (valor === null || valor === undefined) return '$0,00';
    return '$' + valor.toLocaleString('es-AR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/**
 * Formatea moneda en versión corta para ejes
 */
function formatearMonedaCorta(valor) {
    if (valor >= 1000000) {
        return '$' + (valor / 1000000).toFixed(1) + 'M';
    } else if (valor >= 1000) {
        return '$' + (valor / 1000).toFixed(0) + 'K';
    }
    return '$' + valor.toFixed(0);
}

/**
 * Manejo del formulario de filtros
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('filtros-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Validar que desde <= hasta
            const desde = document.getElementById('desde').value;
            const hasta = document.getElementById('hasta').value;
            
            if (desde && hasta && desde > hasta) {
                e.preventDefault();
                alert('La fecha "desde" no puede ser mayor que la fecha "hasta"');
                return false;
            }
        });
    }
    
    // Atajos de teclado para rangos de fechas comunes
    document.addEventListener('keydown', function(e) {
        // Alt + H = Hoy
        if (e.altKey && e.key === 'h') {
            e.preventDefault();
            setRangoFechas(0);
        }
        // Alt + S = Semana
        if (e.altKey && e.key === 's') {
            e.preventDefault();
            setRangoFechas(7);
        }
        // Alt + M = Mes
        if (e.altKey && e.key === 'm') {
            e.preventDefault();
            setRangoFechas(30);
        }
        // Alt + T = Trimestre
        if (e.altKey && e.key === 't') {
            e.preventDefault();
            setRangoFechas(90);
        }
    });
});

/**
 * Establece un rango de fechas relativo
 */
function setRangoFechas(dias) {
    const hoy = new Date();
    const desde = new Date();
    desde.setDate(hoy.getDate() - dias);
    
    document.getElementById('desde').value = formatearFecha(desde);
    document.getElementById('hasta').value = formatearFecha(hoy);
}

/**
 * Formatea fecha para input type="date"
 */
function formatearFecha(fecha) {
    return fecha.toISOString().split('T')[0];
}

/**
 * Exportar reporte a PDF (usando print del navegador)
 */
function exportarPDF() {
    window.print();
}

/**
 * Actualizar solo una sección del reporte via HTMX (opcional)
 */
function actualizarSeccion(seccion) {
    const desde = document.getElementById('desde').value;
    const hasta = document.getElementById('hasta').value;
    
    htmx.ajax('GET', `/api/reporte-gerencial/${seccion}?desde=${desde}&hasta=${hasta}`, {
        target: `#seccion-${seccion}`,
        swap: 'innerHTML'
    });
}
