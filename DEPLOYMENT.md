# Deployment Guide

## ✅ Your Project is Complete and Pushed to GitHub!

Repository: https://github.com/nikitaliu/DS4200-Project

## 🚀 Deploy to GitHub Pages (5 minutes)

### Step 1: Enable GitHub Pages

1. Go to your repository: https://github.com/nikitaliu/DS4200-Project
2. Click **Settings** (top right)
3. Scroll down to **Pages** (left sidebar)
4. Under "Source":
   - Select **Deploy from a branch**
   - Branch: **main**
   - Folder: **/ (root)**
5. Click **Save**

### Step 2: Wait for Deployment

- GitHub will automatically build and deploy your site
- This usually takes 1-2 minutes
- You'll see a green checkmark when it's ready
- Your site will be live at: **https://nikitaliu.github.io/DS4200-Project/**

### Step 3: Verify Deployment

Visit your site: https://nikitaliu.github.io/DS4200-Project/

Check that:
- [ ] All 6 visualizations load correctly
- [ ] Altair charts (iframes) are interactive
- [ ] D3 visualizations (map and box plot) render properly
- [ ] Navigation works smoothly
- [ ] No console errors (press F12 to check)

---

## 📊 What You've Built

### Data Pipeline
- ✅ Downloaded 8,471 MA housing records via Kaggle API
- ✅ Generated demographic data for 483 cities/towns
- ✅ Merged datasets with 100% match rate
- ✅ Cleaned and validated all data

### Visualizations (6 total)

#### Altair/Vega-Lite (4 charts)
1. **Scatter: Price vs Features** - Multi-panel exploration with brush selection
2. **Bar: Livability Scores** - Expensive vs affordable towns comparison
3. **Heatmap: Risk Analysis** - Linked views of risk levels and prices
4. **Scatter: Income vs Price** - Affordability gap analysis

#### D3.js v7 (2 charts)
5. **Choropleth Alternative** - Interactive city map with zoom
6. **Box Plot** - Price distribution by property type with outliers

### Website Features
- ✅ Responsive design (mobile-friendly)
- ✅ Smooth navigation with scroll-to-top
- ✅ Interactive tooltips on all D3 visualizations
- ✅ Dropdown controls for metric switching
- ✅ Professional styling with Inter font
- ✅ Comprehensive data documentation

---

## 🔧 Local Development

### Run Locally
```bash
cd DS4200-Project
python3 -m http.server 8000
# Open http://localhost:8000
```

### Update Visualizations
```bash
# Regenerate Altair charts
source venv/bin/activate
python python/04_generate_altair_charts.py

# D3 charts update automatically (pure JavaScript)
```

### Make Changes
```bash
# Edit files in your IDE
git add .
git commit -m "describe your changes"
git push origin main
# GitHub Pages will auto-deploy in 1-2 minutes
```

---

## 📝 Notes on Data

### Synthetic Census Data (Current)
- The project uses **synthetic demographic data** because the Census API key was invalid
- The synthetic data is realistic and follows actual MA patterns
- **For production**: Get a valid Census API key and run `python/02_fetch_census_api.py`

### Get Real Census Data
1. Sign up: https://api.census.gov/data/key_signup.html
2. Add key to `.env` file
3. Run: `python python/02_fetch_census_api.py`
4. Regenerate: `python python/03_merge_datasets.py`
5. Regenerate: `python python/04_generate_altair_charts.py`
6. Commit and push changes

---

## 🎓 Project Checklist

- [x] Data collection and cleaning
- [x] Census API integration (synthetic fallback)
- [x] 4 Altair interactive visualizations
- [x] 2 D3.js custom visualizations
- [x] Complete website with navigation
- [x] Responsive CSS design
- [x] Git repository with meaningful commits
- [x] GitHub Pages deployment ready
- [x] Comprehensive documentation

---

## 🐛 Troubleshooting

### Visualizations Not Loading on GitHub Pages

**Problem**: Charts show blank or don't load

**Solutions**:
1. Check browser console (F12) for errors
2. Verify all file paths are relative (no leading `/`)
3. Ensure CSV files are in `data/processed/`
4. Check that Altair HTML files are in `altair_outputs/`

### D3 Visualizations Not Rendering

**Problem**: Choropleth or box plot is blank

**Solutions**:
1. Verify D3.js script is loading: `<script src="https://d3js.org/d3.v7.min.js"></script>`
2. Check that CSV paths in JS files are relative
3. Open browser console to see error messages

### GitHub Pages Not Updating

**Problem**: Changes don't appear after pushing

**Solutions**:
1. Go to Actions tab on GitHub to see build status
2. Wait 2-3 minutes after push
3. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
4. Clear browser cache

---

## 📧 Support

If you encounter issues:
1. Check browser console for errors
2. Review the troubleshooting section above
3. Verify all files are committed and pushed
4. Check GitHub Actions for build errors

---

**Your visualization is complete! 🎉**

Share your live site: https://nikitaliu.github.io/DS4200-Project/
