# Building Distributable Executables

This guide explains how to create distributable executables for Gmail Processor that work on Windows and macOS.

## Prerequisites

1. Python 3.8+ installed
2. All project dependencies installed: `pip install -r requirements.txt`

## Quick Build

Run the automated build script:

```bash
python build.py
```

This will:
- Clean previous builds
- Install dependencies
- Create platform-specific executable
- Package everything for distribution

## Manual Build Process

If you prefer to build manually:

1. **Install PyInstaller** (if not already installed):
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**:
   ```bash
   pyinstaller gmail_processor.spec --clean
   ```

3. **Find your executable** in the `dist/` directory

## Cross-Platform Building

To build for different platforms:

### On macOS:
- Builds macOS executable natively
- For Windows: Use a Windows machine or VM

### On Windows:
- Builds Windows executable natively
- For macOS: Use a macOS machine or VM

### Using GitHub Actions (Recommended for Both Platforms)

Create `.github/workflows/build.yml` for automated cross-platform builds:

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Build executable
      run: python build.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: gmail-processor-${{ matrix.os }}
        path: dist/gmail_processor_*
```

## Distribution Package Contents

The build script creates a complete distribution package containing:

- **Executable file** (`gmail_processor_[platform]_[arch]`)
- **Configuration template** (`.env.example`)
- **Credentials placeholder** (`credentials.json`)
- **Setup instructions** (`README.txt`)

## Troubleshooting

### Common Issues:

1. **Missing modules**: Add them to `hiddenimports` in `gmail_processor.spec`
2. **Large executable size**: This is normal for PyInstaller (includes Python runtime)
3. **Antivirus warnings**: Some antivirus software flags PyInstaller executables as suspicious

### Reducing Executable Size:

```bash
# Use --onefile for smaller distribution (but slower startup)
pyinstaller --onefile gmail_processor.py

# Exclude unnecessary modules
pyinstaller --exclude-module tkinter gmail_processor.py
```

## File Sizes

Typical executable sizes:
- Windows: ~100-150 MB
- macOS: ~80-120 MB

This includes the Python runtime and all dependencies, making the executable truly standalone.