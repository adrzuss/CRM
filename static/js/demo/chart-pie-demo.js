// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example
var ctx = document.getElementById("myPieChart");
var tipoPagos;
var cantPagos;
var coloresPie;

/*coloresPie = ['#4e73df', '#1cc88a', '#36b9cc', '#731d56', '#c81b90', '#277540'];*/
coloresPie = ['#1150af', '#008060', '#bb1133', '#eb4315ff', '#f6a22d', '#80184eff'];
coloresPieHover = ['#1870F5','#00EDB2', '#FF1746', '#ec6e4bff', '#fac06eff', '#81345cff']

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
