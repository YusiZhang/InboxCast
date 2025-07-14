# InboxCast

Convert inbox emails into PodCast

## Project Structure

```
InboxCast/
├── services/                 # Service layer for external API integrations
│   ├── __init__.py          # Services package initialization
│   ├── gmail_service.py     # Gmail API service implementation
│   └── rss_service.py       # RSS feed service implementation
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
- **OAuth2 Authentication**: Secure authentication flow with Google
- **Message Processing**: Extract and display email metadata and content
- **Feed Processing**: Extract and display RSS feed entries and metadata
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

### 3. Environment Configuration

1. Copy the example environment file:
   ```bash
   cp example.env local.env
   ```
2. Edit `local.env` with your project configuration (optional)

### 4. Run the Application

```bash
uv run python main.py
```

The application will test both Gmail and RSS integrations:

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
├── test_gmail_service.py     # Tests for Gmail API service with mocked responses
└── test_rss_service.py       # Tests for RSS service with mocked feeds
```

### Test Coverage

The test suite aims for high coverage and includes:

- **Gmail Service Tests**: Mock Gmail API responses to test authentication, message fetching, and error handling
- **RSS Service Tests**: Mock HTTP requests and RSS feeds to test feed parsing and content extraction
- **Content Model Tests**: Validate Pydantic model behavior, validation, and serialization
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

## Gmail Service API

The `GmailService` class provides the following methods:

- `authenticate()`: Handles OAuth2 authentication with Google
- `get_inbox_messages(max_results)`: Retrieves inbox messages
- `extract_message_info(message)`: Extracts useful information from messages
- `print_inbox_summary(max_results)`: Displays inbox summary for testing

## RSS Service API

The `RSSService` class provides the following methods:

- `fetch_feed(feed_url)`: Fetches and parses an RSS feed from URL
- `get_feed_entries(feed_url, max_entries)`: Retrieves RSS feed entries
- `extract_entry_info(entry)`: Extracts useful information from RSS entries
- `get_feed_info(feed_url)`: Gets metadata about the RSS feed
- `print_feed_summary(feed_url, max_entries)`: Displays feed summary for testing

### RSS Service Usage Example

```python
from services import RSSService

# Initialize RSS service
rss_service = RSSService()

# Get feed entries
entries = rss_service.get_feed_entries("https://example.com/feed.xml", max_entries=10)

# Get feed information
feed_info = rss_service.get_feed_info("https://example.com/feed.xml")

# Print feed summary
rss_service.print_feed_summary("https://example.com/feed.xml", max_entries=5)
```

## Security Notes

- The `credentials.json` file contains sensitive OAuth2 credentials
- The `token.json` file (auto-generated) contains user access tokens
- Both files are ignored by git (see `.gitignore`)
- Never commit these files to version control

## Troubleshooting

### Authentication Issues
- Ensure `credentials.json` is in the project root
- Check that Gmail API is enabled in Google Cloud Console
- Verify OAuth2 consent screen is configured

### Permission Errors
- The application requests read-only access to Gmail
- Approve all requested permissions during OAuth flow
- Check Google account security settings if authentication fails

## Future Enhancements

- Add email content processing for podcast generation
- Implement email filtering and categorization
- Add RSS feed content processing for podcast generation
- Implement RSS feed subscription management
- Add text-to-speech integration
- Create unified content processing pipeline for both emails and RSS feeds
- Create web interface for better user experience
