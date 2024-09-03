// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example
var ctx = document.getElementById("myPieChart");
var tipoEvento;
var cantTipoEvento;
var coloresPie;

/*coloresPie = ['#4e73df', '#1cc88a', '#36b9cc', '#731d56', '#c81b90', '#277540'];*/
coloresPie = ['#1e3c7c', '#d0daea', '#fdca8f', '#a95943', '#f6a22d', '#4f3844'];

window.onload = () => {
  const titulosPie = document.getElementById('coloresPie');
  for(let i = 0; i < tipoEvento.length; i++){
    titulosPie.innerHTML += '<span class="mr-2">  <i class="fas fa-circle" style="color:' + coloresPie[i] + '"></i> ' + tipoEvento[i] + ' </span>';
  }
  
}

var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: tipoEvento,
    datasets: [{
      data: cantTipoEvento,
      backgroundColor: coloresPie,
      hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
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
