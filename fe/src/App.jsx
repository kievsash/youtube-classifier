import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Clock, Video, AlertTriangle, Shield, Settings, Flame, Wine, Pill } from 'lucide-react';

const VideoModerator = () => {
  const DEFAULT_VIDEO_URL = 'https://www.youtube.com/watch?v=PNFwsOTvJ40';
  
  // Load videoUrl from localStorage or use default
  const [videoUrl, setVideoUrl] = useState(() => {
    const savedUrl = localStorage.getItem('lastVideoUrl');
    return savedUrl || DEFAULT_VIDEO_URL;
  });
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [backendUrl, setBackendUrl] = useState('http://localhost:5001');
  
  // Detection type checkboxes
  const [detectionTypes, setDetectionTypes] = useState({
    nudity: true,
    violence: true,
    drugs: true,
    alcohol: true,
    weapons: true,
    gore: false
  });

  // Save videoUrl to localStorage whenever it changes
  useEffect(() => {
    if (videoUrl.trim()) {
      localStorage.setItem('lastVideoUrl', videoUrl);
    }
  }, [videoUrl]);

  const toggleDetectionType = (type) => {
    setDetectionTypes(prev => ({ ...prev, [type]: !prev[type] }));
  };

  const analyzeVideo = async () => {
    setIsProcessing(true);
    setError('');
    setResults(null);

    try {
      // Create an AbortController with a longer timeout (10 minutes)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minute timeout

      const response = await fetch(`${backendUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          video_url: videoUrl,
          detection_types: detectionTypes
        }),
        signal: controller.signal,
        // Disable default timeout
        keepalive: false
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Server error: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Request timed out. The video might be too long or the server is overloaded.');
      } else {
        setError(err.message || 'Failed to connect to backend. Make sure it\'s running!');
      }
      console.error('Analysis error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getTypeColor = (type) => {
    const colors = {
      nudity: 'bg-red-100 text-red-800 border-red-300',
      violence: 'bg-orange-100 text-orange-800 border-orange-300',
      drugs: 'bg-purple-100 text-purple-800 border-purple-300',
      alcohol: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      weapons: 'bg-gray-700 text-white border-gray-500',
      gore: 'bg-red-900 text-red-100 border-red-700'
    };
    return colors[type] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getTypeIcon = (type) => {
    const icons = {
      nudity: <AlertCircle className="w-4 h-4" />,
      violence: <AlertTriangle className="w-4 h-4" />,
      drugs: <Pill className="w-4 h-4" />,
      alcohol: <Wine className="w-4 h-4" />,
      weapons: <Shield className="w-4 h-4" />,
      gore: <Flame className="w-4 h-4" />
    };
    return icons[type] || <AlertCircle className="w-4 h-4" />;
  };

  const exportResults = () => {
    if (!results) return;
    
    const exportData = {
      video_id: results.video_id,
      analyzed_at: new Date().toISOString(),
      summary: results.summary,
      detections: results.detections.map(d => ({
        type: d.type,
        timespan: `${formatTime(d.start)} - ${formatTime(d.end)}`,
        confidence: (d.confidence * 100).toFixed(1) + '%',
        severity: d.severity
      }))
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `moderation-report-${results.video_id}-${Date.now()}.json`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Video className="w-10 h-10 text-green-400" />
            <h1 className="text-4xl font-bold text-white">AI Video Moderator</h1>
          </div>
          <p className="text-gray-300 text-lg">
            Multi-Model Detection: Nudity, Violence, Drugs, Weapons & More
          </p>
        </div>

        {/* Settings */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Settings className="w-5 h-5 text-gray-300" />
            <span className="text-white font-medium">Backend URL</span>
          </div>
          <input
            type="text"
            value={backendUrl}
            onChange={(e) => setBackendUrl(e.target.value)}
            placeholder="http://localhost:5001"
            className="w-full px-4 py-2 rounded-lg bg-white/20 border border-white/30 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-400"
          />
        </div>

        {/* Detection Types */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 mb-6">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Select Detection Types
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(detectionTypes).map(([type, enabled]) => (
              <label key={type} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={() => toggleDetectionType(type)}
                  className="w-5 h-5 rounded border-gray-300 text-green-500 focus:ring-green-400"
                />
                <span className="text-white capitalize flex items-center gap-2">
                  {getTypeIcon(type)}
                  {type}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Input Section */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 mb-6">
          <label className="block text-white font-medium mb-2">
            YouTube Video URL
          </label>
          <input
            type="text"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=..."
            className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-400 mb-4"
            disabled={isProcessing}
            onKeyDown={(e) => e.key === 'Enter' && !isProcessing && analyzeVideo()}
          />
          
          <button
            onClick={analyzeVideo}
            disabled={isProcessing || !videoUrl.trim()}
            className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isProcessing ? 'Processing Video...' : 'Analyze Video'}
          </button>

          {error && (
            <div className="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200">
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        {results && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="bg-red-500/20 backdrop-blur-lg rounded-xl p-4 border border-red-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-5 h-5 text-red-400" />
                  <h3 className="text-white font-semibold text-sm">Nudity</h3>
                </div>
                <p className="text-2xl font-bold text-red-300">{results.summary?.nudity || 0}</p>
              </div>

              <div className="bg-orange-500/20 backdrop-blur-lg rounded-xl p-4 border border-orange-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-5 h-5 text-orange-400" />
                  <h3 className="text-white font-semibold text-sm">Violence</h3>
                </div>
                <p className="text-2xl font-bold text-orange-300">{results.summary?.violence || 0}</p>
              </div>

              <div className="bg-purple-500/20 backdrop-blur-lg rounded-xl p-4 border border-purple-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <Pill className="w-5 h-5 text-purple-400" />
                  <h3 className="text-white font-semibold text-sm">Drugs</h3>
                </div>
                <p className="text-2xl font-bold text-purple-300">{results.summary?.drugs || 0}</p>
              </div>

              <div className="bg-yellow-500/20 backdrop-blur-lg rounded-xl p-4 border border-yellow-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <Wine className="w-5 h-5 text-yellow-400" />
                  <h3 className="text-white font-semibold text-sm">Alcohol</h3>
                </div>
                <p className="text-2xl font-bold text-yellow-300">{results.summary?.alcohol || 0}</p>
              </div>

              <div className="bg-gray-700/40 backdrop-blur-lg rounded-xl p-4 border border-gray-500/50">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="w-5 h-5 text-gray-300" />
                  <h3 className="text-white font-semibold text-sm">Weapons</h3>
                </div>
                <p className="text-2xl font-bold text-gray-200">{results.summary?.weapons || 0}</p>
              </div>

              <div className="bg-red-900/40 backdrop-blur-lg rounded-xl p-4 border border-red-700/50">
                <div className="flex items-center gap-2 mb-2">
                  <Flame className="w-5 h-5 text-red-300" />
                  <h3 className="text-white font-semibold text-sm">Gore</h3>
                </div>
                <p className="text-2xl font-bold text-red-200">{results.summary?.gore || 0}</p>
              </div>
            </div>

            {/* Timeline */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  <Clock className="w-6 h-6" />
                  Detection Timeline
                </h2>
                <button
                  onClick={exportResults}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm"
                >
                  Export Report
                </button>
              </div>

              {results.detections && results.detections.length === 0 ? (
                <div className="text-center py-12">
                  <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
                  <p className="text-white text-xl font-semibold">No issues detected!</p>
                  <p className="text-gray-400 mt-2">This video appears to be safe.</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {results.detections?.map((detection, idx) => (
                    <div key={idx} className={`p-4 rounded-lg border-2 ${getTypeColor(detection.type)}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          {getTypeIcon(detection.type)}
                          <div>
                            <h3 className="font-semibold capitalize">{detection.type.replace('_', ' ')}</h3>
                            <p className="text-sm mt-1">
                              <span className="font-mono">
                                {formatTime(detection.start)} - {formatTime(detection.end)}
                              </span>
                              <span className="mx-2">•</span>
                              <span>Duration: {detection.end - detection.start}s</span>
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold">
                            {(detection.confidence * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Processing Info */}
            {results.processing_time && (
              <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-4 border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-gray-300 text-sm">
                    <span className="font-semibold">Processing time:</span> {results.processing_time.toFixed(2)}s
                    {results.frames_processed && <span> • Frames: {results.frames_processed}</span>}
                    {results.video_id && <span> • Video ID: {results.video_id}</span>}
                  </p>
                  {results.cached && (
                    <span className="bg-green-500/20 text-green-300 px-3 py-1 rounded-full text-xs font-semibold">
                      ⚡ Cached Result
                    </span>
                  )}
                </div>
                
                {results.optimization_stats && (
                  <div className="mt-3 pt-3 border-t border-slate-600">
                    <p className="text-gray-400 text-xs">
                      <span className="font-semibold">Optimizations:</span> Batch={results.optimization_stats.batch_size}, 
                      FPS={results.optimization_stats.fps_sampling}, 
                      FP16={results.optimization_stats.fp16_enabled ? '✓' : '✗'}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoModerator;
