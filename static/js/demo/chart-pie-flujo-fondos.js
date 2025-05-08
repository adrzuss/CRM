// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example
let ctx = document.getElementById("pieChartIngEgr");
var tipoPagos;
var cantPagos;
let coloresPie;

/*coloresPie = ['#4e73df', '#1cc88a', '#36b9cc', '#731d56', '#c81b90', '#277540'];*/
coloresVtasCompras = ['#008060', '#AF2715', '#af2ea0'];
coloresVtasComprasHover = ['#00EDB2', '#C35D50', '#d797d0'];

coloresPie = ['#1150af', '#008060', '#bb1133', '#a95943', '#f6a22d', '#4f3844'];
coloresPieHover = ['#1870F5','#00EDB2', '#FF1746'];

let myPieChart = new Chart(ctx, {
  type: 'pie',
  data: {
    labels: tipoPagos,
    datasets: [{
      data: cantPagos,
      backgroundColor: coloresVtasCompras,
      hoverBackgroundColor: coloresVtasComprasHover,
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 0,
  },
});


let ctxCC = document.getElementById("pieChartCtaCtes");
let tipoCtaCtes;
let totCtaCtes;
totCtaCtes = [100, 200];
tipoCtaCtes = ['Cta ctes clientes', 'Cta cte proeveedores'];
/*coloresPie = ['#4e73df', '#1cc88a', '#36b9cc', '#731d56', '#c81b90', '#277540'];*/
coloresPie = ['#1150af', '#008060', '#bb1133', '#a95943', '#f6a22d', '#4f3844'];
coloresPieHover = ['#1870F5','#00EDB2', '#FF1746'];

window.onload = () => {
  const titulosCtaCtes = document.getElementById('ctaCtes');
  for(let i = 0; i < tipoCtaCtes.length; i++){
    titulosCtaCtes.innerHTML += '<span class="mr-2">  <i class="fas fa-circle" style="color:' + coloresPie[i] + '"></i> ' + tipoCtaCtes[i] + ' </span>';
  }

  const titulosIngresosEgresos = document.getElementById('ingresosEgresos');
  for(let i = 0; i < tipoPagos.length; i++){
    titulosIngresosEgresos.innerHTML += '<span class="mr-2">  <i class="fas fa-circle" style="color:' + coloresVtasCompras[i] + '"></i> ' + tipoPagos[i] + ' </span>';
  }
  
}

let myPieChartCC = new Chart(ctxCC, {
  type: 'doughnut', // Pie Chart
  data: {
    labels: tipoCtaCtes,
    datasets: [{
      data: totCtaCtes,
      backgroundColor: coloresPie,
      hoverBackgroundColor: coloresPieHover,
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 30,
  },
});


function number_format(number, decimals, dec_point, thousands_sep) {
  // *     example: number_format(1234.56, 2, ',', ' ');
  // *     return: '1 234,56'
  number = (number + '').replace(',', '').replace(' ', '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.round(n * k) / k;
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}

var coloresBarras;
coloresBarras = ['#9BB0C1', '#E1AFD1', '#C5EBAA', '#FFCF81', '#FF8080', '#B0A695', '#AC87C5', '#99BC85', '#d0daea', '#fdca8f', '#a95943', '#f6a22d', '#4f3844', '#1e3c7c', '#d0daea', '#fdca8f', '#a95943', '#f6a22d'];

// Bar Chart Example
var ctx_gastos = document.getElementById("barrasDetalleGastos");
var det_gastos;
var total_gastos;

var myHorizontalBarChart = new Chart(ctx_gastos, {
    type: 'horizontalBar', // Cambiar a 'horizontalBar' para barras horizontales
    data: {
      labels: det_gastos,
      datasets: [{
        label: "Detalle de gastos",
        backgroundColor: coloresBarras,
        hoverBackgroundColor: "#2e59d9",
        borderColor: "#4e73df",
        data: total_gastos,
      }],
    },
    options: {
      maintainAspectRatio: false,
      layout: {
        padding: {
          left: 10,
          right: 25,
          top: 25,
          bottom: 0
        }
      },
      scales: {
        xAxes: [{
          gridLines: {
            display: false,
            drawBorder: false
          },
          ticks: {
            maxTicksLimit: 6
          },
          maxBarThickness: 50,
        }],
        yAxes: [{
          ticks: {
            min: 0,
            maxTicksLimit: 5,
            padding: 10,
            callback: function(value, index, values) {
              return number_format(value);
            }
          },
          gridLines: {
            color: "rgb(234, 236, 244)",
            zeroLineColor: "rgb(234, 236, 244)",
            drawBorder: false,
            borderDash: [2],
            zeroLineBorderDash: [2]
          }
        }],
      },
      legend: {
        display: false
      },
      tooltips: {
        titleMarginBottom: 10,
        titleFontColor: '#6e707e',
        titleFontSize: 14,
        backgroundColor: "rgb(255,255,255)",
        bodyFontColor: "#858796",
        borderColor: '#dddfeb',
        borderWidth: 1,
        xPadding: 15,
        yPadding: 15,
        displayColors: false,
        caretPadding: 10,
        callbacks: {
          label: function(tooltipItem, chart) {
            var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
            return datasetLabel + ' ' + number_format(tooltipItem.xLabel) + ' articulos';
          }
        }
      },
    }
  });