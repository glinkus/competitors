export default class UniversalMetricChart {
    constructor(config) {
        this.chartId = config.chartId;
        this.triggerId = config.triggerId;
        this.metricSelectId = config.metricSelectId || config.toneSelectId; // 🎯 fallback for old tone config
        this.chartTypeSelectId = config.chartTypeSelectId;
        this.labels = config.labels;
        this.datasets = config.datasets || config.dataSet; // 🎯 fallback for flat array
        this.chart = null;
        this.colors = config.colors || {
            border: '#0d6efd',
            background: 'rgba(13, 110, 253, 0.2)',
            point: '#0d6efd'
        };
    }

    init() {
        const trigger = document.getElementById(this.triggerId);
        if (trigger) {
            trigger.addEventListener('click', () => this.render());
        }
    }

    render() {
        const metric = document.getElementById(this.metricSelectId)?.value || 'unknown';
        const chartType = this.chartTypeSelectId
            ? document.getElementById(this.chartTypeSelectId).value
            : 'line';

        const ctx = document.getElementById(this.chartId);

        if (this.chart) {
            this.chart.destroy();
        }

        let data = [];

        // Support for: datasets = [{ key: 'ttfb', values: [...] }]
        if (Array.isArray(this.datasets) && typeof this.datasets[0] === 'object') {
            data = this.datasets.find(d => d.key === metric)?.values || [];
        }
        // Support for: datasets = { ttfb: [...] }
        else if (typeof this.datasets === 'object' && this.datasets !== null) {
            data = this.datasets[metric] || [];
        }
        // Support for: dataSet = flat array for tone (no selector used)
        else if (Array.isArray(this.datasets)) {
            // supports array of objects (tone-style)
            if (typeof this.datasets[0] === 'object') {
                data = this.datasets.map(d => d[metric] ?? 0);
            } else {
                // flat values array fallback
                data = this.datasets;
            }
        }
        

        this.chart = new Chart(ctx, {
            type: chartType,
            data: {
                labels: this.labels,
                datasets: [
                    {
                        label: `${metric.charAt(0).toUpperCase() + metric.slice(1)} per Page`,
                        data: data,
                        borderColor: this.colors.border,
                        backgroundColor: this.colors.background,
                        pointBackgroundColor: this.colors.point,
                        tension: 0.4,
                        fill: chartType === 'line',
                        pointRadius: 3
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Value'
                        }
                    }
                }
            }
        });
    }
}
