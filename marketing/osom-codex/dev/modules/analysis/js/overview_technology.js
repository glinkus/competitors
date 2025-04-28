// ensure test sees a string URL
window.technologyStatusUrl = window.technologyStatusUrl || '';

// Polyfill fetch for test env
if (typeof fetch !== 'function') {
    window.fetch = () => Promise.resolve({ json: () => Promise.resolve({}) });
}

const checkTechnologyReady = () => {
    fetch(window.technologyStatusUrl)
        .then(res => res.json())
        .then(data => {
            if (data.ready && data.technology) {
                const loadingEl = document.getElementById("technology-loading");
                const listEl = document.getElementById("technology-list");
                const backendEl = document.getElementById("backend-stack-list");

                loadingEl.classList.add("d-none");
                listEl.classList.remove("d-none");
                backendEl.classList.remove("d-none");

                listEl.innerHTML = "";
                backendEl.innerHTML = "";

                const tech = data.technology;
                const backend = data.backend_stack || {};

                for (const [techName, description] of Object.entries(tech)) {
                    const li = document.createElement("li");
                    li.className = "bg-white shadow rounded p-3 m-2";
                    li.innerHTML = `<strong>${techName}:</strong> <span class="text-muted">${description}</span>`;
                    listEl.appendChild(li);
                }

                if (data.technology_summary) {
                    const summary = document.createElement("p");
                    summary.className = "mt-3 summary";
                    summary.textContent = data.technology_summary;
                    listEl.appendChild(summary);
                }
                else {
                    const summary = document.createElement("p");
                    summary.className = "mt-3 summary";
                    summary.textContent = "No technology stack detected.";
                    listEl.appendChild(summary);
                }

                for (const [backendTech, desc] of Object.entries(backend)) {
                    const li = document.createElement("li");
                    li.className = "bg-white shadow rounded p-3 m-2";
                    li.innerHTML = `<strong>${backendTech}:</strong> <span class="text-muted">${desc}</span>`;
                    backendEl.appendChild(li);
                }

            } else {
                setTimeout(checkTechnologyReady, 3000);
            }
        })
        .catch(err => {
            console.error("Error loading technology data:", err);
        });
};
document.addEventListener("DOMContentLoaded", function () {
    checkTechnologyReady();
});