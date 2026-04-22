class PropertyTypeBoxPlot {
    constructor(containerId) {
        this.container = d3.select(`#${containerId}`);
        this.width = 880;
        this.height = 520;
        this.margin = {top: 36, right: 24, bottom: 90, left: 86};
        this.colors = {
            "Single Family": "#2b6cb0",
            Condo: "#e53e3e",
            Townhouse: "#38a169",
            "Multi Family": "#d69e2e",
        };
    }

    async init() {
        const rows = await d3.csv("data/ma_housing_cleaned.csv", (d) => ({
            propertyType: d.propertyType,
            price: +d.price,
            address: d.address,
            city: d.city,
            sqft: +d.sqft,
            bedrooms: +d.bedrooms,
        }));

        this.data = rows.filter((row) => row.propertyType && Number.isFinite(row.price));
        this.tooltip = this.container.append("div").attr("class", "map-tooltip");
        this.detailCard = this.container
            .append("div")
            .attr("class", "detail-card empty")
            .html("<h3>Outlier details</h3><p>Click an outlier point to inspect the underlying listing.</p>");

        this.svg = this.container
            .append("svg")
            .attr("viewBox", `0 0 ${this.width} ${this.height}`)
            .attr("role", "img")
            .attr("aria-label", "Box plot of listing price by property type");

        this.plot = this.svg
            .append("g")
            .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

        this.resizeObserver = new ResizeObserver(() => this.render());
        this.resizeObserver.observe(this.container.node());
        this.render();
    }

    computeStats(type) {
        const items = this.data
            .filter((row) => row.propertyType === type)
            .sort((a, b) => d3.ascending(a.price, b.price));
        const values = items.map((row) => row.price);
        const q1 = d3.quantile(values, 0.25);
        const median = d3.quantile(values, 0.5);
        const q3 = d3.quantile(values, 0.75);
        const iqr = q3 - q1;
        const whiskerMin = Math.max(d3.min(values), q1 - 1.5 * iqr);
        const whiskerMax = Math.min(d3.max(values), q3 + 1.5 * iqr);
        const outliers = items.filter((row) => row.price < whiskerMin || row.price > whiskerMax);

        return {type, items, values, q1, median, q3, whiskerMin, whiskerMax, outliers};
    }

    render() {
        this.width = Math.max(720, this.container.node().getBoundingClientRect().width || 880);
        this.svg.attr("viewBox", `0 0 ${this.width} ${this.height}`);
        const plotWidth = this.width - this.margin.left - this.margin.right;
        const plotHeight = this.height - this.margin.top - this.margin.bottom;
        const types = Array.from(new Set(this.data.map((row) => row.propertyType)));
        const stats = types.map((type) => this.computeStats(type)).sort((a, b) => d3.descending(a.median, b.median));

        const x = d3.scaleBand().domain(stats.map((d) => d.type)).range([0, plotWidth]).padding(0.28);
        const y = d3
            .scaleLinear()
            .domain([0, d3.max(stats, (d) => d.whiskerMax)])
            .nice()
            .range([plotHeight, 0]);

        this.plot.selectAll("*").remove();

        this.plot
            .append("g")
            .attr("transform", `translate(0,${plotHeight})`)
            .call(d3.axisBottom(x))
            .selectAll("text")
            .attr("transform", "rotate(-18)")
            .style("text-anchor", "end");

        this.plot
            .append("g")
            .call(d3.axisLeft(y).tickFormat((d) => window.maUtils.formatShortCurrency(d)))
            .call((g) => g.select(".domain").remove())
            .call((g) =>
                g
                    .selectAll(".tick line")
                    .clone()
                    .attr("x2", plotWidth)
                    .attr("stroke-opacity", 0.08)
            );

        this.plot
            .append("text")
            .attr("x", -plotHeight / 2)
            .attr("y", -58)
            .attr("transform", "rotate(-90)")
            .attr("fill", "#1a365d")
            .attr("font-weight", 700)
            .text("Listing Price");

        const groups = this.plot
            .selectAll(".box-group")
            .data(stats)
            .join("g")
            .attr("class", "box-group")
            .attr("transform", (d) => `translate(${x(d.type)},0)`);

        groups
            .append("line")
            .attr("x1", x.bandwidth() / 2)
            .attr("x2", x.bandwidth() / 2)
            .attr("y1", (d) => y(d.whiskerMin))
            .attr("y2", (d) => y(d.whiskerMax))
            .attr("stroke", "#475569")
            .attr("stroke-width", 1.2);

        groups
            .append("line")
            .attr("x1", x.bandwidth() * 0.25)
            .attr("x2", x.bandwidth() * 0.75)
            .attr("y1", (d) => y(d.whiskerMin))
            .attr("y2", (d) => y(d.whiskerMin))
            .attr("stroke", "#475569");

        groups
            .append("line")
            .attr("x1", x.bandwidth() * 0.25)
            .attr("x2", x.bandwidth() * 0.75)
            .attr("y1", (d) => y(d.whiskerMax))
            .attr("y2", (d) => y(d.whiskerMax))
            .attr("stroke", "#475569");

        groups
            .append("rect")
            .attr("x", 0)
            .attr("width", x.bandwidth())
            .attr("y", (d) => y(d.median))
            .attr("height", 0)
            .attr("rx", 14)
            .attr("fill", (d) => this.colors[d.type] || "#2b6cb0")
            .attr("fill-opacity", 0.84)
            .attr("stroke", "#16324f")
            .on("mousemove", (event, d) => this.showStatsTooltip(event, d))
            .on("mouseleave", () => this.tooltip.style("opacity", 0))
            .transition()
            .duration(900)
            .attr("y", (d) => y(d.q3))
            .attr("height", (d) => y(d.q1) - y(d.q3));

        groups
            .append("line")
            .attr("x1", 0)
            .attr("x2", x.bandwidth())
            .attr("y1", (d) => y(d.median))
            .attr("y2", (d) => y(d.median))
            .attr("stroke", "#ffffff")
            .attr("stroke-width", 2.2);

        groups.each((d, index, nodes) => {
            d3.select(nodes[index])
                .selectAll(".outlier")
                .data(d.outliers)
                .join("circle")
                .attr("class", "outlier")
                .attr("cx", () => x.bandwidth() / 2 + (Math.random() - 0.5) * x.bandwidth() * 0.32)
                .attr("cy", (row) => y(row.price))
                .attr("r", 0)
                .attr("fill", this.colors[d.type] || "#2b6cb0")
                .attr("fill-opacity", 0.72)
                .attr("stroke", "#16324f")
                .attr("stroke-width", 0.7)
                .on("mousemove", (event, row) =>
                    this.tooltip
                        .style("opacity", 1)
                        .style("left", `${event.offsetX + 16}px`)
                        .style("top", `${event.offsetY + 12}px`)
                        .html(
                            `<strong>${row.city}</strong><div>${window.maUtils.formatCurrency(row.price)}</div><div>${window.maUtils.formatNumber(row.sqft, 0)} sqft</div>`
                        )
                )
                .on("mouseleave", () => this.tooltip.style("opacity", 0))
                .on("click", (_, row) => this.showOutlierDetails(row))
                .transition()
                .delay(300)
                .duration(700)
                .attr("r", 3.6);
        });
    }

    showStatsTooltip(event, stats) {
        this.tooltip
            .style("opacity", 1)
            .style("left", `${event.offsetX + 16}px`)
            .style("top", `${event.offsetY + 12}px`)
            .html(`
                <strong>${stats.type}</strong>
                <div>Median: ${window.maUtils.formatCurrency(stats.median)}</div>
                <div>Q1 to Q3: ${window.maUtils.formatCurrency(stats.q1)} to ${window.maUtils.formatCurrency(stats.q3)}</div>
                <div>Whiskers: ${window.maUtils.formatCurrency(stats.whiskerMin)} to ${window.maUtils.formatCurrency(stats.whiskerMax)}</div>
                <div>Listings: ${stats.items.length.toLocaleString("en-US")}</div>
            `);
    }

    showOutlierDetails(row) {
        this.detailCard
            .classed("empty", false)
            .html(`
                <h3>Selected outlier</h3>
                <p><strong>${row.address || `${row.city}, MA`}</strong></p>
                <p>${row.propertyType} listed at ${window.maUtils.formatCurrency(row.price)} with ${window.maUtils.formatNumber(row.sqft, 0)} sqft and ${window.maUtils.formatNumber(row.bedrooms, 0)} bedrooms.</p>
            `);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("boxplot-container");
    if (container) {
        new PropertyTypeBoxPlot("boxplot-container").init();
    }
});
