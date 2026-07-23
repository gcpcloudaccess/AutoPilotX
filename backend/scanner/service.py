import json
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from teraformers.backend.scanner.config import config
from teraformers.backend.scanner.models import ScanResult
from teraformers.backend.scanner.scanners import ScannerFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScanningService:
    """Main scanning service orchestrator"""

    def __init__(self, scanner_type: str = None, output_dir: str = "./scans"):
        self.scanner_type = scanner_type or config.SCANNER_TYPE
        self.scanner = ScannerFactory.create(self.scanner_type)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def scan_image(self, image: str) -> ScanResult:
        """Scan a single image"""
        return self.scanner.scan(image)

    def scan_images(self, images: List[str]) -> List[ScanResult]:
        """Scan multiple images"""
        results = []
        for image in images:
            try:
                result = self.scan_image(image)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to scan {image}: {e}")
                continue
        return results

    def save_results(self, results: List[ScanResult], format: str = "json") -> str:
        """Save scan results to file"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"scan_results_{timestamp}.{format}"

        if format == "json":
            data = [r.to_dict() for r in results]
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Results saved to {filename}")
        return str(filename)

    def filter_by_severity(self, results: List[ScanResult], min_severity: str) -> List[ScanResult]:
        """Filter results by minimum severity"""
        severity_levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        min_level = severity_levels.get(min_severity.upper(), 0)

        filtered = []
        for result in results:
            filtered_vulns = [
                v for v in result.vulnerabilities
                if severity_levels.get(v.severity.value, 0) >= min_level
            ]
            if filtered_vulns:
                result.vulnerabilities = filtered_vulns
                result.calculate_stats()
                filtered.append(result)

        return filtered

    def get_summary(self, results: List[ScanResult]) -> dict:
        """Generate summary statistics"""
        total_vulns = sum(r.total_vulns for r in results)
        critical = sum(r.critical_count for r in results)
        high = sum(r.high_count for r in results)
        medium = sum(r.medium_count for r in results)

        return {
            "total_images_scanned": len(results),
            "total_vulnerabilities": total_vulns,
            "critical": critical,
            "high": high,
            "medium": medium,
            "images_with_vulns": len([r for r in results if r.total_vulns > 0])
        }

    def generate_report(self, results: List[ScanResult]) -> str:
        """Generate human-readable report"""
        summary = self.get_summary(results)
        report = f"""
╔════════════════════════════════════════════════╗
║         VULNERABILITY SCAN REPORT              ║
╚════════════════════════════════════════════════╝

📊 SUMMARY
──────────────────────────────────────────────────
Images Scanned:        {summary['total_images_scanned']}
Total Vulnerabilities: {summary['total_vulnerabilities']}
  🔴 Critical:        {summary['critical']}
  🟠 High:            {summary['high']}
  🟡 Medium:          {summary['medium']}
Affected Images:       {summary['images_with_vulns']}

📋 DETAILS
──────────────────────────────────────────────────
"""
        for result in results:
            if result.total_vulns > 0:
                report += f"\n🐳 {result.image}:{result.tag}\n"
                report += f"   Total: {result.total_vulns} | Critical: {result.critical_count} | High: {result.high_count}\n"

                # Show top 5 vulnerabilities
                critical_vulns = [v for v in result.vulnerabilities if v.severity.value == "CRITICAL"]
                high_vulns = [v for v in result.vulnerabilities if v.severity.value == "HIGH"]

                for vuln in (critical_vulns + high_vulns)[:5]:
                    report += f"   - [{vuln.severity.value}] {vuln.id} ({vuln.package})\n"
                    if vuln.fixed_version:
                        report += f"     Fix available: {vuln.fixed_version}\n"

        return report
