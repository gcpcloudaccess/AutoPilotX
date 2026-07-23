import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from teraformers.backend.scanner.models import ScanResult, Vulnerability, Severity
import logging

logger = logging.getLogger(__name__)

class ScanDataLoader:
    """Load and manage scan results from JSON files"""

    def __init__(self, scan_dir: str = "./scans"):
        self.scan_dir = Path(scan_dir)
        self.scan_dir.mkdir(exist_ok=True)

    def load_latest_scan(self) -> Optional[List[ScanResult]]:
        """Load the most recent scan file"""
        files = sorted(self.scan_dir.glob("scan_results_*.json"), reverse=True)
        if not files:
            return None
        return self._parse_json_file(files[0])

    def load_scan_by_timestamp(self, timestamp: str) -> Optional[List[ScanResult]]:
        """Load scan by timestamp (YYYYMMDD_HHMMSS)"""
        file_path = self.scan_dir / f"scan_results_{timestamp}.json"
        if not file_path.exists():
            return None
        return self._parse_json_file(file_path)

    def list_scans(self) -> List[Dict]:
        """List all available scans with metadata"""
        scans = []
        for file_path in sorted(self.scan_dir.glob("scan_results_*.json"), reverse=True):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        scan_time = Path(file_path).stem.replace("scan_results_", "")
                        total_vulns = sum(s.get("total_vulns", 0) for s in data)
                        images = len(data)
                        scans.append({
                            "timestamp": scan_time,
                            "date": self._format_timestamp(scan_time),
                            "images_count": images,
                            "total_vulns": total_vulns,
                            "critical": sum(s.get("critical_count", 0) for s in data),
                        })
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
        return scans

    def get_scan_summary(self, scans: List[ScanResult]) -> Dict:
        """Generate summary statistics from scans"""
        if not scans:
            return {}

        total_vulns = sum(s.total_vulns for s in scans)
        total_critical = sum(s.critical_count for s in scans)
        total_high = sum(s.high_count for s in scans)
        total_medium = sum(s.medium_count for s in scans)

        return {
            "total_images": len(scans),
            "images_with_vulns": len([s for s in scans if s.total_vulns > 0]),
            "total_vulnerabilities": total_vulns,
            "critical": total_critical,
            "high": total_high,
            "medium": total_medium,
            "avg_vulns_per_image": round(total_vulns / len(scans), 1) if scans else 0,
        }

    def get_vulnerabilities_by_severity(self, scans: List[ScanResult]) -> Dict[str, int]:
        """Count vulnerabilities by severity"""
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for scan in scans:
            for vuln in scan.vulnerabilities:
                counts[vuln.severity.value] += 1
        return counts

    def get_top_packages_by_vulns(self, scans: List[ScanResult], limit: int = 10) -> List[Dict]:
        """Get top packages with most vulnerabilities"""
        package_vulns = {}
        for scan in scans:
            for vuln in scan.vulnerabilities:
                key = vuln.package
                if key not in package_vulns:
                    package_vulns[key] = {
                        "package": key,
                        "count": 0,
                        "critical": 0,
                        "high": 0,
                    }
                package_vulns[key]["count"] += 1
                if vuln.severity == Severity.CRITICAL:
                    package_vulns[key]["critical"] += 1
                elif vuln.severity == Severity.HIGH:
                    package_vulns[key]["high"] += 1

        return sorted(package_vulns.values(), key=lambda x: x["count"], reverse=True)[:limit]

    def get_fixable_vulnerabilities(self, scans: List[ScanResult]) -> List[Dict]:
        """Get vulnerabilities with available fixes"""
        fixable = []
        for scan in scans:
            for vuln in scan.vulnerabilities:
                if vuln.fixed_version:
                    fixable.append({
                        "image": f"{scan.image}:{scan.tag}",
                        "vuln_id": vuln.id,
                        "package": vuln.package,
                        "severity": vuln.severity.value,
                        "current_version": vuln.installed_version,
                        "fixed_version": vuln.fixed_version,
                    })
        return fixable

    def _parse_json_file(self, file_path: Path) -> List[ScanResult]:
        """Parse JSON file into ScanResult objects"""
        try:
            with open(file_path) as f:
                data = json.load(f)

            results = []
            for item in data:
                vulns = [
                    Vulnerability(
                        id=v["id"],
                        severity=Severity(v["severity"]),
                        description=v["description"],
                        package=v["package"],
                        installed_version=v["installed_version"],
                        fixed_version=v.get("fixed_version"),
                        source=v.get("source", "unknown"),
                    )
                    for v in item.get("vulnerabilities", [])
                ]

                result = ScanResult(
                    image=item["image"],
                    tag=item["tag"],
                    digest=item["digest"],
                    scan_timestamp=datetime.fromisoformat(item["scan_timestamp"]),
                    scanner=item["scanner"],
                    vulnerabilities=vulns,
                    total_vulns=item.get("total_vulns", 0),
                    critical_count=item.get("critical_count", 0),
                    high_count=item.get("high_count", 0),
                    medium_count=item.get("medium_count", 0),
                )
                results.append(result)

            return results
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return []

    @staticmethod
    def _format_timestamp(timestamp: str) -> str:
        """Format timestamp string to readable date"""
        try:
            dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            return dt.strftime("%b %d, %H:%M")
        except:
            return timestamp
