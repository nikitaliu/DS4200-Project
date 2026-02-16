// D3 Choropleth Map Alternative: City Bubbles on Map
// Shows MA cities as circles colored by price metrics
// (Simplified version that doesn't require exact TopoJSON boundaries)

class ChoroplethMap {
    constructor(containerId) {
        this.containerId = containerId;
        this.margin = {top: 40, right: 30, bottom: 30, left: 30};
        this.width = 900 - this.margin.left - this.margin.right;
        this.height = 600 - this.margin.top - this.margin.bottom;
        
        this.currentMetric = 'avgPrice';
    }
    
    async init() {
        // Load and process data
        const rawData = await d3.csv('data/processed/merged_data.csv', d => ({
            city: d.city,
            price: +d.price,
            pricePerSqft: +d.pricePerSqft,
            medianIncome: +d.medianIncome,
            population: +d.population,
            sqft: +d.sqft
        }));
        
        // Aggregate by city
        const cityMap = d3.rollup(rawData,
            v => ({
                avgPrice: d3.mean(v, d => d.price),
                avgPricePerSqft: d3.mean(v, d => d.pricePerSqft),
                medianIncome: v[0].medianIncome,
                population: v[0].population,
                count: v.length,
                priceToIncome: d3.mean(v, d => d.price) / v[0].medianIncome
            }),
            d => d.city
        );
        
        this.cityData = Array.from(cityMap, ([city, stats]) => ({
            city,
            ...stats
        })).filter(d => d.city !== 'Unknown');
        
        // Create approximate geographic layout (simplified grid)
        this.assignCoordinates();
        
        // Create SVG
        this.svg = d3.select(`#${this.containerId}`)
            .append('svg')
            .attr('width', this.width + this.margin.left + this.margin.right)
            .attr('height', this.height + this.margin.top + this.margin.bottom)
            .append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
        
        // Add zoom
        const zoom = d3.zoom()
            .scaleExtent([0.8, 8])
            .on('zoom', (event) => {
                this.svg.attr('transform', event.transform);
            });
        
        d3.select(`#${this.containerId} svg`).call(zoom);
        
        // Create tooltip
        this.tooltip = d3.select('body')
            .append('div')
            .attr('class', 'map-tooltip')
            .style('opacity', 0);
        
        // Add controls
        this.addControls();
        
        // Draw
        this.draw();
    }
    
    assignCoordinates() {
        // Assign approximate grid coordinates to cities
        // In a real implementation, you would use actual lat/long
        const cols = Math.ceil(Math.sqrt(this.cityData.length));
        
        // Sort cities by name for consistent layout
        this.cityData.sort((a, b) => a.city.localeCompare(b.city));
        
        this.cityData.forEach((d, i) => {
            d.x = (i % cols) * (this.width / cols) + (this.width / cols / 2);
            d.y = Math.floor(i / cols) * (this.height / Math.ceil(this.cityData.length / cols)) + 20;
        });
        
        // Add some jitter for visual interest
        this.cityData.forEach(d => {
            d.x += (Math.random() - 0.5) * 20;
            d.y += (Math.random() - 0.5) * 20;
        });
    }
    
    addControls() {
        const controls = d3.select(`#${this.containerId}`)
            .insert('div', ':first-child')
            .attr('class', 'chart-controls')
            .style('margin-bottom', '15px');
        
        controls.append('label')
            .text('Color by: ')
            .style('font-weight', 'bold')
            .style('margin-right', '10px');
        
        const select = controls.append('select')
            .attr('class', 'metric-select')
            .on('change', (event) => {
                this.currentMetric = event.target.value;
                this.draw();
            });
        
        const options = [
            {value: 'avgPrice', label: 'Average Price'},
            {value: 'avgPricePerSqft', label: 'Price per Sqft'},
            {value: 'priceToIncome', label: 'Price-to-Income Ratio'},
            {value: 'medianIncome', label: 'Median Income'}
        ];
        
        select.selectAll('option')
            .data(options)
            .enter()
            .append('option')
            .attr('value', d => d.value)
            .text(d => d.label);
        
        controls.append('p')
            .style('font-size', '12px')
            .style('color', '#666')
            .style('margin-top', '5px')
            .text('💡 Hover over circles for details. Use mouse wheel to zoom.');
    }
    
    draw() {
        // Remove existing circles and legend
        this.svg.selectAll('.city-circle').remove();
        this.svg.selectAll('.legend').remove();
        
        // Get value extent for color scale
        const values = this.cityData.map(d => d[this.currentMetric]);
        const extent = d3.extent(values);
        
        // Color scale
        const colorScale = d3.scaleQuantize()
            .domain(extent)
            .range(d3.schemeYlOrRd[7]);
        
        // Size scale based on population
        const sizeScale = d3.scaleSqrt()
            .domain(d3.extent(this.cityData, d => d.population))
            .range([4, 20]);
        
        // Draw cities as circles
        this.svg.selectAll('.city-circle')
            .data(this.cityData)
            .enter()
            .append('circle')
            .attr('class', 'city-circle')
            .attr('cx', d => d.x)
            .attr('cy', d => d.y)
            .attr('r', d => sizeScale(d.population))
            .attr('fill', d => colorScale(d[this.currentMetric]))
            .attr('stroke', '#333')
            .attr('stroke-width', 0.5)
            .attr('opacity', 0.8)
            .style('cursor', 'pointer')
            .on('mouseover', (event, d) => {
                d3.select(event.target)
                    .attr('stroke-width', 2)
                    .attr('opacity', 1);
                
                this.tooltip.transition().duration(200).style('opacity', 0.9);
                this.tooltip.html(`
                    <strong>${d.city}</strong><br/>
                    Avg Price: $${d3.format(',.0f')(d.avgPrice)}<br/>
                    Median Income: $${d3.format(',.0f')(d.medianIncome)}<br/>
                    Listings: ${d.count}<br/>
                    Price/Income: ${d.priceToIncome.toFixed(2)}x<br/>
                    Population: ${d3.format(',.0f')(d.population)}
                `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', (event) => {
                d3.select(event.target)
                    .attr('stroke-width', 0.5)
                    .attr('opacity', 0.8);
                
                this.tooltip.transition().duration(500).style('opacity', 0);
            });
        
        // Add legend
        this.addLegend(colorScale, extent);
        
        // Add title
        this.svg.selectAll('.chart-title').remove();
        this.svg.append('text')
            .attr('class', 'chart-title')
            .attr('x', this.width / 2)
            .attr('y', -10)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .style('font-weight', 'bold')
            .text('Massachusetts Housing by City');
    }
    
    addLegend(colorScale, extent) {
        const legendWidth = 300;
        const legendHeight = 15;
        const legendX = this.width - legendWidth - 20;
        const legendY = this.height - 40;
        
        const legend = this.svg.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(${legendX},${legendY})`);
        
        // Color gradient
        const colorRange = colorScale.range();
        const steps = colorRange.length;
        const stepWidth = legendWidth / steps;
        
        legend.selectAll('rect')
            .data(colorRange)
            .enter()
            .append('rect')
            .attr('x', (d, i) => i * stepWidth)
            .attr('y', 0)
            .attr('width', stepWidth)
            .attr('height', legendHeight)
            .attr('fill', d => d);
        
        // Labels
        const metricLabels = {
            'avgPrice': 'Price',
            'avgPricePerSqft': 'Price/Sqft',
            'priceToIncome': 'Price-to-Income',
            'medianIncome': 'Income'
        };
        
        legend.append('text')
            .attr('x', 0)
            .attr('y', legendHeight + 15)
            .style('font-size', '11px')
            .text(d3.format('$,.0f')(extent[0]));
        
        legend.append('text')
            .attr('x', legendWidth)
            .attr('y', legendHeight + 15)
            .attr('text-anchor', 'end')
            .style('font-size', '11px')
            .text(d3.format('$,.0f')(extent[1]));
        
        legend.append('text')
            .attr('x', legendWidth / 2)
            .attr('y', -5)
            .attr('text-anchor', 'middle')
            .style('font-size', '12px')
            .style('font-weight', 'bold')
            .text(metricLabels[this.currentMetric]);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('choropleth-container')) {
        const map = new ChoroplethMap('choropleth-container');
        map.init();
    }
});
