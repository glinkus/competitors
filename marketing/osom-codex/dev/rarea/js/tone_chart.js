import Chart from 'chart.js/auto';

document.addEventListener("DOMContentLoaded", function () {
  if (document.getElementById("toneChart")) {
    const ctx = document.getElementById("toneChart").getContext("2d");
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: window.toneLabels,
        datasets: [{
          label: 'Tone Score (%)',
          data: window.toneData,
          backgroundColor: 'rgba(255, 203, 119, 1)',
          borderWidth: 1
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    });
  }
});