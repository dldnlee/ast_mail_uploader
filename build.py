#!/usr/bin/env python3
"""
Build script for creating distributable executables of Gmail Processor.
Supports both Windows and macOS builds.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"Running: {cmd}")
    if description:
        print(f"Description: {description}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    
    if result.stdout:
        print(result.stdout)

def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}/")
    
    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    run_command("pip install -r requirements.txt", "Installing project dependencies")

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    # Get platform info
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    print(f"Building for: {system} ({arch})")
    
    # Build with PyInstaller
    run_command("pyinstaller gmail_processor.spec --clean", "Building executable with PyInstaller")
    
    # Rename executable based on platform
    if system == "windows":
        old_name = "dist/gmail_processor.exe"
        new_name = f"dist/gmail_processor_windows_{arch}.exe"
    elif system == "darwin":
        old_name = "dist/gmail_processor"
        new_name = f"dist/gmail_processor_macos_{arch}"
    else:
        old_name = "dist/gmail_processor"
        new_name = f"dist/gmail_processor_linux_{arch}"
    
    if os.path.exists(old_name):
        if os.path.exists(new_name):
            os.remove(new_name)
        os.rename(old_name, new_name)
        print(f"Executable created: {new_name}")
        
        # Make executable on Unix systems
        if system != "windows":
            os.chmod(new_name, 0o755)
    else:
        print(f"Warning: Expected executable not found at {old_name}")

def create_distribution_package():
    """Create a distribution package with necessary files."""
    print("Creating distribution package...")
    
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    package_name = f"gmail_processor_{system}_{arch}"
    package_dir = f"dist/{package_name}"
    
    # Create package directory
    os.makedirs(package_dir, exist_ok=True)
    
    # Copy executable
    if system == "windows":
        exe_name = f"gmail_processor_windows_{arch}.exe"
    elif system == "darwin":
        exe_name = f"gmail_processor_macos_{arch}"
    else:
        exe_name = f"gmail_processor_linux_{arch}"
    
    exe_path = f"dist/{exe_name}"
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, f"{package_dir}/{exe_name}")
    
    # Copy configuration files
    config_files = [".env.example", "credentials.json"]
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy2(config_file, package_dir)
    
    # Create README for distribution
    readme_content = f"""# Gmail Processor Executable

## Quick Start

1. Rename `.env.example` to `.env` and fill in your credentials:
   - SUPABASE_URL=your_supabase_url
   - SUPABASE_KEY=your_supabase_key
   - OPENAI_API_KEY=your_openai_api_key

2. Set up Gmail API credentials:
   - Place your Google API credentials in `credentials.json`
   - You'll need to enable Gmail API in Google Cloud Console

3. Run the executable:
   - Windows: Double-click `{exe_name}` or run from command line
   - macOS/Linux: `chmod +x {exe_name} && ./{exe_name}`

## Requirements

- Internet connection for API calls
- Valid Supabase project and credentials
- Gmail API credentials from Google Cloud Console
- OpenAI API key

## Troubleshooting

- Make sure all environment variables are set correctly
- Ensure your Supabase database has the required tables (mail_history, company_entity)
- Check that Gmail API is enabled and credentials are valid
"""
    
    with open(f"{package_dir}/README.txt", "w") as f:
        f.write(readme_content)
    
    print(f"Distribution package created: {package_dir}/")

def main():
    """Main build process."""
    print("Gmail Processor Build Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("gmail_processor.py"):
        print("Error: gmail_processor.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    try:
        clean_build()
        install_dependencies()
        build_executable()
        create_distribution_package()
        
        print("\n" + "=" * 40)
        print("Build completed successfully!")
        print("Check the 'dist/' directory for your executable.")
        
    except KeyboardInterrupt:
        print("\nBuild cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nBuild failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()