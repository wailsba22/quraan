# Quran Video Generator - Android APK

This repository contains an automated system to build Android APK files for the Quran Video Generator app using GitHub Actions.

## 🚀 Automatic APK Building

Every time you push code to this repository, GitHub Actions will automatically:
1. Build the Android APK
2. Upload it as an artifact
3. Create a release (if you push a tag)

## 📦 How to Get the APK

### Method 1: Download from GitHub Actions (Latest Build)
1. Go to the **Actions** tab in this repository
2. Click on the latest successful workflow run
3. Scroll down to **Artifacts**
4. Download `quran-video-generator-apk`
5. Extract the ZIP file to get the APK

### Method 2: Download from Releases (Tagged Versions)
1. Go to the **Releases** section
2. Download the APK from the latest release
3. Install on your Android device

## 🏷️ Creating a Release

To trigger a release build with automatic APK publishing:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Replace `v1.0.0` with your desired version number.

## 📱 Installing the APK

1. Download the APK file to your Android device
2. Enable "Install from Unknown Sources" in your Android settings:
   - Settings > Security > Unknown Sources (Android 7 and below)
   - Settings > Apps > Special Access > Install Unknown Apps (Android 8+)
3. Open the APK file and tap Install
4. Grant necessary permissions when prompted

## 🔧 Local Development

If you want to build the APK locally instead of using GitHub Actions:

### Requirements
- Ubuntu/Linux system
- Python 3.10+
- Buildozer
- Android SDK/NDK (automatically downloaded by Buildozer)

### Build Commands
```bash
# Install dependencies
pip install buildozer cython

# Build debug APK
buildozer android debug

# Build release APK (requires keystore)
buildozer android release
```

The APK will be generated in the `bin/` directory.

## 📋 Features

- Generate random Quran video clips with subtitles
- Generate custom videos from specific Surahs and Ayahs
- 9 different reciters to choose from
- 10 languages for translations (Arabic always included)
- Automatic subtitle synchronization
- Beautiful background videos
- Portrait mode (9:16 aspect ratio)
- Offline functionality (no server required)

## 🛠️ Project Files

- `android_app.py` - Main Kivy application
- `quran_video_generator.py` - Core video generation engine
- `main.py` - Entry point for Buildozer
- `buildozer.spec` - Android build configuration
- `.github/workflows/build-apk.yml` - GitHub Actions automation

## ⚙️ Configuration

The app requires:
- Internet permission (to download Quran audio/text)
- Storage permission (to save generated videos)
- FFmpeg (bundled with app)

Videos are saved to: `/storage/emulated/0/QuranVideos/`

## 📝 Notes

- First build may take 20-40 minutes as GitHub Actions downloads Android SDK/NDK
- Subsequent builds are faster due to caching
- APK size will be approximately 50-100MB due to FFmpeg and dependencies

## 🐛 Troubleshooting

If the build fails:
1. Check the Actions tab for error logs
2. Ensure all Python files are present in the repository
3. Verify `buildozer.spec` configuration is correct
4. Check that no large files exceed GitHub's 100MB limit

## 📄 License

This project uses:
- FFmpeg (LGPL/GPL)
- Quran data from alquran.cloud API
- Python and Kivy frameworks
