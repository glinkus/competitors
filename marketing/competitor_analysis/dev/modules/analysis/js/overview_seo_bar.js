document.addEventListener("DOMContentLoaded", function () {
    const score = window.seoScore;
    const bar = document.getElementById("seoScoreOverviewBar");

    if (bar) {
        bar.style.width = score + "%";
        bar.textContent = score + "%";

        bar.classList.remove("bg-success", "bg-warning", "bg-danger");
        bar.classList.add(
            score >= 70 ? "bg-success" :
                score >= 40 ? "bg-warning" :
                    "bg-danger"
        );
    }
});
