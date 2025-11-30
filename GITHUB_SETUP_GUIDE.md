# 🚀 GitHub Actions APK Build Setup Guide

## Step 1: Initialize Git Repository

Open PowerShell in your project folder and run:

```powershell
git init
git add .
git commit -m "Initial commit: Quran Video Generator for Android"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Name your repository (e.g., `quran-video-generator`)
3. Set visibility (Public or Private - both work)
4. **DO NOT** initialize with README, .gitignore, or license
5. Click "Create repository"

## Step 3: Push to GitHub

Copy the commands from GitHub's "push an existing repository" section:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual values.

## Step 4: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. GitHub will automatically detect the workflow file
4. The build will start automatically!

## Step 5: Monitor the Build

1. In the Actions tab, click on the running workflow
2. Click on the "build" job to see live logs
3. First build takes 20-40 minutes (downloads Android SDK/NDK)
4. Future builds are faster (5-15 minutes) due to caching

## Step 6: Download Your APK

### Option A: From Actions Artifacts
1. Wait for the build to complete (green checkmark)
2. Scroll down to the "Artifacts" section
3. Click "quran-video-generator-apk" to download
4. Extract the ZIP file to get the APK

### Option B: Create a Release (Recommended)
1. After first successful build, create a tag:
   ```powershell
   git tag v1.0.0
   git push origin v1.0.0
   ```
2. GitHub Actions will automatically create a release
3. Go to the "Releases" section in your repository
4. Download the APK directly from the release

## Step 7: Install on Android

1. Transfer the APK to your Android device
2. Enable "Install from Unknown Sources":
   - **Android 8+**: Settings > Apps > Special Access > Install Unknown Apps > Select your browser/file manager > Allow
   - **Android 7 and below**: Settings > Security > Unknown Sources > Enable
3. Open the APK file and tap "Install"
4. Grant permissions when prompted (Internet and Storage)

## 🔄 Automatic Updates

Every time you push code to GitHub, a new APK will be automatically built:

```powershell
git add .
git commit -m "Updated app"
git push
```

Check the Actions tab to monitor the build progress.

## 🏷️ Version Releases

To create numbered releases:

```powershell
git tag v1.0.1
git push origin v1.0.1
```

The APK will appear in the Releases section automatically.

## ⚠️ Important Notes

1. **First Build Duration**: 20-40 minutes (one-time Android SDK download)
2. **Subsequent Builds**: 5-15 minutes (cached dependencies)
3. **APK Size**: Approximately 50-100MB (includes FFmpeg)
4. **Build Triggers**: Automatic on push to main/master branch
5. **Manual Trigger**: Available in Actions tab (workflow_dispatch)

## 🛠️ Troubleshooting

### Build Failed?
1. Check the Actions tab for error logs
2. Click on the failed job to see detailed logs
3. Common issues:
   - Missing files: Ensure all .py files are committed
   - Large files: GitHub has 100MB file size limit
   - Syntax errors: Test Python files locally first

### Cannot Push to GitHub?
```powershell
# If you need to authenticate
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Use personal access token instead of password
# Generate at: https://github.com/settings/tokens
```

### APK Won't Install?
1. Check Android version compatibility (minimum API 21 / Android 5.0)
2. Ensure "Install from Unknown Sources" is enabled
3. Try uninstalling previous versions first
4. Check device storage space

## 📱 Testing the APK

After installation:
1. Open the app
2. Grant storage and internet permissions
3. Try generating a random video (1 count, English translation)
4. Check `/storage/emulated/0/QuranVideos/` for output
5. Verify video plays correctly with subtitles

## 🎯 Next Steps

- Share the APK with others via GitHub Releases
- Add more features and push updates
- Monitor build times and optimize if needed
- Consider signing APK for Google Play Store (requires keystore setup)

## 📊 Build Status Badge

Add this to your repository README to show build status:

```markdown
![Build Status](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/build-apk.yml/badge.svg)
```

---

**Need Help?** Check the Actions logs for detailed error messages. The GitHub Actions runner provides comprehensive debugging information.
