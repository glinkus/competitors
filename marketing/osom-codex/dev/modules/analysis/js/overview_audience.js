// ensure test sees a string URL
window.audienceStatusUrl = window.audienceStatusUrl || '';

const checkAudienceReady = () => {
    fetch(window.audienceStatusUrl)
        .then(res => res.json())
        .then(data => {
            if (data.ready) {
                const listEl = document.getElementById("target-audience-list");
                const loadingEl = document.getElementById("target-audience-loading");
                loadingEl.classList.add("d-none");
                listEl.classList.remove("d-none");

                const audience = data.audience;
                listEl.innerHTML = "";

                for (const [segment, explanation] of Object.entries(audience)) {
                    const li = document.createElement("li");
                    li.className = "bg-white shadow rounded p-3 m-2";
                    li.innerHTML = `<strong>${segment}:</strong> <span class="text-muted">${explanation}</span>`;
                    listEl.appendChild(li);
                }
            } else {
                setTimeout(checkAudienceReady, 3000);
            }
        });
};

document.addEventListener("DOMContentLoaded", function () {
    checkAudienceReady();
});