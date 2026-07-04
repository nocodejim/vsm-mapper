#!/usr/bin/env python3
"""
Setup script for Selenium tests
Creates virtual environment and installs required dependencies
"""

import subprocess
import sys
import os
import shutil

def create_venv():
    """Create virtual environment for testing"""
    venv_path = os.path.join(os.path.dirname(__file__), "test_env")
    
    if os.path.exists(venv_path):
        print(f"Virtual environment already exists at {venv_path}")
        return venv_path
    
    print("Creating virtual environment for testing...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        print(f"✅ Virtual environment created at {venv_path}")
        return venv_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return None

def get_venv_python(venv_path):
    """Get the Python executable path for the virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Unix/Linux/Mac
        return os.path.join(venv_path, "bin", "python")

def install_requirements(venv_python):
    """Install required Python packages in virtual environment"""
    requirements = [
        "selenium",
        "webdriver-manager"
    ]
    
    print("Installing required packages in virtual environment...")
    for package in requirements:
        try:
            subprocess.check_call([venv_python, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def check_chrome():
    """Check if Chrome is available"""
    chrome_commands = ["google-chrome", "chrome", "chromium", "chromium-browser"]
    
    for cmd in chrome_commands:
        if shutil.which(cmd):
            print(f"✅ Chrome found: {cmd}")
            return True
    
    print("❌ Chrome not found. Please install Google Chrome or Chromium")
    print("   Ubuntu/Debian: sudo apt install google-chrome-stable")
    print("   Or: sudo apt install chromium-browser")
    return False

def create_download_dir():
    """Create download directory for tests"""
    download_dir = "/tmp/vsm_test_downloads"
    
    try:
        os.makedirs(download_dir, exist_ok=True)
        print(f"✅ Download directory created: {download_dir}")
        return True
    except Exception as e:
        print(f"❌ Failed to create download directory: {e}")
        return False

def verify_app_running():
    """Check if the VSM app is running"""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:8080", timeout=5)
        print("✅ VSM Generator app is running on localhost:8080")
        return True
    except Exception:
        print("⚠️  VSM Generator app not detected on localhost:8080")
        print("   Make sure to run: ./scripts/deploy.sh")
        return False

def main():
    print("VSM Generator Selenium Test Setup")
    print("=================================")
    print("Following environment isolation rules - creating virtual environment")
    
    success = True
    
    # Create virtual environment
    venv_path = create_venv()
    if not venv_path:
        success = False
    else:
        venv_python = get_venv_python(venv_path)
        
        # Install requirements in venv
        if not install_requirements(venv_python):
            success = False
    
    # Check Chrome
    if not check_chrome():
        success = False
    
    # Create download directory
    if not create_download_dir():
        success = False
    
    # Check if app is running
    verify_app_running()  # This is a warning, not a failure
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\nVirtual environment created with test dependencies.")
        print("\nNext steps:")
        print("1. Make sure VSM Generator app is running: ./scripts/deploy.sh")
        print("2. Activate virtual environment:")
        if os.name == 'nt':
            print(f"   tests\\test_env\\Scripts\\activate")
        else:
            print(f"   source tests/test_env/bin/activate")
        print("3. Run tests: python tests/run_tests.py")
        print("   - Tests run in headless mode by default (faster, no browser window)")
        print("   - Use --windowed flag to see browser window for debugging")
        print("4. Deactivate when done: deactivate")
    else:
        print("\n❌ Setup failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()