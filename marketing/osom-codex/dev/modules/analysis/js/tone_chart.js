export default class ToneChart {
    constructor(chartId) {
        this.chartId = chartId;
        console.info('[ToneChart] initialized.');
    }

    init() {
        document.addEventListener("DOMContentLoaded", () => {
            const chartElement = document.getElementById(this.chartId);
            if (chartElement) {
                const ctx = chartElement.getContext("2d");
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
    }
  }
