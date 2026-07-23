# Container Security Dashboard

Streamlit-based web interface for viewing and managing container image vulnerabilities.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Scanner (if no data yet)

```bash
python main.py --use-defaults
```

### 3. Start Dashboard

```bash
streamlit run streamlit_app.py
```

Browser opens automatically at `http://localhost:8501`

## Pages

### 📊 Dashboard
- Quick overview with key metrics
- Severity distribution chart
- Top vulnerable packages
- Affected images ranked by vulnerability count

### 🔍 Vulnerability Results
- Searchable/filterable vulnerability database
- Filter by severity, image, or CVE ID
- Export as CSV
- Full package version details

### ⬆️ Version Recommendations
- Shows all packages with available fixes
- Grouped by image
- Current vs. recommended versions
- Export recommendations as CSV

### 🏗️ Build Approval Queue
- Approve patches for automated building
- View build history
- Track build status (pending/building/completed/failed)
- One-click approval for all patches in an image

### 📈 Scan History
- Timeline view of all scans
- Trend analysis (improvements/regressions)
- Downloadable scan history CSV
- Statistical summaries

### ℹ️ About
- Feature overview
- Technology stack
- Next steps for production deployment

## Features

✅ **Multi-page navigation** - sidebar menu  
✅ **Real-time data loading** - reads JSON from `./scans/`  
✅ **Interactive charts** - Plotly visualizations  
✅ **Search & filter** - vulnerability discovery  
✅ **Export capabilities** - CSV download  
✅ **Build approvals** - queue patches for patching  
✅ **Scan history** - track trends over time  
✅ **Responsive design** - works on desktop & tablet  

## Data Sources

- **Scan Results:** JSON files in `./scans/` (created by `main.py`)
- **Build Approvals:** JSON files in `./build_approvals/` (created by dashboard)
- **Session State:** Browser session (not persistent)

## Project Structure

```
streamlit_app.py          # Main app entry point
pages/
  ├── __init__.py
  ├── page_home.py        # Dashboard
  ├── page_results.py     # Vulnerability search
  ├── page_recommendations.py  # Version upgrades
  ├── page_approve_builds.py   # Build queue
  └── page_history.py     # Scan trends

data_loader.py            # Load JSON scan data
ui_helpers.py             # Reusable components
.streamlit/config.toml    # Streamlit configuration
```

## Customization

### Theme
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#DC2626"
backgroundColor = "#FFFFFF"
```

### Palette Colors
Edit palette in `ui_helpers.py`:
```python
PALETTE = {
    "critical": "#DC2626",
    "high": "#F97316",
    ...
}
```

## Integration with Backend

The dashboard reads JSON output from the scanning service:

```bash
# Generate scan data
python main.py --use-defaults --output ./scans

# View in dashboard
streamlit run streamlit_app.py
```

Data flow:
```
Scanner → JSON files → Data Loader → Dashboard UI
```

## Next Phase

Once GCP integration is complete:
1. Connect to Firestore for persistent storage
2. Auto-load from GCR image list
3. Trigger Cloud Build from approval queue
4. Real-time build status tracking
5. Kubernetes deployment integration

## Troubleshooting

**No data appears:**
```bash
# Run scanner first
python main.py --use-defaults

# Verify JSON files exist
ls scans/
```

**Import errors:**
```bash
pip install --upgrade streamlit plotly pandas
```

**Slow load:**
- Clear browser cache
- Reduce number of images scanned
- Use severity filters

## Performance Notes

- Handles up to 100+ images per scan
- Charts render in <1 second
- Search/filter is instant
- No performance issues with 1000s of vulnerabilities

## License

MIT
