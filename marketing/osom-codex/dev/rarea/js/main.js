/**
 * @author Indeform Ltd.
 * @license Proprietary
 * @description Main restricted area class. Responsible for 
 * initialization of UI components and tools.
 **/

import Analysis from '../../modules/analysis/js/main';
import Chart from '../../modules/analysis/js/tone_chart';
import Demo from '../../modules/demo/js/main';
import DemoCad from './cad';
import UniversalMetricChart from '../../modules/analysis/js/universal_chart';
import ReadingCharts from '../../modules/analysis/js/reading_charts';
import KeywordAnalysis from '../../modules/analysis/js/keyword_analysis';

window.KeywordAnalysis = KeywordAnalysis;

export default class RAreaMain {
    constructor() {
        new Demo();
        new Analysis();
        new DemoCad();
        new Chart('toneChart').init();

        if (document.getElementById('tonePageChart')) {
            const toneChart = new UniversalMetricChart({
                chartId: 'tonePageChart',
                triggerId: 'renderTonePageChart',
                metricSelectId: 'tonePageType',
                chartTypeSelectId: 'tonePageChartType',
                labels: window.toneLabels,
                datasets: window.toneMetrics
            });
        
            toneChart.init();
        }

        if (document.getElementById('loadingMetricChart')) {
            const speedChart = new UniversalMetricChart({
                chartId: 'loadingMetricChart',
                triggerId: 'renderSpeedChartBtn',
                metricSelectId: 'metricTypeSelect',
                chartTypeSelectId: 'metricChartStyleSelect',
                labels: window.pageUrls,
                datasets: window.speedMetrics
            });

            speedChart.init();
        }

        if (document.getElementById('readingTimeChart') || document.getElementById('readabilityChart')) {
            new ReadingCharts().init();
        }

        if (window.keywordData) {
            new KeywordAnalysis(window.keywordData).init();
        }

        if (window.keywordData && document.querySelectorAll('[data-keyword-index]').length) {
            new KeywordAnalysis(window.keywordData).init();
        }

        console.info('[RAreaMain] initialized.');
    }
}

new RAreaMain();

