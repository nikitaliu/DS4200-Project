# Massachusetts Housing Visualization Project

An interactive data visualization exploring housing costs, livability, and demographic patterns across Massachusetts.

## 🎯 Project Overview

This project combines housing market data with Census demographic information to answer:
- Where is housing most expensive in Massachusetts?
- What features drive property prices?
- Does livability cost extra?
- Are affordable areas riskier?
- How do income and housing prices relate?

## 🛠️ Tech Stack

- **Data Processing**: Python (pandas, requests, altair)
- **Visualization**: D3.js v7, Altair/Vega-Lite
- **Data Sources**: Kaggle MA Housing Data, US Census Bureau API

## 📁 Project Structure

```
DS4200-Project/
├── data/
│   ├── raw/              # Original data files
│   └── processed/        # Cleaned and merged data
├── python/
│   ├── 01_clean_kaggle_data.py      # Clean housing data
│   ├── 02_fetch_census_api.py       # Fetch Census API data
│   ├── 03_merge_datasets.py         # Merge datasets
│   └── 04_generate_altair_charts.py # Generate Altair visualizations
├── js/
│   ├── choropleth.js    # D3 map visualization
│   ├── boxplot.js       # D3 box plot
│   └── main.js          # Main JavaScript coordinator
├── css/
│   └── style.css        # Styles
├── altair_outputs/      # Generated Altair HTML charts
└── index.html           # Main webpage

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/DS4200-Project.git
cd DS4200-Project
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r python/requirements.txt
```

### 3. Get Census API Key

1. Sign up for a free API key at: https://api.census.gov/data/key_signup.html
2. You'll receive the key via email in a few minutes
3. Add it to your `.env` file (already created with your key)

### 4. Download Data

**Kaggle Housing Data:**
1. Go to: https://www.kaggle.com/datasets/vraj105/massachusetts-housing-data
2. Download the CSV file
3. Save it as: `data/raw/ma_housing_raw.csv`

**MA Town Boundaries (TopoJSON):**
1. Download: https://www2.census.gov/geo/tiger/TIGER2022/COUSUB/tl_2022_25_cousub.zip
2. Extract the shapefile
3. Convert to TopoJSON using mapshaper.org or CLI
4. Save as: `data/processed/ma_towns.topojson`

### 5. Run Data Pipeline

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Run scripts in order
python python/01_clean_kaggle_data.py
python python/02_fetch_census_api.py
python python/03_merge_datasets.py
python python/04_generate_altair_charts.py  # Coming next
```

### 6. View the Project

```bash
# Start local server
python -m http.server 8000

# Open in browser
# http://localhost:8000
```

## 📊 Visualizations

1. **Choropleth Map** - Interactive map showing price patterns across MA towns
2. **Price vs Features Scatter** - Explore relationships between property features and price
3. **Livability Bar Chart** - Compare walkability, bikeability, and transit scores
4. **Box Plot** - Price distribution by property type
5. **Risk Heatmap** - Examine risk levels and their relationship to prices
6. **Income vs Price Scatter** - Analyze the affordability gap

## 📚 Data Sources

- **Kaggle**: Massachusetts Housing Data (vraj105/massachusetts-housing-data)
- **US Census Bureau**: American Community Survey 5-Year Estimates (2022)
  - Median household income
  - Population data
  - Town-level demographics
- **Census TIGER/Line**: Massachusetts geographic boundaries

## 🤝 Contributing

This is a student project for DS4200. For questions or suggestions, please open an issue.

## 📄 License

MIT License - Feel free to use this project for learning purposes.

## ✨ Acknowledgments

- Data: Kaggle community & US Census Bureau
- Course: DS4200 Information Visualization
- Tools: D3.js, Altair, pandas

---

**Status**: 🚧 In Development

**Last Updated**: February 15, 2026
