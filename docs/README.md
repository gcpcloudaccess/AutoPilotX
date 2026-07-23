# Container Image Vulnerability Scanner

Production-ready Python backend for scanning container images with open-source tools.

## Quick Start

### 1. Check Environment
```bash
python check_env.py
```

### 2. Install Trivy
```bash
# macOS
brew install trivy

# Linux
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# Windows (Chocolatey)
choco install trivy
```

### 3. Run Scan
```bash
# Scan default public images
python main.py --use-defaults

# Scan specific images
python main.py --images alpine:latest ubuntu:22.04 nginx:latest

# Filter by severity
python main.py --use-defaults --severity HIGH

# Custom output directory
python main.py --use-defaults --output ./reports
```

## Architecture

```
main.py                    # CLI interface
  ↓
scanning_service.py        # Orchestration
  ↓
scanners.py (TrivyScanner)  # Execution
  ↓
models.py                  # Data structures
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point with argparse |
| `scanning_service.py` | Core service - scan, filter, report |
| `scanners.py` | Scanner implementations (Trivy) |
| `models.py` | Vulnerability & ScanResult classes |
| `config.py` | Configuration & test images |
| `example.py` | Usage examples |
| `check_env.py` | Dependency verification |
| `gcp_integration.py` | Placeholder for GCP connection |

## Features

✅ Scan public/private container images  
✅ Multi-image batch scanning  
✅ Severity filtering (CRITICAL, HIGH, MEDIUM, LOW)  
✅ JSON output for storage/processing  
✅ Human-readable reports  
✅ Extensible scanner architecture  
✅ Zero hardcoded dummy data  

## Usage Examples

### As CLI

```bash
# Default test images
python main.py --use-defaults

# Custom images with HIGH severity filter
python main.py --images myapp:v1.0 api:v2.1 --severity HIGH

# Report only (no JSON save)
python main.py --use-defaults --report-only
```

### As Library

```python
from scanning_service import ScanningService

service = ScanningService()
results = service.scan_images(["alpine:latest", "nginx:latest"])

# Filter and report
filtered = service.filter_by_severity(results, "HIGH")
print(service.generate_report(filtered))

# Save results
service.save_results(filtered, format="json")
```

## Output

```json
{
  "image": "alpine",
  "tag": "latest",
  "digest": "sha256:abc123",
  "scan_timestamp": "2024-01-15T10:30:45",
  "scanner": "trivy",
  "total_vulns": 5,
  "critical_count": 1,
  "high_count": 2,
  "medium_count": 2,
  "low_count": 0,
  "vulnerabilities": [
    {
      "id": "CVE-2024-1234",
      "severity": "CRITICAL",
      "package": "openssl",
      "installed_version": "1.1.1",
      "fixed_version": "1.1.1w",
      "description": "Buffer overflow...",
      "source": "trivy"
    }
  ]
}
```

## Configuration

Edit `config.py` to customize:
- Default test images
- Scanner type
- Output format
- Severity threshold
- Scan timeout

## Next Steps

1. **Test the scanner**
   ```bash
   python check_env.py
   python main.py --use-defaults --report-only
   ```

2. **Connect to GCP** (later)
   - Uncomment GCP client initialization in `gcp_integration.py`
   - Use `FirestoreStorage` to save results to Cloud Firestore
   - Use `GCRClient` to list/scan images from Google Container Registry

3. **Build Streamlit Dashboard** (next phase)
   - Read from JSON files or Firestore
   - Visualize vulnerabilities
   - Approve/reject patches

4. **Setup Cloud Automation** (final phase)
   - Deploy as Cloud Run service
   - Trigger via Cloud Scheduler
   - Auto-build patches via Cloud Build

## Testing Without GCP

All scanning works locally with public images from Docker Hub. No GCP setup required for initial testing:

```bash
python main.py --images \
  alpine:latest \
  ubuntu:22.04 \
  python:3.11-slim \
  node:20-alpine
```

## Requirements

- Python 3.9+
- Docker or Podman
- Trivy (vulnerability scanner)
- (Optional) GCP credentials for Firestore integration

## Troubleshooting

**Trivy not found:**
```bash
trivy version
```

**Docker connection error:**
```bash
docker ps
```

**Image pull timeout:**
Increase `TIMEOUT` in `config.py`:
```python
TIMEOUT: int = 600  # 10 minutes
```

## License

MIT
