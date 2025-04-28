export default class AnalyseFilter {
    constructor() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initFilters();
        });
    }

    initFilters() {
        const statusFilter = document.getElementById('status-filter');
        const sortFilter = document.getElementById('sort-filter');
        const cardsContainer = document.querySelector('.row.row-cols-1');
        const allCards = Array.from(cardsContainer.querySelectorAll('.col'));

        function applyFilters() {
            const selectedStatus = statusFilter.value;
            const sortOrder = sortFilter.value;

            allCards.forEach(card => {
                const badge = card.querySelector('.status');
                let show = true;

                if (selectedStatus) {
                    if (selectedStatus === 'finished' && !(badge.innerText.includes('Finished') || badge.innerText.includes('🟢'))) show = false;
                    if (selectedStatus === 'stopped' && !(badge.innerText.includes('Stopped') || badge.innerText.includes('🔴 Stopped'))) show = false;
                    if (selectedStatus === 'in_progress' && !(badge.innerText.includes('In Progress') || badge.innerText.includes('🟡'))) show = false;
                }

                if (show) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });

            const visibleCards = allCards.filter(card => !card.classList.contains('hidden'));

            visibleCards.sort((a, b) => {
                const aDate = new Date(a.querySelector('.card-body p.mb-2').innerText.replace('Last Visited:', '').trim());
                const bDate = new Date(b.querySelector('.card-body p.mb-2').innerText.replace('Last Visited:', '').trim());
                return sortOrder === 'asc' ? aDate - bDate : bDate - aDate;
            });

            cardsContainer.innerHTML = '';
            visibleCards.forEach(card => cardsContainer.appendChild(card));
        }

        statusFilter.addEventListener('change', applyFilters);
        sortFilter.addEventListener('change', applyFilters);
    }
}
