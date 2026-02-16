"""
Step 1: Clean Kaggle Massachusetts Housing Data
Reads raw CSV, cleans columns, handles missing values, and exports cleaned dataset.
"""

import pandas as pd
import numpy as np
import os

# File paths
RAW_DATA_PATH = 'data/raw/ma_housing_raw.csv'
OUTPUT_PATH = 'data/processed/housing_cleaned.csv'

def clean_housing_data():
    """Clean and standardize the Massachusetts housing dataset."""
    
    print("Loading raw housing data...")
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Raw data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()[:10]}...")
    
    # Drop unnamed columns
    df = df.drop(columns=[col for col in df.columns if 'Unnamed' in col])
    
    # Drop duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    print(f"Removed {initial_rows - len(df)} duplicate rows")
    
    # Rename region to city for consistency
    if 'region' in df.columns:
        df = df.rename(columns={'region': 'city'})
    
    # Standardize city names (title case, strip whitespace)
    if 'city' in df.columns:
        df['city'] = df['city'].str.strip().str.title()
        df['city'] = df['city'].fillna('Unknown')
    
    # Clean price column (remove $ and commas, convert to numeric)
    if 'price' in df.columns:
        df['price'] = df['price'].replace('[\$,\s]', '', regex=True)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    # Clean sqft column (remove commas)
    if 'sqft' in df.columns:
        df['sqft'] = df['sqft'].replace('[,]', '', regex=True)
        df['sqft'] = pd.to_numeric(df['sqft'], errors='coerce')
    
    # Clean sqft_lot column
    if 'sqft_lot' in df.columns:
        df['sqft_lot'] = df['sqft_lot'].replace('[,sqft\s]', '', regex=True)
        df['sqft_lot'] = pd.to_numeric(df['sqft_lot'], errors='coerce')
    
    # Rename beds/baths to bedrooms/bathrooms
    if 'beds' in df.columns:
        df = df.rename(columns={'beds': 'bedrooms'})
    if 'baths' in df.columns:
        df = df.rename(columns={'baths': 'bathrooms'})
    
    # Clean bedrooms and bathrooms
    df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
    df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce')
    
    # Standardize property type
    if 'property_type' in df.columns:
        df = df.rename(columns={'property_type': 'propertyType'})
        # Standardize names
        type_mapping = {
            'single family': 'Single Family',
            'singlefamily': 'Single Family',
            'house': 'Single Family',
            'condo': 'Condo',
            'condominium': 'Condo',
            'townhouse': 'Townhouse',
            'townhome': 'Townhouse',
            'multi family': 'Multi Family',
            'multifamily': 'Multi Family',
            'multi-family': 'Multi Family'
        }
        df['propertyType'] = df['propertyType'].str.lower().str.strip()
        df['propertyType'] = df['propertyType'].replace(type_mapping)
        df['propertyType'] = df['propertyType'].str.title()
    
    # Clean livability scores (remove /100 and convert to numeric)
    for score_col in ['walk_score', 'bike_score', 'transit_score']:
        if score_col in df.columns:
            df[score_col] = df[score_col].replace('[/100\s]', '', regex=True)
            df[score_col] = pd.to_numeric(df[score_col], errors='coerce')
    
    # Clean risk columns (extract numeric value from "Level (X/10)" format)
    risk_cols = ['flood_risk', 'fire_risk', 'wind_risk', 'air_risk', 'heat_risk']
    for risk_col in risk_cols:
        if risk_col in df.columns:
            # Extract number from pattern like "Major (6/10)"
            df[risk_col] = df[risk_col].str.extract(r'\((\d+)/10\)')[0]
            df[risk_col] = pd.to_numeric(df[risk_col], errors='coerce')
    
    # Remove rows with missing critical fields
    critical_cols = ['price', 'city']
    df = df.dropna(subset=critical_cols)
    
    # Filter out unrealistic values
    df = df[(df['price'] >= 50000) & (df['price'] <= 10000000)]  # Reasonable price range
    df = df[(df['bedrooms'] >= 0) & (df['bedrooms'] <= 20)] if 'bedrooms' in df.columns else df
    df = df[(df['bathrooms'] >= 0) & (df['bathrooms'] <= 15)] if 'bathrooms' in df.columns else df
    
    # Recalculate price per sqft (clean version)
    if 'sqft' in df.columns and 'price' in df.columns:
        df['pricePerSqft'] = df['price'] / df['sqft']
        df['pricePerSqft'] = df['pricePerSqft'].replace([np.inf, -np.inf], np.nan)
    
    # Sort by city and price
    df = df.sort_values(['city', 'price']).reset_index(drop=True)
    
    print(f"\nCleaned data shape: {df.shape}")
    print(f"Unique cities: {df['city'].nunique()}")
    print(f"Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
    
    # Save cleaned data
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nCleaned data saved to: {OUTPUT_PATH}")
    
    # Display column info
    print("\nColumn summary:")
    print(df.dtypes)
    
    return df

if __name__ == "__main__":
    clean_housing_data()
