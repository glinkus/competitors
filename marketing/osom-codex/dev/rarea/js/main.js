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
import TonePageChart from '../../modules/analysis/js/tone_page_chart';
import ReadingCharts from '../../modules/analysis/js/reading_charts'; 

export default class RAreaMain {
    constructor() {
        new Demo();
        new Analysis();
        new DemoCad();
        new Chart('toneChart').init();

        if (document.getElementById('tonePageChart')) {
            const readingLabels = window.readingLabels || [];
            const perPageTones = window.perPageTones || [];

            const toneChart = new TonePageChart({
                chartId: 'tonePageChart',
                triggerId: 'renderTonePageChart',
                toneSelectId: 'tonePageType',
                chartTypeSelectId: 'tonePageChartType',
                labels: readingLabels,
                dataSet: perPageTones
            });

            toneChart.init();
        }

        if (document.getElementById('readingTimeChart') || document.getElementById('readabilityChart')) {
            new ReadingCharts().init();
        }

        console.info('[RAreaMain] initialized.');
    }
}

new RAreaMain();

