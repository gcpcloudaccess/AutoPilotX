#!/usr/bin/env python3
import argparse
import logging
from typing import List

from teraformers.backend.scanner.config import config
from teraformers.backend.scanner.service import ScanningService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Container Image Vulnerability Scanner")
    parser.add_argument(
        "--images",
        nargs="+",
        help="Images to scan (space-separated)"
    )
    parser.add_argument(
        "--use-defaults",
        action="store_true",
        help=f"Scan default test images: {', '.join(config.TEST_IMAGES)}"
    )
    parser.add_argument(
        "--severity",
        default="LOW",
        choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        help="Minimum severity to report"
    )
    parser.add_argument(
        "--output",
        default="./scans",
        help="Output directory for scan results"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only print report, don't save JSON"
    )
    parser.add_argument(
        "--scanner",
        default=config.SCANNER_TYPE,
        help="Scanner to use (trivy, grype, etc)"
    )

    args = parser.parse_args()

    # Determine images to scan
    images = args.images
    if not images:
        if args.use_defaults:
            images = config.TEST_IMAGES
        else:
            parser.print_help()
            return

    logger.info(f"Starting scan of {len(images)} image(s)")
    print(f"\n🔍 Scanning {len(images)} image(s)...\n")

    # Initialize service
    service = ScanningService(scanner_type=args.scanner, output_dir=args.output)

    # Scan images
    results = service.scan_images(images)

    if not results:
        logger.error("No successful scans")
        return

    # Filter by severity
    filtered_results = service.filter_by_severity(results, args.severity)

    # Generate and print report
    report = service.generate_report(filtered_results)
    print(report)

    # Save results
    if not args.report_only:
        output_file = service.save_results(filtered_results, format="json")
        print(f"\n✅ Results saved to: {output_file}\n")

if __name__ == "__main__":
    main()
