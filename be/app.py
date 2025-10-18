from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import cv2
import os
import time
# Try to import ML libraries - make them optional for development
try:
    from nudenet import NudeDetector
    NUDENET_AVAILABLE = True
except ImportError:
    NUDENET_AVAILABLE = False
    print("⚠️  NudeNet not available - nudity detection disabled")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️  PyTorch not available - running in limited mode")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers not available - some detections disabled")

import numpy as np
# from pymongo import MongoClient
from datetime import datetime
# import hashlib

app = Flask(__name__)
CORS(app)

# Configure Flask for long-running requests
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024  # 16GB max request size

# MongoDB connection (commented out for local development)
# MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
# mongo_client = MongoClient(MONGO_URI)
# db = mongo_client['video_moderation']
# results_collection = db['analysis_results']

# Create index on video_id and detection_types for fast lookup
# results_collection.create_index([('video_id', 1), ('detection_hash', 1)])

# Initialize models
print("Loading models...")
nude_detector = None
nsfw_classifier = None

if NUDENET_AVAILABLE:
    try:
        nude_detector = NudeDetector()
        print("✅ NudeNet loaded")
    except Exception as e:
        print(f"⚠️  Failed to load NudeNet: {e}")

if TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE:
    try:
        nsfw_classifier = pipeline("image-classification", 
                                  model="Falconsai/nsfw_image_detection",
                                  device=0 if torch.cuda.is_available() else -1)
        print("✅ NSFW classifier loaded")
    except Exception as e:
        print(f"⚠️  Failed to load NSFW classifier: {e}")

# Violence/drugs detector (amshrbo model)
# Load your violence detection model here
# violence_model = load_model('path/to/violence_model')

# Configuration
CONFIDENCE_THRESHOLD = 0.6
BATCH_SIZE = 32  # Process 32 frames at once
FPS_SAMPLING = 0.5  # Sample 0.5 frames per second (2x faster than 1 FPS)
USE_FP16 = TORCH_AVAILABLE and torch.cuda.is_available()  # Use half precision if GPU available

if USE_FP16:
    print("✅ Using FP16 mixed precision for faster inference")

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    ydl = yt_dlp.YoutubeDL({'quiet': True})
    try:
        info = ydl.extract_info(url, download=False)
        return info.get('id', None)
    except:
        # Fallback: extract from URL patterns
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[-1].split('?')[0]
        elif 'watch?v=' in url:
            return url.split('watch?v=')[-1].split('&')[0]
        return None

# MongoDB caching functions (commented out for local development)
# def create_detection_hash(detection_types):
#     """Create hash of detection types for cache lookup"""
#     # Sort keys to ensure consistent hash
#     sorted_types = sorted([k for k, v in detection_types.items() if v])
#     hash_string = ','.join(sorted_types)
#     return hashlib.md5(hash_string.encode()).hexdigest()

# def get_cached_result(video_id, detection_hash):
#     """Check if analysis exists in MongoDB"""
#     result = results_collection.find_one({
#         'video_id': video_id,
#         'detection_hash': detection_hash
#     })
#     
#     if result:
#         # Remove MongoDB _id field
#         result.pop('_id', None)
#         print(f"✅ Cache HIT for video {video_id}")
#         return result
#     
#     print(f"❌ Cache MISS for video {video_id}")
#     return None

# def save_result_to_mongo(video_id, detection_types, detections, summary, frames_processed, processing_time):
#     """Save analysis result to MongoDB"""
#     detection_hash = create_detection_hash(detection_types)
#     
#     document = {
#         'video_id': video_id,
#         'detection_hash': detection_hash,
#         'detection_types': detection_types,
#         'detections': detections,
#         'summary': summary,
#         'frames_processed': frames_processed,
#         'processing_time': processing_time,
#         'analyzed_at': datetime.utcnow(),
#         'cached': False  # Mark as fresh analysis
#     }
#     
#     # Upsert: update if exists, insert if not
#     results_collection.update_one(
#         {'video_id': video_id, 'detection_hash': detection_hash},
#         {'$set': document},
#         upsert=True
#     )
#     
#     print(f"💾 Saved result to MongoDB for video {video_id}")
#     return document

def download_video(url):
    """Download YouTube video - optimized for speed"""
    output_path = 'downloaded_video.mp4'
    
    # Remove existing file if it exists
    if os.path.exists(output_path):
        os.remove(output_path)
    
    # Check if ffmpeg is available
    has_ffmpeg = os.system('which ffmpeg > /dev/null 2>&1') == 0
    if not has_ffmpeg:
        print("⚠️  FFmpeg not found - using pre-merged video formats (may have lower quality)")
    
    ydl_opts = {
        # Prefer pre-merged formats (no ffmpeg needed), then fall back to merging if ffmpeg is available
        # Progressive MP4 formats work best with OpenCV
        'format': (
            'best[ext=mp4][height<=480]/best[height<=480]/worst[ext=mp4]/worst' 
            if not has_ffmpeg else
            'bestvideo[ext=mp4][height<=480]+bestaudio[ext=m4a]/best[ext=mp4][height<=480]/worst[ext=mp4]/worst'
        ),
        'outtmpl': output_path,
        'quiet': False,  # Show errors
        'no_warnings': False,  # Show warnings
        'socket_timeout': 30,  # Add socket timeout
        'retries': 3,  # Retry on failure
        'fragment_retries': 3,
        'ignoreerrors': False,
        'nocheckcertificate': True,  # Some videos have certificate issues
        'merge_output_format': 'mp4',  # Force MP4 container
        # Post-processing to ensure OpenCV compatibility (only if ffmpeg available)
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }] if has_ffmpeg else [],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"📥 Starting download: {url}")
            info = ydl.extract_info(url, download=True)
            print(f"✅ Downloaded: {info.get('title', 'Unknown')}")
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        raise ValueError(f"Video download failed: {str(e)}")
    
    # Verify the file was downloaded and has content
    if not os.path.exists(output_path):
        raise ValueError("Video download failed - file was not created")
    
    if os.path.getsize(output_path) == 0:
        os.remove(output_path)
        raise ValueError("Video download failed - file is empty")
    
    print(f"✅ Video file size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
    return output_path

def extract_frames(video_path, fps=FPS_SAMPLING):
    """Extract frames from video - optimized version"""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(
            "Failed to open video file. The video format may not be compatible with OpenCV. "
            "This is usually fixed by installing ffmpeg:\n"
            "  - macOS: brew install ffmpeg\n"
            "  - Ubuntu/Debian: apt-get install ffmpeg\n"
            "  - Windows: Download from https://ffmpeg.org/download.html"
        )
    
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    
    if video_fps == 0 or video_fps is None:
        cap.release()
        raise ValueError(
            "Failed to get video FPS. The video file may be corrupted, invalid, or in an incompatible format. "
            "Installing ffmpeg may help resolve this issue."
        )
    
    frame_interval = int(video_fps / fps)
    
    frames = []
    frame_count = 0
    extracted_count = 0
    
    # Pre-allocate list for better performance
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    estimated_extracts = int(total_frames / frame_interval)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            # Resize frame to reduce processing (optional but faster)
            # frame = cv2.resize(frame, (640, 480))
            
            frame_path = f'frame_{extracted_count}.jpg'
            cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frames.append({
                'path': frame_path,
                'timestamp': frame_count / video_fps
            })
            extracted_count += 1
        
        frame_count += 1
    
    cap.release()
    print(f"✅ Extracted {len(frames)} frames (sampled at {fps} FPS)")
    return frames

def detect_nudity(frame_path):
    """Detect nudity using NudeNet"""
    if not nude_detector:
        return []
    
    results = nude_detector.detect(frame_path)
    detections = []
    
    for det in results:
        if det['score'] > CONFIDENCE_THRESHOLD:
            label = det['class']
            if label in ['FEMALE_BREAST_EXPOSED', 'FEMALE_GENITALIA_EXPOSED', 
                        'MALE_GENITALIA_EXPOSED', 'BUTTOCKS_EXPOSED']:
                detections.append({
                    'type': 'nudity',
                    'confidence': det['score'],
                    'severity': 'high'
                })
    
    return detections

def detect_nudity_batch(frame_paths):
    """BATCH PROCESSING: Detect nudity for multiple frames at once"""
    all_detections = []
    
    # NudeNet supports batch processing
    for frame_path in frame_paths:
        detections = detect_nudity(frame_path)
        all_detections.append(detections)
    
    return all_detections

def detect_nsfw_general_batch(frame_paths):
    """BATCH PROCESSING: General NSFW detection for multiple frames"""
    all_detections = []
    
    if not nsfw_classifier:
        return [[] for _ in frame_paths]
    
    # Process all frames at once (much faster!)
    results = nsfw_classifier(frame_paths)
    
    for result in results:
        frame_detections = []
        for item in result:
            if item['label'] == 'nsfw' and item['score'] > CONFIDENCE_THRESHOLD:
                frame_detections.append({
                    'type': 'adult_content',
                    'confidence': item['score'],
                    'severity': 'medium'
                })
        all_detections.append(frame_detections)
    
    return all_detections

def detect_violence_drugs(frame_path):
    """Detect violence and drugs"""
    # TODO: Implement violence/drugs detection
    # This would use the amshrbo model or similar
    detections = []
    
    # Example placeholder:
    # violence_score = violence_model.predict(frame_path)
    # if violence_score > CONFIDENCE_THRESHOLD:
    #     detections.append({
    #         'type': 'violence',
    #         'confidence': violence_score,
    #         'severity': 'high'
    #     })
    
    return detections

def detect_violence_drugs_batch(frame_paths):
    """BATCH PROCESSING: Detect violence and drugs for multiple frames"""
    all_detections = []
    
    # TODO: Implement batch violence detection
    # For now, process individually (replace with batch model)
    for frame_path in frame_paths:
        detections = detect_violence_drugs(frame_path)
        all_detections.append(detections)
    
    return all_detections

def detect_weapons_alcohol(frame_path):
    """Detect weapons and alcohol"""
    # TODO: Implement object detection for weapons, alcohol, drugs
    # You can use YOLO or other object detection models
    detections = []
    
    # Example placeholder
    # objects = yolo_model(frame_path)
    # for obj in objects:
    #     if obj['class'] in ['gun', 'knife']:
    #         detections.append({
    #             'type': 'weapons',
    #             'confidence': obj['confidence'],
    #             'severity': 'high'
    #         })
    #     elif obj['class'] in ['beer', 'wine']:
    #         detections.append({
    #             'type': 'alcohol',
    #             'confidence': obj['confidence'],
    #             'severity': 'low'
    #         })
    
    return detections

def detect_weapons_alcohol_batch(frame_paths):
    """BATCH PROCESSING: Detect weapons and alcohol for multiple frames"""
    all_detections = []
    
    # TODO: Implement batch object detection with YOLO
    # For now, process individually (replace with batch model)
    for frame_path in frame_paths:
        detections = detect_weapons_alcohol(frame_path)
        all_detections.append(detections)
    
    return all_detections

def analyze_frames(frames, detection_types):
    """Analyze frames with selected detection types - OPTIMIZED WITH BATCHING"""
    all_detections = []
    total_frames = len(frames)
    
    print(f"🚀 Processing {total_frames} frames in batches of {BATCH_SIZE}")
    
    # Process frames in batches for massive speedup
    for batch_start in range(0, total_frames, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total_frames)
        batch_frames = frames[batch_start:batch_end]
        
        batch_paths = [f['path'] for f in batch_frames]
        batch_timestamps = [f['timestamp'] for f in batch_frames]
        
        print(f"  Processing batch {batch_start//BATCH_SIZE + 1}/{(total_frames + BATCH_SIZE - 1)//BATCH_SIZE}")
        
        # Run enabled detectors on batch
        batch_results = [[] for _ in range(len(batch_frames))]
        
        if detection_types.get('nudity', False):
            nudity_results = detect_nudity_batch(batch_paths)
            for i, dets in enumerate(nudity_results):
                batch_results[i].extend(dets)
        
        if detection_types.get('violence', False) or detection_types.get('drugs', False):
            violence_results = detect_violence_drugs_batch(batch_paths)
            for i, dets in enumerate(violence_results):
                batch_results[i].extend(dets)
        
        if detection_types.get('weapons', False) or detection_types.get('alcohol', False):
            weapons_results = detect_weapons_alcohol_batch(batch_paths)
            for i, dets in enumerate(weapons_results):
                batch_results[i].extend(dets)
        
        # Add timestamps to detections
        for i, frame_detections in enumerate(batch_results):
            for det in frame_detections:
                det['timestamp'] = batch_timestamps[i]
                all_detections.append(det)
        
        # Clean up batch frames
        for path in batch_paths:
            if os.path.exists(path):
                os.remove(path)
    
    print(f"✅ Found {len(all_detections)} detections")
    return all_detections

def cluster_detections(detections, gap_threshold=5):
    """Cluster detections into timespans"""
    if not detections:
        return []
    
    detections.sort(key=lambda x: (x['type'], x['timestamp']))
    timespans = []
    current_span = None
    
    for det in detections:
        if not current_span or \
           det['type'] != current_span['type'] or \
           det['timestamp'] - current_span['end'] > gap_threshold:
            if current_span:
                timespans.append(current_span)
            current_span = {
                'type': det['type'],
                'start': int(det['timestamp']),
                'end': int(det['timestamp']),
                'confidence': det['confidence'],
                'severity': det.get('severity', 'medium')
            }
        else:
            current_span['end'] = int(det['timestamp'])
            current_span['confidence'] = max(current_span['confidence'], det['confidence'])
    
    if current_span:
        timespans.append(current_span)
    
    return timespans

@app.route('/analyze', methods=['POST'])
def analyze_video():
    video_path = None
    try:
        data = request.json
        video_url = data.get('video_url')
        detection_types = data.get('detection_types', {})
        
        if not video_url:
            return jsonify({'error': 'No video URL provided'}), 400
        
        print(f"\n{'='*60}")
        print(f"🎬 New analysis request for: {video_url}")
        print(f"🔍 Detection types: {[k for k, v in detection_types.items() if v]}")
        print(f"{'='*60}\n")
        
        # Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({'error': 'Could not extract video ID from URL'}), 400
        
        print(f"📝 Video ID: {video_id}")
        
        # MongoDB caching disabled for local development
        # detection_hash = create_detection_hash(detection_types)
        # cached_result = get_cached_result(video_id, detection_hash)
        # if cached_result:
        #     cached_result['cached'] = True
        #     return jsonify(cached_result)
        
        # Process video
        start_time = time.time()
        
        # Download video
        download_start = time.time()
        video_path = download_video(video_url)
        download_time = time.time() - download_start
        print(f"⏱️  Download time: {download_time:.2f}s")
        
        # Extract frames
        print("\n🎞️  Extracting frames...")
        extract_start = time.time()
        frames = extract_frames(video_path, fps=FPS_SAMPLING)
        extract_time = time.time() - extract_start
        print(f"⏱️  Frame extraction: {extract_time:.2f}s")
        
        # Analyze frames
        print(f"\n🔍 Analyzing {len(frames)} frames with batch processing...")
        analyze_start = time.time()
        detections = analyze_frames(frames, detection_types)
        analyze_time = time.time() - analyze_start
        print(f"⏱️  Frame analysis: {analyze_time:.2f}s")
        
        # Cluster detections
        timespans = cluster_detections(detections)
        
        # Generate summary
        summary = {
            'nudity': sum(1 for t in timespans if t['type'] == 'nudity'),
            'violence': sum(1 for t in timespans if t['type'] == 'violence'),
            'drugs': sum(1 for t in timespans if t['type'] == 'drugs'),
            'alcohol': sum(1 for t in timespans if t['type'] == 'alcohol'),
            'weapons': sum(1 for t in timespans if t['type'] == 'weapons'),
            'gore': sum(1 for t in timespans if t['type'] == 'gore')
        }
        
        # Clean up
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
            print(f"🗑️  Cleaned up video file")
        
        processing_time = time.time() - start_time
        print(f"\n✅ Analysis complete! Total time: {processing_time:.2f}s")
        print(f"{'='*60}\n")
        
        # MongoDB saving disabled for local development
        # result = save_result_to_mongo(
        #     video_id=video_id,
        #     detection_types=detection_types,
        #     detections=timespans,
        #     summary=summary,
        #     frames_processed=len(frames),
        #     processing_time=processing_time
        # )
        
        return jsonify({
            'video_id': video_id,
            'detections': timespans,
            'summary': summary,
            'frames_processed': len(frames),
            'processing_time': processing_time,
            'cached': False,
            'optimization_stats': {
                'batch_size': BATCH_SIZE,
                'fps_sampling': FPS_SAMPLING,
                'fp16_enabled': USE_FP16
            }
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ ERROR: {error_msg}")
        print(f"{'='*60}\n")
        
        # Clean up on error
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                print(f"🗑️  Cleaned up video file after error")
            except:
                pass
        
        # Clean up any leftover frame files
        try:
            import glob
            for frame_file in glob.glob('frame_*.jpg'):
                os.remove(frame_file)
        except:
            pass
        
        return jsonify({'error': error_msg}), 500

@app.route('/health', methods=['GET'])
def health():
    # MongoDB check disabled for local development
    # try:
    #     mongo_client.admin.command('ping')
    #     mongo_status = 'connected'
    # except:
    #     mongo_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy', 
        'gpu_available': TORCH_AVAILABLE and torch.cuda.is_available(),
        'torch_available': TORCH_AVAILABLE,
        'nudenet_available': NUDENET_AVAILABLE,
        'transformers_available': TRANSFORMERS_AVAILABLE,
        'models_loaded': nude_detector is not None or nsfw_classifier is not None,
        'mongodb': 'disabled'
    })

# MongoDB cache endpoints disabled for local development
# @app.route('/cache/stats', methods=['GET'])
# def cache_stats():
#     """Get cache statistics"""
#     try:
#         total_cached = results_collection.count_documents({})
#         unique_videos = len(results_collection.distinct('video_id'))
#         
#         return jsonify({
#             'total_analyses': total_cached,
#             'unique_videos': unique_videos,
#             'cache_size_mb': db.command('collstats', 'analysis_results')['size'] / (1024*1024)
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/cache/clear', methods=['POST'])
# def clear_cache():
#     """Clear all cached results"""
#     try:
#         result = results_collection.delete_many({})
#         return jsonify({
#             'message': 'Cache cleared',
#             'deleted_count': result.deleted_count
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@app.route('/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config = {
        'batch_size': BATCH_SIZE,
        'fps_sampling': FPS_SAMPLING,
        'confidence_threshold': CONFIDENCE_THRESHOLD,
        'fp16_enabled': USE_FP16,
    }
    
    if TORCH_AVAILABLE:
        config['gpu_name'] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'
        config['gpu_memory_gb'] = torch.cuda.get_device_properties(0).total_memory / (1024**3) if torch.cuda.is_available() else 0
    else:
        config['gpu_name'] = 'N/A (PyTorch not available)'
        config['gpu_memory_gb'] = 0
    
    return jsonify(config)

if __name__ == '__main__':
    print("="*60)
    print("🚀 Video Moderation API Starting...")
    print(f"   PyTorch Available: {TORCH_AVAILABLE}")
    if TORCH_AVAILABLE:
        print(f"   GPU Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
    print(f"   NudeNet: {'✅ Loaded' if nude_detector else '❌ Not available'}")
    print(f"   NSFW Classifier: {'✅ Loaded' if nsfw_classifier else '❌ Not available'}")
    print(f"   Batch Size: {BATCH_SIZE}")
    print(f"   FPS Sampling: {FPS_SAMPLING}")
    print(f"   FP16 Mode: {USE_FP16}")
    print(f"   MongoDB: DISABLED (local development)")
    print("="*60)
    print("📡 Server will be available at: http://localhost:5001")
    
    # Run with threaded mode and increased timeouts
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5001, app, 
               use_reloader=False, 
               use_debugger=False, 
               threaded=True,
               # Allow long-running requests
               request_handler=None)
