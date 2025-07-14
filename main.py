"""
InboxCast - Convert inbox emails into PodCast
Main entry point for testing Gmail API integration.
"""

import os
from services import GmailService


def main():
    """Main function to test Gmail API integration."""
    print("=== InboxCast - Gmail API Integration Test ===")
    
    # Initialize Gmail service
    gmail_service = GmailService()
    
    # Check for credentials file
    if not os.path.exists('credentials.json'):
        print("\nError: credentials.json not found!")
        print("Please follow these steps:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("2. Create a new project or select existing one")
        print("3. Enable Gmail API")
        print("4. Create OAuth2 credentials (Desktop application)")
        print("5. Download credentials and save as 'credentials.json' in project root")
        print("\nSee README.md for detailed setup instructions.")
        return
    
    # Authenticate with Gmail API
    print("\nAuthenticating with Gmail API...")
    if not gmail_service.authenticate():
        print("Authentication failed. Please check your credentials.")
        return
    
    print("Authentication successful!")
    
    # Test inbox reading
    print("\nReading inbox messages...")
    try:
        gmail_service.print_inbox_summary(max_results=5)
        print("\nGmail API integration test completed successfully!")
        
    except Exception as e:
        print(f"Error during inbox reading: {str(e)}")


if __name__ == "__main__":
    main()
