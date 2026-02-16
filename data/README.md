# Data Directory

## Structure

- `raw/` - Original data files from Kaggle and Census
- `processed/` - Cleaned and merged datasets ready for visualization

## Data Sources

1. **Kaggle**: Massachusetts Housing Data
   - URL: https://www.kaggle.com/datasets/vraj105/massachusetts-housing-data
   - File: `raw/ma_housing_raw.csv`

2. **US Census Bureau**: 
   - API: https://api.census.gov/data.html
   - Demographic and income data for MA counties and towns

3. **Census TIGER/Line**: Massachusetts Town Boundaries
   - TopoJSON file for D3 choropleth map
   - File: `processed/ma_towns.topojson`

## Processing Pipeline

1. `01_clean_kaggle_data.py` → `processed/housing_cleaned.csv`
2. `02_fetch_census_api.py` → `processed/census_data.csv`
3. `03_merge_datasets.py` → `processed/merged_data.csv`
