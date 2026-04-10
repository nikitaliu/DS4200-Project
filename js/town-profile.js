class TownProfilePanel {
    constructor() {
        this.panel = document.getElementById("town-profile-panel");
        this.backdrop = document.getElementById("town-profile-backdrop");
        this.content = document.getElementById("town-profile-content");
        this.title = document.getElementById("profile-town-name");
        this.tabs = Array.from(document.querySelectorAll(".profile-tab"));
        this.closeButton = document.getElementById("close-profile");
        this.currentTab = "housing";
        this.currentTownKey = null;
        this.ready = this.loadData();
        this.bindEvents();
    }

    async loadData() {
        const [listings, profiles, townSummary] = await Promise.all([
            d3.csv("data/ma_housing_cleaned.csv", (d) => ({
                city: d.city,
                cityKey: d.cityKey,
                propertyType: d.propertyType,
                price: +d.price,
                pricePerSqFt: +d.pricePerSqFt,
                bedrooms: +d.bedrooms,
                bathrooms: +d.bathrooms,
                monthlyAffordabilityIndex: +d.monthlyAffordabilityIndex,
            })),
            d3.csv("data/census_town_profiles.csv", (d) => ({
                town: d.town,
                townKey: d.townKey,
                medianHouseholdIncome: +d.medianHouseholdIncome,
                ownerOccupied: +d.ownerOccupied,
                renterOccupied: +d.renterOccupied,
                medianHomeValueCensus: +d.medianHomeValueCensus,
                race_total: +d.race_total,
                pop_white: +d.pop_white,
                pop_black: +d.pop_black,
                pop_asian: +d.pop_asian,
                pop_other: +d.pop_other,
                pop_hispanic: +d.pop_hispanic,
                ageUnder18: +d.ageUnder18,
                age18to64: +d.age18to64,
                age65Plus: +d.age65Plus,
                ownerShare: +d.ownerShare,
                renterShare: +d.renterShare,
                dominantIndustry: d.dominantIndustry,
                employmentTotalSelected: +d.employmentTotalSelected,
                emp_agriculture: +d.emp_agriculture,
                emp_construction: +d.emp_construction,
                emp_manufacturing: +d.emp_manufacturing,
                emp_wholesale: +d.emp_wholesale,
                emp_retail: +d.emp_retail,
                emp_information: +d.emp_information,
                emp_finance_real_estate: +d.emp_finance_real_estate,
                emp_professional: +d.emp_professional,
                emp_education_health: +d.emp_education_health,
                emp_arts_food: +d.emp_arts_food,
                emp_other_services: +d.emp_other_services,
                emp_public_administration: +d.emp_public_administration,
            })),
            d3.csv("data/town_summary.csv", (d) => ({
                town: d.town,
                cityKey: d.cityKey,
                listingCount: +d.listingCount,
                medianListingPrice: +d.medianListingPrice,
                medianPricePerSqFt: +d.medianPricePerSqFt,
                medianBedrooms: +d.medianBedrooms,
                monthlyAffordabilityIndexTown: +d.monthlyAffordabilityIndexTown,
                medianHouseholdIncome: +d.medianHouseholdIncome,
                medianHomeValueCensus: +d.medianHomeValueCensus,
            })),
        ]);

        this.listingsByTown = d3.group(listings, (d) => d.cityKey);
        this.profileByTown = new Map(profiles.map((d) => [d.townKey, d]));
        this.summaryByTown = new Map(townSummary.map((d) => [d.cityKey, d]));
        this.profileRows = profiles;
        this.stateIndustryShares = this.computeStateIndustryShares(profiles);
    }

    bindEvents() {
        this.closeButton.addEventListener("click", () => this.close());
        this.backdrop.addEventListener("click", () => this.close());
        this.tabs.forEach((tab) => {
            tab.addEventListener("click", () => {
                this.currentTab = tab.dataset.tab;
                this.tabs.forEach((button) =>
                    button.classList.toggle("active", button.dataset.tab === this.currentTab)
                );
                this.render();
            });
        });

        window.addEventListener("town-selected", async (event) => {
            await this.open(event.detail.townKey, event.detail.townName);
        });
    }

    computeStateIndustryShares(profiles) {
        const labels = this.getIndustrySeries();
        const totals = {};
        let totalEmployment = 0;
        labels.forEach(({key}) => {
            totals[key] = d3.sum(profiles, (row) => row[key] || 0);
            totalEmployment += totals[key];
        });
        return Object.fromEntries(
            labels.map(({key}) => [key, totalEmployment > 0 ? totals[key] / totalEmployment : 0])
        );
    }

    getIndustrySeries(profile = null) {
        const series = [
            ["emp_agriculture", "Agriculture"],
            ["emp_construction", "Construction"],
            ["emp_manufacturing", "Manufacturing"],
            ["emp_wholesale", "Wholesale"],
            ["emp_retail", "Retail"],
            ["emp_information", "Information"],
            ["emp_finance_real_estate", "Finance / Real Estate"],
            ["emp_professional", "Professional"],
            ["emp_education_health", "Education / Health"],
            ["emp_arts_food", "Arts / Food"],
            ["emp_other_services", "Other Services"],
            ["emp_public_administration", "Public Administration"],
        ];
        return series.map(([key, label]) => ({
            key,
            label,
            value: profile ? profile[key] || 0 : 0,
        }));
    }

    async open(townKey, townName) {
        await this.ready;
        this.currentTownKey = townKey;
        this.currentTab = "housing";
        this.tabs.forEach((button) =>
            button.classList.toggle("active", button.dataset.tab === this.currentTab)
        );
        const summary = this.summaryByTown.get(townKey);
        const profile = this.profileByTown.get(townKey);
        this.title.textContent = `${summary?.town || profile?.town || townName || "Town"}, MA`;
        this.panel.classList.remove("hidden");
        this.backdrop.classList.remove("hidden");
        requestAnimationFrame(() => {
            this.panel.classList.add("active");
            this.backdrop.classList.add("active");
        });
        document.body.classList.add("no-scroll");
        this.panel.setAttribute("aria-hidden", "false");
        this.render();
    }

    close() {
        this.panel.classList.remove("active");
        this.backdrop.classList.remove("active");
        document.body.classList.remove("no-scroll");
        this.panel.setAttribute("aria-hidden", "true");
        setTimeout(() => {
            this.panel.classList.add("hidden");
            this.backdrop.classList.add("hidden");
        }, 260);
    }

    render() {
        if (!this.currentTownKey) {
            return;
        }
        if (this.currentTab === "housing") {
            this.renderHousing();
        } else if (this.currentTab === "demographics") {
            this.renderDemographics();
        } else {
            this.renderEmployment();
        }
    }

    renderHousing() {
        const utils = window.maUtils;
        const listings = this.listingsByTown.get(this.currentTownKey) || [];
        const summary = this.summaryByTown.get(this.currentTownKey);

        this.content.innerHTML = `
            <div class="profile-stat-grid">
                <div class="profile-stat-card">
                    <h4>Median listing price</h4>
                    <div class="value">${utils.formatCurrency(summary?.medianListingPrice)}</div>
                    <div class="meta">Median asking price for homes in this town sample</div>
                </div>
                <div class="profile-stat-card">
                    <h4>Listings in sample</h4>
                    <div class="value">${utils.formatNumber(summary?.listingCount || listings.length, 0)}</div>
                    <div class="meta">Number of listings included after cleaning</div>
                </div>
                <div class="profile-stat-card">
                    <h4>Median price per sqft</h4>
                    <div class="value">${utils.formatCurrency(summary?.medianPricePerSqFt)}</div>
                    <div class="meta">A size-adjusted way to compare homes</div>
                </div>
                <div class="profile-stat-card">
                    <h4>Affordability index</h4>
                    <div class="value">${utils.formatNumber(summary?.monthlyAffordabilityIndexTown, 2)}</div>
                    <div class="meta">Above 1 is more reachable, below 1 means more strain</div>
                </div>
            </div>
            <div class="profile-grid">
                <div class="mini-chart-card">
                    <h4>Property type breakdown</h4>
                    <p>Which kinds of homes appear most often in the cleaned listing sample for this town.</p>
                    <svg id="profile-property-breakdown" class="mini-chart"></svg>
                </div>
                <div class="mini-chart-card">
                    <h4>Price distribution</h4>
                    <p>Each dot is a listing. This shows whether the town has a tight price range or a wide spread.</p>
                    <svg id="profile-price-distribution" class="mini-chart"></svg>
                </div>
            </div>
        `;

        this.drawPropertyTypeBreakdown(listings);
        this.drawPriceDistribution(listings);
    }

    renderDemographics() {
        const utils = window.maUtils;
        const summary = this.summaryByTown.get(this.currentTownKey);
        const profile = this.profileByTown.get(this.currentTownKey);

        if (!profile) {
            this.content.innerHTML = `<div class="profile-note"><p>No Census profile data was available for this town.</p></div>`;
            return;
        }

        this.content.innerHTML = `
            <div class="profile-stat-grid">
                <div class="profile-stat-card">
                    <h4>Median household income</h4>
                    <div class="value">${utils.formatCurrency(profile.medianHouseholdIncome)}</div>
                    <div class="meta">2023 ACS 5-year estimate</div>
                </div>
                <div class="profile-stat-card">
                    <h4>Census median home value</h4>
                    <div class="value">${utils.formatCurrency(profile.medianHomeValueCensus)}</div>
                    <div class="meta">Census estimate for occupied homes</div>
                </div>
                <div class="profile-stat-card">
                    <h4>Owner-occupied share</h4>
                    <div class="value">${utils.formatPercent(profile.ownerShare)}</div>
                    <div class="meta">Share of occupied housing units that are owner occupied</div>
                </div>
                <div class="profile-stat-card">
                    <h4>Age 65+ share</h4>
                    <div class="value">${utils.formatPercent((profile.age65Plus || 0) / (profile.race_total || 1))}</div>
                    <div class="meta">Older residents as a share of ACS residents counted in this town</div>
                </div>
            </div>
            <div class="profile-grid">
                <div class="mini-chart-card">
                    <h4>Owner versus renter split</h4>
                    <p>A town with more renters can feel very different from a town where most households own their homes.</p>
                    <svg id="profile-tenure-chart" class="mini-chart"></svg>
                </div>
                <div class="mini-chart-card">
                    <h4>Race and ethnicity counts</h4>
                    <p>Hispanic or Latino is an ethnicity measure in the ACS, so it can overlap with race categories.</p>
                    <svg id="profile-race-chart" class="mini-chart"></svg>
                </div>
            </div>
            <div class="mini-chart-card" style="margin-top: 1rem;">
                <h4>Census home value versus listing market</h4>
                <p>This compares the ACS median home value estimate with the median listing price in our cleaned Zillow sample.</p>
                <svg id="profile-home-value-chart" class="mini-chart"></svg>
            </div>
        `;

        this.drawTenureDonut(profile);
        this.drawRaceChart(profile);
        this.drawHomeValueComparison(summary, profile);
    }

    renderEmployment() {
        const profile = this.profileByTown.get(this.currentTownKey);
        if (!profile) {
            this.content.innerHTML = `<div class="profile-note"><p>No employment-by-industry data was available for this town.</p></div>`;
            return;
        }

        this.content.innerHTML = `
            <div class="profile-note">
                <p>The dominant industry in this town is <strong>${profile.dominantIndustry || "not available"}</strong>.
                The chart below compares the town’s employment mix with the statewide average share for the same set of industries.</p>
            </div>
            <div class="mini-chart-card" style="margin-top: 1rem;">
                <h4>Employment by industry</h4>
                <p>Blue bars show the selected town. The small red markers show the statewide average share.</p>
                <svg id="profile-employment-chart" class="mini-chart"></svg>
            </div>
        `;

        this.drawEmploymentChart(profile);
    }

    drawPropertyTypeBreakdown(listings) {
        const counts = d3.rollups(
            listings,
            (rows) => rows.length,
            (row) => row.propertyType || "Other"
        )
            .map(([type, count]) => ({type, count}))
            .sort((a, b) => d3.descending(a.count, b.count));

        const svg = d3.select("#profile-property-breakdown");
        const width = svg.node().clientWidth || 360;
        const height = 280;
        svg.attr("viewBox", `0 0 ${width} ${height}`);
        svg.selectAll("*").remove();
        if (!counts.length) {
            return;
        }
        const margin = {top: 20, right: 16, bottom: 30, left: 120};
        const x = d3.scaleLinear().domain([0, d3.max(counts, (d) => d.count)]).nice().range([margin.left, width - margin.right]);
        const y = d3.scaleBand().domain(counts.map((d) => d.type)).range([margin.top, height - margin.bottom]).padding(0.2);

        svg.append("g")
            .selectAll("rect")
            .data(counts)
            .join("rect")
            .attr("x", margin.left)
            .attr("y", (d) => y(d.type))
            .attr("width", (d) => x(d.count) - margin.left)
            .attr("height", y.bandwidth())
            .attr("rx", 10)
            .attr("fill", "#2b6cb0");

        svg.append("g")
            .attr("transform", `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x).ticks(4).tickSizeOuter(0));
        svg.append("g")
            .attr("transform", `translate(${margin.left},0)`)
            .call(d3.axisLeft(y).tickSizeOuter(0));
    }

    drawPriceDistribution(listings) {
        const prices = listings.map((row) => row.price).filter(Number.isFinite).sort(d3.ascending);
        const svg = d3.select("#profile-price-distribution");
        const width = svg.node().clientWidth || 360;
        const height = 280;
        svg.attr("viewBox", `0 0 ${width} ${height}`);
        svg.selectAll("*").remove();
        if (!prices.length) {
            return;
        }
        const margin = {top: 20, right: 18, bottom: 34, left: 52};
        const x = d3.scaleLinear().domain(d3.extent(prices)).nice().range([margin.left, width - margin.right]);

        svg.append("g")
            .selectAll("circle")
            .data(prices)
            .join("circle")
            .attr("cx", (d) => x(d))
            .attr("cy", () => 80 + Math.random() * 110)
            .attr("r", 4)
            .attr("fill", "#e53e3e")
            .attr("fill-opacity", 0.45);

        svg.append("g")
            .attr("transform", `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x).ticks(4).tickFormat((d) => window.maUtils.formatShortCurrency(d)));
    }

    drawTenureDonut(profile) {
        const svg = d3.select("#profile-tenure-chart");
        const width = svg.node().clientWidth || 360;
        const height = 280;
        svg.attr("viewBox", `0 0 ${width} ${height}`);
        svg.selectAll("*").remove();

        const data = [
            {label: "Owner occupied", value: profile.ownerOccupied, color: "#2b6cb0"},
            {label: "Renter occupied", value: profile.renterOccupied, color: "#e53e3e"},
        ];

        const radius = Math.min(width, height) / 2 - 30;
        const group = svg.append("g").attr("transform", `translate(${width / 2},${height / 2})`);
        const pie = d3.pie().value((d) => d.value)(data);
        const arc = d3.arc().innerRadius(radius * 0.58).outerRadius(radius);

        group.selectAll("path")
            .data(pie)
            .join("path")
            .attr("d", arc)
            .attr("fill", (d) => d.data.color)
            .attr("stroke", "white")
            .attr("stroke-width", 2);

        group.append("text")
            .attr("text-anchor", "middle")
            .attr("dy", "-0.1em")
            .attr("fill", "#1a365d")
            .attr("font-weight", 700)
            .text(window.maUtils.formatPercent(profile.ownerShare));
        group.append("text")
            .attr("text-anchor", "middle")
            .attr("dy", "1.2em")
            .attr("fill", "#4a5568")
            .text("owner share");
    }

    drawRaceChart(profile) {
        const rows = [
            {label: "White", value: profile.pop_white},
            {label: "Black", value: profile.pop_black},
            {label: "Asian", value: profile.pop_asian},
            {label: "Other", value: profile.pop_other},
            {label: "Hispanic / Latino", value: profile.pop_hispanic},
        ];
        const svg = d3.select("#profile-race-chart");
        const width = svg.node().clientWidth || 360;
        const height = 300;
        svg.attr("viewBox", `0 0 ${width} ${height}`);
        svg.selectAll("*").remove();

        const margin = {top: 20, right: 20, bottom: 24, left: 130};
        const x = d3.scaleLinear().domain([0, d3.max(rows, (d) => d.value)]).nice().range([margin.left, width - margin.right]);
        const y = d3.scaleBand().domain(rows.map((d) => d.label)).range([margin.top, height - margin.bottom]).padding(0.22);

        svg.append("g")
            .selectAll("rect")
            .data(rows)
            .join("rect")
            .attr("x", margin.left)
            .attr("y", (d) => y(d.label))
            .attr("width", (d) => x(d.value) - margin.left)
            .attr("height", y.bandwidth())
            .attr("rx", 10)
            .attr("fill", "#38a169");

        svg.append("g")
            .attr("transform", `translate(${margin.left},0)`)
            .call(d3.axisLeft(y).tickSizeOuter(0));
    }

    drawHomeValueComparison(summary, profile) {
        const rows = [
            {label: "Median listing price", value: summary?.medianListingPrice || 0, color: "#e53e3e"},
            {label: "Census median home value", value: profile?.medianHomeValueCensus || 0, color: "#2b6cb0"},
        ];
        const svg = d3.select("#profile-home-value-chart");
        const width = svg.node().clientWidth || 560;
        const height = 220;
        svg.attr("viewBox", `0 0 ${width} ${height}`);
        svg.selectAll("*").remove();
        const margin = {top: 22, right: 16, bottom: 28, left: 160};
        const x = d3.scaleLinear().domain([0, d3.max(rows, (d) => d.value)]).nice().range([margin.left, width - margin.right]);
        const y = d3.scaleBand().domain(rows.map((d) => d.label)).range([margin.top, height - margin.bottom]).padding(0.28);

        svg.append("g")
            .selectAll("rect")
            .data(rows)
            .join("rect")
            .attr("x", margin.left)
            .attr("y", (d) => y(d.label))
            .attr("width", (d) => x(d.value) - margin.left)
            .attr("height", y.bandwidth())
            .attr("rx", 10)
            .attr("fill", (d) => d.color);

        svg.append("g")
            .attr("transform", `translate(${margin.left},0)`)
            .call(d3.axisLeft(y).tickSizeOuter(0));
    }

    drawEmploymentChart(profile) {
        const series = this.getIndustrySeries(profile).map((entry) => ({
            ...entry,
            share:
                profile.employmentTotalSelected > 0
                    ? entry.value / profile.employmentTotalSelected
                    : 0,
            stateShare: this.stateIndustryShares[entry.key] || 0,
        }));

        const svg = d3.select("#profile-employment-chart");
        const width = svg.node().clientWidth || 640;
        const height = 420;
        svg.attr("viewBox", `0 0 ${width} ${height}`);
        svg.selectAll("*").remove();

        const margin = {top: 20, right: 24, bottom: 28, left: 180};
        const x = d3.scaleLinear().domain([0, d3.max(series, (d) => Math.max(d.share, d.stateShare))]).nice().range([margin.left, width - margin.right]);
        const y = d3.scaleBand().domain(series.map((d) => d.label)).range([margin.top, height - margin.bottom]).padding(0.18);

        svg.append("g")
            .selectAll("rect")
            .data(series)
            .join("rect")
            .attr("x", margin.left)
            .attr("y", (d) => y(d.label))
            .attr("width", (d) => x(d.share) - margin.left)
            .attr("height", y.bandwidth())
            .attr("rx", 10)
            .attr("fill", "#2b6cb0");

        svg.append("g")
            .selectAll("line")
            .data(series)
            .join("line")
            .attr("x1", (d) => x(d.stateShare))
            .attr("x2", (d) => x(d.stateShare))
            .attr("y1", (d) => y(d.label))
            .attr("y2", (d) => y(d.label) + y.bandwidth())
            .attr("stroke", "#e53e3e")
            .attr("stroke-width", 3);

        svg.append("g")
            .attr("transform", `translate(${margin.left},0)`)
            .call(d3.axisLeft(y).tickSizeOuter(0));
        svg.append("g")
            .attr("transform", `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x).ticks(4).tickFormat((d) => window.maUtils.formatPercent(d)));
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.townProfile = new TownProfilePanel();
});
