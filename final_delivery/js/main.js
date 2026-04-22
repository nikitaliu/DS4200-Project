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

const mapExplanations = {
    medianListingPrice: `<p>We mapped the median listing price for every town in Massachusetts. The color shading ranges
        from light yellow for lower-priced towns to deep red for the most expensive — making it easy to spot
        where housing costs cluster. The highest prices concentrate in coastal and island communities like
        Nantucket and Martha's Vineyard, and in inner-ring Boston suburbs such as Wellesley and Weston.
        Western Massachusetts towns are notably cheaper.</p>
        <p>This directly answers Research Question 1: location is the strongest broad filter on
        affordability before buyers even compare individual homes. Use the dropdown above to switch
        the map metric and explore how income pressure, investment returns, and environmental risk
        vary across the same geography.</p>`,

    priceToIncomeRatio: `<p>The price-to-income ratio measures how expensive housing is relative to what local residents
        typically earn — specifically, how many years of a town's median household income it takes to equal
        the median listing price. A ratio of 8 means a typical home costs 8 years' worth of local income.
        Higher values (darker color) signal greater financial strain for buyers who live and work in that town.</p>
        <p>The map reveals that many suburban and coastal towns sit well above the traditional affordability
        benchmark of 4–5x. Even towns with moderate listing prices can appear stressed when local wages
        are low. This metric is one of the clearest lenses on Research Question 1: it shifts the question
        from "where are homes expensive?" to "where are homes expensive <em>for the people who live there</em>?"</p>`,

    estimatedCapRate: `<p>The estimated cap rate is a rough measure of a property's potential rental return — calculated
        as estimated annual rent divided by listing price, expressed as a percentage. A higher cap rate
        (darker color) suggests better potential returns for investors relative to what they pay upfront.
        This is a proxy measure based on estimated rent, not observed rent rolls.</p>
        <p>Interestingly, the cap rate map roughly inverts the price map: lower-priced towns in central and
        western Massachusetts tend to show higher cap rates, while expensive coastal and metro towns show
        lower returns. This tells us that the priciest markets are driven more by lifestyle demand and
        scarcity than by investment fundamentals — useful context for anyone weighing buying versus renting,
        or evaluating a market as an investor.</p>`,

    environmentalRiskComposite: `<p>The environmental risk composite averages five risk scores — flood, fire, wind, heat, and
        air quality — into a single number per listing. Higher values (darker color) mean greater combined
        environmental exposure. Coastal communities show elevated flood and wind risk, while parts of western
        Massachusetts show higher heat and air quality scores.</p>
        <p>A key finding: high environmental risk does not consistently push prices down. Many high-risk
        towns remain expensive, suggesting that environmental hazards are not yet fully reflected in
        listing prices. This connects directly to Research Question 4 — buyers in desirable but
        risk-exposed locations may be taking on more long-term exposure than the price tag suggests.</p>`,
};

function updateMapExplanation(metric) {
    const el = document.getElementById("rq1-explanation");
    if (el && mapExplanations[metric]) {
        el.innerHTML = mapExplanations[metric];
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    initScrollButton();
    populateSummary();
    window.addEventListener("map-metric-changed", (event) => {
        updateMapExplanation(event.detail.metric);
    });
});
