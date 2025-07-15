#!/bin/bash

# InboxCast Demo Web App Startup Script

echo "🎙️ Starting InboxCast Demo Web App..."
echo

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: app/main.py not found. Please run this script from the InboxCast root directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Installing dependencies..."
    uv sync
    echo
fi

# Check for environment configuration
if [ ! -f "local.env" ]; then
    echo "⚠️  Warning: local.env file not found."
    echo "   The demo will work with limited functionality."
    echo "   To enable full features, create local.env with:"
    echo "   GEMINI_API_KEY=your_gemini_api_key"
    echo "   MINIMAX_API_KEY=your_minimax_api_key"
    echo
fi

# Check for Gmail credentials
if [ ! -f "credentials.json" ]; then
    echo "⚠️  Warning: credentials.json not found."
    echo "   Gmail integration will not work."
    echo "   Follow the setup instructions in README.md to enable Gmail."
    echo
fi

echo "🚀 Starting FastAPI server..."
echo "   Web App: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo
echo "   Press Ctrl+C to stop the server"
echo

# Load environment variables if local.env exists
if [ -f "local.env" ]; then
    export $(cat local.env | grep -v '^#' | xargs)
fi

# Start the application
uv run python -m app.main