# Directory Structure Improvement

New organized layout for better maintainability and scaling.

## Current vs. New Structure

### Current (Flat)
```
db_2026/
├── main.py
├── scanning_service.py
├── scanners.py
├── models.py
├── config.py
├── streamlit_app.py
├── data_loader.py
├── ui_helpers.py
├── pages/
├── requirements.txt
├── check_env.py
├── example.py
├── README.md
├── ...docs
└── scans/
```

### New (Organized)
```
db_2026/
├── backend/                 # Scanner & services
│   ├── scanner/
│   │   ├── __init__.py
│   │   ├── main.py          # CLI entry point
│   │   ├── service.py       # scanning_service.py
│   │   ├── scanners.py
│   │   ├── models.py
│   │   └── config.py
│   ├── storage/             # Storage (file/GCP)
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract storage
│   │   ├── file_store.py    # JSON file storage
│   │   └── gcp_store.py     # GCP Firestore (future)
│   └── __init__.py
│
├── frontend/                # Streamlit dashboard
│   ├── streamlit_app.py
│   ├── data_loader.py
│   ├── ui_helpers.py
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── page_home.py
│   │   ├── page_results.py
│   │   ├── page_recommendations.py
│   │   ├── page_approve_builds.py
│   │   └── page_history.py
│   └── __init__.py
│
├── scripts/                 # Utilities
│   ├── check_env.py
│   ├── example.py
│   └── test_all.sh
│
├── config/                  # Configuration
│   ├── .streamlit/
│   │   └── config.toml
│   └── requirements.txt
│
├── docs/                    # Documentation
│   ├── README.md
│   ├── SETUP.md
│   ├── GETTING_STARTED.md
│   ├── DASHBOARD.md
│   ├── DASHBOARD_SUMMARY.md
│   ├── TESTING_GUIDE.md
│   └── ARCHITECTURE.md
│
├── output/                  # Generated files
│   ├── scans/               # Scan results (JSON)
│   └── build_approvals/     # Approvals (JSON)
│
├── .gitignore
└── pyproject.toml           # Python package config
```

## Migration Steps

### Step 1: Create Directories
```bash
mkdir -p backend/scanner backend/storage
mkdir -p frontend/pages
mkdir -p scripts
mkdir -p config/.streamlit
mkdir -p docs
mkdir -p output/{scans,build_approvals}
```

### Step 2: Move Backend Files
```bash
# Scanner module
mv scanning_service.py backend/scanner/service.py
mv scanners.py backend/scanner/
mv models.py backend/scanner/
mv config.py backend/scanner/
mv main.py backend/scanner/

# Storage module
mv gcp_integration.py backend/storage/gcp_store.py

# Create init files
touch backend/__init__.py
touch backend/scanner/__init__.py
touch backend/storage/__init__.py
```

### Step 3: Move Frontend Files
```bash
mv streamlit_app.py frontend/
mv data_loader.py frontend/
mv ui_helpers.py frontend/
mv pages/* frontend/pages/
rmdir pages
touch frontend/__init__.py
```

### Step 4: Move Config & Scripts
```bash
mv .streamlit/config.toml config/.streamlit/
mv requirements.txt config/
mv check_env.py scripts/
mv example.py scripts/
touch scripts/__init__.py
```

### Step 5: Move Documentation
```bash
mv README.md docs/
mv SETUP.md docs/
mv GETTING_STARTED.md docs/
mv DASHBOARD.md docs/
mv DASHBOARD_SUMMARY.md docs/
mv TESTING_GUIDE.md docs/
mv RESTRUCTURE.md docs/
```

### Step 6: Create pyproject.toml
```bash
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=65.0"]
build-backend = "setuptools.build_meta"

[project]
name = "container-security-scanner"
version = "0.1.0"
description = "Container image vulnerability scanner with Streamlit dashboard"
requires-python = ">=3.9"
dependencies = [
    "streamlit>=1.28.0",
    "plotly>=5.17.0",
    "pandas>=2.0.0",
    "google-cloud-firestore>=2.12.0",
    "google-cloud-container-analysis>=1.11.0",
]

[project.scripts]
scanner = "backend.scanner.main:main"
dashboard = "frontend.streamlit_app:main"
EOF
```

---

## Updated Commands After Migration

### Run Scanner
```bash
cd backend/scanner
python main.py --use-defaults
```

Or from root:
```bash
python -m backend.scanner.main --use-defaults
```

### Run Dashboard
```bash
streamlit run frontend/streamlit_app.py
```

### Check Environment
```bash
python scripts/check_env.py
```

### Run Tests
```bash
bash scripts/test_all.sh
```

### View Documentation
```bash
# README
cat docs/README.md

# Setup guide
cat docs/SETUP.md

# Getting started
cat docs/GETTING_STARTED.md
```

---

## Updated .gitignore

```
# Output directories
output/scans/
output/build_approvals/

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Virtual env
venv/
.venv/
ENV/

# IDE
.vscode/
.idea/
*.swp

# Environment
.env
.env.local
credentials.json

# OS
.DS_Store
```

---

## Benefits of New Structure

✅ **Clear separation** - Backend and frontend are distinct  
✅ **Scalable** - Easy to add Cloud Build, Cloud Run modules  
✅ **Maintainable** - Related files grouped together  
✅ **Professional** - Follows Python package conventions  
✅ **Modular** - Can import as package: `from backend.scanner import ...`  
✅ **Documentation** - All docs in one place  
✅ **Testing** - Scripts folder for utilities  

---

## Backwards Compatibility

Old import statements:
```python
from scanning_service import ScanningService
from data_loader import ScanDataLoader
```

New import statements:
```python
from backend.scanner.service import ScanningService
from frontend.data_loader import ScanDataLoader
```

Or use aliases in `__init__.py`:
```python
# backend/__init__.py
from backend.scanner.service import ScanningService
from backend.scanner.scanners import TrivyScanner

__all__ = ["ScanningService", "TrivyScanner"]
```

Then:
```python
from backend import ScanningService
```

---

## Future Additions

With this structure, easy to add:

```
backend/
├── cloud_build/     # Cloud Build integration
├── cloud_run/       # Cloud Run wrapper
├── k8s/             # Kubernetes integration
└── tests/           # Unit tests
```

---

## Summary

**Before:** Flat directory with 15+ files in root  
**After:** Organized into modules with clear responsibility

Run migration steps 1-6 above to restructure.

