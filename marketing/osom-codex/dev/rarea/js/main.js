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

export default class RAreaMain {
    constructor() {
        new Demo();
        new Analysis();
        new DemoCad();
        new Chart('toneChart').init();
        console.info('[RAreaMain] initialized.');
    }
}

new RAreaMain();
