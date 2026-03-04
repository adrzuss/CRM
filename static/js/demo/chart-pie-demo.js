// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example
var ctx = document.getElementById("myPieChart");
var tipoPagos;
var cantPagos;
var coloresPie;


var ctx2 = document.getElementById("myPieChart2");
var ctx3 = document.getElementById("myPieChart3");
var nombresRubros;
var ventasRubros;
var cantidadRubros;

coloresPie = ['#1150af', '#008060', '#bb1133', '#eb4315ff', '#f6a22d', '#80184eff'];
coloresPieHover = ['#1870F5','#00EDB2', '#FF1746', '#ec6e4bff', '#fac06eff', '#81345cff']

// Paleta moderna - Tailwind CSS vibrantes equilibrados
coloresPie2 = ['#EF4444', '#F97316', '#F59E0B', '#EAB308',
               '#84CC16', '#22C55E', '#10B981', '#14B8A6',
               '#06B6D4', '#0EA5E9', '#3B82F6', '#6366F1',
               '#8B5CF6', '#A855F7', '#D946EF', '#EC4899'];
coloresPieHover2 = ['#FCA5A5', '#FDBA74', '#FCD34D', '#FDE047',
                    '#BEF264', '#86EFAC', '#6EE7B7', '#5EEAD4',
                    '#67E8F9', '#7DD3FC', '#93C5FD', '#A5B4FC',
                    '#C4B5FD', '#D8B4FE', '#F0ABFC', '#F9A8D4'];


window.onload = () => {
  const titulosPie = document.getElementById('coloresPie');
  for(let i = 0; i < tipoPagos.length; i++){
    titulosPie.innerHTML += '<span class="mr-2">  <i class="fas fa-circle" style="color:' + coloresPie[i] + '"></i> ' + tipoPagos[i] + ' </span>';
  }
  
}

var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: tipoPagos,
    datasets: [{
      data: cantPagos,
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
    cutoutPercentage: 50,
  },
});

var myPieChart2 = new Chart(ctx2, {
  type: 'pie',
  data: {
    labels: nombresRubros,
    datasets: [{
      data: ventasRubros,
      backgroundColor: coloresPie2,
      hoverBackgroundColor: coloresPieHover2,
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

var myPieChart3 = new Chart(ctx3, {
  type: 'pie',
  data: {
    labels: nombresRubros,
    datasets: [{
      data: cantidadRubros,
      backgroundColor: coloresPie2,
      hoverBackgroundColor: coloresPieHover2,
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
