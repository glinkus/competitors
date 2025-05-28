document.addEventListener("DOMContentLoaded", function () {
    const keywordModal = document.getElementById('keywordTrendModal');
    if (keywordModal) {
        keywordModal.addEventListener('hidden.bs.modal', function () {
            document.body.classList.remove('modal-open');
            document.body.style = '';
            const modalBackdrop = document.querySelector('.modal-backdrop');
            if (modalBackdrop) modalBackdrop.remove();
        });
    }
});
