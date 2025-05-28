export default class AnalyseCompare {
    constructor() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initCompare();
        });
    }

    initCompare() {
        let compareMode = false;
        const startBtn = document.getElementById('start-compare-btn');
        const compareBtn = document.getElementById('compare-btn');
        const compareIdsInput = document.getElementById('compare-ids');
        const cards = document.querySelectorAll('.card[data-id]');

        function updateCompareState() {
            const checked = [...document.querySelectorAll('.compare-check input:checked')];
            compareBtn.disabled = checked.length !== 2;
            compareIdsInput.value = checked.map(cb => cb.value).join(',');
        }

        startBtn.addEventListener('click', () => {
            compareMode = !compareMode;
            startBtn.textContent = compareMode ? 'Cancel Compare' : 'Select websites to compare';

            cards.forEach(card => {
                const checkWrapper = card.querySelector('.compare-check');
                const checkbox = checkWrapper.querySelector('input');
                const badge = card.querySelector('.status');

                checkWrapper.classList.toggle('d-none', !compareMode);
                checkbox.checked = false;
                checkbox.disabled = !compareMode;
            });

            compareBtn.hidden = !compareMode;
            compareBtn.disabled = true;
            compareIdsInput.value = '';
        });

        cards.forEach(card => {
            const checkbox = card.querySelector('.compare-check input');
            checkbox.addEventListener('click', () => {
                const checked = [...document.querySelectorAll('.compare-check input:checked')];
                if (checked.length > 2) {
                    checkbox.checked = false;
                    alert('You can compare a maximum of 2 websites.');
                    return;
                }
                updateCompareState();
            });
        });
    }
}
