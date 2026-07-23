import streamlit as st
import logging
from datetime import datetime
from teraformers.frontend.data_loader import ScanDataLoader
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Container Security Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
@st.cache_resource
def get_data_loader():
    return ScanDataLoader(scan_dir="./scans")

loader = get_data_loader()

# Sidebar navigation
st.sidebar.title("🔐 Container Security")
page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Dashboard",
        "🔍 Vulnerability Results",
        "⬆️ Version Recommendations",
        "🏗️ Build Approval Queue",
        "📈 Scan History",
        "ℹ️ About",
    ],
)

# Load scan data
scan_list = loader.list_scans()
latest_scan = loader.load_latest_scan() if scan_list else None

with st.sidebar:
    st.divider()
    if scan_list:
        st.subheader("Recent Scans")
        selected_scan = st.selectbox(
            "Select scan",
            options=[s["timestamp"] for s in scan_list[:10]],
            format_func=lambda x: loader._format_timestamp(x),
            key="scan_selector",
        )
        if selected_scan:
            latest_scan = loader.load_scan_by_timestamp(selected_scan)
    else:
        st.warning("No scan data found. Run: `python main.py --use-defaults`")

    st.divider()
    st.caption("💡 Tip: Run scans from terminal and reload the page")

# Route to pages
if page == "📊 Dashboard":
    if latest_scan:
        from teraformers.frontend.pages import page_home
        page_home.render(latest_scan, loader)
    else:
        st.error("No scan data available")

elif page == "🔍 Vulnerability Results":
    if latest_scan:
        from teraformers.frontend.pages import page_results
        page_results.render(latest_scan, loader)
    else:
        st.error("No scan data available")

elif page == "⬆️ Version Recommendations":
    if latest_scan:
        from teraformers.frontend.pages import page_recommendations
        page_recommendations.render(latest_scan, loader)
    else:
        st.error("No scan data available")

elif page == "🏗️ Build Approval Queue":
    from teraformers.frontend.pages import page_approve_builds
    page_approve_builds.render(latest_scan, loader)

elif page == "📈 Scan History":
    if scan_list:
        from teraformers.frontend.pages import page_history
        page_history.render(scan_list, loader)
    else:
        st.error("No scan history available")

elif page == "ℹ️ About":
    st.title("About This Dashboard")
    st.markdown("""
    ### Container Image Security Scanner

    **Purpose:** Monitor and manage vulnerabilities in container images deployed to Kubernetes.

    **Features:**
    - 🔍 Scan images from Docker Hub & registries
    - 📊 Visualize vulnerability distribution
    - 📈 Track scan history & trends
    - ⬆️ Identify version upgrades
    - ✅ Approve patches for automated building

    **Tech Stack:**
    - Backend: Python + Trivy scanner
    - Frontend: Streamlit
    - Storage: JSON (Firestore ready)
    - CI/CD: Cloud Build (ready for integration)

    **Next Steps:**
    1. Run scans: `python main.py --use-defaults`
    2. View results in this dashboard
    3. Approve patches for automated remediation
    4. Connect to GCP for production deployment

    **Documentation:**
    - See `README.md` for setup
    - See `SETUP.md` for Trivy installation
    """)
