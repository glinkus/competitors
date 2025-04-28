export default class AnalyseFilter {
    constructor() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initFilters());
        } else {
            this.initFilters();
        }
    }

    initFilters() {
        const statusFilter = document.getElementById('status-filter');
        const sortFilter   = document.getElementById('sort-filter');
        const cardsContainer = document.querySelector('.row.row-cols-1');

        // Guard: bail out if DOM not yet present
        if (!statusFilter || !sortFilter || !cardsContainer) return;

        const allCards = Array.from(cardsContainer.querySelectorAll('.col'));

        function applyFilters() {
            const selectedStatus = statusFilter.value;
            const sortOrder = sortFilter.value;

            allCards.forEach(card => {
                const badge = card.querySelector('.status');
                let show = true;

                if (selectedStatus && badge) {
                    const badgeText = badge.innerText || '';
                    if (selectedStatus === 'finished' && !(badgeText.includes('Finished') || badgeText.includes('🟢'))) show = false;
                    if (selectedStatus === 'stopped' && !(badgeText.includes('Stopped') || badgeText.includes('🔴 Stopped'))) show = false;
                    if (selectedStatus === 'in_progress' && !(badgeText.includes('In Progress') || badgeText.includes('🟡'))) show = false;
                }

                if (show) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });

            const visibleCards = allCards.filter(card => !card.classList.contains('hidden'));

            visibleCards.sort((a, b) => {
                const aEl = a.querySelector('.card-body p.mb-2');
                const bEl = b.querySelector('.card-body p.mb-2');
                const aDate = aEl ? new Date(aEl.innerText.replace('Last Visited:', '').trim()) : new Date(0);
                const bDate = bEl ? new Date(bEl.innerText.replace('Last Visited:', '').trim()) : new Date(0);
                return sortOrder === 'asc' ? aDate - bDate : bDate - aDate;
            });

            cardsContainer.innerHTML = '';
            visibleCards.forEach(card => cardsContainer.appendChild(card));
        }

        statusFilter.addEventListener('change', applyFilters);
        sortFilter.addEventListener('change', applyFilters);
    }
}
