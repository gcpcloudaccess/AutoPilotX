#!/usr/bin/env python3
"""
Generate realistic mock scan data for testing/demo purposes.
Creates JSON files that can be loaded into the dashboard.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

def generate_vulnerabilities(image: str, count: int = None) -> List[Dict]:
    """Generate mock vulnerabilities for an image"""
    # Real CVE data
    vulnerabilities_db = {
        "alpine:latest": [
            {"id": "CVE-2024-1086", "severity": "CRITICAL", "package": "linux-kernel", "current": "6.6.8", "fixed": "6.6.11"},
            {"id": "CVE-2024-0863", "severity": "HIGH", "package": "openssl", "current": "3.1.0", "fixed": "3.1.4"},
            {"id": "CVE-2024-0567", "severity": "MEDIUM", "package": "curl", "current": "8.4.0", "fixed": "8.5.0"},
        ],
        "ubuntu:22.04": [
            {"id": "CVE-2023-46604", "severity": "CRITICAL", "package": "log4j", "current": "2.14.1", "fixed": "2.19.0"},
            {"id": "CVE-2023-44487", "severity": "HIGH", "package": "nghttp2", "current": "1.43.0", "fixed": "1.47.0"},
            {"id": "CVE-2023-42665", "severity": "HIGH", "package": "systemd", "current": "251.11", "fixed": "252.5"},
            {"id": "CVE-2023-39615", "severity": "MEDIUM", "package": "python3", "current": "3.10.10", "fixed": "3.10.13"},
            {"id": "CVE-2023-38709", "severity": "LOW", "package": "libc", "current": "2.35", "fixed": "2.36"},
        ],
        "nginx:latest": [
            {"id": "CVE-2023-44487", "severity": "HIGH", "package": "nginx", "current": "1.24.0", "fixed": "1.25.3"},
            {"id": "CVE-2023-30581", "severity": "MEDIUM", "package": "zlib", "current": "1.2.12", "fixed": "1.2.13"},
            {"id": "CVE-2023-22518", "severity": "LOW", "package": "openssl", "current": "3.0.7", "fixed": "3.1.0"},
        ],
        "python:3.11-slim": [
            {"id": "CVE-2024-0341", "severity": "HIGH", "package": "python", "current": "3.11.6", "fixed": "3.11.8"},
            {"id": "CVE-2023-24329", "severity": "MEDIUM", "package": "urllib3", "current": "2.0.0", "fixed": "2.0.7"},
        ],
        "node:20-alpine": [
            {"id": "CVE-2024-21892", "severity": "HIGH", "package": "node.js", "current": "20.8.0", "fixed": "20.10.0"},
            {"id": "CVE-2023-44487", "severity": "MEDIUM", "package": "npm", "current": "10.1.0", "fixed": "10.2.5"},
            {"id": "CVE-2024-1234", "severity": "LOW", "package": "openssl", "current": "3.0.9", "fixed": "3.0.12"},
        ],
    }

    vulns = vulnerabilities_db.get(image, [])
    if count:
        vulns = vulns[:count]

    return [
        {
            "id": v["id"],
            "severity": v["severity"],
            "package": v["package"],
            "installed_version": v["current"],
            "fixed_version": v["fixed"],
            "description": f"Security vulnerability in {v['package']} - update to {v['fixed']} or later",
            "source": "trivy"
        }
        for v in vulns
    ]

def generate_scan_result(image: str, tag: str, timestamp: datetime) -> Dict:
    """Generate a complete scan result"""
    vulns = generate_vulnerabilities(f"{image}:{tag}")

    severity_counts = {
        "CRITICAL": sum(1 for v in vulns if v["severity"] == "CRITICAL"),
        "HIGH": sum(1 for v in vulns if v["severity"] == "HIGH"),
        "MEDIUM": sum(1 for v in vulns if v["severity"] == "MEDIUM"),
        "LOW": sum(1 for v in vulns if v["severity"] == "LOW"),
    }

    return {
        "image": image,
        "tag": tag,
        "digest": f"sha256:{''.join([str(ord(c) % 16) for c in image[:32]])[:64]}",
        "scan_timestamp": timestamp.isoformat(),
        "scanner": "trivy",
        "total_vulns": len(vulns),
        "critical_count": severity_counts["CRITICAL"],
        "high_count": severity_counts["HIGH"],
        "medium_count": severity_counts["MEDIUM"],
        "low_count": severity_counts["LOW"],
        "vulnerabilities": vulns,
    }

def generate_demo_scans(output_dir: str = "output/scans", days_back: int = 3) -> str:
    """Generate multiple scan files for demo"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    images = [
        ("alpine", "latest"),
        ("ubuntu", "22.04"),
        ("nginx", "latest"),
        ("python", "3.11-slim"),
        ("node", "20-alpine"),
    ]

    # Generate scans for past N days
    scan_files = []
    for day_offset in range(days_back, 0, -1):
        timestamp = datetime.utcnow() - timedelta(days=day_offset)
        scans = [generate_scan_result(img, tag, timestamp) for img, tag in images]

        filename = output_path / f"scan_results_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(scans, f, indent=2)

        scan_files.append(str(filename))
        print(f"✅ Created: {filename.name}")
        print(f"   📊 {len(scans)} images, {sum(s['total_vulns'] for s in scans)} vulnerabilities")

    return scan_files[0]

def print_sample_output():
    """Print sample scan output"""
    sample = generate_scan_result("alpine", "latest", datetime.utcnow())

    print("\n" + "=" * 60)
    print("SAMPLE SCAN OUTPUT (JSON)")
    print("=" * 60)
    print(json.dumps(sample, indent=2))
    print("=" * 60)

if __name__ == "__main__":
    print("🎬 Generating demo scan data...")
    print()

    # Generate 3 days of demo data
    latest_file = generate_demo_scans(days_back=3)

    print()
    print("✅ Demo data generated!")
    print()
    print("📂 Files created in: output/scans/")
    print()
    print("🚀 Next steps:")
    print("   1. View sample output:")
    print_sample_output()
    print()
    print("   2. Start dashboard with demo data:")
    print("      streamlit run frontend/streamlit_app.py")
    print()
    print("   3. Try the features:")
    print("      - View Dashboard tab for overview")
    print("      - Search vulnerabilities in Results tab")
    print("      - Check version recommendations")
    print("      - Approve patches in Build Queue")
    print("      - View trends in History tab")
