"""
Gmail API service for reading authenticated user's inbox.
"""

import os
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from models import ContentItem


class GmailService:
    """Service class for Gmail API integration."""
    
    # Gmail API scope for reading emails
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.json'):
        """
        Initialize Gmail service.
        
        Args:
            credentials_file: Path to OAuth2 credentials file from Google Cloud Console
            token_file: Path to store user access token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.creds = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Load existing token if available
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
            # If there are no valid credentials, request authorization
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        print(f"Error: Credentials file '{self.credentials_file}' not found.")
                        print("Please download OAuth2 credentials from Google Cloud Console.")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(self.token_file, 'w') as token:
                    token.write(self.creds.to_json())
            
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=self.creds)
            return True
            
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False
    
    def get_inbox_messages(self, max_results: int = 10) -> Optional[List[ContentItem]]:
        """
        Get messages from the user's inbox.
        
        Args:
            max_results: Maximum number of messages to retrieve
            
        Returns:
            List of ContentItem instances or None if error
        """
        if not self.service:
            print("Error: Gmail service not authenticated. Call authenticate() first.")
            return None
        
        try:
            # Get list of messages from inbox
            results = self.service.users().messages().list(
                userId='me', labelIds=['INBOX'], maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("No messages found in inbox.")
                return []
            
            # Get detailed information for each message
            detailed_messages = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id'], format='full'
                ).execute()
                content_item = self.extract_message_info(msg)
                detailed_messages.append(content_item)
            
            return detailed_messages
            
        except Exception as e:
            print(f"Error retrieving inbox messages: {str(e)}")
            return None
    
    def extract_message_info(self, message: Dict[str, Any]) -> ContentItem:
        """
        Extract useful information from a Gmail message.
        
        Args:
            message: Gmail message object
            
        Returns:
            ContentItem with extracted message information
        """
        headers = message['payload'].get('headers', [])
        
        # Extract common headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
        
        # Extract message body (simplified - gets plain text if available)
        body = self._extract_body(message['payload'])
        
        return ContentItem(
            title=subject,
            source='Gmail',
            author=sender,
            content=body or message.get('snippet', ''),
            metadata={
                'id': message['id'],
                'date': date,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', [])
            }
        )
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract body text from message payload.
        
        Args:
            payload: Message payload
            
        Returns:
            Extracted body text
        """
        body = ""
        
        if 'body' in payload and 'data' in payload['body']:
            import base64
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    import base64
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        
        return body
    
    def print_inbox_summary(self, max_results: int = 5) -> None:
        """
        Print a summary of inbox messages for testing purposes.
        
        Args:
            max_results: Maximum number of messages to display
        """
        messages = self.get_inbox_messages(max_results)
        
        if messages is None:
            return
        
        if not messages:
            print("No messages found in inbox.")
            return
        
        print(f"\n=== INBOX SUMMARY ({len(messages)} messages) ===")
        print("-" * 60)
        
        for i, content_item in enumerate(messages, 1):
            print(f"{i}. Subject: {content_item.title}")
            print(f"   From: {content_item.author}")
            print(f"   Date: {content_item.metadata.get('date', 'Unknown')}")
            print(f"   Snippet: {content_item.metadata.get('snippet', '')[:100]}...")
            print("-" * 60)