#!/usr/bin/env python3
"""
Example usage of the scanning service as a library.
"""

from teraformers.backend.scanner.service import ScanningService

def example_basic():
    """Basic scanning of public images"""
    service = ScanningService()
    results = service.scan_images([
        "alpine:latest",
        "nginx:latest",
    ])
    print(service.generate_report(results))

def example_with_filtering():
    """Scan and filter by severity"""
    service = ScanningService()
    results = service.scan_images(["ubuntu:22.04"])

    # Only show HIGH and CRITICAL
    filtered = service.filter_by_severity(results, "HIGH")

    for result in filtered:
        print(f"\n{result.image}:{result.tag}")
        print(f"  Critical: {result.critical_count}, High: {result.high_count}")
        for vuln in result.vulnerabilities[:3]:
            print(f"  - {vuln.id}: {vuln.package}")

def example_custom_output():
    """Scan and save to custom location"""
    service = ScanningService(output_dir="./custom_reports")
    results = service.scan_images(["python:3.11-slim"])

    output_file = service.save_results(results, format="json")
    summary = service.get_summary(results)

    print(f"Saved to: {output_file}")
    print(f"Summary: {summary}")

if __name__ == "__main__":
    print("=== Example 1: Basic Scan ===")
    example_basic()

    # Uncomment to run other examples:
    # print("\n=== Example 2: Filtering ===")
    # example_with_filtering()
    #
    # print("\n=== Example 3: Custom Output ===")
    # example_custom_output()
