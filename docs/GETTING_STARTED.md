# Getting Started - Complete Guide

End-to-end setup from scanning to dashboard visualization.

## Prerequisites

- Python 3.9+
- Docker or Podman
- Trivy scanner

## Step 1: Check Environment

```bash
python check_env.py
```

Output should show:
```
✓ Docker is installed
✓ Trivy is installed
✓ google-cloud-firestore is installed
```

If Trivy is missing:
```bash
# macOS
brew install trivy

# Linux
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# Windows
choco install trivy
```

## Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Packages installed:
- `streamlit` - Web dashboard
- `plotly` - Interactive charts
- `pandas` - Data processing
- `google-cloud-firestore` - Future GCP integration
- `python-docker` - Docker interaction

## Step 3: Run Your First Scan

### Option A: Scan Test Images (Recommended)
```bash
python main.py --use-defaults
```

This scans public images:
- `alpine:latest`
- `ubuntu:22.04`
- `nginx:latest`
- `python:3.11-slim`
- `node:20-alpine`

### Option B: Scan Specific Images
```bash
python main.py --images myapp:v1.0 api:v2.1 worker:latest
```

### Option C: Run with Filters
```bash
# Only show HIGH and CRITICAL vulns
python main.py --use-defaults --severity HIGH

# Save to custom directory
python main.py --use-defaults --output ./reports

# Report only (don't save JSON)
python main.py --use-defaults --report-only
```

**Expected output:**
```
╔════════════════════════════════════════════════╗
║         VULNERABILITY SCAN REPORT              ║
╚════════════════════════════════════════════════╝

📊 SUMMARY
──────────────────────────────────────────────────
Images Scanned:        5
Total Vulnerabilities: 24
  🔴 Critical:        2
  🟠 High:            8
  🟡 Medium:          14
Affected Images:       4

✅ Results saved to: scans/scan_results_20240115_103045.json
```

## Step 4: View Results in Dashboard

```bash
streamlit run streamlit_app.py
```

Browser opens at: **http://localhost:8501**

### What You'll See

**📊 Dashboard Tab:**
- 5 key metrics (images, vulns, critical count)
- Severity distribution chart
- Top vulnerable packages
- Affected images ranked

**🔍 Vulnerability Results Tab:**
- Searchable table of all vulnerabilities
- Filter by severity, image, or CVE ID
- Download as CSV

**⬆️ Version Recommendations Tab:**
- Packages with available fixes
- Current vs. recommended versions
- Show by image

**🏗️ Build Approval Queue Tab:**
- Approve patches for automated building
- View approval history
- (Real building in GCP phase)

**📈 Scan History Tab:**
- Timeline of all scans
- Trend charts
- Vulnerability reduction tracking

## Step 5: Use the Dashboard

### Search Vulnerabilities
1. Go to "Vulnerability Results"
2. Filter by:
   - Severity (CRITICAL, HIGH, MEDIUM, LOW)
   - Image name
   - CVE ID or package name

### Review Recommended Fixes
1. Go to "Version Recommendations"
2. See what packages can be upgraded
3. Current version → Fixed version

### Approve Patches
1. Go to "Build Approval Queue"
2. Click "✅ Approve All" for images to patch
3. Approval saved (ready for Cloud Build in GCP phase)

### Track Trends
1. Go to "Scan History"
2. See vulnerability trends over time
3. Compare scans to track improvements

## Step 6: Next Steps (When Ready)

### Generate More Scan Data
```bash
# Scan your own images
python main.py --images gcr.io/myproject/myapp:v1.0

# Run periodically
python main.py --use-defaults --output ./scans
```

### Integrate with GCP (Tomorrow)
- Connect to Google Container Registry (GCR)
- Store results in Cloud Firestore
- Auto-trigger Cloud Build for patches
- Deploy via Kubernetes

### Set Up Automation
- Cloud Scheduler (run scans daily)
- Cloud Run (host scanner service)
- Cloud Build (patch & rebuild images)

## Troubleshooting

### "No scan data available"
```bash
# Generate data first
python main.py --use-defaults

# Verify JSON files
ls -la scans/
```

### "Trivy not found"
```bash
trivy version

# If not installed, see Step 1
```

### "Docker daemon not running"
```bash
docker ps

# Start Docker Desktop or daemon
```

### Dashboard won't load
```bash
# Check port 8501 is free
netstat -an | grep 8501

# Use different port
streamlit run streamlit_app.py --server.port 8502
```

### Slow scanning
- Scan fewer images at once
- Trivy caches results (subsequent runs faster)
- Use `--severity` to filter

## Project Structure

```
db_2026/
├── main.py                    # Scanner CLI
├── scanning_service.py        # Core scanner
├── scanners.py               # Trivy implementation
├── models.py                 # Data models
├── config.py                 # Configuration
│
├── streamlit_app.py          # Dashboard entry
├── data_loader.py            # Load JSON
├── ui_helpers.py             # UI components
├── pages/                    # Dashboard pages
│   ├── page_home.py
│   ├── page_results.py
│   ├── page_recommendations.py
│   ├── page_approve_builds.py
│   └── page_history.py
│
├── scans/                    # Scan results (JSON)
├── build_approvals/          # Approved builds
│
├── requirements.txt
├── README.md
├── SETUP.md
├── DASHBOARD.md
└── GETTING_STARTED.md
```

## Common Workflows

### "I want to scan my own images"
```bash
python main.py --images image1:tag1 image2:tag2 image3:tag3
streamlit run streamlit_app.py
```

### "I want to see only critical vulns"
```bash
python main.py --use-defaults --severity CRITICAL --report-only
```

### "I want to export vulnerabilities"
1. Run scanner: `python main.py --use-defaults`
2. Open dashboard: `streamlit run streamlit_app.py`
3. Go to "Vulnerability Results"
4. Click "📥 Download as CSV"

### "I want to approve patches"
1. Run scanner: `python main.py --use-defaults`
2. Open dashboard: `streamlit run streamlit_app.py`
3. Go to "Build Approval Queue"
4. Click "✅ Approve All" for each image
5. Wait for GCP integration to auto-build

## Performance Tips

- ✅ Scan time: 30-60 seconds per image
- ✅ Dashboard loads instantly
- ✅ Charts render in <1 second
- ✅ No lag with 1000+ vulnerabilities

To speed up:
- Trivy caches images (cold start slower)
- Subsequent scans are faster
- Reduce number of images
- Use severity filters

## What's Next?

**Today:**
- ✅ Scanner backend (done)
- ✅ Dashboard (done)
- 🔨 Cloud Build automation (next)
- 🔨 Cloud Run wrapper (next)

**Tomorrow:**
- GCP Integration
  - Firestore for results
  - GCR image list
  - Cloud Build trigger
  - Cloud Scheduler automation

## Support

- See `README.md` for architecture
- See `SETUP.md` for scanner details
- See `DASHBOARD.md` for dashboard features
- See `DASHBOARD_SUMMARY.md` for implementation details

---

**You're all set!** Run your first scan now:
```bash
python main.py --use-defaults
streamlit run streamlit_app.py
```
