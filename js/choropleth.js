class ChoroplethMap {
    constructor(containerId) {
        this.container = d3.select(`#${containerId}`);
        this.metric = "medianListingPrice";
        this.width = 920;
        this.height = 600;
        this.margin = {top: 20, right: 24, bottom: 24, left: 24};
        this.metricConfig = {
            medianListingPrice: {
                label: "Median Listing Price",
                formatter: window.maUtils.formatCurrency,
                interpolator: d3.interpolateYlOrRd,
            },
            priceToIncomeRatio: {
                label: "Price-to-Income Ratio",
                formatter: (value) => `${window.maUtils.formatNumber(value, 2)}x`,
                interpolator: d3.interpolateBlues,
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
                monthlyAffordabilityIndexTown: +d.monthlyAffordabilityIndexTown,
            })),
        ]);

        const features = topojson.feature(topology, topology.objects.towns);
        this.lookup = new Map(rows.map((row) => [row.cityKey, row]));
        this.features = features.features.map((feature) => {
            const townKey = window.maUtils.normalizeTownName(feature.properties.town);
            return {
                ...feature,
                townKey,
                summary: this.lookup.get(townKey),
            };
        });

        const controls = this.container.append("div").attr("class", "chart-controls");
        controls.append("label").attr("for", "map-metric-select").text("Color metric");
        controls
            .append("select")
            .attr("id", "map-metric-select")
            .selectAll("option")
            .data([
                ["medianListingPrice", "Median Listing Price"],
                ["priceToIncomeRatio", "Price-to-Income Ratio"],
                ["estimatedCapRate", "Estimated Cap Rate"],
                ["environmentalRiskComposite", "Environmental Risk Composite"],
            ])
            .join("option")
            .attr("value", (d) => d[0])
            .text((d) => d[1]);

        controls
            .select("select")
            .on("change", (event) => {
                this.metric = event.target.value;
                this.render();
            });

        controls
            .append("button")
            .attr("type", "button")
            .text("Reset zoom")
            .on("click", () => this.resetZoom());

        this.status = this.container.append("div").attr("class", "map-status");

        this.svg = this.container
            .append("svg")
            .attr("viewBox", `0 0 ${this.width} ${this.height}`)
            .attr("role", "img")
            .attr("aria-label", "Massachusetts housing choropleth map");

        this.root = this.svg.append("g");

        this.tooltip = this.container.append("div").attr("class", "map-tooltip");

        this.projection = d3.geoIdentity().reflectY(true).fitSize(
            [this.width - this.margin.left - this.margin.right, this.height - this.margin.top - this.margin.bottom],
            features
        );
        this.path = d3.geoPath(this.projection);

        this.zoomBehavior = d3
            .zoom()
            .scaleExtent([1, 7])
            .translateExtent([
                [0, 0],
                [this.width, this.height],
            ])
            .on("zoom", (event) => this.root.attr("transform", event.transform));

        this.svg.call(this.zoomBehavior);
        this.render();
    }

    getScale() {
        const values = this.features
            .map((feature) => feature.summary?.[this.metric])
            .filter((value) => Number.isFinite(value));

        const domain = d3.extent(values);
        return d3.scaleSequential(this.metricConfig[this.metric].interpolator).domain(domain);
    }

    renderLegend(scale) {
        this.svg.selectAll(".map-legend").remove();
        const legend = this.svg.append("g").attr("class", "map-legend").attr("transform", "translate(620,530)");
        const legendWidth = 220;
        const legendHeight = 12;
        const gradientId = `map-gradient-${this.metric}`;
        const defs = this.svg.append("defs");
        const gradient = defs
            .append("linearGradient")
            .attr("id", gradientId)
            .attr("x1", "0%")
            .attr("x2", "100%")
            .attr("y1", "0%")
            .attr("y2", "0%");

        d3.range(0, 1.01, 0.1).forEach((stop) => {
            gradient
                .append("stop")
                .attr("offset", `${stop * 100}%`)
                .attr("stop-color", scale(scale.domain()[0] + stop * (scale.domain()[1] - scale.domain()[0])));
        });

        legend
            .append("text")
            .attr("x", 0)
            .attr("y", -10)
            .attr("class", "legend-label")
            .text(this.metricConfig[this.metric].label);

        legend
            .append("rect")
            .attr("width", legendWidth)
            .attr("height", legendHeight)
            .attr("rx", 999)
            .attr("fill", `url(#${gradientId})`);

        const [min, max] = scale.domain();
        legend
            .append("text")
            .attr("x", 0)
            .attr("y", 28)
            .attr("class", "legend-label")
            .text(this.metricConfig[this.metric].formatter(min));

        legend
            .append("text")
            .attr("x", legendWidth)
            .attr("y", 28)
            .attr("text-anchor", "end")
            .attr("class", "legend-label")
            .text(this.metricConfig[this.metric].formatter(max));
    }

    render() {
        const scale = this.getScale();
        const formatMetric = this.metricConfig[this.metric].formatter;
        const covered = this.features.filter((feature) => feature.summary).length;
        this.status.text(`${covered} of ${this.features.length} municipalities have listing data in the cleaned sample.`);

        const towns = this.root.selectAll(".town-shape").data(this.features, (d) => d.id);

        towns
            .join(
                (enter) =>
                    enter
                        .append("path")
                        .attr("class", "town-shape")
                        .attr("d", this.path)
                        .attr("fill", "#d9e2ec")
                        .attr("stroke", "rgba(16, 35, 63, 0.25)")
                        .attr("stroke-width", 0.8)
                        .on("mousemove", (event, feature) => this.showTooltip(event, feature, formatMetric))
                        .on("mouseleave", () => this.hideTooltip())
                        .on("click", (event, feature) => this.zoomToFeature(feature))
                        .call((enterSelection) =>
                            enterSelection
                                .transition()
                                .duration(650)
                                .attr("fill", (feature) =>
                                    feature.summary ? scale(feature.summary[this.metric]) : "#d9e2ec"
                                )
                        ),
                (update) =>
                    update
                        .transition()
                        .duration(500)
                        .attr("fill", (feature) =>
                            feature.summary ? scale(feature.summary[this.metric]) : "#d9e2ec"
                        ),
            );

        this.renderLegend(scale);
    }

    showTooltip(event, feature, formatMetric) {
        const summary = feature.summary;
        const html = summary
            ? `
                <strong>${summary.town}</strong>
                <div>${this.metricConfig[this.metric].label}: ${formatMetric(summary[this.metric])}</div>
                <div>Median income: ${window.maUtils.formatCurrency(summary.medianHouseholdIncome)}</div>
                <div>Price-to-income: ${window.maUtils.formatNumber(summary.priceToIncomeRatio, 2)}x</div>
                <div>Listings: ${summary.listingCount.toLocaleString("en-US")}</div>
            `
            : `
                <strong>${window.maUtils.titleCase(feature.properties.town)}</strong>
                <div>No cleaned listing sample for this municipality.</div>
            `;

        this.tooltip
            .style("opacity", 1)
            .style("left", `${event.offsetX + 16}px`)
            .style("top", `${event.offsetY + 16}px`)
            .html(html);
    }

    hideTooltip() {
        this.tooltip.style("opacity", 0);
    }

    zoomToFeature(feature) {
        const [[x0, y0], [x1, y1]] = this.path.bounds(feature);
        const dx = x1 - x0;
        const dy = y1 - y0;
        const x = (x0 + x1) / 2;
        const y = (y0 + y1) / 2;
        const scale = Math.max(
            1,
            Math.min(7, 0.9 / Math.max(dx / this.width, dy / this.height))
        );
        const translate = [
            this.width / 2 - scale * x,
            this.height / 2 - scale * y,
        ];

        this.svg
            .transition()
            .duration(750)
            .call(
                this.zoomBehavior.transform,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
            );
    }

    resetZoom() {
        this.svg.transition().duration(650).call(this.zoomBehavior.transform, d3.zoomIdentity);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("choropleth-container");
    if (container) {
        new ChoroplethMap("choropleth-container").init();
    }
});
