# Installing FFmpeg

FFmpeg is **required** for the YouTube classifier to work properly. It ensures that downloaded videos are in a format that OpenCV can read.

## Why FFmpeg?

Many YouTube videos use formats like MPEG-TS or have incompatible timestamps that OpenCV cannot process directly. FFmpeg automatically converts these to a compatible MP4 format.

## Installation

### macOS

```bash
brew install ffmpeg
```

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Windows

1. Download FFmpeg from: https://ffmpeg.org/download.html
2. Extract the archive
3. Add the `bin` folder to your system PATH

### Verify Installation

After installation, verify it works:

```bash
ffmpeg -version
```

You should see version information printed to the console.

## Common Errors Without FFmpeg

**Error:** `Failed to open video file. The video format may not be compatible with OpenCV.`

**Cause:** The video was downloaded in a format that OpenCV cannot read (e.g., MPEG-TS in MP4 container).

**Solution:** Install ffmpeg using the instructions above.

---

**Warning:** `WARNING: Possible MPEG-TS in MP4 container or malformed AAC timestamps`

**Cause:** yt-dlp downloaded a video with incompatible encoding.

**Solution:** Install ffmpeg - it will automatically fix this during download.

## After Installing FFmpeg

1. Restart your backend server
2. The application will automatically detect ffmpeg and use it for post-processing
3. Videos should now work properly with OpenCV


