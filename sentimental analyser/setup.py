#!/usr/bin/env python
"""
setup.py - Setup script for Engagement Sentiment Analyzer
This script sets up the project and installs dependencies.
"""

import os
import sys
import subprocess

def main():
    """Main setup function."""
    print("=" * 70)
    print("Engagement Sentiment Analyzer - Setup Script")
    print("=" * 70)
    
    # Check Python version
    print("\n✓ Checking Python version...")
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"✗ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        sys.exit(1)
    print(f"✓ Python {python_version.major}.{python_version.minor} detected")
    
    # Install dependencies
    print("\n✓ Installing dependencies...")
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if os.path.exists(requirements_file):
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
            capture_output=False
        )
        if result.returncode != 0:
            print("✗ Failed to install dependencies")
            sys.exit(1)
    else:
        print("✗ requirements.txt not found")
        sys.exit(1)
    
    print("\n✓ Setup complete!")
    print("\n" + "=" * 70)
    print("Next steps:")
    print("1. Run the Streamlit app: streamlit run app.py")
    print("2. Open browser to: http://localhost:8501")
    print("=" * 70)

if __name__ == "__main__":
    main()
