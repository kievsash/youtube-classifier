#!/usr/bin/env python3
"""
Quick test script to diagnose video download issues
"""
import sys
import yt_dlp

def test_download(url):
    """Test downloading a specific YouTube video"""
    print(f"🎬 Testing video: {url}\n")
    
    # First, try to extract info without downloading
    print("Step 1: Extracting video info...")
    ydl_opts_info = {
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"✅ Video ID: {info.get('id')}")
            print(f"✅ Title: {info.get('title')}")
            print(f"✅ Duration: {info.get('duration')}s")
            print(f"✅ Available formats: {len(info.get('formats', []))}")
            
            # Show available formats
            print("\n📋 Available video formats:")
            for fmt in info.get('formats', [])[:10]:  # Show first 10
                if fmt.get('height'):
                    print(f"  - {fmt.get('format_id')}: {fmt.get('height')}p, "
                          f"{fmt.get('ext')}, {fmt.get('filesize', 0) / (1024*1024):.1f}MB")
    except Exception as e:
        print(f"❌ Failed to extract info: {e}")
        return False
    
    # Now try to download
    print("\n\nStep 2: Attempting download...")
    output_path = 'test_download.mp4'
    
    ydl_opts_download = {
        'format': 'worst[height>=360][ext=mp4]/worst[ext=mp4]/worst',
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': False,
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
        'nocheckcertificate': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
            ydl.download([url])
        print(f"✅ Download successful!")
        
        import os
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024*1024)
            print(f"✅ File size: {size_mb:.2f}MB")
            
            # Test if OpenCV can read it
            print("\n\nStep 3: Testing OpenCV compatibility...")
            import cv2
            cap = cv2.VideoCapture(output_path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                print(f"✅ OpenCV can read video")
                print(f"✅ FPS: {fps}")
                print(f"✅ Total frames: {frame_count}")
                cap.release()
            else:
                print(f"❌ OpenCV cannot read video!")
            
            # Clean up
            os.remove(output_path)
            print(f"\n🗑️  Cleaned up test file")
        else:
            print(f"❌ File was not created!")
        
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = "https://www.youtube.com/watch?v=PNFwsOTvJ40"
    
    print("="*60)
    print("YouTube Video Download Diagnostics")
    print("="*60 + "\n")
    
    success = test_download(test_url)
    
    print("\n" + "="*60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("="*60)


