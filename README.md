# 🎥 YouTube Video Classifier

AI-powered video content moderation system for analyzing and classifying YouTube videos with real-time detection of nudity, violence, drugs, alcohol, weapons, and gore.

## 📁 Project Structure

```
youtube-classifier/
├── be/                    # Backend - Flask API with ML models
│   ├── app.py            # Main Flask application
│   ├── requirements.txt  # Python dependencies
│   └── venv/            # Python virtual environment
├── fe/                    # Frontend - React + Vite
│   ├── src/
│   │   ├── App.jsx      # Main React component
│   │   └── main.jsx     # React entry point
│   ├── package.json     # Frontend dependencies
│   └── dist/            # Production build output
├── package.json          # Root package.json (this file)
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.11 or higher)
- **pip** (Python package manager)

### 1. Install All Dependencies

Run this command from the root directory to install both frontend and backend dependencies:

```bash
npm run install:all
```

Or install them separately:

```bash
# Install frontend dependencies
npm run install:fe

# Install backend dependencies (creates Python venv and installs packages)
npm run install:be
```

### 2. Start Development Servers

Start both frontend and backend simultaneously:

```bash
npm run dev
```

This will:
- Start the **Flask backend** on `http://localhost:5000`
- Start the **React frontend** on `http://localhost:5173`

Or run them separately:

```bash
# Start only frontend
npm run dev:fe

# Start only backend
npm run dev:be
```

### 3. Access the Application

Open your browser and navigate to:
- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:5000](http://localhost:5000)

## 📦 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run install:all` | Install dependencies for both frontend and backend |
| `npm run install:fe` | Install frontend dependencies only |
| `npm run install:be` | Setup Python venv and install backend dependencies |
| `npm run dev` or `npm start` | Start both frontend and backend in development mode |
| `npm run dev:fe` | Start frontend development server only |
| `npm run dev:be` | Start backend Flask server only |
| `npm run build` | Build frontend for production |
| `npm run preview` | Preview production build locally |
| `npm run clean` | Remove all node_modules and build artifacts |
| `npm run health` | Check if both servers are running |

## 🎯 Features

### Backend Features
- ✅ **6 Detection Types**: Nudity, Violence, Drugs, Alcohol, Weapons, Gore
- ✅ **YouTube Video Download**: Automatic video fetching with yt-dlp
- ✅ **ML Models**: NudeNet, Falconsai NSFW, Violence detection
- ✅ **GPU Acceleration**: NVIDIA CUDA support for faster processing
- ✅ **MongoDB Caching**: Optional caching for repeated analyses
- ✅ **Batch Processing**: Optimized frame analysis
- ✅ **RESTful API**: Clean JSON API endpoints

### Frontend Features
- ✅ **Modern UI**: Beautiful gradient design with Tailwind CSS
- ✅ **Real-time Status**: Live processing updates
- ✅ **Timeline View**: Detailed timestamp tracking
- ✅ **Detection Filters**: Toggle specific detection types
- ✅ **Export Results**: Download analysis as JSON
- ✅ **Responsive Design**: Mobile and desktop friendly
- ✅ **Backend Configuration**: Configurable API endpoint

## ⚙️ Configuration

### Backend Configuration

Edit `be/app.py` to configure:

```python
BATCH_SIZE = 32              # Frames per batch
FPS_SAMPLING = 0.5           # Frames per second to analyze
CONFIDENCE_THRESHOLD = 0.6   # Detection confidence threshold
```

### Frontend Configuration

Edit `fe/src/App.jsx` to change default backend URL:

```javascript
const [backendUrl, setBackendUrl] = useState('http://localhost:5000');
```

Or use the settings panel in the UI to configure at runtime.

## 🔌 API Endpoints

### Analyze Video
```bash
POST http://localhost:5000/analyze
Content-Type: application/json

{
  "video_url": "https://youtube.com/watch?v=...",
  "detection_types": {
    "nudity": true,
    "violence": true,
    "drugs": false,
    "alcohol": false,
    "weapons": false,
    "gore": false
  }
}
```

### Health Check
```bash
GET http://localhost:5000/health
```

### Get Configuration
```bash
GET http://localhost:5000/config
```

### Cache Statistics
```bash
GET http://localhost:5000/cache/stats
```

## 🛠️ Development

### Backend Development

```bash
# Activate Python virtual environment
cd be
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install new dependencies
pip install package_name
pip freeze > requirements.txt

# Run Flask with auto-reload
python app.py
```

### Frontend Development

```bash
cd fe

# Install new dependencies
npm install package_name

# Run dev server with hot reload
npm run dev

# Build for production
npm run build
```

## 🚀 Deployment

### Backend Deployment (RunPod)

See detailed instructions in `be/README.md`

1. Setup RunPod GPU instance (RTX 3090 recommended)
2. Install Python dependencies
3. Configure MongoDB (optional)
4. Run Flask app with `python app.py`

### Frontend Deployment

**Option 1: Vercel (Recommended)**
```bash
cd fe
npm install -g vercel
vercel
```

**Option 2: Netlify**
```bash
cd fe
npm run build
netlify deploy --prod --dir=dist
```

**Option 3: Static Hosting**
```bash
npm run build
# Upload fe/dist/ folder to your hosting provider
```

## 🔧 Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
cd be
source venv/bin/activate
pip install -r requirements.txt
```

**"CUDA out of memory":**
- Reduce `BATCH_SIZE` in `app.py`
- Lower `FPS_SAMPLING` value

### Frontend Issues

**"Cannot connect to backend":**
- Verify backend is running: `curl http://localhost:5000/health`
- Check backend URL in frontend settings
- Ensure Flask-CORS is enabled

**CORS errors:**
```bash
cd be
source venv/bin/activate
pip install flask-cors
```

### Both Not Starting

**Check if ports are already in use:**
```bash
# Check port 5000 (backend)
lsof -i :5000

# Check port 5173 (frontend)
lsof -i :5173
```

## 💰 Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| **RunPod GPU (RTX 3090)** | $0.20/hour | Pay per second |
| **MongoDB Atlas** | FREE | 512MB free tier |
| **Models** | FREE | All open-source |
| **Result** | **$0.03-0.07/video-hour** | With optimizations |

## 🤖 Models Used

| Model | Detection | Accuracy | Source |
|-------|-----------|----------|--------|
| **NudeNet** | Nudity | ~90% | [GitHub](https://github.com/notAI-tech/NudeNet) |
| **Falconsai NSFW** | General NSFW | ~85% | [HuggingFace](https://huggingface.co/Falconsai/nsfw_image_detection) |
| **amshrbo Violence** | Violence/Drugs | ~80% | Open Source |

## 📊 Performance Benchmarks

| GPU | Batch Size | Video Minutes/Hour | Cost/Video-Hour |
|-----|------------|-------------------|-----------------|
| RTX 3090 | 32 | 300-600 | $0.03-0.07 |
| RTX 4090 | 32 | 450-900 | $0.04-0.08 |
| RTX 4090 | 64 | 600-1200 | $0.03-0.06 |

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional detection models
- TensorRT optimization
- Real-time streaming support
- Custom model training
- UI/UX enhancements

## 📄 License

MIT License - free to use for commercial projects!

## 🆘 Support

- **Backend Details**: See `be/README.md`
- **Frontend Details**: See `fe/README.md`
- **Issues**: Create an issue in the repository

## 🎉 Credits

- NudeNet by notAI-tech
- Falconsai NSFW Detection
- RunPod for GPU infrastructure
- MongoDB for database
- React + Vite for frontend
- Flask for backend

---

Built with ❤️ for content moderation and safety



