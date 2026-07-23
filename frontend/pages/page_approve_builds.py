import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

APPROVAL_DIR = Path("./build_approvals")
APPROVAL_DIR.mkdir(exist_ok=True)

def render(scans, loader):
    """Build approval queue page"""
    st.title("🏗️ Build Approval Queue")

    tab1, tab2 = st.tabs(["Pending Approvals", "Build History"])

    with tab1:
        render_pending_approvals(scans, loader)

    with tab2:
        render_build_history()

def render_pending_approvals(scans, loader):
    """Show pending build approvals"""
    if not scans:
        st.warning("No scan data available")
        return

    fixable = loader.get_fixable_vulnerabilities(scans)

    if not fixable:
        st.success("✅ No patches available to approve")
        return

    st.info(f"📦 {len(fixable)} packages have available fixes")

    # Group by image
    images = {}
    for item in fixable:
        image = item["image"]
        if image not in images:
            images[image] = []
        images[image].append(item)

    # Display per image
    for image, patches in sorted(images.items()):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### 🐳 {image}")
                st.write(f"**{len(patches)} packages to update**")

            with col2:
                if st.button("✅ Approve All", key=f"approve_{image}"):
                    approve_build(image, patches)
                    st.success(f"Approved build for {image}")
                    st.rerun()

            # Show details
            with st.expander("View patch details"):
                for patch in patches:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"`{patch['package']}`")
                    with col2:
                        st.code(patch["current_version"], language="text")
                    with col3:
                        st.code(patch["fixed_version"], language="text")

def approve_build(image: str, patches: list):
    """Save build approval"""
    approval = {
        "timestamp": datetime.utcnow().isoformat(),
        "image": image,
        "patch_count": len(patches),
        "status": "pending",
        "patches": patches,
    }

    # Save to file
    filename = APPROVAL_DIR / f"{image.replace(':', '_')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(approval, f, indent=2)

    st.session_state[f"approved_{image}"] = True

def render_build_history():
    """Show past build approvals"""
    approvals = list(APPROVAL_DIR.glob("*.json"))

    if not approvals:
        st.info("No build history yet")
        return

    st.success(f"📋 {len(approvals)} build approval(s)")

    for approval_file in sorted(approvals, reverse=True)[:20]:
        try:
            with open(approval_file) as f:
                approval = json.load(f)

            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**{approval['image']}**")
                    st.caption(approval["timestamp"])

                with col2:
                    st.metric("Patches", approval["patch_count"])

                with col3:
                    status = approval.get("status", "pending")
                    if status == "pending":
                        st.info("⏳ Pending")
                    elif status == "building":
                        st.info("🔨 Building")
                    elif status == "completed":
                        st.success("✅ Completed")
                    elif status == "failed":
                        st.error("❌ Failed")

        except Exception as e:
            st.error(f"Error reading {approval_file}: {e}")

    # Info box
    st.info("""
    **Build Process:**
    1. ✅ Approve patches above
    2. 🔨 Cloud Build automatically generates patched Dockerfiles
    3. 📦 New images pushed to GCR with tag: `{image}:patched-{timestamp}`
    4. ✅ Deploy patched images to Kubernetes
    """)
