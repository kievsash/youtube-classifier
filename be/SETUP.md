# Backend Setup Guide

This guide will help you set up the backend environment on a new computer.

## Prerequisites

### 1. Python 3.11 (REQUIRED)

**⚠️ This project requires Python 3.11 specifically.**

#### Check Your Python Version
```bash
python3 --version
# Should show: Python 3.11.x
```

#### Install Python 3.11

**macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3.11 --version
```

**Ubuntu/Debian:**
```bash
# Add deadsnakes PPA
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev

# Verify installation
python3.11 --version
```

**Windows:**
1. Download Python 3.11 installer from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify in Command Prompt: `python --version`

### 2. FFmpeg (REQUIRED)

FFmpeg is required for video processing. See [INSTALL_FFMPEG.md](INSTALL_FFMPEG.md) for detailed instructions.

**Quick Install:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Verify
ffmpeg -version
```

## Installation Steps

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd "youtube classifier/be"
```

### Step 2: Create Virtual Environment with Python 3.11

**macOS/Linux:**
```bash
# Create virtual environment
python3.11 -m venv venv311

# Activate virtual environment
source venv311/bin/activate

# Verify Python version inside venv
python --version  # Should show 3.11.x
```

**Windows:**
```bash
# Create virtual environment
python -m venv venv311

# Activate virtual environment
venv311\Scripts\activate

# Verify Python version
python --version  # Should show 3.11.x
```

### Step 3: Install Dependencies
```bash
# Make sure virtual environment is activated
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Download AI Models (First Time Only)

The models will auto-download on first use, but you can pre-download them:

```bash
# NudeNet model
python -c "from nudenet import NudeDetector; NudeDetector()"

# Falconsai NSFW detection model
python -c "from transformers import pipeline; pipeline('image-classification', model='Falconsai/nsfw_image_detection')"
```

**Note:** Model downloads require ~5GB disk space and may take 10-20 minutes depending on your internet connection.

### Step 5: Configure MongoDB (Optional)

If using MongoDB caching:

```bash
# Set MongoDB connection string
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"

# Or add to ~/.bashrc (Linux/macOS) for persistence
echo 'export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"' >> ~/.bashrc
source ~/.bashrc
```

### Step 6: Run the Backend

```bash
# Make sure virtual environment is activated
python app.py
```

The server will start on `http://localhost:5000`

## Verification

Check if everything is working:

```bash
# Test health endpoint
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "gpu_available": true/false,
  "models_loaded": true,
  "ffmpeg_available": true
}
```

## Troubleshooting

### Wrong Python Version

If you see errors about Python version:
```bash
# Deactivate current environment
deactivate

# Remove old venv
rm -rf venv

# Create new venv with Python 3.11
python3.11 -m venv venv311
source venv311/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### FFmpeg Not Found

```bash
# Check if ffmpeg is installed
which ffmpeg

# If not installed, see INSTALL_FFMPEG.md
```

### Import Errors

```bash
# Make sure virtual environment is activated
which python  # Should point to venv311/bin/python

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### CUDA/GPU Issues

If you don't have an NVIDIA GPU, the models will automatically fall back to CPU mode (slower but functional).

To use GPU:
- Ensure CUDA is installed (CUDA 11.8 or later)
- Install PyTorch with CUDA support:
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```

## Development Notes

### Virtual Environment Locations

This project uses `venv311/` directory for the Python 3.11 virtual environment:
- **macOS/Linux**: `be/venv311/`
- **Windows**: `be\venv311\`

### Activating Environment

Always activate the virtual environment before running the app:
```bash
# macOS/Linux
source venv311/bin/activate

# Windows
venv311\Scripts\activate
```

### Deactivating Environment

When done:
```bash
deactivate
```

## Quick Reference

```bash
# Complete setup from scratch
python3.11 -m venv venv311
source venv311/bin/activate  # or venv311\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## System Requirements

- **Python**: 3.11.x (required)
- **Disk Space**: ~10GB (for models and dependencies)
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: Optional (NVIDIA GPU with CUDA for faster processing)
- **FFmpeg**: Required for video processing

## Additional Resources

- [Main README](README.md) - Full project documentation
- [INSTALL_FFMPEG.md](INSTALL_FFMPEG.md) - FFmpeg installation guide
- [requirements.txt](requirements.txt) - Python dependencies list

---

**Need Help?** Check the troubleshooting section in the [main README](README.md) or open an issue.

