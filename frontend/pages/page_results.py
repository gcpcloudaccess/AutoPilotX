import streamlit as st
import pandas as pd
from typing import List
from teraformers.backend.scanner.models import ScanResult, Severity
from teraformers.frontend.data_loader import ScanDataLoader
from teraformers.frontend.ui_helpers import severity_badge

def render(scans: List[ScanResult], loader: ScanDataLoader):
    """Vulnerability results page"""
    st.title("🔍 Vulnerability Results")

    # Filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_severity = st.multiselect(
            "Severity",
            options=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            default=["CRITICAL", "HIGH"],
        )

    with col2:
        selected_image = st.multiselect(
            "Image",
            options=sorted(set(f"{s.image}:{s.tag}" for s in scans)),
            default=None,
        )

    with col3:
        search_term = st.text_input("Search (CVE, package)", placeholder="CVE-2024-1234")

    # Build filtered list
    all_vulns = []
    for scan in scans:
        # Filter by image
        if selected_image and f"{scan.image}:{scan.tag}" not in selected_image:
            continue

        for vuln in scan.vulnerabilities:
            # Filter by severity
            if vuln.severity.value not in selected_severity:
                continue

            # Filter by search term
            if search_term:
                if not (search_term.lower() in vuln.id.lower() or
                        search_term.lower() in vuln.package.lower()):
                    continue

            all_vulns.append({
                "image": f"{scan.image}:{scan.tag}",
                "cve_id": vuln.id,
                "severity": vuln.severity.value,
                "package": vuln.package,
                "current_version": vuln.installed_version,
                "fixed_version": vuln.fixed_version or "—",
                "description": vuln.description[:100] + ("..." if len(vuln.description) > 100 else ""),
            })

    # Display results
    st.divider()
    if all_vulns:
        st.info(f"📋 Found {len(all_vulns)} vulnerability records")

        df = pd.DataFrame(all_vulns)

        # Color by severity
        def severity_color(val):
            colors = {
                "CRITICAL": "background-color: #FEE2E2",
                "HIGH": "background-color: #FEF3C7",
                "MEDIUM": "background-color: #FEF08A",
                "LOW": "background-color: #DCFCE7",
            }
            return [colors.get(val, "")] * len(df.columns)

        st.dataframe(
            df.style.apply(lambda row: severity_color(row["severity"]), axis=1),
            use_container_width=True,
            hide_index=True,
            column_config={
                "image": st.column_config.TextColumn("Image", width="medium"),
                "severity": st.column_config.TextColumn("Severity", width="small"),
                "cve_id": st.column_config.TextColumn("CVE", width="medium"),
                "package": st.column_config.TextColumn("Package", width="medium"),
                "current_version": st.column_config.TextColumn("Current", width="small"),
                "fixed_version": st.column_config.TextColumn("Fixed", width="small"),
                "description": st.column_config.TextColumn("Description", width="large"),
            },
        )

        # Export option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="vulnerabilities.csv",
            mime="text/csv",
        )
    else:
        st.success("✅ No vulnerabilities found matching filters")
