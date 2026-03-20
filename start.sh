#!/bin/bash

# VoiceFlow - Complete Startup Script for Mac/Linux
# This script starts both backend and frontend servers

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║   🎤 VoiceFlow - Complete System Startup   ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.9+ from https://python.org"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

echo "✅ Python3 and Node.js found"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Start Backend
echo "Starting Backend Server..."
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Check if requirements are installed
if ! python3 -c "import fastapi" 2>&1 | grep -q "ImportError"; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  WARNING: backend/.env not found!"
    echo ""
    echo "Please create backend/.env with your OpenAI API key:"
    echo ""
    echo "OPENAI_API_KEY=sk-xxx..."
    echo ""
    echo "Get your key from: https://platform.openai.com/api/keys"
    echo ""
    read -p "Press Enter to continue..."
fi

echo ""
echo "🚀 Starting FastAPI Backend on http://localhost:8000"
echo ""

# Start backend in background
python3 main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Frontend
echo ""
echo "Starting Frontend Server..."
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

echo ""
echo "🎨 Starting Next.js Frontend on http://localhost:3000"
echo ""

# Start frontend
npm run dev

# Handle graceful shutdown
trap "kill $BACKEND_PID" EXIT
