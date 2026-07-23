import streamlit as st
import pandas as pd
from typing import List
from teraformers.backend.scanner.models import ScanResult
from teraformers.frontend.data_loader import ScanDataLoader
from teraformers.frontend.ui_helpers import (
    metric_card, severity_badge, render_severity_bar_chart,
    render_affected_images_chart, render_packages_table
)

def render(scans: List[ScanResult], loader: ScanDataLoader):
    """Dashboard home page"""
    st.title("📊 Security Dashboard")

    # Get summary stats
    summary = loader.get_scan_summary(scans)

    if not summary:
        st.info("No scan data available")
        return

    # Top metrics
    st.subheader("Overview")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Images Scanned", summary["total_images"])

    with col2:
        st.metric("Affected Images", summary["images_with_vulns"])

    with col3:
        st.metric("🔴 Critical", summary["critical"], delta=None)

    with col4:
        st.metric("🟠 High", summary["high"])

    with col5:
        st.metric("Total Vulns", summary["total_vulnerabilities"])

    st.divider()

    # Charts
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Severity Distribution")
        severity_data = loader.get_vulnerabilities_by_severity(scans)
        fig = render_severity_bar_chart(severity_data)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Vulnerable Packages")
        packages = loader.get_top_packages_by_vulns(scans, limit=5)
        render_packages_table(packages)

    st.divider()

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader("Affected Images (Top 10)")
        fig = render_affected_images_chart(scans)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Quick Stats")
        with st.container(border=True):
            st.write(f"**Avg Vulns/Image:** {summary['avg_vulns_per_image']}")
            critical_pct = (
                (summary['critical'] / summary['total_vulnerabilities'] * 100)
                if summary['total_vulnerabilities'] > 0 else 0
            )
            st.write(f"**Critical %:** {critical_pct:.1f}%")

            if summary["critical"] > 0:
                st.warning(f"⚠️ {summary['critical']} critical vulnerabilities require immediate attention")
            elif summary["high"] > 0:
                st.info(f"ℹ️ {summary['high']} high-severity vulnerabilities to review")
            else:
                st.success("✅ No critical or high-severity vulnerabilities")
