# Release Instructions

## Creating a New Release

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Update Gmail processor"
   git push
   ```

2. **Create and push a tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **GitHub Actions will automatically**:
   - Build executables for Windows and macOS
   - Create a GitHub release
   - Upload both executables as release assets

## Manual Testing

To test the workflow without creating a release:

```bash
# Push to trigger PR workflow (builds but doesn't release)
git push origin your-branch
```

## Release Artifacts

Each release creates:
- `gmail_processor_windows_x64.exe` - Windows executable
- `gmail_processor_macos_arm64` - macOS executable (Apple Silicon)

## Workflow Features

- ✅ **Cross-platform builds** (Windows + macOS)
- ✅ **Automatic releases** on git tags
- ✅ **Artifact caching** for faster builds
- ✅ **Error handling** for missing files
- ✅ **Manual trigger** option via GitHub UI

## First Release Setup

**IMPORTANT**: Before creating releases, you must configure GitHub Secrets.

### Step 1: Configure GitHub Secrets
See `GITHUB_SECRETS_SETUP.md` for detailed instructions.

**Required secrets**:
- `SUPABASE_URL`
- `SUPABASE_KEY` 
- `OPENAI_API_KEY`
- `GMAIL_CREDENTIALS_JSON` (recommended)

### Step 2: Create Your First Release
After setting up secrets:

1. Push your changes: `git push`
2. Create your first tag: `git tag v1.0.0 && git push origin v1.0.0`
3. Check the **Releases** page for your executables

## Security Benefits

✅ **Credentials managed via GitHub Secrets**
✅ **No sensitive data in Git history**  
✅ **Encrypted credential storage**
✅ **Masked in workflow logs**