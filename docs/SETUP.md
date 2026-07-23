# Container Image Scanning Service

Lightweight Python-based vulnerability scanner for container images using Trivy.

## Prerequisites

### 1. Install Trivy

**Linux/macOS:**
```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh
```

**Windows (with Chocolatey):**
```powershell
choco install trivy
```

**Or build from source:** https://github.com/aquasecurity/trivy

### 2. Install Docker/Podman
- Docker: https://docs.docker.com/install
- Podman: https://podman.io/docs/installation

### 3. Python 3.9+

## Installation

```bash
pip install -r requirements.txt
chmod +x main.py  # Unix only
```

## Usage

### Scan test images (default public images)
```bash
python main.py --use-defaults
```

### Scan specific images
```bash
python main.py --images alpine:latest ubuntu:22.04 nginx:latest
```

### Filter by severity
```bash
python main.py --use-defaults --severity HIGH
```

### Save and report
```bash
python main.py --use-defaults --output ./vulnerability_reports
```

### Report only (no JSON output)
```bash
python main.py --use-defaults --report-only
```

## Project Structure

```
.
├── main.py                 # CLI entry point
├── config.py              # Configuration settings
├── models.py              # Data models (Vulnerability, ScanResult)
├── scanners.py            # Scanner implementations (Trivy)
├── scanning_service.py    # Main orchestration service
├── requirements.txt       # Python dependencies
└── scans/                 # Output directory for scan results
```

## Output Format

JSON scan results contain:
- Image name, tag, digest
- Scan timestamp
- List of vulnerabilities with severity
- Package versions and available fixes

Example:
```json
{
  "image": "alpine",
  "tag": "latest",
  "digest": "sha256:...",
  "scan_timestamp": "2024-01-15T10:30:45",
  "scanner": "trivy",
  "total_vulns": 5,
  "critical_count": 1,
  "high_count": 2,
  "vulnerabilities": [
    {
      "id": "CVE-2024-1234",
      "severity": "CRITICAL",
      "package": "openssl",
      "installed_version": "1.1.1",
      "fixed_version": "1.1.1w",
      "description": "Buffer overflow in..."
    }
  ]
}
```

## Next Steps

1. **Integrate with Firestore:** Modify `scanning_service.py` to save results to Cloud Firestore
2. **Build Streamlit Dashboard:** Connect to saved results for visualization
3. **Automate with Cloud Scheduler:** Run scans on schedule via Cloud Run
4. **Implement Remediation:** Auto-generate patch Dockerfiles for HIGH/CRITICAL vulns

## Troubleshooting

**Trivy not found:**
```bash
trivy version  # Check installation
which trivy    # On Unix
```

**Image pull timeout:**
Increase timeout in `config.py`:
```python
TIMEOUT: int = 600  # Increase to 600 seconds
```

**Docker daemon not running:**
```bash
docker ps  # Verify Docker is running
```
