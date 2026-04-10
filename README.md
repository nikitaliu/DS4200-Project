# Massachusetts Housing Financial Analysis Dashboard

Single-page DS4200 project site exploring how property features, livability, affordability, and environmental risk shape Massachusetts home prices.

## What’s in this repo

- `index.html`: final GitHub Pages landing page
- `css/style.css`: site styling and design system
- `js/choropleth.js`: D3 choropleth using Massachusetts town boundaries
- `js/boxplot.js`: D3 box plot with outlier click details
- `js/utils.js`: shared formatters and name-normalization helpers
- `js/main.js`: summary-stat injection and page behavior
- `js/town-profile.js`: slide-in town profile panel with housing, demographics, and employment tabs
- `python/data_cleaning.py`: PRD-aligned cleaning and feature-engineering pipeline
- `python/fetch_census.py`: 2023 ACS town-level income, tenure, race, home value, age, and employment fetch
- `python/generate_altair.py`: Altair chart export script
- `python/generate_design_doc.py`: Word design document generator
- `data/ma_housing_cleaned.csv`: single source of truth for the dashboard
- `data/town_summary.csv`: town-level derivative used by the map and summaries
- `data/analysis_summary.json`: computed statewide metrics used by the webpage text
- `data/census_town_profiles.csv`: ACS-backed town profile data for the slide-in panel
- `data/ma_towns.topojson`: Massachusetts municipal boundaries for the choropleth
- `altair_charts/`: exported standalone Altair HTML charts
- `design_document.docx`: generated design rationale document
- `presentation_script.md`: 10-minute presentation script with speaker assignments

## Pipeline

1. `python/fetch_census.py`
2. `python/data_cleaning.py`
3. `python/generate_altair.py`
4. `python/generate_design_doc.py`

The cleaner:

- parses currency, score, and risk strings
- de-duplicates listing IDs
- filters non-Massachusetts listings
- removes extreme outliers above `$10M` or `15,000 sqft`
- extracts prior sale price and sale date from property history
- engineers price per sqft, home age, livability, environmental risk, appreciation, cap-rate proxy, gross rent multiplier, price-to-income ratio, and affordability index

The website:

- follows the v3 structure of Introduction, Research Questions, Methodology, Terminology, Findings, Future Directions, and References
- links technical terms back to a plain-English glossary
- opens a slide-in town profile when a user clicks a town on the choropleth map

## Quick start

```bash
source venv/bin/activate
python python/fetch_census.py
python python/data_cleaning.py
python python/generate_altair.py
python python/generate_design_doc.py
python -m http.server 8080
```

Open `http://localhost:8080`.

## Key outputs

- Cleaned listings: `8,726`
- Unique listing towns in the raw sample after cleanup: `428`
- Towns with ACS affordability coverage: `328`
- Statewide sample median listing price: `$725,000`

## Deployment

GitHub Pages target:

`https://nikitaliu.github.io/DS4200-Project/`

Enable Pages from the `main` branch root directory in repository settings.

## Notes

- The choropleth now uses a real Massachusetts town TopoJSON instead of the previous empty placeholder file.
- Cap rate is explicitly documented as a proxy based on estimated monthly payment, not observed rent.
- A few listing locations arrive as neighborhood or village names, so the pipeline includes normalization aliases to merge them into municipal boundaries and ACS towns where possible.
- Population was removed from the affordability visuals in v3 so the public-facing story stays focused on prices, income, and town context rather than point-size encoding.
