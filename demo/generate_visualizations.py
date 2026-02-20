"""
Quick script to generate and save the two visualizations as HTML files.
"""

import sys
sys.path.append('..')

from visualization_demo import create_income_price_visualization, create_risk_analysis_visualization
import pandas as pd

# Load data
print("Loading data...")
df = pd.read_csv('../data/processed/merged_data.csv')
print(f"✓ Loaded {len(df):,} records\n")

# Generate and save Visualization 1
print("Generating Visualization 1: Income vs Price...")
chart1 = create_income_price_visualization(df)
chart1.save('income_vs_price.html')
print("✓ Saved to: demo/income_vs_price.html\n")

# Generate and save Visualization 2
print("Generating Visualization 2: Risk Analysis...")
chart2 = create_risk_analysis_visualization(df)
chart2.save('risk_analysis.html')
print("✓ Saved to: demo/risk_analysis.html\n")

print("="*70)
print("DONE! Open the HTML files in a browser to view the visualizations.")
print("="*70)
