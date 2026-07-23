import json
import subprocess
from datetime import datetime
from typing import List
import logging

from teraformers.backend.scanner.models import ScanResult, Vulnerability, Severity

logger = logging.getLogger(__name__)

class BaseScanner:
    """Abstract base scanner"""
    def scan(self, image: str) -> ScanResult:
        raise NotImplementedError

class TrivyScanner(BaseScanner):
    """Trivy-based vulnerability scanner"""

    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self._verify_installed()

    def _verify_installed(self):
        """Check if trivy is installed"""
        try:
            subprocess.run(["trivy", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Trivy not found. Install with: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh"
            )

    def scan(self, image: str) -> ScanResult:
        """Scan image using trivy"""
        logger.info(f"Scanning {image} with Trivy...")

        # Parse image name and tag
        image_parts = image.split(":")
        image_name = image_parts[0]
        tag = image_parts[1] if len(image_parts) > 1 else "latest"

        try:
            # Run trivy scan
            cmd = [
                "trivy", "image",
                "--format", "json",
                "--severity", "LOW,MEDIUM,HIGH,CRITICAL",
                "--scanners", "vuln",
                image
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode not in [0, 1]:  # 1 is when vulnerabilities found
                raise RuntimeError(f"Trivy scan failed: {result.stderr}")

            # Parse JSON output
            output = json.loads(result.stdout)
            vulns = self._parse_trivy_output(output)

            # Get image digest (simplified - in real scenario fetch from registry)
            digest = self._get_image_digest(image)

            scan_result = ScanResult(
                image=image_name,
                tag=tag,
                digest=digest,
                scan_timestamp=datetime.utcnow(),
                scanner="trivy",
                vulnerabilities=vulns
            )
            scan_result.calculate_stats()

            logger.info(f"Scan complete: {scan_result.total_vulns} vulnerabilities found")
            return scan_result

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Trivy scan timeout for {image}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse trivy output: {e}")

    def _parse_trivy_output(self, output: dict) -> List[Vulnerability]:
        """Parse trivy JSON output to Vulnerability objects"""
        vulns = []

        results = output.get("Results", [])
        for result in results:
            misconfigs = result.get("Misconfigurations", [])
            vulnerabilities = result.get("Vulnerabilities", [])

            for vuln in vulnerabilities:
                try:
                    severity = Severity(vuln.get("Severity", "UNKNOWN"))
                except ValueError:
                    severity = Severity.UNKNOWN

                vuln_obj = Vulnerability(
                    id=vuln.get("VulnerabilityID", ""),
                    severity=severity,
                    description=vuln.get("Description", "")[:200],  # Truncate
                    package=vuln.get("PkgName", ""),
                    installed_version=vuln.get("InstalledVersion", ""),
                    fixed_version=vuln.get("FixedVersion"),
                    source="trivy"
                )
                vulns.append(vuln_obj)

        return vulns

    def _get_image_digest(self, image: str) -> str:
        """Get image digest from local docker"""
        try:
            cmd = ["docker", "inspect", image, "--format={{.RepoDigests}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                digests = result.stdout.strip().strip("[]").split()
                return digests[0].split("@")[1] if digests and "@" in digests[0] else "unknown"
        except Exception as e:
            logger.warning(f"Could not get image digest: {e}")
        return "unknown"


class ScannerFactory:
    """Factory to create scanner instances"""
    _scanners = {
        "trivy": TrivyScanner,
    }

    @staticmethod
    def create(scanner_type: str, **kwargs) -> BaseScanner:
        scanner_class = ScannerFactory._scanners.get(scanner_type.lower())
        if not scanner_class:
            raise ValueError(f"Unknown scanner type: {scanner_type}")
        return scanner_class(**kwargs)
