"""
RSS feed router for handling RSS feed processing
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional

from services import RSSService

router = APIRouter()

class RSSFeedRequest(BaseModel):
    url: HttpUrl
    max_entries: Optional[int] = 10

class RSSFeedResponse(BaseModel):
    title: str
    description: Optional[str]
    total_entries: int
    entries: List[Dict]


@router.post("/fetch")
async def fetch_feed(request: RSSFeedRequest) -> RSSFeedResponse:
    """Fetch and parse an RSS feed."""
    try:
        rss_service = RSSService()
        
        # Get feed info
        feed_info = rss_service.get_feed_info(str(request.url))
        if not feed_info:
            raise HTTPException(status_code=400, detail="Could not fetch RSS feed")
        
        # Get feed entries
        entries = rss_service.get_feed_entries(str(request.url), max_entries=request.max_entries)
        
        # Extract entry information
        processed_entries = []
        for entry in entries:
            entry_info = rss_service.extract_entry_info(entry, str(request.url))
            processed_entries.append(entry_info.dict())
        
        return RSSFeedResponse(
            title=feed_info.get("title", "Unknown"),
            description=feed_info.get("description"),
            total_entries=feed_info.get("total_entries", 0),
            entries=processed_entries
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching RSS feed: {str(e)}")


@router.get("/test")
async def test_rss():
    """Test RSS functionality with a sample feed."""
    try:
        rss_service = RSSService()
        
        # Create a test feed content
        test_feed_content = '''<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>InboxCast Test Feed</title>
    <description>A sample RSS feed for testing InboxCast functionality</description>
    <item>
      <title>Welcome to InboxCast</title>
      <description>This is a test article about InboxCast features.</description>
      <link>https://example.com/article1</link>
      <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
    </item>
    <item>
      <title>AI-Powered Content Generation</title>
      <description>Learn how InboxCast uses AI to create audio content.</description>
      <link>https://example.com/article2</link>
      <pubDate>Mon, 01 Jan 2024 13:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>'''
        
        import feedparser
        feed = feedparser.parse(test_feed_content)
        
        # Process the feed
        entries = []
        for entry in feed.entries:
            entry_info = rss_service.extract_entry_info(entry, "test://feed")
            entries.append(entry_info.dict())
        
        return RSSFeedResponse(
            title=feed.feed.get('title', 'Test Feed'),
            description=feed.feed.get('description', 'Test description'),
            total_entries=len(feed.entries),
            entries=entries
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in RSS test: {str(e)}")