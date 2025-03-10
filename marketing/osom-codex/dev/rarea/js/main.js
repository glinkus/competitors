/**
 * @author Indeform Ltd.
 * @license Proprietary
 * @description Main restricted area class. Responsible for 
 * initialization of UI components and tools.
 **/

import Demo from '../../modules/demo/js/main';
import Analysis from '../../modules/analysis/js/main';
import DemoCad from './cad';

export default class RAreaMain {
    constructor() {
        new Demo();
        new Analysis();
        new DemoCad();
        console.info('[RAreaMain] initialized.');
    }
}

new RAreaMain();
