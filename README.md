# InboxCast

Convert inbox emails into PodCast

## Project Structure

```
InboxCast/
├── services/                 # Service layer for external API integrations
│   ├── __init__.py          # Services package initialization
│   ├── gemini_service.py    # Google Gemini API service implementation
│   ├── gmail_service.py     # Gmail API service implementation
│   └── rss_service.py       # RSS feed service implementation
├── models/                  # Data models for content and configurations
│   ├── __init__.py          # Models package initialization
│   ├── content_model.py     # Content item data model
│   └── gemini_model.py      # Gemini API configuration and response models
├── main.py                  # Main application entry point
├── pyproject.toml          # Project configuration and dependencies
├── example.env             # Environment configuration template
├── README.md               # This file
├── .gitignore             # Git ignore rules
└── requirements files      # uv.lock for dependency management
```

## Features

- **Gmail API Integration**: Authenticate and read user's inbox messages
- **RSS Feed Integration**: Parse and process RSS feeds from various sources
- **Google Gemini AI Integration**: Generate and enhance content using Google's Gemini AI
- **OAuth2 Authentication**: Secure authentication flow with Google
- **Message Processing**: Extract and display email metadata and content
- **Feed Processing**: Extract and display RSS feed entries and metadata
- **AI Content Enhancement**: Summarize, tag, and analyze content using Gemini AI
- **Extensible Architecture**: Clean service layer for future integrations

## Setup Instructions

### 1. Install Dependencies

This project uses Python 3.12+ and uv for dependency management:

```bash
# Install uv if not already installed
pip install uv

# Install project dependencies
uv sync

# Install with test dependencies for development
uv sync --extra test

# Install with development dependencies (linting, type checking)
uv sync --extra dev
```

### 2. Google Cloud Console Setup

#### Gmail API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the credentials file
5. Save the downloaded file as `credentials.json` in the project root

#### Google Gemini API Setup
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key for the Gemini API
3. Copy the API key for use in the next step

### 3. Environment Configuration

1. Copy the example environment file:
   ```bash
   cp example.env local.env
   ```
2. Edit `local.env` with your project configuration:
   ```bash
   # Google Gemini API key (required for AI features)
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Other optional configurations
   # (Gmail credentials are stored in credentials.json)
   ```

### 4. Run the Application

```bash
uv run python main.py
```

The application will test Gmail, RSS, and Gemini integrations:

**RSS Integration (no credentials required):**
- Tests RSS feed parsing with popular feeds
- Displays feed metadata and entry summaries
- Demonstrates RSS service functionality

**Gmail Integration (requires credentials):**
On first run, the Gmail integration will:
1. Open a browser window for Google OAuth2 authentication
2. Request permission to read your Gmail inbox
3. Save authentication tokens for future use
4. Display a summary of your recent inbox messages

**Gemini Integration (requires API key):**
The Gemini integration will:
1. Test connection to Google's Gemini AI API
2. Generate a sample AI response to verify functionality
3. Display AI-generated content and usage statistics
4. Demonstrate AI content enhancement capabilities

## Testing

This project includes comprehensive unit tests for all services and models.

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=services --cov=models --cov-report=term-missing

# Run tests in verbose mode
uv run pytest -v

# Run specific test file
uv run pytest tests/test_gmail_service.py

# Run specific test class or method
uv run pytest tests/test_gmail_service.py::TestGmailService::test_authenticate_with_valid_existing_token
```

### Test Structure

```
tests/
├── __init__.py
├── test_content_model.py     # Tests for Pydantic ContentItem model
├── test_gemini_model.py      # Tests for Gemini configuration and response models
├── test_gemini_service.py    # Tests for Gemini AI service with mocked responses
├── test_gmail_service.py     # Tests for Gmail API service with mocked responses
└── test_rss_service.py       # Tests for RSS service with mocked feeds
```

### Test Coverage

The test suite aims for high coverage and includes:

- **Gmail Service Tests**: Mock Gmail API responses to test authentication, message fetching, and error handling
- **RSS Service Tests**: Mock HTTP requests and RSS feeds to test feed parsing and content extraction
- **Gemini Service Tests**: Mock Gemini API responses to test AI content generation and enhancement
- **Content Model Tests**: Validate Pydantic model behavior, validation, and serialization
- **Configuration Model Tests**: Test Gemini configuration and response models
- **Error Handling**: Test various failure scenarios and edge cases

### Development Tools

```bash
# Run linter
uv run ruff check services/ models/ tests/

# Run formatter
uv run ruff format services/ models/ tests/

# Run type checker
uv run mypy services/ models/

# Install all development dependencies
uv sync --extra dev --extra test
```

## Service APIs

### Gmail Service API

The `GmailService` class provides the following methods:

- `authenticate()`: Handles OAuth2 authentication with Google
- `get_inbox_messages(max_results)`: Retrieves inbox messages
- `extract_message_info(message)`: Extracts useful information from messages
- `print_inbox_summary(max_results)`: Displays inbox summary for testing

### RSS Service API

The `RSSService` class provides the following methods:

- `fetch_feed(feed_url)`: Fetches and parses an RSS feed from URL
- `get_feed_entries(feed_url, max_entries)`: Retrieves RSS feed entries
- `extract_entry_info(entry)`: Extracts useful information from RSS entries
- `get_feed_info(feed_url)`: Gets metadata about the RSS feed
- `print_feed_summary(feed_url, max_entries)`: Displays feed summary for testing

### Gemini Service API

The `GeminiService` class provides the following methods:

- `configure()`: Configures the Gemini API client with API key
- `generate_content(config)`: Generates content using Gemini AI
- `summarize_content(content, max_words)`: Summarizes text content
- `enhance_content_item(item, enhancement_type)`: Enhances ContentItem with AI-generated metadata
- `print_generation_test(test_prompt)`: Tests Gemini API integration

### Gemini Service Usage Example

```python
from services import GeminiService
from models import GeminiConfig

# Initialize Gemini service with API key
gemini_service = GeminiService(api_key="your-api-key")

# Create configuration for content generation
config = GeminiConfig(
    model_name="gemini-1.5-flash",
    system_prompt="You are a helpful AI assistant.",
    user_prompt="Explain quantum computing in simple terms.",
    temperature=0.7,
    max_output_tokens=500
)

# Generate content
response = gemini_service.generate_content(config)
if response:
    print(f"Generated: {response.text}")
    print(f"Tokens used: {response.prompt_tokens} -> {response.response_tokens}")

# Summarize content
summary = gemini_service.summarize_content("Long article text here...", max_words=50)

# Enhance ContentItem with AI
from models import ContentItem
item = ContentItem(title="Article", content="Content here...")
enhanced_item = gemini_service.enhance_content_item(item, enhancement_type="summary")
```

## Security Notes

- The `credentials.json` file contains sensitive OAuth2 credentials
- The `token.json` file (auto-generated) contains user access tokens  
- The `GEMINI_API_KEY` environment variable contains your Gemini API key
- All credential files are ignored by git (see `.gitignore`)
- Never commit these files or API keys to version control

## Troubleshooting

### Gmail Authentication Issues
- Ensure `credentials.json` is in the project root
- Check that Gmail API is enabled in Google Cloud Console
- Verify OAuth2 consent screen is configured

### Gemini API Issues
- Ensure `GEMINI_API_KEY` environment variable is set
- Verify your API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Check API quota and rate limits

### Permission Errors
- The application requests read-only access to Gmail
- Approve all requested permissions during OAuth flow
- Check Google account security settings if authentication fails

## Future Enhancements

- Add email content processing for podcast generation using Gemini AI
- Implement email filtering and categorization with AI assistance
- Add RSS feed content processing for podcast generation using Gemini AI
- Implement RSS feed subscription management
- Add text-to-speech integration for full podcast generation
- Create unified content processing pipeline for emails, RSS feeds, and AI enhancement
- Integrate with podcast hosting platforms
- Add voice synthesis with different AI voices
- Create web interface for better user experience
