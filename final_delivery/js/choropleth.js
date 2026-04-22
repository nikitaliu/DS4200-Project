class ChoroplethMap {
    constructor(containerId) {
        this.container = d3.select(`#${containerId}`);
        this.metric = "medianListingPrice";
        this.height = 620;
        this.metricConfig = {
            medianListingPrice: {
                label: "Median Listing Price",
                formatter: window.maUtils.formatCurrency,
                interpolator: d3.interpolateYlOrRd,
            },
            priceToIncomeRatio: {
                label: "Price-to-Income Ratio",
                formatter: (value) => `${window.maUtils.formatNumber(value, 2)}x`,
                interpolator: d3.interpolateRdYlGn,
                reverse: true,
            },
            estimatedCapRate: {
                label: "Estimated Cap Rate",
                formatter: (value) => `${window.maUtils.formatNumber(value, 2)}%`,
                interpolator: d3.interpolateGnBu,
            },
            environmentalRiskComposite: {
                label: "Environmental Risk Composite",
                formatter: (value) => window.maUtils.formatNumber(value, 2),
                interpolator: d3.interpolateOrRd,
            },
        };
    }

    async init() {
        const [topology, rows] = await Promise.all([
            d3.json("data/ma_towns.topojson"),
            d3.csv("data/town_summary.csv", (d) => ({
                cityKey: d.cityKey,
                town: d.town,
                listingCount: +d.listingCount,
                medianListingPrice: +d.medianListingPrice,
                medianHouseholdIncome: +d.medianHouseholdIncome,
                priceToIncomeRatio: +d.priceToIncomeRatio,
                estimatedCapRate: +d.estimatedCapRate,
                environmentalRiskComposite: +d.environmentalRiskComposite,
            })),
        ]);

        this.lookup = new Map(rows.map((row) => [row.cityKey, row]));
        const geoFeatures = topojson.feature(topology, topology.objects.towns);
        this.features = geoFeatures.features.map((feature) => {
            const townKey = window.maUtils.normalizeTownName(feature.properties.town);
            return {
                ...feature,
                townKey,
                summary: this.lookup.get(townKey),
            };
        });

        const controls = this.container.append("div").attr("class", "chart-controls");
        controls.append("label").attr("for", "map-metric-select").text("Map metric");
        controls
            .append("select")
            .attr("id", "map-metric-select")
            .selectAll("option")
            .data([
                ["medianListingPrice", "Median listing price"],
                ["priceToIncomeRatio", "Price-to-income ratio"],
                ["estimatedCapRate", "Estimated cap rate"],
                ["environmentalRiskComposite", "Environmental risk"],
            ])
            .join("option")
            .attr("value", (d) => d[0])
            .text((d) => d[1]);

        controls.select("select").on("change", (event) => {
            this.metric = event.target.value;
            this.draw();
            window.dispatchEvent(new CustomEvent("map-metric-changed", { detail: { metric: this.metric } }));
        });

        this.status = this.container.append("div").attr("class", "map-status");
        this.canvas = this.container.append("div").attr("class", "map-svg-shell");
        this.svg = this.canvas
            .append("svg")
            .attr("role", "img")
            .attr("aria-label", "Massachusetts town-level housing choropleth");
        this.root = this.svg.append("g");
        this.tooltip = this.container.append("div").attr("class", "map-tooltip");
        this.geoFeatures = geoFeatures;

        this.resizeObserver = new ResizeObserver(() => this.draw());
        this.resizeObserver.observe(this.container.node());
        this.draw();
    }

    getWidth() {
        return Math.max(620, this.container.node().getBoundingClientRect().width - 8);
    }

    getScale() {
        const values = this.features
            .map((feature) => feature.summary?.[this.metric])
            .filter((value) => Number.isFinite(value));
        const domain = d3.extent(values);
        const config = this.metricConfig[this.metric];
        const scale = d3.scaleSequential(config.interpolator);
        return scale.domain(config.reverse ? [domain[1], domain[0]] : domain);
    }

    drawLegend(scale, width, height) {
        this.svg.selectAll(".map-legend").remove();
        this.svg.selectAll("defs").remove();
        const legend = this.svg.append("g").attr("class", "map-legend").attr("transform", `translate(${width - 250},${height - 42})`);
        const defs = this.svg.append("defs");
        const gradientId = `legend-${this.metric}`;
        const gradient = defs.append("linearGradient").attr("id", gradientId);
        gradient.attr("x1", "0%").attr("x2", "100%").attr("y1", "0%").attr("y2", "0%");

        d3.range(0, 1.01, 0.1).forEach((stop) => {
            const [a, b] = scale.domain();
            gradient.append("stop")
                .attr("offset", `${stop * 100}%`)
                .attr("stop-color", scale(a + (b - a) * stop));
        });

        legend.append("text").attr("class", "legend-label").attr("y", -8).text(this.metricConfig[this.metric].label);
        legend.append("rect").attr("width", 220).attr("height", 12).attr("rx", 999).attr("fill", `url(#${gradientId})`);
        const [min, max] = scale.domain().slice().sort((a, b) => a - b);
        legend.append("text").attr("class", "legend-label").attr("y", 28).text(this.metricConfig[this.metric].formatter(min));
        legend.append("text").attr("class", "legend-label").attr("x", 220).attr("y", 28).attr("text-anchor", "end").text(this.metricConfig[this.metric].formatter(max));
    }

    draw() {
        const width = this.getWidth();
        const height = this.height;
        this.svg.attr("viewBox", `0 0 ${width} ${height}`);

        this.projection = d3.geoIdentity().reflectY(true).fitSize([width - 20, height - 64], this.geoFeatures);
        this.path = d3.geoPath(this.projection);
        const scale = this.getScale();
        const availableCount = this.features.filter((feature) => feature.summary).length;

        this.status.text(`${availableCount} municipalities in the cleaned sample can open a town profile from this map.`);

        this.root.selectAll("*").remove();
        this.root
            .selectAll("path")
            .data(this.features)
            .join("path")
            .attr("d", this.path)
            .attr("class", "town-shape")
            .attr("fill", (feature) =>
                feature.summary && Number.isFinite(feature.summary[this.metric])
                    ? scale(feature.summary[this.metric])
                    : "#d9e2ec"
            )
            .attr("stroke", "rgba(16, 35, 63, 0.25)")
            .attr("stroke-width", 0.8)
            .style("cursor", "pointer")
            .on("mousemove", (event, feature) => this.showTooltip(event, feature))
            .on("mouseleave", () => this.tooltip.style("opacity", 0))
            .on("click", (_, feature) => this.openProfile(feature));

        this.drawLegend(scale, width, height);
    }

    showTooltip(event, feature) {
        const summary = feature.summary;
        const label = summary?.town || window.maUtils.titleCase(feature.properties.town);
        const config = this.metricConfig[this.metric];
        const html = summary
            ? `
                <strong>${label}</strong>
                <div>${config.label}: ${config.formatter(summary[this.metric])}</div>
                <div>Median income: ${window.maUtils.formatCurrency(summary.medianHouseholdIncome)}</div>
                <div>Listings: ${summary.listingCount.toLocaleString("en-US")}</div>
                <div>Click to open town profile</div>
            `
            : `
                <strong>${label}</strong>
                <div>No cleaned listing sample was available for this municipality.</div>
            `;
        this.tooltip
            .style("opacity", 1)
            .style("left", `${event.offsetX + 18}px`)
            .style("top", `${event.offsetY + 16}px`)
            .html(html);
    }

    openProfile(feature) {
        const summary = feature.summary;
        if (!summary && !feature.townKey) {
            return;
        }
        window.dispatchEvent(
            new CustomEvent("town-selected", {
                detail: {
                    townKey: feature.townKey,
                    townName: summary?.town || window.maUtils.titleCase(feature.properties.town),
                },
            })
        );
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("choropleth-container");
    if (container) {
        new ChoroplethMap("choropleth-container").init();
    }
});
