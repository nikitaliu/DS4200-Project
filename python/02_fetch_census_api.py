"""
Step 2: Fetch Census API Data
Retrieves demographic and income data for Massachusetts counties and towns.
"""

import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from .env
API_KEY = os.getenv("CENSUS_API_KEY")

if not API_KEY:
    raise ValueError("CENSUS_API_KEY not found in .env file. Please add your Census API key.")

# API endpoints
BASE_URL = "https://api.census.gov/data"
YEAR = "2022"  # Most recent ACS 5-year estimates
ACS_ENDPOINT = f"{BASE_URL}/{YEAR}/acs/acs5"

# Massachusetts FIPS code
MA_FIPS = "25"

# Output path
OUTPUT_PATH = 'data/processed/census_data.csv'

def fetch_county_data():
    """Fetch county-level demographic data for Massachusetts."""
    
    print("Fetching county-level data from Census API...")
    
    # Variables to fetch
    # B19013_001E: Median household income
    # B01003_001E: Total population
    # B25077_001E: Median home value
    variables = [
        "NAME",
        "B19013_001E",  # Median household income
        "B01003_001E",  # Total population
        "B25077_001E"   # Median home value
    ]
    
    params = {
        "get": ",".join(variables),
        "for": "county:*",
        "in": f"state:{MA_FIPS}",
        "key": API_KEY
    }
    
    response = requests.get(ACS_ENDPOINT, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching county data: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    
    # Convert to DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    
    # Rename columns
    df = df.rename(columns={
        'NAME': 'countyName',
        'B19013_001E': 'medianIncome',
        'B01003_001E': 'population',
        'B25077_001E': 'medianHomeValue'
    })
    
    # Convert to numeric
    df['medianIncome'] = pd.to_numeric(df['medianIncome'], errors='coerce')
    df['population'] = pd.to_numeric(df['population'], errors='coerce')
    df['medianHomeValue'] = pd.to_numeric(df['medianHomeValue'], errors='coerce')
    
    # Clean county names (remove ', Massachusetts' and ' County')
    df['countyName'] = df['countyName'].str.replace(', Massachusetts', '').str.replace(' County', '')
    
    print(f"Fetched data for {len(df)} counties")
    
    return df

def fetch_town_data():
    """Fetch town/city-level demographic data for Massachusetts."""
    
    print("\nFetching town-level data from Census API...")
    
    # Variables to fetch
    variables = [
        "NAME",
        "B19013_001E",  # Median household income
        "B01003_001E"   # Total population
    ]
    
    params = {
        "get": ",".join(variables),
        "for": "county subdivision:*",
        "in": f"state:{MA_FIPS}",
        "key": API_KEY
    }
    
    response = requests.get(ACS_ENDPOINT, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching town data: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    
    # Convert to DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    
    # Rename columns
    df = df.rename(columns={
        'NAME': 'townName',
        'B19013_001E': 'medianIncome',
        'B01003_001E': 'population'
    })
    
    # Convert to numeric
    df['medianIncome'] = pd.to_numeric(df['medianIncome'], errors='coerce')
    df['population'] = pd.to_numeric(df['population'], errors='coerce')
    
    # Clean town names
    # Format: "Town name town/city, County name, Massachusetts"
    df['townName'] = df['townName'].str.replace(', Massachusetts', '')
    df['townName'] = df['townName'].str.split(',').str[0]  # Get first part before comma
    
    # Remove common suffixes
    suffixes = [' town', ' Town', ' city', ' City', ' CDP']
    for suffix in suffixes:
        df['townName'] = df['townName'].str.replace(suffix, '')
    
    df['townName'] = df['townName'].str.strip()
    
    # Remove duplicates (keep first occurrence)
    df = df.drop_duplicates(subset=['townName'], keep='first')
    
    print(f"Fetched data for {len(df)} towns/cities")
    
    return df

def main():
    """Main function to fetch and combine census data."""
    
    # Fetch county data
    county_df = fetch_county_data()
    
    # Fetch town data
    town_df = fetch_town_data()
    
    if county_df is not None and town_df is not None:
        # Add a 'level' column to distinguish
        county_df['level'] = 'county'
        town_df['level'] = 'town'
        
        # For merging with housing data, we'll primarily use town data
        # Save town data as the main census dataset
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        town_df.to_csv(OUTPUT_PATH, index=False)
        
        print(f"\nCensus data saved to: {OUTPUT_PATH}")
        print(f"\nTown data summary:")
        print(town_df.describe())
        
        # Also save county data separately for reference
        county_output = OUTPUT_PATH.replace('census_data.csv', 'census_county_data.csv')
        county_df.to_csv(county_output, index=False)
        print(f"\nCounty data also saved to: {county_output}")
        
        return town_df
    else:
        print("Failed to fetch census data")
        return None

if __name__ == "__main__":
    main()
