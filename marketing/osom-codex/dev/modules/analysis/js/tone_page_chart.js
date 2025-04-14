export default class TonePageChart {
    constructor(config) {
        this.chartId = config.chartId;
        this.triggerId = config.triggerId;
        this.toneSelectId = config.toneSelectId;
        this.chartTypeSelectId = config.chartTypeSelectId;
        this.labels = config.labels;
        this.dataSet = config.dataSet;
        this.chart = null;
        console.info('[TonePageChart] initialized.');
    }

    init() {
        const trigger = document.getElementById(this.triggerId);
        if (trigger) {
            trigger.addEventListener('click', () => this.render());
        }
    }

    render() {
        const toneType = document.getElementById(this.toneSelectId).value;
        const chartType = document.getElementById(this.chartTypeSelectId).value;
        const ctx = document.getElementById(this.chartId);

        if (this.chart) {
            this.chart.destroy();
        }

        const data = this.dataSet.map(tone => tone[toneType] || 0);

        this.chart = new Chart(ctx, {
            type: chartType,
            data: {
                labels: this.labels,
                datasets: [{
                    label: `${toneType.charAt(0).toUpperCase() + toneType.slice(1)} Score`,
                    data: data,
                    borderColor: '#0dcaf0',
                    backgroundColor: 'rgba(13, 202, 240, 0.2)',
                    tension: 0.4,
                    fill: chartType === 'line',
                    pointRadius: 4,
                    pointBackgroundColor: '#0dcaf0'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}
