export default class AnalyseStatus {
    constructor() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initStatusCheck();
            this.initDelete();
        });
    }

    initStatusCheck() {
        const websiteCards = document.querySelectorAll('[id^="website-row-"]');
        websiteCards.forEach(card => {
            const websiteId = card.id.replace('website-row-', '');
            const statusEl = card.querySelector('.status');
            if (statusEl && statusEl.innerText.includes("In Progress")) {
                this.checkScrapingStatus(websiteId);
            }
        });
    }

    checkScrapingStatus(websiteId) {
        fetch(`/analysis/analyse/?website_id=${websiteId}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            const card = document.getElementById(`website-row-${websiteId}`);
            const visitedEl = card.querySelector('.visited-count');
            const statusEl = card.querySelector('.status');
            const actionEl = card.querySelector('.action');
            const stopBtn = card.querySelector(`#stop-btn-${websiteId}`);
            const stoppedMsg = card.querySelector(`#scraping-stopped-${websiteId}`);

            if (visitedEl) {
                visitedEl.innerHTML = `<strong>Pages:</strong> ${data.visited_count}`;
            }

            if (data.crawling_finished) {
                statusEl.innerHTML = '🟢 Finished';
                statusEl.className = 'badge bg-success mb-3 status';
                if (stopBtn) stopBtn.remove();
                if (stoppedMsg) stoppedMsg.classList.add('d-none');
                actionEl.innerHTML = `
                    <a href="/analysis/website_page/${websiteId}/" class="btn btn-outline-primary btn-sm">
                      Pages overview
                    </a>
                    <a href="/analysis/overview/${websiteId}/" class="btn btn-outline-dark btn-sm">
                      Website overview
                    </a>
                `;
            } else if (data.crawling_in_progress) {
                statusEl.innerHTML = '🟡 In Progress';
                statusEl.className = 'badge bg-warning text-dark mb-3 status';
                setTimeout(() => this.checkScrapingStatus(websiteId), 2000);
            }
        })
        .catch(error => console.error("Error checking status for website " + websiteId, error));
    }

    static getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (const cookie of cookies) {
                const trimmed = cookie.trim();
                if (trimmed.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    static stopScraping(websiteId) {
        fetch(`/analysis/stop-scraping/${websiteId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': AnalyseStatus.getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.stopped) {
                location.reload();
            }
        })
        .catch(error => {
            console.error("Failed to stop scraping:", error);
        });
    }

    static continueScraping(websiteId) {
        fetch(`/analysis/continue-scraping/${websiteId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': AnalyseStatus.getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.continued) {
                location.reload();
            }
        })
        .catch(error => {
            console.error("Failed to continue scraping:", error);
        });
    }

    initDelete() {
        window.deleteWebsite = function(websiteId) {
            if (!confirm("Are you sure you want to delete this website?")) {
                return;
            }
            fetch("/analysis/analyse/", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': AnalyseStatus.getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `delete_website_id=${websiteId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.deleted) {
                    const websiteRow = document.getElementById(`website-row-${websiteId}`);
                    if (websiteRow) {
                        websiteRow.classList.add('fade-out');
                        setTimeout(() => {
                            websiteRow.remove();
                        }, 500);
                    }
                } else {
                    alert('Failed to delete the website.');
                }
            })
            .catch(error => {
                console.error('Error deleting website:', error);
            });
        };
        window.stopScraping = AnalyseStatus.stopScraping;
        window.continueScraping = AnalyseStatus.continueScraping;
    }
}
