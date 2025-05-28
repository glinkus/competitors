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
      
        modalElement.addEventListener('hidden.bs.modal', () => {
          if (this.trendChartInstance) {
            this.trendChartInstance.destroy();
            this.trendChartInstance = null;
          }
          if (this.regionChartInstance) {
            this.regionChartInstance.destroy();
            this.regionChartInstance = null;
          }
        }, { once: true });
      
        const onModalShown = () => {
          const trendCanvas = document.getElementById("trendChartModal");
          Chart.getChart(trendCanvas)?.destroy();
      
          const regionCanvas = document.getElementById("regionChartModal");
          Chart.getChart(regionCanvas)?.destroy();
      
          const trendCtx = trendCanvas.getContext("2d");
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
                y: {
                  beginAtZero: true,
                  min: 0,
                  max: 100
                }
              }
            }
          });
      
          const regionData = data.interest_by_region || {};
          const regionLabels = Object.keys(regionData);
          const rawValues     = Object.values(regionData);
          const total         = rawValues.reduce((sum, v) => sum + v, 0) || 1;
          const regionValues  = rawValues.map(v => ((v / total) * 100).toFixed(2));
      
          const regionCtx = regionCanvas.getContext("2d");
          this.regionChartInstance = new Chart(regionCtx, {
            type: 'pie',
            data: {
              labels: regionLabels,
              datasets: [{
                data: regionValues,
                backgroundColor: regionLabels.map(() =>
                  `hsl(${Math.random() * 360}, 60%, 70%)`
                ),
              }]
            },
            options: {
              responsive: true,
              plugins: {
                legend: { position: 'right' },
                tooltip: {
                  callbacks: {
                    label: ctx => `${ctx.label}: ${ctx.parsed}%`
                  }
                }
              }
            }
          });
        };
      
        modalElement.addEventListener('shown.bs.modal', onModalShown, { once: true });
      
        new bootstrap.Modal(modalElement).show();
      }
}