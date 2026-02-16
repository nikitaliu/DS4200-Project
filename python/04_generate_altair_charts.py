"""
Step 4: Generate Altair Interactive Visualizations
Creates 4 interactive charts and saves as standalone HTML files.
"""

import pandas as pd
import altair as alt
import os

# File paths
DATA_PATH = 'data/processed/merged_data.csv'
OUTPUT_DIR = 'altair_outputs/'

# Color palette for property types
PROPERTY_COLORS = {
    'Single Family': '#3A7CA5',
    'Condo': '#F4845F',
    'Townhouse': '#2ECC71',
    'Multi Family': '#9B59B6'
}

def load_data():
    """Load the merged dataset."""
    print("Loading merged data...")
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} records")
    return df

def chart1_scatter_price_features(df):
    """
    Chart 1: Scatter plot of price vs features
    - Interactive dropdown to change x-axis
    - Colored by property type
    - Brush selection
    """
    print("\n1. Generating scatter plot: Price vs Features...")
    
    # Prepare data
    chart_df = df[['price', 'sqft', 'bedrooms', 'bathrooms', 'propertyType', 
                   'city', 'pricePerSqft']].dropna()
    
    # Create dropdown selection for x-axis
    x_dropdown = alt.binding_select(
        options=['sqft', 'bedrooms', 'bathrooms', 'pricePerSqft'],
        labels=['Square Feet', 'Bedrooms', 'Bathrooms', 'Price per Sqft'],
        name='X-Axis: '
    )
    x_var = alt.param(name='x_var', value='sqft', bind=x_dropdown)
    
    # Brush selection
    brush = alt.selection_interval(encodings=['x'])
    
    # Base chart
    base = alt.Chart(chart_df).encode(
        x=alt.X(alt.repeat('column'), type='quantitative'),
        y=alt.Y('price:Q', title='Price ($)', scale=alt.Scale(zero=False)),
        color=alt.condition(
            brush,
            alt.Color('propertyType:N', 
                     scale=alt.Scale(domain=list(PROPERTY_COLORS.keys()),
                                   range=list(PROPERTY_COLORS.values())),
                     title='Property Type'),
            alt.value('lightgray')
        ),
        tooltip=[
            alt.Tooltip('city:N', title='City'),
            alt.Tooltip('price:Q', title='Price', format='$,.0f'),
            alt.Tooltip('sqft:Q', title='Sqft', format=',.0f'),
            alt.Tooltip('bedrooms:Q', title='Beds'),
            alt.Tooltip('bathrooms:Q', title='Baths'),
            alt.Tooltip('propertyType:N', title='Type'),
            alt.Tooltip('pricePerSqft:Q', title='$/Sqft', format='$,.0f')
        ]
    ).properties(
        width=700,
        height=400,
        title='Property Price vs Features (Interactive)'
    ).add_params(brush)
    
    # Create scatter plot
    chart = base.mark_circle(size=50, opacity=0.6).repeat(
        column=['sqft', 'bedrooms', 'bathrooms', 'pricePerSqft']
    ).resolve_scale(x='independent')
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, 'scatter_price_features.html')
    chart.save(output_path)
    print(f"   ✓ Saved to: {output_path}")
    
    return chart

def chart2_bar_livability(df):
    """
    Chart 2: Grouped bar chart comparing livability scores
    - Top 20 expensive vs bottom 20 affordable towns
    """
    print("\n2. Generating bar chart: Livability Scores...")
    
    # Calculate average price per town
    town_stats = df.groupby('city').agg({
        'price': 'mean',
        'walk_score': 'mean',
        'bike_score': 'mean',
        'transit_score': 'mean'
    }).reset_index()
    
    # Get top 20 expensive and bottom 20 affordable
    town_stats = town_stats.sort_values('price')
    bottom_20 = town_stats.head(20).copy()
    bottom_20['category'] = 'Most Affordable (Bottom 20)'
    
    top_20 = town_stats.tail(20).copy()
    top_20['category'] = 'Most Expensive (Top 20)'
    
    # Combine
    comparison_df = pd.concat([bottom_20, top_20])
    
    # Reshape for grouped bar chart
    melted = comparison_df.melt(
        id_vars=['city', 'category'],
        value_vars=['walk_score', 'bike_score', 'transit_score'],
        var_name='score_type',
        value_name='score'
    )
    
    # Clean up score type labels
    melted['score_type'] = melted['score_type'].str.replace('_score', '').str.title()
    
    # Create chart
    chart = alt.Chart(melted).mark_bar().encode(
        x=alt.X('score_type:N', title='Livability Metric'),
        y=alt.Y('mean(score):Q', title='Average Score', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('category:N', 
                       scale=alt.Scale(domain=['Most Affordable (Bottom 20)', 
                                             'Most Expensive (Top 20)'],
                                     range=['#E74C3C', '#27AE60']),
                       title='Town Category'),
        column=alt.Column('score_type:N', title=''),
        tooltip=[
            alt.Tooltip('category:N', title='Category'),
            alt.Tooltip('score_type:N', title='Metric'),
            alt.Tooltip('mean(score):Q', title='Avg Score', format='.1f')
        ]
    ).properties(
        width=200,
        height=400,
        title='Livability: Expensive vs Affordable Towns'
    )
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, 'bar_livability.html')
    chart.save(output_path)
    print(f"   ✓ Saved to: {output_path}")
    
    return chart

def chart3_heatmap_risk(df):
    """
    Chart 3: Heatmap of risk levels linked to scatter plot
    """
    print("\n3. Generating heatmap: Risk Analysis...")
    
    # Aggregate by town
    town_risk = df.groupby('city').agg({
        'flood_risk': 'mean',
        'fire_risk': 'mean',
        'wind_risk': 'mean',
        'air_risk': 'mean',
        'heat_risk': 'mean',
        'price': 'mean'
    }).reset_index()
    
    # Calculate average risk
    risk_cols = ['flood_risk', 'fire_risk', 'wind_risk', 'air_risk', 'heat_risk']
    town_risk['avg_risk'] = town_risk[risk_cols].mean(axis=1)
    
    # Take top 30 towns by average price for readability
    town_risk = town_risk.nlargest(30, 'price')
    
    # Melt for heatmap
    risk_melted = town_risk.melt(
        id_vars=['city', 'price', 'avg_risk'],
        value_vars=risk_cols,
        var_name='risk_type',
        value_name='risk_level'
    )
    risk_melted['risk_type'] = risk_melted['risk_type'].str.replace('_risk', '').str.title()
    
    # Selection
    click = alt.selection_point(fields=['city'], empty=False)
    
    # Heatmap
    heatmap = alt.Chart(risk_melted).mark_rect().encode(
        y=alt.Y('city:N', title='Town', sort=alt.EncodingSortField(field='avg_risk', order='descending')),
        x=alt.X('risk_type:N', title='Risk Type'),
        color=alt.Color('risk_level:Q', 
                       scale=alt.Scale(scheme='reds', domain=[0, 10]),
                       title='Risk Level (0-10)'),
        opacity=alt.condition(click, alt.value(1.0), alt.value(0.3)),
        tooltip=[
            alt.Tooltip('city:N', title='Town'),
            alt.Tooltip('risk_type:N', title='Risk Type'),
            alt.Tooltip('risk_level:Q', title='Level', format='.1f'),
            alt.Tooltip('price:Q', title='Avg Price', format='$,.0f')
        ]
    ).properties(
        width=300,
        height=600,
        title='Risk Levels by Town'
    ).add_params(click)
    
    # Scatter plot
    scatter = alt.Chart(town_risk).mark_circle(size=100).encode(
        x=alt.X('avg_risk:Q', title='Average Risk Level', scale=alt.Scale(domain=[0, 10])),
        y=alt.Y('price:Q', title='Average Price ($)'),
        color=alt.condition(click, alt.value('#E74C3C'), alt.value('lightgray')),
        tooltip=[
            alt.Tooltip('city:N', title='Town'),
            alt.Tooltip('avg_risk:Q', title='Avg Risk', format='.2f'),
            alt.Tooltip('price:Q', title='Avg Price', format='$,.0f')
        ]
    ).properties(
        width=350,
        height=600,
        title='Risk vs Price'
    ).add_params(click)
    
    # Combine
    chart = alt.hconcat(heatmap, scatter).resolve_legend(
        color='independent'
    )
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, 'heatmap_risk.html')
    chart.save(output_path)
    print(f"   ✓ Saved to: {output_path}")
    
    return chart

def chart4_scatter_income_price(df):
    """
    Chart 4: Scatter of income vs price per town
    - Sized by population
    - Colored by livability (average of walk/bike/transit scores)
    """
    print("\n4. Generating scatter: Income vs Price...")
    
    # Aggregate by town
    town_stats = df.groupby('city').agg({
        'price': 'mean',
        'medianIncome': 'first',
        'population': 'first',
        'walk_score': 'mean',
        'bike_score': 'mean',
        'transit_score': 'mean'
    }).reset_index()
    
    # Calculate average livability score
    town_stats['livability'] = (
        town_stats['walk_score'] + 
        town_stats['bike_score'] + 
        town_stats['transit_score']
    ) / 3
    
    # Remove any rows with missing data
    town_stats = town_stats.dropna()
    
    # Create chart
    chart = alt.Chart(town_stats).mark_circle().encode(
        x=alt.X('medianIncome:Q', title='Median Household Income ($)', 
               scale=alt.Scale(zero=False)),
        y=alt.Y('price:Q', title='Average Listing Price ($)',
               scale=alt.Scale(zero=False)),
        size=alt.Size('population:Q', 
                     title='Population',
                     scale=alt.Scale(range=[50, 1000])),
        color=alt.Color('livability:Q',
                       scale=alt.Scale(scheme='viridis', domain=[0, 100]),
                       title='Livability Score'),
        tooltip=[
            alt.Tooltip('city:N', title='Town'),
            alt.Tooltip('medianIncome:Q', title='Median Income', format='$,.0f'),
            alt.Tooltip('price:Q', title='Avg Price', format='$,.0f'),
            alt.Tooltip('population:Q', title='Population', format=',.0f'),
            alt.Tooltip('livability:Q', title='Livability', format='.1f')
        ]
    ).properties(
        width=700,
        height=500,
        title='Income vs Housing Price: The Affordability Gap'
    ).interactive()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, 'scatter_income_price.html')
    chart.save(output_path)
    print(f"   ✓ Saved to: {output_path}")
    
    return chart

def main():
    """Main function to generate all charts."""
    print("=" * 70)
    print("GENERATING ALTAIR VISUALIZATIONS")
    print("=" * 70)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load data
    df = load_data()
    
    # Generate all charts
    chart1_scatter_price_features(df)
    chart2_bar_livability(df)
    chart3_heatmap_risk(df)
    chart4_scatter_income_price(df)
    
    print("\n" + "=" * 70)
    print("✅ ALL VISUALIZATIONS COMPLETE!")
    print("=" * 70)
    print(f"\nGenerated 4 interactive HTML charts in: {OUTPUT_DIR}")
    print("\nYou can open them directly in a browser to test:")
    print(f"  - {OUTPUT_DIR}scatter_price_features.html")
    print(f"  - {OUTPUT_DIR}bar_livability.html")
    print(f"  - {OUTPUT_DIR}heatmap_risk.html")
    print(f"  - {OUTPUT_DIR}scatter_income_price.html")

if __name__ == "__main__":
    main()
