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
    
    # Standardize column names (lowercase, replace spaces with underscores)
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Drop duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    print(f"Removed {initial_rows - len(df)} duplicate rows")
    
    # Clean price column (remove $ and commas, convert to numeric)
    if 'price' in df.columns:
        df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)
    
    # Clean sqft columns
    sqft_cols = [col for col in df.columns if 'sqft' in col or 'square' in col]
    for col in sqft_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Clean bedrooms and bathrooms
    if 'bedrooms' in df.columns:
        df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
    if 'bathrooms' in df.columns:
        df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce')
    
    # Standardize city names (title case, strip whitespace)
    if 'city' in df.columns:
        df['city'] = df['city'].str.strip().str.title()
    elif 'town' in df.columns:
        df = df.rename(columns={'town': 'city'})
        df['city'] = df['city'].str.strip().str.title()
    
    # Standardize property type
    if 'property_type' in df.columns or 'type' in df.columns:
        property_col = 'property_type' if 'property_type' in df.columns else 'type'
        df = df.rename(columns={property_col: 'propertyType'})
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
    
    # Remove rows with missing critical fields
    critical_cols = ['price', 'city']
    df = df.dropna(subset=[col for col in critical_cols if col in df.columns])
    
    # Filter out unrealistic values
    if 'price' in df.columns:
        df = df[(df['price'] >= 50000) & (df['price'] <= 10000000)]  # Reasonable price range
    
    if 'bedrooms' in df.columns:
        df = df[(df['bedrooms'] >= 0) & (df['bedrooms'] <= 20)]
    
    if 'bathrooms' in df.columns:
        df = df[(df['bathrooms'] >= 0) & (df['bathrooms'] <= 15)]
    
    # Add derived columns
    sqft_col = next((col for col in df.columns if 'sqft' in col), None)
    if sqft_col and 'price' in df.columns:
        df['pricePerSqft'] = df['price'] / df[sqft_col]
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
