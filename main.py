"""
InboxCast - Convert inbox emails into PodCast
Main entry point for testing Gmail API and RSS integration.
"""

import os
from dotenv import load_dotenv

from services import GeminiService, GmailService, RSSService, MiniMaxService
from models import VoiceOverRequest

# Load environment variables from local.env
load_dotenv(dotenv_path="local.env")


def test_gmail_integration():
    """Test Gmail API integration."""
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
        return False

    # Authenticate with Gmail API
    print("\nAuthenticating with Gmail API...")
    if not gmail_service.authenticate():
        print("Authentication failed. Please check your credentials.")
        return False

    print("Authentication successful!")

    # Test inbox reading
    print("\nReading inbox messages...")
    try:
        gmail_service.print_inbox_summary(max_results=5)
        print("\nGmail API integration test completed successfully!")
        return True

    except Exception as e:
        print(f"Error during inbox reading: {str(e)}")
        return False


def test_rss_integration():
    """Test RSS feed integration."""
    print("\n\n=== InboxCast - RSS Integration Test ===")

    # Initialize RSS service
    rss_service = RSSService()

    # Test with some popular RSS feeds
    test_feeds = [
        "https://feeds.feedburner.com/oreilly/radar",  # O'Reilly Radar
        "https://rss.cnn.com/rss/edition.rss",         # CNN
        "https://feeds.feedburner.com/TechCrunch",     # TechCrunch
    ]

    success_count = 0

    for feed_url in test_feeds:
        print(f"\nTesting RSS feed: {feed_url}")
        try:
            # Try to get feed info first
            feed_info = rss_service.get_feed_info(feed_url)
            if feed_info:
                print(f"✓ Feed Title: {feed_info['title']}")
                print(f"✓ Total Entries: {feed_info['total_entries']}")
                success_count += 1
            else:
                print("✗ Could not fetch feed (network may be limited in this environment)")

        except Exception as e:
            print(f"✗ Error testing RSS feed: {str(e)}")

    # Test with local example if available
    try:
        import feedparser
        # Create a simple test feed content
        test_feed_content = '''<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>Test RSS Feed</title>
    <description>A sample feed for InboxCast testing</description>
    <item>
      <title>Sample Article</title>
      <description>This is a test article</description>
      <link>https://example.com/article</link>
    </item>
  </channel>
</rss>'''

        feed = feedparser.parse(test_feed_content)
        if feed.entries:
            print("\n✓ Local RSS parsing test successful!")
            print(f"  Feed Title: {feed.feed.get('title', 'Unknown')}")
            print(f"  Sample Entry: {feed.entries[0].get('title', 'Unknown')}")
            success_count += 1
    except Exception as e:
        print(f"✗ Local RSS test failed: {str(e)}")

    print(f"\nRSS integration test completed: {success_count} tests successful")
    return success_count > 0


def test_gemini_integration():
    """Test Google Gemini API integration."""
    print("\n\n=== InboxCast - Google Gemini API Integration Test ===")

    # Initialize Gemini service
    gemini_service = GeminiService()

    # Check for API key
    if not gemini_service.api_key:
        print("\nError: No Gemini API key found!")
        print("Please set GEMINI_API_KEY environment variable or provide api_key parameter.")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        print("\nSee README.md for detailed setup instructions.")
        return False

    # Test Gemini API
    print("\nTesting Gemini API...")
    try:
        gemini_service.print_generation_test()
        print("\nGemini API integration test completed successfully!")
        return True

    except Exception as e:
        print(f"Error during Gemini API test: {str(e)}")

def test_minimax_integration():
    """Test MiniMax AI voice-over integration."""
    print("\n\n=== InboxCast - MiniMax Voice-over Integration Test ===")

    # Initialize MiniMax service
    minimax_service = MiniMaxService()

    # Check for API key and Group ID
    if not minimax_service.api_key or not minimax_service.group_id:
        print("\nMiniMax API key or Group ID not found!")
        print("To test MiniMax integration:")
        print("1. Get an API key and Group ID from MiniMax AI (https://www.minimaxi.com/)")
        print("2. Set the MINIMAX_API_KEY and MINIMAX_GROUP_ID environment variables")
        print("3. Run the test again")
        print(
            "\nNote: The MiniMax service is fully implemented and ready to use once you provide the credentials."
        )
        return False

    print(f"\nFound MiniMax API key: {minimax_service.api_key[:8]}...")
    print(f"Found MiniMax Group ID: {minimax_service.group_id}")

    # Test voice-over generation
    print("\nTesting voice-over generation...")
    try:
        # Create a test voice-over request
        test_request = VoiceOverRequest(
            text="Welcome to InboxCast! This is a test of the MiniMax voice-over integration.",
            voice_id="English_captivating_female1",  # Example voice_id from API doc
        )

        # Generate voice-over
        response = minimax_service.generate_voice_over(test_request)

        if response.success:
            print("✓ Voice-over generation successful!")
            if response.audio_data:
                print(f"  Audio data size: {len(response.audio_data)} bytes")
            if response.audio_format:
                print(f"  Format: {response.audio_format}")

            # Try to save the audio file
            if response.audio_data:
                output_file = f"./tmp/test_voiceover.{response.audio_format or 'mp3'}"
                if minimax_service.save_audio_to_file(response, output_file):
                    print(f"✓ Audio saved to: {output_file}")
                else:
                    print("✗ Failed to save audio file")

            return True
        else:
            print(f"✗ Voice-over generation failed: {response.error_message}")
            return False

    except Exception as e:
        print(f"✗ Error during voice-over test: {str(e)}")
        return False


def main():
    """Main function to test Gmail, RSS, and MiniMax integrations."""
    print("=== InboxCast - Testing Gmail, RSS, Gemini, and MiniMax Integration ===\n")
    
    # Test RSS integration (doesn't require credentials)
    # rss_success = test_rss_integration()

    # Test Gmail integration (requires credentials)
    # gmail_success = test_gmail_integration()

    # Test Gemini integration (requires API key)
    # gemini_success = test_gemini_integration()

    
    # Test MiniMax integration (requires API key)
    minimax_success = test_minimax_integration()
    
    print("\n" + "="*60)
    print("INTEGRATION TEST SUMMARY:")
    # print(f"RSS Integration: {'✓ SUCCESS' if rss_success else '✗ FAILED'}")
    # print(f"Gmail Integration: {'✓ SUCCESS' if gmail_success else '✗ FAILED (credentials needed)'}")
    # print(f"Gemini Integration: {'✓ SUCCESS' if gemini_success else '✗ FAILED (API key needed)'}")
    print(f"MiniMax Voice-over: {'✓ SUCCESS' if minimax_success else '✗ FAILED (API key needed)'}")
    print("="*60)


if __name__ == "__main__":
    main()
