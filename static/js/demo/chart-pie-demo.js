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

coloresPie2 = ['#b30505ff', '#cf7704ff', '#f8fc05ff', '#669103ff',
               '#0be703ff', '#00c050ff', '#03ece1ff', '#02d2eeff',
               '#0196ecff', '#0155f1ff', '#0414ecff', '#6300c0ff',
               '#b501ecff', '#f101b5ff', '#ec045dff', '#5698beff'];
coloresPieHover2 = ['#b95656ff', '#cf9c59ff', '#f6f86cff', '#758d3dff',
                    '#6ae466ff', '#54be80ff', '#6aebe4ff', '#65dbebff',
                    '#6ab9e7ff', '#6b9bf3ff', '#646ef0ff', '#8f5bc0ff',
                    '#cb64ebff', '#ee73cfff', '#ec6d9eff', '#8eacbdff'];


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
