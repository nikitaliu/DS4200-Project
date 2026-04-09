function setText(id, value) {
    document.querySelectorAll(`#${id}, [data-fill="${id}"]`).forEach((node) => {
        node.textContent = value;
    });
}

function setHTML(id, value) {
    const node = document.getElementById(id);
    if (node) {
        node.innerHTML = value;
    }
}

function renderTownList(id, rows, formatter) {
    const list = document.getElementById(id);
    if (!list || !rows) {
        return;
    }
    list.innerHTML = rows
        .map(
            (row) =>
                `<li><strong>${row.town}</strong> ${formatter(row.medianListingPrice)} median across ${row.listingCount} listings</li>`
        )
        .join("");
}

async function populateSummary() {
    try {
        const summary = await d3.json("data/analysis_summary.json");
        const utils = window.maUtils;

        setText("hero-listings", summary.listingCount.toLocaleString("en-US"));
        setText("hero-towns", summary.incomeCoverageTownCount.toLocaleString("en-US"));
        setText("hero-median", utils.formatCurrency(summary.statewideMedianPrice));
        setText("hero-risk", utils.formatSigned(summary.environmentalRiskPriceCorrelation, 3));

        setText("median-price", utils.formatCurrency(summary.statewideMedianPrice));
        setText("mean-price", utils.formatCurrency(summary.statewideMeanPrice));
        setText("top-town", summary.top10TownsByMedianPrice[0]?.town ?? "--");
        setText("bottom-town", summary.bottom10TownsByMedianPrice[0]?.town ?? "--");
        setText("unaffordable-count", String(summary.unaffordableTownCount));
        setText("coverage-count", String(summary.incomeCoverageTownCount));
        setText("max-ratio-town", summary.priceToIncomeMaxTown[0]?.town ?? "--");
        setText(
            "max-ratio-value",
            `${utils.formatNumber(summary.priceToIncomeMaxTown[0]?.priceToIncomeRatio, 1)}x`
        );
        setText("min-ratio-town", summary.priceToIncomeMinTown[0]?.town ?? "--");
        setText(
            "min-ratio-value",
            `${utils.formatNumber(summary.priceToIncomeMinTown[0]?.priceToIncomeRatio, 1)}x`
        );

        const positive = summary.topPositivePriceCorrelations || [];
        const negative = summary.topNegativePriceCorrelations || [];
        setText("corr-feature-1", utils.labelizeVariable(positive[0]?.variable ?? "sqft"));
        setText("corr-feature-1-value", utils.formatSigned(positive[0]?.correlation ?? 0, 3));
        setText("corr-feature-2", utils.labelizeVariable(positive[1]?.variable ?? "bathrooms"));
        setText("corr-feature-2-value", utils.formatSigned(positive[1]?.correlation ?? 0, 3));
        setText("corr-feature-3", utils.labelizeVariable(negative[negative.length - 1]?.variable ?? "fireRisk"));
        setText(
            "corr-feature-3-value",
            utils.formatSigned(negative[negative.length - 1]?.correlation ?? 0, 3)
        );

        setText(
            "sensitivity-sqft",
            utils.formatCurrency(summary.sensitivityByOneStdDev?.sqft ?? 0)
        );
        setText(
            "sensitivity-livability",
            utils.formatCurrency(summary.sensitivityByOneStdDev?.livabilityComposite ?? 0)
        );
        setText(
            "sensitivity-risk",
            utils.formatCurrency(summary.sensitivityByOneStdDev?.environmentalRiskComposite ?? 0)
        );

        setText(
            "risk-correlation",
            utils.formatSigned(summary.environmentalRiskPriceCorrelation, 3)
        );

        renderTownList("top-town-list", summary.top10TownsByMedianPrice.slice(0, 5), utils.formatCurrency);
        renderTownList(
            "bottom-town-list",
            summary.bottom10TownsByMedianPrice.slice(0, 5),
            utils.formatCurrency
        );
    } catch (error) {
        console.error("Unable to load analysis summary", error);
    }
}

function initNavigation() {
    document.querySelectorAll('a[href^="#"]').forEach((link) => {
        link.addEventListener("click", (event) => {
            const target = document.querySelector(link.getAttribute("href"));
            if (!target) {
                return;
            }
            event.preventDefault();
            target.scrollIntoView({behavior: "smooth", block: "start"});
        });
    });
}

function initScrollButton() {
    const button = document.createElement("button");
    button.className = "scroll-to-top";
    button.type = "button";
    button.setAttribute("aria-label", "Back to top");
    button.textContent = "↑";
    document.body.appendChild(button);

    button.addEventListener("click", () => {
        window.scrollTo({top: 0, behavior: "smooth"});
    });

    window.addEventListener("scroll", () => {
        button.style.display = window.scrollY > 500 ? "block" : "none";
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    initScrollButton();
    populateSummary();
});
