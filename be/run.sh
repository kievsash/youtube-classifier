#!/bin/bash

# YouTube Classifier Backend Runner
# This script activates the Python 3.11 virtual environment and starts the Flask server

cd "$(dirname "$0")"

echo "🔧 Activating Python 3.11 virtual environment..."
source venv311/bin/activate

echo "🐍 Python version: $(python --version)"
echo ""

echo "🚀 Starting Flask backend server..."
python app.py


