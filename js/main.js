function setText(target, value) {
    document.querySelectorAll(`#${target}, [data-fill="${target}"]`).forEach((node) => {
        node.textContent = value;
    });
}

async function populateSummary() {
    try {
        const summary = await d3.json("data/analysis_summary.json");
        const utils = window.maUtils;
        const townExample = summary.glossaryTownExample?.[0] || {};
        const listingExample = summary.glossaryListingExample?.[0] || {};

        setText("hero-listings", summary.listingCount.toLocaleString("en-US"));
        setText("hero-towns", summary.incomeCoverageTownCount.toLocaleString("en-US"));
        setText("hero-median", utils.formatCurrency(summary.statewideMedianPrice));
        setText("hero-risk", utils.formatSigned(summary.environmentalRiskPriceCorrelation, 3));

        setText("method-raw-rows", summary.rawRowCount.toLocaleString("en-US"));
        setText("method-duplicates", summary.duplicatesRemoved.toLocaleString("en-US"));
        setText("method-non-ma", summary.nonMassachusettsRowsRemoved.toLocaleString("en-US"));
        setText("method-cleaned-rows", summary.listingCount.toLocaleString("en-US"));
        setText("method-income-towns", summary.incomeCoverageTownCount.toLocaleString("en-US"));

        if (listingExample.price && listingExample.sqft && listingExample.pricePerSqFt) {
            setText(
                "glossary-ppsf-example",
                `${utils.formatCurrency(listingExample.price)} ÷ ${utils.formatNumber(listingExample.sqft, 0)} sqft = ${utils.formatCurrency(listingExample.pricePerSqFt)} per sqft`
            );
        }

        if (townExample.town) {
            setText(
                "glossary-ratio-example",
                `${townExample.town} median price ${utils.formatCurrency(townExample.medianListingPrice)} ÷ median income ${utils.formatCurrency(townExample.medianHouseholdIncome)} = ${utils.formatNumber(townExample.priceToIncomeRatio, 1)}`
            );
        }

        if (listingExample.estimatedCapRate) {
            setText(
                "glossary-cap-rate-example",
                `${listingExample.city} is estimated at ${utils.formatNumber(listingExample.estimatedCapRate, 2)}%`
            );
        }

        if (listingExample.grossRentMultiplier) {
            setText(
                "glossary-grm-example",
                `${listingExample.city} has an estimated GRM of ${utils.formatNumber(listingExample.grossRentMultiplier, 1)}`
            );
        }

        if (listingExample.priceAppreciation) {
            setText(
                "glossary-roi-example",
                `${listingExample.city} shows an estimated ROI of ${utils.formatPercent(listingExample.priceAppreciation, 1)} since the past sale`
            );
        }

        if (listingExample.annualizedAppreciation) {
            setText(
                "glossary-appreciation-example",
                `${listingExample.city} averages about ${utils.formatPercent(listingExample.annualizedAppreciation, 1)} per year`
            );
        }
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
