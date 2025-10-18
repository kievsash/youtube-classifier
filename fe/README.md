# Video Moderator Frontend

React frontend for AI video content moderation system.

## 📁 Project Structure

```
video-moderator-frontend/
├── public/
├── src/
│   ├── App.jsx          # Main component with video analysis UI
│   ├── main.jsx         # React entry point
│   └── index.css        # Tailwind CSS imports
├── index.html           # HTML template
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind configuration
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Backend URL

The app defaults to `http://localhost:5000`. You can change this in the UI settings or edit `App.jsx`:

```javascript
const [backendUrl, setBackendUrl] = useState('https://your-runpod-url.proxy.runpod.net');
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for Production

```bash
npm run build
```

The build output will be in the `dist/` folder.

## 🌐 Deployment Options

### Option 1: Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

### Option 2: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build and deploy
npm run build
netlify deploy --prod --dir=dist
```

### Option 3: GitHub Pages

1. Update `vite.config.js`:
```javascript
export default defineConfig({
  plugins: [react()],
  base: '/your-repo-name/'
})
```

2. Build and deploy:
```bash
npm run build
# Push dist folder to gh-pages branch
```

### Option 4: Static Hosting (AWS S3, Cloudflare Pages, etc.)

```bash
npm run build
# Upload dist/ folder to your hosting provider
```

## ⚙️ Configuration

### Change Default Backend URL

Edit `src/App.jsx`:

```javascript
const [backendUrl, setBackendUrl] = useState('https://your-backend-url.com');
```

### Customize Detection Types

Edit the default checkboxes in `src/App.jsx`:

```javascript
const [detectionTypes, setDetectionTypes] = useState({
  nudity: true,
  violence: true,
  drugs: false,      // Change to true to enable by default
  alcohol: false,
  weapons: false,
  gore: false
});
```

### Change Theme Colors

Edit `src/App.jsx` gradient classes:

```javascript
// Current: purple gradient
className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"

// Example: blue gradient
className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900"
```

## 🎨 Features

- ✅ YouTube URL input
- ✅ 6 detection type checkboxes (Nudity, Violence, Drugs, Alcohol, Weapons, Gore)
- ✅ Real-time processing status
- ✅ Summary cards with detection counts
- ✅ Timeline view with timestamps
- ✅ Export results to JSON
- ✅ Cached result indicator
- ✅ Responsive design (mobile-friendly)
- ✅ Backend URL configuration

## 🔧 Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. Make sure Flask-CORS is installed on backend:
```bash
pip install flask-cors
```

2. Backend should have:
```python
from flask_cors import CORS
CORS(app)
```

### Connection Refused

- Check backend is running: `curl http://localhost:5000/health`
- Verify backend URL in settings matches your backend
- Check firewall/network settings

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| react | UI framework |
| react-dom | React rendering |
| lucide-react | Icons |
| vite | Build tool |
| tailwindcss | Styling |

## 🎯 API Integration

The frontend calls these backend endpoints:

```javascript
// Analyze video
POST /analyze
{
  "video_url": "https://youtube.com/watch?v=...",
  "detection_types": {
    "nudity": true,
    "violence": true,
    ...
  }
}

// Response
{
  "video_id": "abc123",
  "detections": [...],
  "summary": {...},
  "processing_time": 15.5,
  "cached": false
}
```

## 🚀 Performance

- Optimized bundle size with Vite
- Lazy loading for better initial load
- Responsive design with mobile-first approach
- Efficient state management with React hooks

## 📄 License

MIT License - free to use for commercial projects!
