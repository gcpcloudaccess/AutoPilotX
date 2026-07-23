from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional
from enum import Enum

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"

@dataclass
class Vulnerability:
    """Represents a single vulnerability"""
    id: str
    severity: Severity
    description: str
    package: str
    installed_version: str
    fixed_version: Optional[str]
    source: str  # trivy, grype, etc

    def to_dict(self):
        return asdict(self)

@dataclass
class ScanResult:
    """Complete scan result for an image"""
    image: str
    tag: str
    digest: str
    scan_timestamp: datetime
    scanner: str
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    total_vulns: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    def to_dict(self):
        data = asdict(self)
        data['scan_timestamp'] = self.scan_timestamp.isoformat()
        data['vulnerabilities'] = [v.to_dict() for v in self.vulnerabilities]
        return data

    def calculate_stats(self):
        """Calculate vulnerability counts by severity"""
        for vuln in self.vulnerabilities:
            if vuln.severity == Severity.CRITICAL:
                self.critical_count += 1
            elif vuln.severity == Severity.HIGH:
                self.high_count += 1
            elif vuln.severity == Severity.MEDIUM:
                self.medium_count += 1
            elif vuln.severity == Severity.LOW:
                self.low_count += 1

        self.total_vulns = len(self.vulnerabilities)
