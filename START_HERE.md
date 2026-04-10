# Quick Start

## Local preview

```bash
cd /Users/mac/Documents/GitHub/DS4200-Project
source venv/bin/activate
python python/fetch_census.py
python python/data_cleaning.py
python python/generate_altair.py
python python/generate_design_doc.py
python -m http.server 8080
```

Open `http://localhost:8080`.

## Core outputs to check

- `data/ma_housing_cleaned.csv`
- `data/town_summary.csv`
- `data/analysis_summary.json`
- `data/census_town_profiles.csv`
- `data/ma_towns.topojson`
- `altair_charts/`
- `design_document.docx`
- `presentation_script.md`

## GitHub Pages target

`https://nikitaliu.github.io/DS4200-Project/`

Enable Pages from the `main` branch root directory in repository settings if it is not already active.
