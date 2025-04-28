export default class ReadingCharts {
    constructor() {
        console.info('[ReadingCharts] initialized.');
    }

    init() {
        document.addEventListener("DOMContentLoaded", () => {
            const ChartJS = window.Chart;
            const labels = window.readingLabels || [];
            const readingValues = window.readingValues || [];
            const readabilityValues = window.readabilityValues || [];

            const timeCanvas = document.getElementById("readingTimeChart");
            if (timeCanvas) {
                new ChartJS(timeCanvas, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Reading Time (sec)',
                            data: readingValues,
                            borderColor: '#f08080',
                            backgroundColor: 'rgba(240, 128, 128, 0.1)',
                            tension: 0.4,
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: '#f08080'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { 
                                display: false 
                            },
                            y: { beginAtZero: true }
                        }
                    }
                });
            }

            const readabilityCanvas = document.getElementById("readabilityChart");
            if (readabilityCanvas) {
                new ChartJS(readabilityCanvas, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Readability Score',
                            data: readabilityValues,
                            borderColor: '#198754',
                            backgroundColor: 'rgba(25, 135, 84, 0.1)',
                            tension: 0.4,
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: '#198754'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { 
                                display: false 
                            },
                            y: { beginAtZero: true, max: 100 }
                        }
                    }
                });
            }
        });
    }
}
