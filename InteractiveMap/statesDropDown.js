// dropdown to display the district names for pie charts
function azdropDownDist() {
  var selectedPieChart = document.getElementById("pieChartDropDown");
  const pirChart1 = document.getElementById("pieChart1");
  const pirChart2 = document.getElementById("pieChart2");

  if (selectedPieChart.value == 1) {
    pieChart1.src = "/PieCharts/az/current/arizona_pie_chart1.png";
    pieChart2.src = "/PieCharts/az/new/arizona_pie_chart1.png";
  } else if (selectedPieChart.value == 2) {
    pieChart1.src = "/PieCharts/az/current/arizona_pie_chart2.png";
    pieChart2.src = "/PieCharts/az/new/arizona_pie_chart2.png";
  } else if (selectedPieChart.value == 3) {
    pieChart1.src = "/PieCharts/az/current/arizona_pie_chart3.png";
    pieChart2.src = "/PieCharts/az/new/arizona_pie_chart3.png";
  } else if (selectedPieChart.value == 4) {
    pieChart1.src = "/PieCharts/az/current/arizona_pie_chart4.png";
    pieChart2.src = "/PieCharts/az/new/arizona_pie_chart4.png";
  } else if (selectedPieChart.value == 5) {
    pieChart1.src = "/PieCharts/az/current/arizona_pie_chart5.png";
    pieChart2.src = "/PieCharts/az/new/arizona_pie_chart5.png";
  } else if (selectedPieChart.value == 6) {
    pieChart1.src = "/PieCharts/az/current/arizona_pie_chart6.png";
    pieChart2.src = "/PieCharts/az/new/arizona_pie_chart6.png";
  } else if (selectedPieChart.value == 7) {
    pieChart1.src = "/PieCharts/az/current/arizona_pie_chart7.png";
    pieChart2.src = "/PieCharts/az/new/arizona_pie_chart7.png";
  } else if (selectedPieChart.value == 8) {
    pieChart1.src = "/PieCharts/az/current/arizona_pie_chart8.png";
    pieChart2.src = "/PieCharts/az/new/arizona_pie_chart8.png";
  } else if (selectedPieChart.value == 9) {
    pieChart1.src = "/PieCharts/az/current/arizona_pie_chart9.png";
    pieChart2.src = "/PieCharts/az/new/arizona_pie_chart9.png";
  } else {
    pieChart = "";
  }
  document.getElementById("pieChart").src = pieChart;
}

// https://stackoverflow.com/questions/62171089/show-image-when-option-is-selected
