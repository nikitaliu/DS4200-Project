# Demo Folder - Python Visualizations

This folder contains the Python demonstration code for the DS4200 project.

## 📁 Contents

### Python Files

1. **`visualization_demo.py`** (488 lines)
   - Main demonstration file with comprehensive docstrings
   - Contains two visualization functions
   - Professional documentation suitable for academic presentation
   - No automatic file output (clean demo mode)

2. **`generate_visualizations.py`** (28 lines)
   - Helper script to generate and save HTML outputs
   - Imports functions from visualization_demo.py
   - Saves visualizations as standalone HTML files

### Generated Visualizations

3. **`income_vs_price.html`** (~20 KB)
   - Interactive scatter plot: Income vs Housing Price
   - Shows affordability gap across Massachusetts
   - Multi-dimensional encoding (x, y, size, color)
   - Pan and zoom enabled

4. **`risk_analysis.html`** (~25 KB)
   - Interactive linked views: Risk heatmap + scatter plot
   - Shows environmental risks vs housing prices
   - Click selection links both visualizations
   - Explores 5 risk types across 30 most expensive towns

---

## 🚀 Usage

### Option 1: Run Demo (No File Output)
```bash
cd demo
python visualization_demo.py
```
This displays the processing steps and statistics without creating files.

### Option 2: Generate HTML Files
```bash
cd demo
python generate_visualizations.py
```
This creates/updates the HTML visualization files.

### Option 3: Open Existing HTML
Simply open `income_vs_price.html` or `risk_analysis.html` in a web browser.

---

## 📊 Visualizations

### Visualization 1: Income vs Housing Price
- **Data**: 81 Massachusetts towns (with complete data)
- **Encoding**:
  - X-axis: Median household income
  - Y-axis: Average listing price
  - Size: Population
  - Color: Livability score (walk/bike/transit)
- **Interaction**: Pan, zoom, tooltip on hover

### Visualization 2: Environmental Risk Analysis
- **Data**: Top 30 most expensive towns, 5 risk types
- **Left View**: Heatmap (town × risk type)
- **Right View**: Scatter plot (avg risk vs price)
- **Interaction**: Click to link selection across views

---

## 🎯 For Academic Presentation

**Recommend showing**: `visualization_demo.py`
- Professional docstrings explain design rationale
- Clear data transformation steps
- Well-commented code structure
- Academic-appropriate documentation

**Generated files**: For demonstration purposes only
- HTML files can be opened in browser during presentation
- Show interactive features live

---

## 📦 Data Source

Both visualizations use: `../data/processed/merged_data.csv`
- 8,471 property listings
- 483 Massachusetts cities/towns
- Merged housing + Census demographic data

---

## 🛠️ Requirements

- Python 3.11+
- pandas >= 2.0
- altair >= 5.0
- See `../python/requirements.txt` for full list

---

**Author**: DS4200 Student  
**Date**: February 2026  
**Course**: Information Visualization
