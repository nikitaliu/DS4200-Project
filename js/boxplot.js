// D3 Box Plot: Price Distribution by Property Type
// Shows price distribution for each property type with outliers

class BoxPlot {
    constructor(containerId) {
        this.containerId = containerId;
        this.margin = {top: 40, right: 30, bottom: 80, left: 80};
        this.width = 700 - this.margin.left - this.margin.right;
        this.height = 450 - this.margin.top - this.margin.bottom;
        
        // Property type colors
        this.colors = {
            'Single Family': '#3A7CA5',
            'Condo': '#F4845F',
            'Townhouse': '#2ECC71',
            'Multi Family': '#9B59B6'
        };
        
        this.useLogScale = false;
        this.currentMetric = 'price';
    }
    
    async init() {
        // Load data
        const data = await d3.csv('data/processed/merged_data.csv', d => ({
            price: +d.price,
            pricePerSqft: +d.pricePerSqft,
            propertyType: d.propertyType,
            city: d.city,
            sqft: +d.sqft,
            bedrooms: +d.bedrooms
        }));
        
        this.data = data.filter(d => d.propertyType && d.price > 0);
        
        // Create SVG
        this.svg = d3.select(`#${this.containerId}`)
            .append('svg')
            .attr('width', this.width + this.margin.left + this.margin.right)
            .attr('height', this.height + this.margin.top + this.margin.bottom)
            .append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
        
        // Create tooltip
        this.tooltip = d3.select('body')
            .append('div')
            .attr('class', 'map-tooltip')
            .style('opacity', 0);
        
        // Add controls
        this.addControls();
        
        // Draw initial chart
        this.draw();
    }
    
    addControls() {
        const controls = d3.select(`#${this.containerId}`)
            .insert('div', ':first-child')
            .attr('class', 'chart-controls')
            .style('margin-bottom', '15px');
        
        // Toggle button for metric
        controls.append('button')
            .attr('class', 'control-button')
            .text('Switch to Price per Sqft')
            .on('click', () => {
                this.currentMetric = this.currentMetric === 'price' ? 'pricePerSqft' : 'price';
                d3.select('.control-button:first-child')
                    .text(this.currentMetric === 'price' ? 'Switch to Price per Sqft' : 'Switch to Price');
                this.draw();
            });
        
        // Log scale toggle
        controls.append('button')
            .attr('class', 'control-button')
            .style('margin-left', '10px')
            .text('Toggle Log Scale')
            .on('click', () => {
                this.useLogScale = !this.useLogScale;
                this.draw();
            });
    }
    
    calculateBoxStats(values) {
        const sorted = values.sort(d3.ascending);
        const q1 = d3.quantile(sorted, 0.25);
        const median = d3.quantile(sorted, 0.5);
        const q3 = d3.quantile(sorted, 0.75);
        const iqr = q3 - q1;
        const min = q1 - 1.5 * iqr;
        const max = q3 + 1.5 * iqr;
        
        return {
            q1,
            median,
            q3,
            iqr,
            min: Math.max(d3.min(sorted), min),
            max: Math.min(d3.max(sorted), max),
            outliers: sorted.filter(d => d < min || d > max)
        };
    }
    
    draw() {
        // Clear existing elements
        this.svg.selectAll('*').remove();
        
        // Get unique property types
        const propertyTypes = Array.from(new Set(this.data.map(d => d.propertyType)))
            .filter(d => d);
        
        // Calculate box plot statistics for each type
        const boxData = propertyTypes.map(type => {
            const typeData = this.data.filter(d => d.propertyType === type);
            const values = typeData.map(d => d[this.currentMetric]).filter(v => v > 0 && !isNaN(v));
            const stats = this.calculateBoxStats(values);
            
            return {
                type,
                stats,
                data: typeData,
                count: values.length
            };
        });
        
        // Scales
        const x = d3.scaleBand()
            .domain(propertyTypes)
            .range([0, this.width])
            .padding(0.3);
        
        const yValues = boxData.flatMap(d => [d.stats.min, d.stats.max]);
        
        let y;
        if (this.useLogScale) {
            y = d3.scaleLog()
                .domain([d3.min(yValues), d3.max(yValues)])
                .range([this.height, 0])
                .nice();
        } else {
            y = d3.scaleLinear()
                .domain([0, d3.max(yValues)])
                .range([this.height, 0])
                .nice();
        }
        
        // Draw boxes
        const boxes = this.svg.selectAll('.box')
            .data(boxData)
            .enter()
            .append('g')
            .attr('class', 'box')
            .attr('transform', d => `translate(${x(d.type)},0)`);
        
        // Vertical lines (whiskers)
        boxes.append('line')
            .attr('x1', x.bandwidth() / 2)
            .attr('x2', x.bandwidth() / 2)
            .attr('y1', d => y(d.stats.min))
            .attr('y2', d => y(d.stats.max))
            .attr('stroke', 'black')
            .attr('stroke-width', 1);
        
        // Boxes
        boxes.append('rect')
            .attr('x', 0)
            .attr('y', d => y(d.stats.q3))
            .attr('width', x.bandwidth())
            .attr('height', d => y(d.stats.q1) - y(d.stats.q3))
            .attr('fill', d => this.colors[d.type] || '#999')
            .attr('stroke', 'black')
            .attr('stroke-width', 1)
            .style('cursor', 'pointer')
            .on('mouseover', (event, d) => {
                this.tooltip.transition().duration(200).style('opacity', 0.9);
                this.tooltip.html(`
                    <strong>${d.type}</strong><br/>
                    Count: ${d.count}<br/>
                    Median: $${d3.format(',.0f')(d.stats.median)}<br/>
                    Q1: $${d3.format(',.0f')(d.stats.q1)}<br/>
                    Q3: $${d3.format(',.0f')(d.stats.q3)}
                `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', () => {
                this.tooltip.transition().duration(500).style('opacity', 0);
            });
        
        // Median lines
        boxes.append('line')
            .attr('x1', 0)
            .attr('x2', x.bandwidth())
            .attr('y1', d => y(d.stats.median))
            .attr('y2', d => y(d.stats.median))
            .attr('stroke', 'white')
            .attr('stroke-width', 2);
        
        // Whisker caps
        [d => d.stats.min, d => d.stats.max].forEach(accessor => {
            boxes.append('line')
                .attr('x1', x.bandwidth() * 0.25)
                .attr('x2', x.bandwidth() * 0.75)
                .attr('y1', d => y(accessor(d)))
                .attr('y2', d => y(accessor(d)))
                .attr('stroke', 'black')
                .attr('stroke-width', 1);
        });
        
        // Outliers
        boxData.forEach(d => {
            const outlierData = d.data.filter(item => {
                const val = item[this.currentMetric];
                return val < d.stats.min || val > d.stats.max;
            });
            
            this.svg.selectAll(`.outlier-${d.type}`)
                .data(outlierData)
                .enter()
                .append('circle')
                .attr('cx', x(d.type) + x.bandwidth() / 2)
                .attr('cy', item => y(item[this.currentMetric]))
                .attr('r', 3)
                .attr('fill', this.colors[d.type] || '#999')
                .attr('opacity', 0.5)
                .style('cursor', 'pointer')
                .on('mouseover', (event, item) => {
                    this.tooltip.transition().duration(200).style('opacity', 0.9);
                    this.tooltip.html(`
                        <strong>${item.city}</strong><br/>
                        ${this.currentMetric === 'price' ? 'Price' : 'Price/Sqft'}: $${d3.format(',.0f')(item[this.currentMetric])}<br/>
                        Beds: ${item.bedrooms}<br/>
                        Sqft: ${d3.format(',.0f')(item.sqft)}
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
                })
                .on('mouseout', () => {
                    this.tooltip.transition().duration(500).style('opacity', 0);
                });
        });
        
        // Axes
        const xAxis = d3.axisBottom(x);
        const yLabel = this.currentMetric === 'price' ? 'Price ($)' : 'Price per Sqft ($)';
        const yAxis = d3.axisLeft(y)
            .ticks(this.useLogScale ? 10 : 8)
            .tickFormat(d3.format('$,.0f'));
        
        this.svg.append('g')
            .attr('transform', `translate(0,${this.height})`)
            .call(xAxis)
            .selectAll('text')
            .attr('transform', 'rotate(-15)')
            .style('text-anchor', 'end');
        
        this.svg.append('g')
            .call(yAxis);
        
        // Labels
        this.svg.append('text')
            .attr('x', this.width / 2)
            .attr('y', -10)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .style('font-weight', 'bold')
            .text(`Price Distribution by Property Type ${this.useLogScale ? '(Log Scale)' : ''}`);
        
        this.svg.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -this.height / 2)
            .attr('y', -50)
            .attr('text-anchor', 'middle')
            .text(yLabel);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('boxplot-container')) {
        const boxplot = new BoxPlot('boxplot-container');
        boxplot.init();
    }
});
