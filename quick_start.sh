#!/bin/bash
# VoiceFlow Quick Start Script

echo "🚀 VoiceFlow - National Hackathon Edition"
echo "========================================"
echo ""

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  echo "Windows detected! Using PowerShell commands..."
  echo ""
  echo "📝 STEP 1: Install Backend Dependencies"
  echo "cd backend"
  echo "pip install -r requirements.txt"
  echo ""
  echo "📝 STEP 2: Setup Environment Variables"
  echo "Copy-Item .env.example .env"
  echo "# Edit .env and add your OPENAI_API_KEY"
  echo ""
  echo "📝 STEP 3: Start Backend (Terminal 1)"
  echo "cd backend"
  echo "python -m uvicorn main:app --reload"
  echo ""
  echo "📝 STEP 4: Start Frontend (Terminal 2)"
  echo "cd frontend"
  echo "npm install"
  echo "npm run dev"
  echo ""
  echo "📝 STEP 5: Open Browser"
  echo "http://localhost:3000"
  echo ""
  echo "📝 STEP 6: Test It"
  echo "- Click 'Load Demo' button"
  echo "- Click mic button and say a voice command"
  echo ""
fi

# Check if running on Linux/Mac
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
  echo "Linux/Mac detected! Using bash commands..."
  echo ""
  echo "📝 STEP 1: Install Backend Dependencies"
  echo "cd backend && pip install -r requirements.txt"
  echo ""
  echo "📝 STEP 2: Setup Environment Variables"
  echo "cp backend/.env.example backend/.env"
  echo "# Edit backend/.env and add your OPENAI_API_KEY"
  echo ""
  echo "📝 STEP 3: Start Backend"
  echo "cd backend && python -m uvicorn main:app --reload &"
  echo ""
  echo "📝 STEP 4: Start Frontend"
  echo "cd frontend && npm install && npm run dev"
  echo ""
  echo "Then open: http://localhost:3000"
  echo ""
fi

echo "❓ Don't have an OpenAI API key?"
echo "   Get one free at: https://platform.openai.com/api-keys"
echo ""
echo "🎤 Voice commands work best in Chrome, Edge, or Safari"
echo ""
echo "📚 For more details, see SETUP_GUIDE.md"
