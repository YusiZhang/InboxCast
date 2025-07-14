"""
Unit tests for the Gmail service.
"""

from unittest.mock import Mock, mock_open, patch

from models.content_model import ContentItem
from services.gmail_service import GmailService


class TestGmailService:
    """Test cases for GmailService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.gmail_service = GmailService()

        # Sample Gmail API response data
        self.sample_message_list = {
            "messages": [
                {"id": "msg_001", "threadId": "thread_001"},
                {"id": "msg_002", "threadId": "thread_002"},
            ]
        }

        self.sample_message_detail = {
            "id": "msg_001",
            "threadId": "thread_001",
            "labelIds": ["INBOX", "UNREAD"],
            "snippet": "This is a test email snippet...",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Email Subject"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Date", "value": "Mon, 01 Jan 2024 12:00:00 +0000"},
                    {"name": "To", "value": "recipient@example.com"},
                ],
                "body": {
                    "data": "VGhpcyBpcyB0aGUgZW1haWwgYm9keS4="  # Base64 encoded "This is the email body."
                },
            },
        }

        self.sample_multipart_message = {
            "id": "msg_003",
            "threadId": "thread_003",
            "labelIds": ["INBOX"],
            "snippet": "Multipart email snippet...",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Multipart Email"},
                    {"name": "From", "value": "multipart@example.com"},
                    {"name": "Date", "value": "Tue, 02 Jan 2024 14:30:00 +0000"},
                ],
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {
                            "data": "UGxhaW4gdGV4dCBwYXJ0"  # Base64 encoded "Plain text part"
                        },
                    },
                    {
                        "mimeType": "text/html",
                        "body": {
                            "data": "PGh0bWw+SFRNTCBwYXJ0PC9odG1sPg=="  # Base64 encoded "<html>HTML part</html>"
                        },
                    },
                ],
            },
        }

    def test_gmail_service_initialization(self):
        """Test Gmail service initialization with default parameters."""
        service = GmailService()

        assert service.credentials_file == "credentials.json"
        assert service.token_file == "token.json"
        assert service.service is None
        assert service.creds is None

    def test_gmail_service_initialization_custom_files(self):
        """Test Gmail service initialization with custom file paths."""
        service = GmailService(credentials_file="custom_creds.json", token_file="custom_token.json")

        assert service.credentials_file == "custom_creds.json"
        assert service.token_file == "custom_token.json"

    @patch("os.path.exists")
    def test_authenticate_no_credentials_file(self, mock_exists):
        """Test authentication when credentials file doesn't exist."""
        mock_exists.return_value = False

        result = self.gmail_service.authenticate()

        assert result is False
        assert self.gmail_service.service is None

    @patch("os.path.exists")
    @patch("google.oauth2.credentials.Credentials.from_authorized_user_file")
    @patch("services.gmail_service.build")
    def test_authenticate_with_valid_existing_token(self, mock_build, mock_from_file, mock_exists):
        """Test authentication with valid existing token."""
        # Mock existing token file
        mock_exists.side_effect = lambda path: path == "token.json"

        # Mock valid credentials
        mock_creds = Mock()
        mock_creds.valid = True
        mock_from_file.return_value = mock_creds

        # Mock Gmail service build
        mock_service = Mock()
        mock_build.return_value = mock_service

        result = self.gmail_service.authenticate()

        assert result is True
        assert self.gmail_service.creds == mock_creds
        mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)

    @patch("os.path.exists")
    @patch("google.oauth2.credentials.Credentials.from_authorized_user_file")
    @patch("services.gmail_service.Request")
    @patch("services.gmail_service.build")
    @patch("builtins.open", new_callable=mock_open)
    def test_authenticate_with_expired_token_refresh(
        self, mock_file, mock_build, mock_request, mock_from_file, mock_exists
    ):
        """Test authentication with expired token that can be refreshed."""
        # Mock existing token file
        mock_exists.side_effect = lambda path: path == "token.json"

        # Mock expired but refreshable credentials
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token_123"
        mock_from_file.return_value = mock_creds

        # Mock request for refresh
        mock_req = Mock()
        mock_request.return_value = mock_req

        # Mock successful refresh
        def refresh_side_effect(request):
            mock_creds.valid = True

        mock_creds.refresh.side_effect = refresh_side_effect

        # Mock Gmail service build
        mock_service = Mock()
        mock_build.return_value = mock_service

        result = self.gmail_service.authenticate()

        assert result is True
        mock_creds.refresh.assert_called_once_with(mock_req)
        mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)

    @patch("os.path.exists")
    @patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file")
    @patch("services.gmail_service.build")
    @patch("builtins.open", new_callable=mock_open)
    def test_authenticate_new_oauth_flow(self, mock_file, mock_build, mock_flow_class, mock_exists):
        """Test authentication with new OAuth flow."""
        # Mock credentials file exists, token file doesn't
        mock_exists.side_effect = lambda path: path == "credentials.json"

        # Mock OAuth flow
        mock_flow = Mock()
        mock_creds = Mock()
        mock_creds.valid = True
        mock_flow.run_local_server.return_value = mock_creds
        mock_flow_class.return_value = mock_flow

        # Mock Gmail service build
        mock_service = Mock()
        mock_build.return_value = mock_service

        result = self.gmail_service.authenticate()

        assert result is True
        mock_flow.run_local_server.assert_called_once_with(port=0)
        mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)
        # Verify token is saved
        mock_file.assert_called()

    @patch("os.path.exists")
    @patch("google.oauth2.credentials.Credentials.from_authorized_user_file")
    def test_authenticate_exception_handling(self, mock_from_file, mock_exists):
        """Test authentication exception handling."""
        mock_exists.side_effect = lambda path: path == "token.json"
        mock_from_file.side_effect = Exception("Authentication error")

        result = self.gmail_service.authenticate()

        assert result is False

    def test_get_inbox_messages_not_authenticated(self):
        """Test get_inbox_messages when service is not authenticated."""
        result = self.gmail_service.get_inbox_messages()

        assert result is None

    @patch("googleapiclient.discovery.build")
    def test_get_inbox_messages_success(self, mock_build):
        """Test successful inbox messages retrieval."""
        # Set up authenticated service
        mock_service = Mock()
        mock_build.return_value = mock_service
        self.gmail_service.service = mock_service

        # Mock messages list API call
        mock_list_call = Mock()
        mock_list_call.execute.return_value = self.sample_message_list
        mock_service.users().messages().list.return_value = mock_list_call

        # Mock message get API calls
        mock_get_call = Mock()
        mock_get_call.execute.return_value = self.sample_message_detail
        mock_service.users().messages().get.return_value = mock_get_call

        result = self.gmail_service.get_inbox_messages(max_results=2)

        assert result is not None
        assert len(result) == 2
        assert all(isinstance(item, ContentItem) for item in result)

        # Verify API calls
        mock_service.users().messages().list.assert_called_once_with(
            userId="me", labelIds=["INBOX"], maxResults=2
        )
        assert mock_service.users().messages().get.call_count == 2

    @patch("googleapiclient.discovery.build")
    def test_get_inbox_messages_empty_inbox(self, mock_build):
        """Test get_inbox_messages with empty inbox."""
        mock_service = Mock()
        mock_build.return_value = mock_service
        self.gmail_service.service = mock_service

        # Mock empty messages response
        mock_list_call = Mock()
        mock_list_call.execute.return_value = {"messages": []}
        mock_service.users().messages().list.return_value = mock_list_call

        result = self.gmail_service.get_inbox_messages()

        assert result == []

    @patch("googleapiclient.discovery.build")
    def test_get_inbox_messages_api_exception(self, mock_build):
        """Test get_inbox_messages when API call raises exception."""
        mock_service = Mock()
        mock_build.return_value = mock_service
        self.gmail_service.service = mock_service

        # Mock API exception
        mock_service.users().messages().list.side_effect = Exception("API Error")

        result = self.gmail_service.get_inbox_messages()

        assert result is None

    def test_extract_message_info_simple_message(self):
        """Test extracting info from simple email message."""
        content_item = self.gmail_service.extract_message_info(self.sample_message_detail)

        assert isinstance(content_item, ContentItem)
        assert content_item.title == "Test Email Subject"
        assert content_item.source == "Gmail"
        assert content_item.author == "sender@example.com"
        assert content_item.content == "This is the email body."
        assert content_item.metadata["id"] == "msg_001"
        assert content_item.metadata["date"] == "Mon, 01 Jan 2024 12:00:00 +0000"
        assert content_item.metadata["snippet"] == "This is a test email snippet..."
        assert "INBOX" in content_item.metadata["labels"]

    def test_extract_message_info_multipart_message(self):
        """Test extracting info from multipart email message."""
        content_item = self.gmail_service.extract_message_info(self.sample_multipart_message)

        assert isinstance(content_item, ContentItem)
        assert content_item.title == "Multipart Email"
        assert content_item.source == "Gmail"
        assert content_item.author == "multipart@example.com"
        assert content_item.content == "Plain text part"  # Should extract plain text part
        assert content_item.metadata["id"] == "msg_003"

    def test_extract_message_info_missing_headers(self):
        """Test extracting info from message with missing headers."""
        message_no_headers = {
            "id": "msg_004",
            "snippet": "No headers message",
            "payload": {"headers": [], "body": {}},
        }

        content_item = self.gmail_service.extract_message_info(message_no_headers)

        assert content_item.title == "No Subject"
        assert content_item.author == "Unknown Sender"
        assert content_item.metadata["date"] == "Unknown Date"

    def test_extract_message_info_fallback_to_snippet(self):
        """Test fallback to snippet when body extraction fails."""
        message_no_body = {
            "id": "msg_005",
            "snippet": "This is the snippet content",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "No Body Message"},
                    {"name": "From", "value": "nobodysender@example.com"},
                ],
                "body": {},  # No body data
            },
        }

        content_item = self.gmail_service.extract_message_info(message_no_body)

        assert content_item.content == "This is the snippet content"

    def test_extract_body_simple_body(self):
        """Test _extract_body with simple body."""
        payload = {
            "body": {
                "data": "VGVzdCBib2R5IGNvbnRlbnQ="  # Base64 encoded "Test body content"
            }
        }

        body = self.gmail_service._extract_body(payload)

        assert body == "Test body content"

    def test_extract_body_multipart(self):
        """Test _extract_body with multipart payload."""
        payload = {
            "parts": [
                {
                    "mimeType": "text/html",
                    "body": {
                        "data": "PGh0bWw+SFRNTDwvaHRtbD4="  # HTML content
                    },
                },
                {
                    "mimeType": "text/plain",
                    "body": {
                        "data": "UGxhaW4gdGV4dCBjb250ZW50"  # Base64 encoded "Plain text content"
                    },
                },
            ]
        }

        body = self.gmail_service._extract_body(payload)

        assert body == "Plain text content"  # Should prefer plain text

    def test_extract_body_no_data(self):
        """Test _extract_body with no extractable data."""
        payload = {"body": {}, "parts": []}

        body = self.gmail_service._extract_body(payload)

        assert body == ""

    @patch("googleapiclient.discovery.build")
    def test_print_inbox_summary_success(self, mock_build, capsys):
        """Test printing inbox summary successfully."""
        mock_service = Mock()
        mock_build.return_value = mock_service
        self.gmail_service.service = mock_service

        # Mock API responses
        mock_list_call = Mock()
        mock_list_call.execute.return_value = self.sample_message_list
        mock_service.users().messages().list.return_value = mock_list_call

        mock_get_call = Mock()
        mock_get_call.execute.return_value = self.sample_message_detail
        mock_service.users().messages().get.return_value = mock_get_call

        self.gmail_service.print_inbox_summary(max_results=2)

        captured = capsys.readouterr()
        output = captured.out

        assert "INBOX SUMMARY" in output
        assert "Test Email Subject" in output
        assert "sender@example.com" in output

    def test_print_inbox_summary_not_authenticated(self, capsys):
        """Test print_inbox_summary when not authenticated."""
        # Ensure service is None
        self.gmail_service.service = None

        result = self.gmail_service.get_inbox_messages()

        # Should print error message and return None
        captured = capsys.readouterr()
        assert "Error: Gmail service not authenticated" in captured.out
        assert result is None

    @patch("googleapiclient.discovery.build")
    def test_print_inbox_summary_empty_inbox(self, mock_build, capsys):
        """Test print_inbox_summary with empty inbox."""
        mock_service = Mock()
        mock_build.return_value = mock_service
        self.gmail_service.service = mock_service

        mock_list_call = Mock()
        mock_list_call.execute.return_value = {"messages": []}
        mock_service.users().messages().list.return_value = mock_list_call

        self.gmail_service.print_inbox_summary()

        captured = capsys.readouterr()
        output = captured.out

        assert "No messages found in inbox." in output

    def test_extract_body_invalid_base64(self):
        """Test _extract_body with invalid base64 data."""
        payload = {"body": {"data": "invalid-base64!"}}

        # Should handle invalid base64 gracefully and return empty string
        body = self.gmail_service._extract_body(payload)
        assert body == ""

    @patch("base64.urlsafe_b64decode")
    def test_extract_body_decode_exception(self, mock_decode):
        """Test _extract_body when base64 decode raises exception."""
        mock_decode.side_effect = Exception("Decode error")

        payload = {"body": {"data": "VGVzdA=="}}

        # Should handle exception gracefully and return empty string
        body = self.gmail_service._extract_body(payload)
        assert body == ""
