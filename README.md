# InboxCast

Convert inbox emails into PodCast

## Project Structure

```
InboxCast/
├── services/                 # Service layer for external API integrations
│   ├── __init__.py          # Services package initialization
│   └── gmail_service.py     # Gmail API service implementation
├── main.py                  # Main application entry point
├── pyproject.toml          # Project configuration and dependencies
├── example.env             # Environment configuration template
├── README.md               # This file
├── .gitignore             # Git ignore rules
└── requirements files      # uv.lock for dependency management
```

## Features

- **Gmail API Integration**: Authenticate and read user's inbox messages
- **OAuth2 Authentication**: Secure authentication flow with Google
- **Message Processing**: Extract and display email metadata and content
- **Extensible Architecture**: Clean service layer for future integrations

## Setup Instructions

### 1. Install Dependencies

This project uses Python 3.12+ and pip for dependency management:

```bash
pip install -e .
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
python main.py
```

On first run, the application will:
1. Open a browser window for Google OAuth2 authentication
2. Request permission to read your Gmail inbox
3. Save authentication tokens for future use
4. Display a summary of your recent inbox messages

## Gmail Service API

The `GmailService` class provides the following methods:

- `authenticate()`: Handles OAuth2 authentication with Google
- `get_inbox_messages(max_results)`: Retrieves inbox messages
- `extract_message_info(message)`: Extracts useful information from messages
- `print_inbox_summary(max_results)`: Displays inbox summary for testing

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
- Add text-to-speech integration
- Create web interface for better user experience
