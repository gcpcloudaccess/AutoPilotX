import streamlit as st
import pandas as pd
from typing import List
from teraformers.backend.scanner.models import ScanResult
from teraformers.frontend.data_loader import ScanDataLoader

def render(scans: List[ScanResult], loader: ScanDataLoader):
    """Version recommendations page"""
    st.title("⬆️ Version Recommendations")

    # Get fixable vulnerabilities
    fixable = loader.get_fixable_vulnerabilities(scans)

    if not fixable:
        st.success("✅ No available fixes found")
        return

    st.info(f"📦 Found {len(fixable)} packages with available fixes")

    # Convert to DataFrame
    df = pd.DataFrame(fixable)

    # Group by image
    st.subheader("Recommendations by Image")
    for image in sorted(df["image"].unique()):
        with st.container(border=True):
            image_vulns = df[df["image"] == image]
            st.markdown(f"#### 🐳 {image}")

            # Count by severity
            severity_counts = image_vulns["severity"].value_counts().to_dict()
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Critical", severity_counts.get("CRITICAL", 0))
            with col2:
                st.metric("High", severity_counts.get("HIGH", 0))
            with col3:
                st.metric("Medium", severity_counts.get("MEDIUM", 0))
            with col4:
                st.metric("Low", severity_counts.get("LOW", 0))

            # Show packages to update
            st.write("**Packages with available fixes:**")
            for _, row in image_vulns.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"`{row['package']}`")
                with col2:
                    st.code(row["current_version"], language="text")
                with col3:
                    st.code(row["fixed_version"], language="text")

    st.divider()

    # Summary
    st.subheader("Fix Summary")
    col1, col2, col3 = st.columns(3)

    with col1:
        images_to_fix = len(df["image"].unique())
        st.metric("Images to Patch", images_to_fix)

    with col2:
        packages_to_update = len(df["package"].unique())
        st.metric("Packages to Update", packages_to_update)

    with col3:
        st.metric("Total Fixes Available", len(df))

    # Export recommendations
    st.divider()
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Recommendations",
        data=csv,
        file_name="version_recommendations.csv",
        mime="text/csv",
    )

    # Next steps
    st.info("""
    **Next steps:**
    1. Review recommendations above
    2. Go to "Build Approval Queue" to approve patches
    3. Automated builds will create patched images in GCR
    4. Deploy updated images to Kubernetes
    """)
