#!/usr/bin/env python3
"""
Environment check script - verify all dependencies are installed.
"""

import subprocess
import sys

def check_command(cmd: str, name: str) -> bool:
    """Check if a command exists and is executable"""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        print(f"✓ {name} is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"✗ {name} is NOT installed")
        return False

def check_python_packages():
    """Check if required Python packages are available"""
    packages = [
        ("google.cloud", "google-cloud-firestore"),
        ("docker", "docker"),
    ]

    all_ok = True
    for module, package in packages:
        try:
            __import__(module)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed - run: pip install {package}")
            all_ok = False

    return all_ok

def main():
    print("\n🔍 Checking environment...\n")

    # Check system commands
    print("System Dependencies:")
    docker_ok = check_command("docker", "Docker")
    trivy_ok = check_command("trivy", "Trivy")

    print("\nPython Packages:")
    python_ok = check_python_packages()

    print("\n" + "=" * 50)
    if docker_ok and trivy_ok:
        print("✓ All dependencies installed!")
        print("\nNext steps:")
        print("  python main.py --use-defaults --report-only")
        return 0
    else:
        print("✗ Some dependencies missing. See above for install instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
