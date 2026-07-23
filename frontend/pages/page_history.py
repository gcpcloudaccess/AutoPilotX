import streamlit as st
import pandas as pd
from typing import List, Dict
from teraformers.frontend.data_loader import ScanDataLoader
from teraformers.frontend.ui_helpers import render_scan_timeline

def render(scan_list: List[Dict], loader: ScanDataLoader):
    """Scan history and trends page"""
    st.title("📈 Scan History & Trends")

    if not scan_list:
        st.warning("No scan history available")
        return

    st.info(f"📊 {len(scan_list)} scans in history")

    # Timeline chart
    st.subheader("Vulnerability Trend")
    fig = render_scan_timeline(scan_list)
    st.plotly_chart(fig, use_container_width=True)

    # Detailed history table
    st.subheader("Scan Timeline")
    df = pd.DataFrame(scan_list)

    st.dataframe(
        df.style.format({
            "total_vulns": "{:,}",
            "critical": "{:,}",
            "images_count": "{:,}",
        }),
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": st.column_config.TextColumn("Date", width="medium"),
            "images_count": st.column_config.NumberColumn("Images", width="small"),
            "total_vulns": st.column_config.NumberColumn("Total Vulns", width="small"),
            "critical": st.column_config.NumberColumn("Critical", width="small"),
        },
    )

    # Stats
    st.divider()
    st.subheader("Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_scans = len(scan_list)
        st.metric("Total Scans", total_scans)

    with col2:
        avg_vulns = sum(s["total_vulns"] for s in scan_list) / len(scan_list)
        st.metric("Avg Vulns/Scan", f"{avg_vulns:.1f}")

    with col3:
        total_critical = sum(s["critical"] for s in scan_list)
        st.metric("Total Critical", total_critical)

    with col4:
        latest_images = scan_list[0]["images_count"] if scan_list else 0
        st.metric("Latest Scan Images", latest_images)

    # Trends
    st.divider()
    st.subheader("Trend Analysis")

    if len(scan_list) >= 2:
        latest = scan_list[0]
        previous = scan_list[1]

        col1, col2, col3 = st.columns(3)

        with col1:
            delta = latest["total_vulns"] - previous["total_vulns"]
            st.metric(
                "Total Vulnerabilities",
                latest["total_vulns"],
                delta=delta,
                delta_color="inverse"  # Green if negative (fewer vulns)
            )

        with col2:
            delta = latest["critical"] - previous["critical"]
            st.metric(
                "Critical Vulns",
                latest["critical"],
                delta=delta,
                delta_color="inverse"
            )

        with col3:
            delta = latest["images_count"] - previous["images_count"]
            st.metric(
                "Images Scanned",
                latest["images_count"],
                delta=delta
            )
    else:
        st.info("Need at least 2 scans to show trend comparison")

    # Export
    st.divider()
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Scan History",
        data=csv,
        file_name="scan_history.csv",
        mime="text/csv",
    )
