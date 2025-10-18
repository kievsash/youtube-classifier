# Quick Fix for "[Errno 32] Broken pipe" Error

## 🔴 Problem Identified

Your error:
```
BE error: "[Errno 32] Broken pipe"
URL: https://www.youtube.com/watch?v=PNFwsOTvJ40
```

## 🔍 Root Cause

The video downloads successfully, but **OpenCV cannot read it** because:

1. YouTube delivers the video in MPEG-TS format (incompatible with OpenCV)
2. Without ffmpeg, yt-dlp cannot convert it to a compatible MP4 format
3. OpenCV fails to open the file
4. The backend crashes with a "Broken pipe" error when trying to respond

**Diagnostic output showed:**
```
WARNING: Possible MPEG-TS in MP4 container or malformed AAC timestamps. 
Install ffmpeg to fix this automatically
❌ OpenCV cannot read video!
```

## ✅ Solution

**Install FFmpeg** - it's required for the app to work with most YouTube videos.

### For macOS (your system):
```bash
brew install ffmpeg
```

### For Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### For Windows:
Download from: https://ffmpeg.org/download.html

## 🚀 After Installing FFmpeg

1. **Verify installation:**
   ```bash
   ffmpeg -version
   ```

2. **Restart your backend server:**
   ```bash
   cd be
   source venv/bin/activate  # or venv311/bin/activate
   python app.py
   ```

3. **Test again with your URL:**
   - The same video that failed before should now work
   - yt-dlp will automatically use ffmpeg to convert the video
   - OpenCV will be able to read it

## 🔧 Changes Made to Fix This

I've updated your backend code to:

1. ✅ **Better error messages** - tells you exactly what's wrong
2. ✅ **Improved video format selection** - tries multiple formats
3. ✅ **Auto-detection of ffmpeg** - uses it if available
4. ✅ **Better error handling** - no more mysterious "Broken pipe" errors
5. ✅ **Frontend timeout increased** - from default to 10 minutes
6. ✅ **Added cleanup on errors** - removes temporary files

## 📝 What Changed in the Code

### Backend (`be/app.py`):
- Improved download format selection for better compatibility
- Added ffmpeg post-processing when available
- Better error messages that explain the issue
- Proper cleanup of temporary files on error
- More verbose logging to debug issues

### Frontend (`fe/src/App.jsx`):
- Increased request timeout to 10 minutes
- Better error display
- Handles server errors gracefully

## 🧪 Test After Installing

Run this diagnostic script to verify everything works:

```bash
cd be
source venv/bin/activate
python test_video_download.py "https://www.youtube.com/watch?v=PNFwsOTvJ40"
```

You should see:
```
✅ Download successful!
✅ OpenCV can read video
✅ All tests passed!
```

## 📚 Additional Resources

- [INSTALL_FFMPEG.md](be/INSTALL_FFMPEG.md) - Detailed ffmpeg installation guide
- [be/README.md](be/README.md) - Updated with ffmpeg requirement

## 💡 Why This Happened

YouTube uses various video formats and codecs. Some videos are delivered in formats like:
- MPEG-TS (MPEG Transport Stream)
- fragmented MP4
- HLS streams

These formats need to be remuxed/converted to standard MP4 that OpenCV can read. 
FFmpeg handles this conversion automatically.

**Without ffmpeg:** Download succeeds → OpenCV fails → Connection breaks → "Broken pipe"  
**With ffmpeg:** Download succeeds → Auto-convert → OpenCV works → Success! ✅


