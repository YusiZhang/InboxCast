# InboxCast Demo Web App

## Overview

The InboxCast Demo Web App is a complete frontend and backend implementation showcasing the end-to-end functionality of converting emails and RSS feeds into podcast-style audio content using AI.

![InboxCast Demo Homepage](https://github.com/user-attachments/assets/ac705184-0d85-4b55-a79a-5df4652ba41b)

## Features

### 🔐 Authentication
- Google Gmail OAuth2 integration
- Secure authentication flow 
- Read access to Gmail messages

### 📰 RSS Feed Processing
- Support for any RSS feed URL
- Built-in test RSS feed for demonstration
- Automatic parsing and content extraction

### 🤖 AI Content Generation (Powered by Google Gemini)
- Customizable tone (neutral, friendly, professional, energetic, casual)
- Multi-language support (English, Chinese, Japanese, Korean, Spanish, French, German)
- Adjustable content length (100-1000 words)
- Multiple styles (summary, detailed, headlines)

### 🎵 Audio Generation (Powered by MiniMax AI)
- Text-to-speech conversion
- Voice tone customization
- Speech speed control (0.8x to 1.5x)
- High-quality audio output

### 🎧 Audio Playback
- Built-in web audio player
- Downloadable audio files
- Instant playback of generated content

### 🔄 Complete End-to-End Demo
- One-click demonstration of the entire workflow
- Step-by-step progress tracking
- Error handling and user feedback

![Demo with RSS Results](https://github.com/user-attachments/assets/dba40859-2d12-4a2b-b27f-75076dd36d0d)

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI Services**: Google Gemini AI, MiniMax AI
- **OAuth2**: Google Gmail API
- **RSS**: feedparser library
- **Audio**: Web Audio API

## Architecture

```
app/
├── main.py              # FastAPI application entry point
├── routers/             # API route handlers
│   ├── auth.py          # Gmail OAuth2 authentication
│   ├── rss.py           # RSS feed processing
│   ├── content.py       # AI content generation
│   └── audio.py         # Audio generation and playback
├── static/              # Frontend assets
│   ├── style.css        # Responsive CSS styling
│   └── script.js        # Interactive JavaScript
└── templates/           # Jinja2 templates
    └── index.html       # Main demo page
```

## Setup and Installation

### 1. Install Dependencies

```bash
# Ensure uv is installed
pip install uv

# Install all dependencies including web app requirements
uv sync
```

### 2. API Keys Configuration

Create a `local.env` file with your API keys:

```bash
# Google Gemini AI API key (required for content generation)
GEMINI_API_KEY=your_gemini_api_key_here

# MiniMax AI API key (required for audio generation)
MINIMAX_API_KEY=your_minimax_api_key_here
```

### 3. Google OAuth2 Setup

For Gmail integration:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop application)
5. Download credentials file and save as `credentials.json` in project root

### 4. Start the Web App

```bash
# Start the FastAPI server
uv run python -m app.main

# Or use the convenience script
chmod +x start_webapp.sh
./start_webapp.sh
```

The web app will be available at: http://localhost:8000

## API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Available Endpoints

#### Authentication
- `GET /api/auth/status` - Check authentication status
- `GET /api/auth/login` - Initiate Gmail OAuth2 login
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/emails` - Get emails from authenticated Gmail

#### RSS Processing
- `POST /api/rss/fetch` - Fetch and parse RSS feed from URL
- `GET /api/rss/test` - Test RSS functionality with sample feed

#### Content Generation
- `POST /api/content/generate` - Generate AI content from emails/RSS
- `POST /api/content/test` - Test content generation with sample data

#### Audio Generation
- `POST /api/audio/generate` - Generate audio from text
- `GET /api/audio/download/{file_path}` - Download generated audio
- `POST /api/audio/test` - Test audio generation
- `GET /api/audio/test-connection` - Test MiniMax AI connection

## Usage Guide

### Basic Demo Flow

1. **Start the Application**
   ```bash
   uv run python -m app.main
   ```

2. **Open Web Browser**
   Navigate to http://localhost:8000

3. **Test RSS Feed Processing**
   - Click "Use Test RSS Feed" to load sample data
   - Or enter a real RSS feed URL and click "Fetch RSS Feed"

4. **Generate AI Content**
   - Adjust tone, language, and style preferences
   - Click "Test with Sample Data" (works without API keys)
   - Or use "Generate AI Content" with real data (requires GEMINI_API_KEY)

5. **Create Audio**
   - Configure voice tone and speech speed
   - Click "Test Audio Generation" or "Generate Audio" (requires MINIMAX_API_KEY)

6. **Play Audio**
   - Use the built-in audio player to listen to generated content

7. **Complete Demo**
   - Click "Run Complete Demo" for end-to-end demonstration

### With API Keys

When you have configured API keys in `local.env`:

1. **Gmail Authentication**
   - Click "Sign in with Google Gmail"
   - Complete OAuth2 flow in browser
   - Access your Gmail messages with specific labels

2. **Full AI Content Generation**
   - Generate content from your real emails and RSS feeds
   - Customize tone, language, length, and style
   - Get AI-powered summaries and analysis

3. **High-Quality Audio Generation**
   - Convert generated content to natural-sounding audio
   - Download MP3 files for offline listening
   - Adjust voice characteristics and speech speed

## Error Handling

The web app includes comprehensive error handling:

- **Missing API Keys**: Clear messages about required environment variables
- **Network Issues**: Graceful handling of connection failures
- **Invalid Input**: User-friendly validation messages
- **Service Errors**: Detailed error reporting with troubleshooting hints

## Customization

### Frontend Styling
- Modify `app/static/style.css` for visual customization
- Responsive design works on desktop and mobile
- CSS variables for easy theme customization

### Backend Configuration
- Adjust API limits and timeouts in router files
- Customize AI prompts in `app/routers/content.py`
- Modify audio settings in `app/routers/audio.py`

### Content Processing
- Extend RSS parsing logic in `services/rss_service.py`
- Customize email processing in `services/gmail_service.py`
- Adjust AI generation parameters in `services/gemini_service.py`

## Development

### Running in Development Mode

```bash
# Start with auto-reload
uv run python -m app.main

# The server automatically reloads on file changes
```

### Testing

```bash
# Run all existing tests (backend services)
uv run pytest

# Run with coverage
uv run pytest --cov=services --cov=models --cov-report=term-missing
```

### Linting and Formatting

```bash
# Check code style
uv run ruff check app/ services/ models/ tests/

# Format code
uv run ruff format app/ services/ models/ tests/

# Type checking
uv run mypy services/ models/ app/
```

## Production Deployment

For production deployment:

1. **Environment Variables**
   - Set `GEMINI_API_KEY` and `MINIMAX_API_KEY`
   - Configure secure session management
   - Set up proper OAuth2 redirect URLs

2. **Security**
   - Use HTTPS in production
   - Implement proper CORS policies
   - Add rate limiting and authentication middleware

3. **Performance**
   - Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)
   - Implement caching for RSS feeds and content generation
   - Add file storage for persistent audio files

4. **Monitoring**
   - Add logging and error tracking
   - Monitor API usage and costs
   - Set up health checks and alerts

## Troubleshooting

### Common Issues

1. **"credentials.json not found"**
   - Follow Google OAuth2 setup instructions
   - Ensure file is in project root directory

2. **"Gemini API key not configured"**
   - Set `GEMINI_API_KEY` in local.env file
   - Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. **"MiniMax API key not configured"**
   - Set `MINIMAX_API_KEY` in local.env file
   - Get API key from [MiniMax AI Platform](https://platform.minimax.chat/)

4. **RSS feed fetch failures**
   - Check network connectivity
   - Verify RSS feed URL is valid and accessible
   - Some feeds may require user-agent headers

5. **Audio playback issues**
   - Ensure browser supports HTML5 audio
   - Check audio file was generated successfully
   - Verify file permissions and paths

### Getting Help

- Check the main README.md for backend service documentation
- Review API documentation at `/docs` endpoint
- Examine browser console for JavaScript errors
- Check server logs for backend issues