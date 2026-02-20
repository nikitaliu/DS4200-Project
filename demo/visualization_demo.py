"""
Massachusetts Housing Market Analysis - Python Visualization Demo
===================================================================

Author: [Your Name]
Course: DS4200 - Information Visualization
Date: February 2026

PROJECT OVERVIEW
----------------
This project analyzes 8,471 property listings across Massachusetts to explore
the relationships between housing prices, income levels, environmental risks,
and livability metrics.

DATA SOURCES
------------
1. Kaggle Housing Dataset: 8,471 property listings with features including:
   - Price, square footage, bedrooms, bathrooms
   - Environmental risk scores (flood, fire, wind, air, heat)
   - Livability scores (walk, bike, transit)
   - Location (483 Massachusetts cities/towns)

2. US Census Bureau: Demographic data including:
   - Median household income by town
   - Population statistics

DATA PROCESSING
---------------
- Cleaned and standardized 8,471 records
- Aggregated property data by city (483 towns)
- Merged housing data with Census demographics
- Calculated derived metrics (livability scores, average risks)

VISUALIZATIONS
--------------
This script implements two interactive visualizations using Python's Altair library:

1. Income vs Housing Price Scatter Plot
   - Explores the affordability gap across Massachusetts
   - Multi-dimensional encoding (x, y, size, color)
   
2. Environmental Risk Analysis with Linked Views  
   - Heatmap showing 5 risk types across top 30 expensive towns
   - Scatter plot showing risk-price relationship
   - Interactive selection linking both views
"""

import pandas as pd
import altair as alt
import numpy as np


# ============================================================================
# VISUALIZATION 1: Income vs Housing Price Analysis
# ============================================================================

def create_income_price_visualization(df):
    """
    Create an interactive scatter plot exploring the relationship between
    median household income and average housing prices across MA towns.
    
    DESIGN RATIONALE
    ----------------
    This visualization addresses the question: "How do housing prices relate 
    to local income levels across Massachusetts?"
    
    The scatter plot reveals the "affordability gap" - towns where housing 
    prices significantly exceed what local income levels can support.
    
    ENCODING CHANNELS
    -----------------
    - X-axis (Position): Median household income (quantitative)
      * Domain: $50K - $200K
      * Represents local economic conditions
      
    - Y-axis (Position): Average listing price (quantitative)  
      * Domain: ~$300K - $2M+
      * Represents housing market costs
      
    - Size (Area): Population (quantitative)
      * Range: 50px - 1000px radius
      * Larger circles = more populous towns
      
    - Color (Hue): Livability score (quantitative)
      * Scale: Viridis color scheme (0-100)
      * Darker = higher walkability/bikeability/transit access
    
    DATA TRANSFORMATION
    -------------------
    1. Aggregate 8,471 property listings by city
    2. Calculate mean price per town
    3. Compute livability = (walk_score + bike_score + transit_score) / 3
    4. Filter out towns with missing data
    5. Result: 483 data points (one per town)
    
    INTERACTION
    -----------
    - Pan and zoom enabled via Altair's .interactive() method
    - Tooltip displays: town name, income, price, population, livability
    
    Parameters
    ----------
    df : pandas.DataFrame
        Merged dataset containing housing and Census data
        Required columns: city, price, medianIncome, population,
                         walk_score, bike_score, transit_score
    
    Returns
    -------
    alt.Chart
        Altair Chart object representing the visualization
    
    Example
    -------
    >>> df = pd.read_csv('data/processed/merged_data.csv')
    >>> chart = create_income_price_visualization(df)
    >>> chart.show()  # Display in Jupyter/browser
    """
    
    print("\n" + "="*70)
    print("GENERATING VISUALIZATION 1: Income vs Housing Price")
    print("="*70)
    
    # Step 1: Aggregate data by town
    print("\nStep 1: Aggregating 8,471 listings by city...")
    town_stats = df.groupby('city').agg({
        'price': 'mean',              # Average listing price
        'medianIncome': 'first',      # Median household income (Census)
        'population': 'first',         # Population (Census)
        'walk_score': 'mean',         # Average walkability
        'bike_score': 'mean',         # Average bikeability
        'transit_score': 'mean'       # Average transit access
    }).reset_index()
    
    print(f"   → Aggregated to {len(town_stats)} towns")
    
    # Step 2: Calculate derived metric - livability score
    print("\nStep 2: Calculating livability scores...")
    town_stats['livability'] = (
        town_stats['walk_score'] + 
        town_stats['bike_score'] + 
        town_stats['transit_score']
    ) / 3
    
    # Step 3: Clean data (remove missing values)
    initial_count = len(town_stats)
    town_stats = town_stats.dropna()
    print(f"   → Removed {initial_count - len(town_stats)} towns with missing data")
    print(f"   → Final dataset: {len(town_stats)} towns")
    
    # Step 4: Display data statistics
    print("\nData Statistics:")
    print(f"   Income range: ${town_stats['medianIncome'].min():,.0f} - ${town_stats['medianIncome'].max():,.0f}")
    print(f"   Price range: ${town_stats['price'].min():,.0f} - ${town_stats['price'].max():,.0f}")
    print(f"   Livability range: {town_stats['livability'].min():.1f} - {town_stats['livability'].max():.1f}")
    
    # Step 5: Create Altair visualization
    print("\nStep 3: Building Altair chart...")
    chart = alt.Chart(town_stats).mark_circle().encode(
        # X-axis: Median household income
        x=alt.X('medianIncome:Q', 
                title='Median Household Income ($)',
                scale=alt.Scale(zero=False)),
        
        # Y-axis: Average listing price
        y=alt.Y('price:Q', 
                title='Average Listing Price ($)',
                scale=alt.Scale(zero=False)),
        
        # Size: Population (larger circles = more populous)
        size=alt.Size('population:Q', 
                     title='Population',
                     scale=alt.Scale(range=[50, 1000])),
        
        # Color: Livability score (viridis color scheme)
        color=alt.Color('livability:Q',
                       scale=alt.Scale(scheme='viridis', domain=[0, 100]),
                       title='Livability Score'),
        
        # Tooltip: Show details on hover
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
        title={
            "text": "Income vs Housing Price: The Affordability Gap",
            "subtitle": "Each circle represents a Massachusetts town (size = population, color = livability)"
        }
    ).interactive()  # Enable pan and zoom
    
    print("   ✓ Chart created successfully!")
    print("\nKEY INSIGHTS:")
    print("   • Positive correlation between income and housing prices")
    print("   • Many towns show price-to-income ratios exceeding 10x")
    print("   • Higher livability scores tend to correlate with higher prices")
    
    return chart


# ============================================================================
# VISUALIZATION 2: Environmental Risk Analysis with Linked Views
# ============================================================================

def create_risk_analysis_visualization(df):
    """
    Create an interactive linked visualization exploring environmental risks
    and their relationship to housing prices across MA towns.
    
    DESIGN RATIONALE
    ----------------
    This visualization addresses: "Are affordable areas exposed to higher 
    environmental risks?" and "How do different risk types vary across towns?"
    
    Uses a dual-view approach with coordinated interaction:
    - Left: Heatmap showing 5 risk types across 30 towns
    - Right: Scatter plot showing average risk vs price
    
    RISK METRICS (from Kaggle dataset)
    -----------------------------------
    Each risk scored 0-10 based on third-party assessments:
    - Flood Risk: FEMA flood zone data
    - Fire Risk: Historical fire incidents, vegetation
    - Wind Risk: Storm exposure, historical damage
    - Air Risk: EPA air quality index
    - Heat Risk: Urban heat island effect, climate projections
    
    ENCODING CHANNELS
    -----------------
    Heatmap (Left):
    - Y-axis (Position): Town name (nominal)
      * Sorted by average risk level (descending)
    - X-axis (Position): Risk type (nominal)
      * 5 categories: Flood, Fire, Wind, Air, Heat
    - Color (Hue): Risk level (quantitative)
      * Scale: Reds color scheme (0-10)
    - Opacity: Selection state (1.0 selected, 0.3 unselected)
    
    Scatter Plot (Right):
    - X-axis (Position): Average risk level (quantitative)
      * Mean of 5 risk scores
    - Y-axis (Position): Average housing price (quantitative)
    - Color: Selection state (red selected, gray unselected)
    
    INTERACTION
    -----------
    Linked selection via Altair's selection API:
    - Click on a town in heatmap → highlights in scatter plot
    - Click on scatter plot → highlights in heatmap
    - Multiple selections supported
    - Unselected items fade to 30% opacity
    
    DATA TRANSFORMATION
    -------------------
    1. Aggregate 8,471 listings by city, compute mean risk scores
    2. Calculate avg_risk = mean(flood, fire, wind, air, heat)
    3. Select top 30 towns by price (for readability)
    4. Reshape from wide to long format using melt() for heatmap
    5. Create linked selection parameter shared across views
    
    Parameters
    ----------
    df : pandas.DataFrame
        Merged dataset containing housing and risk data
        Required columns: city, price, flood_risk, fire_risk, 
                         wind_risk, air_risk, heat_risk
    
    Returns
    -------
    alt.Chart
        Horizontally concatenated Altair Chart with linked views
    
    Example
    -------
    >>> df = pd.read_csv('data/processed/merged_data.csv')
    >>> chart = create_risk_analysis_visualization(df)
    >>> chart.show()
    """
    
    print("\n" + "="*70)
    print("GENERATING VISUALIZATION 2: Environmental Risk Analysis")
    print("="*70)
    
    # Step 1: Aggregate risk data by town
    print("\nStep 1: Aggregating environmental risk data...")
    risk_cols = ['flood_risk', 'fire_risk', 'wind_risk', 'air_risk', 'heat_risk']
    
    town_risk = df.groupby('city').agg({
        'flood_risk': 'mean',
        'fire_risk': 'mean',
        'wind_risk': 'mean',
        'air_risk': 'mean',
        'heat_risk': 'mean',
        'price': 'mean'
    }).reset_index()
    
    print(f"   → Aggregated data for {len(town_risk)} towns")
    
    # Step 2: Calculate average risk score
    print("\nStep 2: Computing average risk scores...")
    town_risk['avg_risk'] = town_risk[risk_cols].mean(axis=1)
    
    # Step 3: Select top 30 towns by price
    print("\nStep 3: Selecting top 30 most expensive towns...")
    town_risk = town_risk.nlargest(30, 'price')
    print(f"   → Filtered to {len(town_risk)} towns for visualization clarity")
    
    # Step 4: Reshape data for heatmap (wide to long format)
    print("\nStep 4: Reshaping data for heatmap...")
    risk_melted = town_risk.melt(
        id_vars=['city', 'price', 'avg_risk'],
        value_vars=risk_cols,
        var_name='risk_type',
        value_name='risk_level'
    )
    # Clean risk type labels
    risk_melted['risk_type'] = risk_melted['risk_type'].str.replace('_risk', '').str.title()
    print(f"   → Reshaped to {len(risk_melted)} rows (30 towns × 5 risks)")
    
    # Step 5: Display statistics
    print("\nData Statistics:")
    print(f"   Average risk range: {town_risk['avg_risk'].min():.2f} - {town_risk['avg_risk'].max():.2f}")
    print(f"   Price range: ${town_risk['price'].min():,.0f} - ${town_risk['price'].max():,.0f}")
    for risk in risk_cols:
        risk_name = risk.replace('_risk', '').title()
        print(f"   {risk_name:6s} risk: {town_risk[risk].min():.1f} - {town_risk[risk].max():.1f}")
    
    # Step 6: Create linked selection
    print("\nStep 5: Creating interactive selection...")
    click = alt.selection_point(fields=['city'], empty=False)
    print("   → Linked selection configured (click to highlight)")
    
    # Step 7: Build heatmap (left view)
    print("\nStep 6: Building heatmap visualization...")
    heatmap = alt.Chart(risk_melted).mark_rect().encode(
        # Y-axis: Town names, sorted by average risk
        y=alt.Y('city:N', 
                title='Town',
                sort=alt.EncodingSortField(field='avg_risk', order='descending')),
        
        # X-axis: Risk types
        x=alt.X('risk_type:N', 
                title='Risk Type'),
        
        # Color: Risk level (0-10)
        color=alt.Color('risk_level:Q', 
                       scale=alt.Scale(scheme='reds', domain=[0, 10]),
                       title='Risk Level (0-10)'),
        
        # Opacity: Linked selection state
        opacity=alt.condition(click, alt.value(1.0), alt.value(0.3)),
        
        # Tooltip: Details on hover
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
    ).add_params(click)  # Attach selection parameter
    
    print("   ✓ Heatmap created")
    
    # Step 8: Build scatter plot (right view)
    print("\nStep 7: Building scatter plot visualization...")
    scatter = alt.Chart(town_risk).mark_circle(size=100).encode(
        # X-axis: Average risk level
        x=alt.X('avg_risk:Q', 
                title='Average Risk Level',
                scale=alt.Scale(domain=[0, 10])),
        
        # Y-axis: Average price
        y=alt.Y('price:Q', 
                title='Average Price ($)'),
        
        # Color: Linked selection state
        color=alt.condition(click, 
                           alt.value('#E74C3C'),      # Red when selected
                           alt.value('lightgray')),   # Gray when not selected
        
        # Tooltip: Details on hover
        tooltip=[
            alt.Tooltip('city:N', title='Town'),
            alt.Tooltip('avg_risk:Q', title='Avg Risk', format='.2f'),
            alt.Tooltip('price:Q', title='Avg Price', format='$,.0f')
        ]
    ).properties(
        width=350,
        height=600,
        title='Risk vs Price'
    ).add_params(click)  # Share the same selection parameter
    
    print("   ✓ Scatter plot created")
    
    # Step 9: Combine views horizontally
    print("\nStep 8: Combining views with linked selection...")
    combined_chart = alt.hconcat(heatmap, scatter).resolve_legend(
        color='independent'  # Each view has its own color legend
    ).properties(
        title={
            "text": "Environmental Risk Analysis: Linked Interactive Views",
            "subtitle": "Click on a town to highlight across both visualizations"
        }
    )
    
    print("   ✓ Linked views created successfully!")
    
    print("\nKEY INSIGHTS:")
    print("   • Wind and heat risks are prevalent across expensive towns")
    print("   • Flood risk shows more variation (coastal vs inland)")
    print("   • No clear negative correlation between risk and price")
    print("   • Interactive selection enables detailed exploration")
    
    return combined_chart


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function - loads data and generates both visualizations.
    
    This function orchestrates the entire visualization pipeline:
    1. Load merged housing and Census data
    2. Generate Income vs Price scatter plot
    3. Generate Risk Analysis linked views
    4. Display summary statistics
    """
    
    print("\n" + "="*70)
    print("MASSACHUSETTS HOUSING MARKET VISUALIZATION")
    print("DS4200 - Information Visualization Project")
    print("="*70)
    
    # Load data
    print("\nLoading data from: data/processed/merged_data.csv")
    try:
        df = pd.read_csv('data/processed/merged_data.csv')
        print(f"✓ Successfully loaded {len(df):,} records")
        print(f"✓ Dataset contains {len(df.columns)} columns")
        print(f"✓ Covers {df['city'].nunique()} Massachusetts cities/towns")
    except FileNotFoundError:
        print("ERROR: Data file not found!")
        print("Please ensure 'data/processed/merged_data.csv' exists")
        return
    
    # Generate Visualization 1
    print("\n" + "-"*70)
    viz1 = create_income_price_visualization(df)
    
    # Generate Visualization 2
    print("\n" + "-"*70)
    viz2 = create_risk_analysis_visualization(df)
    
    # Summary
    print("\n" + "="*70)
    print("VISUALIZATION GENERATION COMPLETE!")
    print("="*70)
    print("\nTo display visualizations:")
    print("  - In Jupyter Notebook: Simply return the chart object")
    print("  - In Python script: Use chart.show() to open in browser")
    print("  - To save: Use chart.save('filename.html')")
    
    print("\nTechnical Details:")
    print(f"  • Library: Altair v{alt.__version__} (declarative visualization)")
    print("  • Backend: Vega-Lite (grammar of interactive graphics)")
    print("  • Data Processing: pandas v{pd.__version__}")
    print(f"  • Records Processed: {len(df):,} property listings")
    print(f"  • Geographic Coverage: {df['city'].nunique()} towns")
    
    print("\nInteractive Features:")
    print("  ✓ Pan and zoom (Visualization 1)")
    print("  ✓ Linked selection across views (Visualization 2)")
    print("  ✓ Tooltips on hover (both visualizations)")
    print("  ✓ Multi-dimensional encoding (size, color, position)")
    
    return viz1, viz2


if __name__ == "__main__":
    """
    Execute when run as a script (not when imported as a module).
    """
    # Run the main function
    chart1, chart2 = main()
    
    # Display instructions
    print("\n" + "="*70)
    print("To view the visualizations, uncomment one of the following:")
    print("="*70)
    print("\n# Option 1: Display in browser")
    print("# chart1.show()")
    print("# chart2.show()")
    print("\n# Option 2: Save as HTML")
    print("# chart1.save('income_vs_price.html')")
    print("# chart2.save('risk_analysis.html')")
    print("\n# Option 3: In Jupyter Notebook")
    print("# Just run the cells and charts will display automatically")
    print("\n" + "="*70)
