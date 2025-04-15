export default class KeywordAnalysis {
    constructor(data, modalId = 'keywordTrendModal') {
        this.keywordData = data;
        this.modalId = modalId;
        this.trendChartInstance = null;
        this.regionChartInstance = null;
        console.info('[KeywordAnalysis] initialized.');
    }

    init() {
        document.querySelectorAll('[data-keyword-index]').forEach(el => {
            el.addEventListener('click', () => {
                const index = parseInt(el.getAttribute('data-keyword-index'));
                this.openKeywordModal(index);
            });
        });
    }

    openKeywordModal(index) {
        const data = this.keywordData[index];
        const modalElement = document.getElementById(this.modalId);
        const modalTitle = document.getElementById("keywordTrendModalLabel");
        modalTitle.textContent = `Keyword: ${data.keyword}`;

        if (this.trendChartInstance) {
            this.trendChartInstance.destroy();
            this.trendChartInstance = null;
        }
        if (this.regionChartInstance) {
            this.regionChartInstance.destroy();
            this.regionChartInstance = null;
        }

        const onModalShown = () => {
            const trendCtx = document.getElementById("trendChartModal").getContext("2d");
            this.trendChartInstance = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: JSON.parse(data.trend_keys),
                    datasets: [{
                        label: 'Trend over time',
                        data: JSON.parse(data.trend_values),
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { ticks: { maxTicksLimit: 6 } },
                        y: { beginAtZero: true }
                    }
                }
            });

            const regionData = data.interest_by_region || {};
            const regionLabels = Object.keys(regionData);
            const rawValues = Object.values(regionData);
            const total = rawValues.reduce((sum, val) => sum + val, 0);
            const regionValues = rawValues.map(val => ((val / total) * 100).toFixed(2));

            const regionCtx = document.getElementById("regionChartModal").getContext("2d");
            this.regionChartInstance = new Chart(regionCtx, {
                type: 'pie',
                data: {
                    labels: regionLabels,
                    datasets: [{
                        data: regionValues,
                        backgroundColor: regionLabels.map(() => `hsl(${Math.random() * 360}, 60%, 70%)`),
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'right' },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    return `${label}: ${value}%`;
                                }
                            }
                        }
                    }
                }
            });

            modalElement.removeEventListener('shown.bs.modal', onModalShown);
        };

        modalElement.addEventListener('shown.bs.modal', onModalShown);

        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }

}