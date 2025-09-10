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

After pushing this workflow:

1. Go to your GitHub repo
2. Navigate to **Actions** tab
3. Run workflow manually to test it works
4. Create your first tag: `git tag v0.1.0 && git push origin v0.1.0`
5. Check the **Releases** page for your executables

## Security Note

The workflow handles missing `.env` and `credentials.json` files by creating placeholders. For security, consider:
- Using GitHub Secrets for sensitive data
- Building without embedded credentials for public distribution
- Having users provide their own configuration files