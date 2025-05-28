/**
 * @overview Main entry point for UI components and tools initialization.
 * @author Gustas Linkus.
 * @license Proprietary
 */

/**
 * Represents the main UI initializer.
 * Responsible for setting up UI components and other tools.
 */
export default class PAreaMain {
    constructor() {
        console.info('[PAreaMain] initialized.');
    }
}

window.addEventListener('load', () => {
    new PAreaMain();
});
