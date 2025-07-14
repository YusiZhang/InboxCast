"""
RSS service for reading and parsing RSS feeds.
"""

import feedparser
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime


class RSSService:
    """Service class for RSS feed integration."""
    
    def __init__(self, user_agent: str = "InboxCast/1.0"):
        """
        Initialize RSS service.
        
        Args:
            user_agent: User agent string for HTTP requests
        """
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
    
    def fetch_feed(self, feed_url: str) -> Optional[feedparser.FeedParserDict]:
        """
        Fetch and parse an RSS feed from URL.
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            Parsed feed object or None if error
        """
        try:
            # Use feedparser with custom user agent
            response = self.session.get(feed_url, timeout=30)
            response.raise_for_status()
            
            # Parse the feed content
            feed = feedparser.parse(response.content)
            
            if feed.bozo and feed.bozo_exception:
                print(f"Warning: Feed parsing issue - {feed.bozo_exception}")
            
            return feed
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching RSS feed '{feed_url}': {str(e)}")
            return None
        except Exception as e:
            print(f"Error parsing RSS feed: {str(e)}")
            return None
    
    def get_feed_entries(self, feed_url: str, max_entries: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get entries from an RSS feed.
        
        Args:
            feed_url: URL of the RSS feed
            max_entries: Maximum number of entries to retrieve
            
        Returns:
            List of entry dictionaries or None if error
        """
        feed = self.fetch_feed(feed_url)
        
        if not feed:
            return None
        
        if not feed.entries:
            print(f"No entries found in RSS feed: {feed_url}")
            return []
        
        # Extract information from entries
        entries = []
        for entry in feed.entries[:max_entries]:
            entry_info = self.extract_entry_info(entry)
            entries.append(entry_info)
        
        return entries
    
    def extract_entry_info(self, entry: feedparser.FeedParserDict) -> Dict[str, Any]:
        """
        Extract useful information from an RSS entry.
        
        Args:
            entry: RSS entry object
            
        Returns:
            Dictionary with extracted entry information
        """
        # Get published date
        published = getattr(entry, 'published', '')
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                published_dt = datetime(*entry.published_parsed[:6])
                published = published_dt.strftime('%Y-%m-%d %H:%M:%S')
            except (TypeError, ValueError):
                pass
        
        # Get content/summary
        content = ''
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if entry.content else ''
        elif hasattr(entry, 'summary'):
            content = entry.summary
        
        # Get author
        author = getattr(entry, 'author', 'Unknown Author')
        
        return {
            'title': getattr(entry, 'title', 'No Title'),
            'link': getattr(entry, 'link', ''),
            'author': author,
            'published': published,
            'content': content,
            'summary': getattr(entry, 'summary', ''),
            'id': getattr(entry, 'id', getattr(entry, 'link', ''))
        }
    
    def get_feed_info(self, feed_url: str) -> Optional[Dict[str, str]]:
        """
        Get information about the RSS feed itself.
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            Dictionary with feed information or None if error
        """
        feed = self.fetch_feed(feed_url)
        
        if not feed:
            return None
        
        feed_info = feed.get('feed', {})
        
        return {
            'title': feed_info.get('title', 'Unknown Feed'),
            'description': feed_info.get('description', ''),
            'link': feed_info.get('link', ''),
            'language': feed_info.get('language', ''),
            'last_updated': feed_info.get('updated', ''),
            'total_entries': len(feed.entries) if hasattr(feed, 'entries') else 0
        }
    
    def print_feed_summary(self, feed_url: str, max_entries: int = 5) -> None:
        """
        Print a summary of RSS feed entries for testing purposes.
        
        Args:
            feed_url: URL of the RSS feed
            max_entries: Maximum number of entries to display
        """
        print(f"\n=== RSS FEED SUMMARY ===")
        print(f"Feed URL: {feed_url}")
        
        # Get feed info
        feed_info = self.get_feed_info(feed_url)
        if feed_info:
            print(f"Feed Title: {feed_info['title']}")
            print(f"Feed Description: {feed_info['description'][:100]}...")
            print(f"Total Entries: {feed_info['total_entries']}")
        
        # Get entries
        entries = self.get_feed_entries(feed_url, max_entries)
        
        if entries is None:
            return
        
        if not entries:
            print("No entries found in RSS feed.")
            return
        
        print(f"\n=== RECENT ENTRIES ({len(entries)} entries) ===")
        print("-" * 60)
        
        for i, entry in enumerate(entries, 1):
            print(f"{i}. Title: {entry['title']}")
            print(f"   Author: {entry['author']}")
            print(f"   Published: {entry['published']}")
            print(f"   Link: {entry['link']}")
            if entry['summary']:
                summary = entry['summary'][:100].replace('\n', ' ').replace('\r', ' ')
                print(f"   Summary: {summary}...")
            print("-" * 60)