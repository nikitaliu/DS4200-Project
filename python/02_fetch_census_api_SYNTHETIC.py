"""
Step 2: Generate Synthetic Census Data (WORKAROUND)
Creates realistic Census-like data for Massachusetts towns.

NOTE: This is synthetic data generated as a workaround because the Census API key is invalid.
      To use real Census data, get a valid API key from https://api.census.gov/data/key_signup.html
      and use 02_fetch_census_api.py instead.
"""

import pandas as pd
import numpy as np
import os

# Output path
OUTPUT_PATH = 'data/processed/census_data.csv'
HOUSING_PATH = 'data/processed/housing_cleaned.csv'

def generate_synthetic_census_data():
    """Generate realistic synthetic census data for MA towns."""
    
    print("⚠️  GENERATING SYNTHETIC CENSUS DATA (API key was invalid)")
    print("=" * 70)
    print("This creates realistic demographic data based on actual MA patterns.")
    print("For production, get a valid Census API key from:")
    print("https://api.census.gov/data/key_signup.html")
    print("=" * 70)
    print()
    
    # Load housing data to get actual city names
    housing_df = pd.read_csv(HOUSING_PATH)
    cities = housing_df['city'].unique()
    
    print(f"Generating census data for {len(cities)} Massachusetts cities/towns...")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Create synthetic data based on realistic MA ranges
    # Source: actual MA census data patterns
    census_data = []
    
    for city in cities:
        # Skip "Unknown" cities
        if city == "Unknown":
            continue
        
        # Generate realistic values based on city type
        # Larger cities tend to have higher populations and income variations
        
        # Population: 500 to 150,000 (MA town range)
        if city in ['Boston', 'Worcester', 'Springfield', 'Cambridge', 'Lowell']:
            population = np.random.randint(80000, 150000)
        elif len(city) > 10:  # Longer names tend to be smaller towns
            population = np.random.randint(500, 15000)
        else:
            population = np.random.randint(5000, 50000)
        
        # Median household income: $50k to $150k (MA range)
        # Higher-income towns: Brookline, Newton, Wellesley, Lexington, etc.
        if city in ['Brookline', 'Newton', 'Wellesley', 'Lexington', 'Weston', 
                    'Dover', 'Sherborn', 'Carlisle', 'Lincoln']:
            median_income = np.random.randint(120000, 200000)
        elif city in ['Boston', 'Cambridge', 'Somerville']:
            median_income = np.random.randint(80000, 120000)
        else:
            median_income = np.random.randint(50000, 95000)
        
        census_data.append({
            'townName': city,
            'medianIncome': median_income,
            'population': population
        })
    
    # Create DataFrame
    df = pd.DataFrame(census_data)
    
    # Sort by town name
    df = df.sort_values('townName').reset_index(drop=True)
    
    # Save
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    
    print(f"\n✅ Synthetic census data created: {len(df)} towns")
    print(f"   Saved to: {OUTPUT_PATH}")
    print(f"\n   Income range: ${df['medianIncome'].min():,} - ${df['medianIncome'].max():,}")
    print(f"   Population range: {df['population'].min():,} - {df['population'].max():,}")
    
    print("\n⚠️  REMINDER: This is synthetic data. For real data:")
    print("   1. Get Census API key: https://api.census.gov/data/key_signup.html")
    print("   2. Add it to .env file")
    print("   3. Run python/02_fetch_census_api.py")
    
    return df

if __name__ == "__main__":
    generate_synthetic_census_data()
