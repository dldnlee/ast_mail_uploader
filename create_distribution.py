#!/usr/bin/env python3
"""
Create a complete distribution package for Gmail Processor.
"""

import os
import shutil
import platform
from pathlib import Path

def create_distribution():
    """Create a complete distribution package."""
    
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # Create distribution directory
    dist_name = f"gmail_processor_{system}_{arch}"
    dist_dir = Path(f"dist/{dist_name}")
    
    # Clean and create directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating distribution package: {dist_dir}")
    
    # Copy executable
    exe_name = "gmail_processor.exe" if system == "windows" else "gmail_processor"
    exe_source = Path(f"dist/{exe_name}")
    
    if not exe_source.exists():
        print(f"Error: Executable not found at {exe_source}")
        print("Please run 'pyinstaller gmail_processor.spec --clean' first")
        return False
    
    # Copy executable with platform-specific name
    exe_target_name = f"gmail_processor_{system}_{arch}" + (".exe" if system == "windows" else "")
    shutil.copy2(exe_source, dist_dir / exe_target_name)
    
    # Make executable on Unix systems
    if system != "windows":
        os.chmod(dist_dir / exe_target_name, 0o755)
    
    # Copy configuration files
    config_files = [".env.example"]
    for config_file in config_files:
        if Path(config_file).exists():
            shutil.copy2(config_file, dist_dir / config_file)
            print(f"Copied {config_file}")
    
    # Create credentials.json template if it doesn't exist
    credentials_template = {
        "installed": {
            "client_id": "your-client-id.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "your-client-secret",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    import json
    with open(dist_dir / "credentials.json.example", "w") as f:
        json.dump(credentials_template, f, indent=2)
    print("Created credentials.json.example")
    
    # Create README
    readme_content = f"""# Gmail Processor - Standalone Executable

## Quick Setup

1. **Environment Configuration**:
   - Rename `.env.example` to `.env`
   - Fill in your credentials:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     OPENAI_API_KEY=your_openai_api_key
     ```

2. **Gmail API Setup**:
   - Go to Google Cloud Console (https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download credentials and rename to `credentials.json`
   - OR rename `credentials.json.example` to `credentials.json` and fill in your values

3. **Supabase Database Setup**:
   Make sure your Supabase database has these tables:
   
   ```sql
   -- Company entities table
   CREATE TABLE company_entity (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     email TEXT UNIQUE NOT NULL,
     name TEXT,
     company TEXT,
     phone_num TEXT,
     position TEXT,
     category TEXT,
     created_at TIMESTAMP DEFAULT NOW()
   );
   
   -- Mail history table  
   CREATE TABLE mail_history (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     title TEXT NOT NULL,
     original_content TEXT,
     summarized_content TEXT,
     received_date TIMESTAMP,
     company_entity_id UUID REFERENCES company_entity(id),
     receiver_mail TEXT,
     created_at TIMESTAMP DEFAULT NOW()
   );
   ```

## Running the Application

### Windows:
```cmd
{exe_target_name}
```

### macOS/Linux:
```bash
chmod +x {exe_target_name}
./{exe_target_name}
```

## Usage

1. The program will prompt you for:
   - Gmail search query (optional - press Enter for recent emails)
   - Number of emails to process (default: 10)

2. First run will open your browser for Gmail OAuth authorization

3. Emails will be processed and stored in your Supabase database

## Troubleshooting

- **"Environment variables not set"**: Make sure `.env` file exists and has all required values
- **"Gmail API error"**: Check `credentials.json` is valid and Gmail API is enabled
- **"Supabase error"**: Verify your Supabase URL and key are correct
- **"OpenAI error"**: Check your OpenAI API key is valid and has sufficient credits

## File Structure

```
{dist_name}/
├── {exe_target_name}          # Main executable
├── .env.example               # Environment template
├── credentials.json.example   # Gmail API credentials template
└── README.txt                 # This file
```

## Support

For issues, check the project repository or ensure all environment variables are properly configured.
"""
    
    with open(dist_dir / "README.txt", "w") as f:
        f.write(readme_content)
    print("Created README.txt")
    
    # Create a simple batch/shell script to run the executable
    if system == "windows":
        script_content = f"""@echo off
echo Starting Gmail Processor...
{exe_target_name}
pause
"""
        with open(dist_dir / "run_gmail_processor.bat", "w") as f:
            f.write(script_content)
        print("Created run_gmail_processor.bat")
    else:
        script_content = f"""#!/bin/bash
echo "Starting Gmail Processor..."
cd "$(dirname "$0")"
./{exe_target_name}
"""
        script_path = dist_dir / "run_gmail_processor.sh"
        with open(script_path, "w") as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        print("Created run_gmail_processor.sh")
    
    print(f"\n✅ Distribution package created successfully!")
    print(f"📦 Location: {dist_dir}")
    print(f"📝 Files included:")
    for item in sorted(dist_dir.iterdir()):
        size = ""
        if item.is_file():
            size_mb = item.stat().st_size / (1024 * 1024)
            size = f" ({size_mb:.1f}MB)" if size_mb > 1 else f" ({item.stat().st_size} bytes)"
        print(f"   - {item.name}{size}")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Test the package on a clean machine")
    print(f"   2. Zip the '{dist_name}' folder for distribution")
    print(f"   3. Share with users along with setup instructions")
    
    return True

if __name__ == "__main__":
    create_distribution()