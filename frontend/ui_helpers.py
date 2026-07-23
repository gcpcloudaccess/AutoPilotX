import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
import pandas as pd

# Palette - reference: references/palette.md (swap these for your brand)
PALETTE = {
    "critical": "#DC2626",  # Red
    "high": "#F97316",      # Orange
    "medium": "#FBBF24",    # Amber
    "low": "#4ADE80",       # Green
    "neutral": "#6B7280",   # Gray
    "surface_light": "#F9FAFB",
    "surface_dark": "#111827",
}

def metric_card(label: str, value: str, color: str = None, delta: str = None):
    """Display a metric card"""
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.metric(label, value, delta, label_visibility="collapsed")
        if color:
            st.markdown(f"<div style='background: {color}; height: 2px; border-radius: 1px;'></div>",
                       unsafe_allow_html=True)

def severity_badge(severity: str) -> str:
    """Return colored badge for severity"""
    colors = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢",
    }
    return colors.get(severity, "⚪")

def render_severity_bar_chart(data: Dict[str, int]) -> go.Figure:
    """Create severity distribution bar chart"""
    df = pd.DataFrame([
        {"severity": "CRITICAL", "count": data.get("CRITICAL", 0)},
        {"severity": "HIGH", "count": data.get("HIGH", 0)},
        {"severity": "MEDIUM", "count": data.get("MEDIUM", 0)},
        {"severity": "LOW", "count": data.get("LOW", 0)},
    ])

    color_map = {
        "CRITICAL": PALETTE["critical"],
        "HIGH": PALETTE["high"],
        "MEDIUM": PALETTE["medium"],
        "LOW": PALETTE["low"],
    }

    fig = px.bar(
        df,
        x="severity",
        y="count",
        color="severity",
        color_discrete_map=color_map,
        labels={"count": "Vulnerabilities", "severity": "Severity"},
        text="count",
    )

    fig.update_traces(textposition="outside", textfont=dict(size=12))
    fig.update_layout(
        showlegend=False,
        hovermode="x unified",
        height=350,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis_title="",
        yaxis_title="Count",
    )
    return fig

def render_affected_images_chart(scans: List) -> go.Figure:
    """Create affected images bar chart"""
    data = [
        {"image": f"{s.image}:{s.tag}", "vulns": s.total_vulns}
        for s in scans if s.total_vulns > 0
    ]
    data = sorted(data, key=lambda x: x["vulns"], reverse=True)[:10]

    if not data:
        st.info("No vulnerabilities found")
        return None

    df = pd.DataFrame(data)
    fig = px.bar(
        df,
        y="image",
        x="vulns",
        orientation="h",
        labels={"vulns": "Vulnerabilities", "image": "Image"},
        color="vulns",
        color_continuous_scale=[PALETTE["low"], PALETTE["critical"]],
    )

    fig.update_layout(
        height=300 + (len(data) * 20),
        margin=dict(l=200, r=20, t=20, b=40),
        xaxis_title="Number of Vulnerabilities",
        yaxis_title="",
        hovermode="y unified",
    )
    return fig

def render_packages_table(packages: List[Dict]):
    """Display top vulnerable packages as table"""
    df = pd.DataFrame(packages)
    if df.empty:
        st.info("No vulnerable packages found")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "package": st.column_config.TextColumn("Package", width="large"),
            "count": st.column_config.NumberColumn("Total", width="small"),
            "critical": st.column_config.NumberColumn("Critical", width="small"),
            "high": st.column_config.NumberColumn("High", width="small"),
        },
    )

def render_vulnerabilities_table(vulns: List[Dict]):
    """Display vulnerabilities with details"""
    if not vulns:
        st.info("No vulnerabilities found")
        return

    df = pd.DataFrame(vulns)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "image": st.column_config.TextColumn("Image", width="large"),
            "vuln_id": st.column_config.TextColumn("CVE ID", width="medium"),
            "severity": st.column_config.TextColumn("Severity", width="small"),
            "package": st.column_config.TextColumn("Package", width="medium"),
            "current_version": st.column_config.TextColumn("Current", width="small"),
            "fixed_version": st.column_config.TextColumn("Fixed", width="small"),
        },
    )

def render_scan_timeline(scan_list: List[Dict]):
    """Display scan history timeline"""
    if not scan_list:
        st.info("No scan history available")
        return

    df = pd.DataFrame(scan_list)
    fig = px.bar(
        df,
        x="date",
        y="total_vulns",
        color="critical",
        hover_data=["images_count", "critical"],
        labels={
            "total_vulns": "Total Vulnerabilities",
            "critical": "Critical Count",
            "date": "Scan Date",
        },
        color_continuous_scale=[PALETTE["low"], PALETTE["critical"]],
    )

    fig.update_layout(
        height=400,
        hovermode="x unified",
        xaxis_title="",
        yaxis_title="Vulnerabilities",
        margin=dict(l=40, r=20, t=20, b=40),
    )
    return fig

def render_fixable_summary(fixable: List[Dict]) -> go.Figure:
    """Show fixable vulnerabilities summary"""
    if not fixable:
        return None

    df = pd.DataFrame(fixable)
    severity_counts = df["severity"].value_counts().to_dict()

    fig = go.Figure(data=[
        go.Pie(
            labels=list(severity_counts.keys()),
            values=list(severity_counts.values()),
            marker=dict(colors=[
                PALETTE.get(sev.lower(), PALETTE["neutral"])
                for sev in severity_counts.keys()
            ]),
        )
    ])

    fig.update_layout(
        title="Fixable Vulnerabilities by Severity",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig

def status_pill(status: str, label: str = None):
    """Display status pill"""
    colors = {
        "success": "#10B981",
        "warning": "#F59E0B",
        "error": "#EF4444",
        "info": "#3B82F6",
    }
    color = colors.get(status, PALETTE["neutral"])
    display_label = label or status.upper()
    st.markdown(
        f"<span style='background: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;'>{display_label}</span>",
        unsafe_allow_html=True
    )
