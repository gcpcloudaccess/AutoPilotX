from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    """Scanning service configuration"""
    SCANNER_TYPE: str = "trivy"  # or "grype", "syft"
    TEST_IMAGES: List[str] = None
    OUTPUT_FORMAT: str = "json"  # json, table
    SEVERITY_THRESHOLD: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW
    CACHE_DIR: str = "/tmp/image_cache"
    TIMEOUT: int = 300  # seconds

    def __post_init__(self):
        if self.TEST_IMAGES is None:
            self.TEST_IMAGES = [
                "alpine:latest",
                "ubuntu:22.04",
                "nginx:latest",
                "python:3.11-slim",
                "node:20-alpine",
            ]

config = Config()
