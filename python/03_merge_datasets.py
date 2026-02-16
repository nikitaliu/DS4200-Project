"""
Step 3: Merge Housing and Census Data
Combines cleaned housing data with Census demographic/income data.
"""

import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# File paths
HOUSING_PATH = 'data/processed/housing_cleaned.csv'
CENSUS_PATH = 'data/processed/census_data.csv'
OUTPUT_PATH = 'data/processed/merged_data.csv'

def fuzzy_match_cities(housing_cities, census_cities, threshold=85):
    """
    Match city names between housing and census data using fuzzy matching.
    Returns a mapping dictionary.
    """
    mapping = {}
    
    for h_city in housing_cities:
        # Find best match in census data
        match = process.extractOne(h_city, census_cities, scorer=fuzz.ratio)
        if match and match[1] >= threshold:
            mapping[h_city] = match[0]
        else:
            mapping[h_city] = None  # No good match found
    
    return mapping

def merge_datasets():
    """Merge housing and census datasets."""
    
    print("Loading datasets...")
    housing_df = pd.read_csv(HOUSING_PATH)
    census_df = pd.read_csv(CENSUS_PATH)
    
    print(f"Housing data: {housing_df.shape}")
    print(f"Census data: {census_df.shape}")
    
    # Get unique cities from both datasets
    housing_cities = housing_df['city'].unique()
    census_cities = census_df['townName'].unique()
    
    print(f"\nUnique cities in housing data: {len(housing_cities)}")
    print(f"Unique towns in census data: {len(census_cities)}")
    
    # Create mapping using fuzzy matching
    print("\nMatching city names...")
    city_mapping = fuzzy_match_cities(housing_cities, census_cities)
    
    # Add matched census town name to housing data
    housing_df['census_town'] = housing_df['city'].map(city_mapping)
    
    # Count matches
    matched = housing_df['census_town'].notna().sum()
    total = len(housing_df)
    match_rate = (matched / total) * 100
    
    print(f"Match rate: {match_rate:.1f}% ({matched}/{total} records)")
    
    # Show some unmatched cities
    unmatched_cities = housing_df[housing_df['census_town'].isna()]['city'].unique()
    if len(unmatched_cities) > 0:
        print(f"\nSample of unmatched cities ({len(unmatched_cities)} total):")
        print(unmatched_cities[:10])
    
    # Merge datasets
    print("\nMerging datasets...")
    merged_df = housing_df.merge(
        census_df,
        left_on='census_town',
        right_on='townName',
        how='left'
    )
    
    # Drop redundant columns
    cols_to_drop = ['census_town', 'townName', 'level']
    merged_df = merged_df.drop(columns=[col for col in cols_to_drop if col in merged_df.columns])
    
    # Calculate price-to-income ratio
    if 'price' in merged_df.columns and 'medianIncome' in merged_df.columns:
        merged_df['priceToIncomeRatio'] = merged_df['price'] / merged_df['medianIncome']
        merged_df['priceToIncomeRatio'] = merged_df['priceToIncomeRatio'].replace([np.inf, -np.inf], np.nan)
    
    print(f"\nMerged data shape: {merged_df.shape}")
    print(f"Columns: {list(merged_df.columns)}")
    
    # Summary statistics
    print("\n=== Summary Statistics ===")
    if 'medianIncome' in merged_df.columns:
        income_available = merged_df['medianIncome'].notna().sum()
        print(f"Records with income data: {income_available} ({income_available/len(merged_df)*100:.1f}%)")
        print(f"Median income range: ${merged_df['medianIncome'].min():,.0f} - ${merged_df['medianIncome'].max():,.0f}")
    
    if 'population' in merged_df.columns:
        pop_available = merged_df['population'].notna().sum()
        print(f"Records with population data: {pop_available} ({pop_available/len(merged_df)*100:.1f}%)")
    
    # Save merged dataset
    merged_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nMerged data saved to: {OUTPUT_PATH}")
    
    # Show sample
    print("\nSample of merged data:")
    display_cols = ['city', 'price', 'propertyType', 'medianIncome', 'population', 'priceToIncomeRatio']
    display_cols = [col for col in display_cols if col in merged_df.columns]
    print(merged_df[display_cols].head(10))
    
    return merged_df

if __name__ == "__main__":
    try:
        merge_datasets()
    except ImportError:
        print("\nERROR: fuzzywuzzy library not found.")
        print("Installing it now...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'fuzzywuzzy', 'python-Levenshtein'])
        print("Please run the script again.")
