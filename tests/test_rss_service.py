"""
Unit tests for the RSS service.
"""

from unittest.mock import Mock, patch

import feedparser
import responses

from models.content_model import ContentItem
from services.rss_service import RSSService


class TestRSSService:
    """Test cases for RSSService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.rss_service = RSSService()
        self.test_feed_url = "https://example.com/feed.xml"

        # Sample RSS feed content
        self.sample_rss_content = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test RSS Feed</title>
    <description>A sample RSS feed for testing</description>
    <link>https://example.com</link>
    <language>en-us</language>
    <lastBuildDate>Mon, 01 Jan 2024 12:00:00 GMT</lastBuildDate>

    <item>
      <title>First Test Article</title>
      <description>This is the first test article description</description>
      <link>https://example.com/article1</link>
      <author>test@example.com (Test Author)</author>
      <pubDate>Mon, 01 Jan 2024 10:00:00 GMT</pubDate>
      <guid>https://example.com/article1</guid>
    </item>

    <item>
      <title>Second Test Article</title>
      <description>This is the second test article description</description>
      <link>https://example.com/article2</link>
      <author>author2@example.com (Another Author)</author>
      <pubDate>Sun, 31 Dec 2023 15:30:00 GMT</pubDate>
      <guid>https://example.com/article2</guid>
    </item>
  </channel>
</rss>"""

    @responses.activate
    def test_fetch_feed_success(self):
        """Test successful RSS feed fetching."""
        responses.add(
            responses.GET,
            self.test_feed_url,
            body=self.sample_rss_content,
            status=200,
            content_type="application/rss+xml",
        )

        feed = self.rss_service.fetch_feed(self.test_feed_url)

        assert feed is not None
        assert hasattr(feed, "feed")
        assert hasattr(feed, "entries")
        assert feed.feed.title == "Test RSS Feed"
        assert len(feed.entries) == 2

    @responses.activate
    def test_fetch_feed_network_error(self):
        """Test RSS feed fetching with network error."""
        responses.add(responses.GET, self.test_feed_url, body="Not Found", status=404)

        feed = self.rss_service.fetch_feed(self.test_feed_url)

        assert feed is None

    @responses.activate
    def test_fetch_feed_timeout_error(self):
        """Test RSS feed fetching with timeout."""
        responses.add(responses.GET, self.test_feed_url, body=Exception("Connection timeout"))

        feed = self.rss_service.fetch_feed(self.test_feed_url)

        assert feed is None

    @responses.activate
    def test_get_feed_entries_success(self):
        """Test getting RSS feed entries successfully."""
        responses.add(
            responses.GET,
            self.test_feed_url,
            body=self.sample_rss_content,
            status=200,
            content_type="application/rss+xml",
        )

        entries = self.rss_service.get_feed_entries(self.test_feed_url, max_entries=5)

        assert entries is not None
        assert len(entries) == 2  # Our sample has 2 entries
        assert all(isinstance(entry, ContentItem) for entry in entries)

        # Check first entry
        first_entry = entries[0]
        assert first_entry.title == "First Test Article"
        assert first_entry.source == f"RSS: {self.test_feed_url}"
        assert "Test Author" in first_entry.author
        assert first_entry.content == "This is the first test article description"
        assert first_entry.metadata["link"] == "https://example.com/article1"

    @responses.activate
    def test_get_feed_entries_max_limit(self):
        """Test that max_entries parameter limits results."""
        responses.add(
            responses.GET,
            self.test_feed_url,
            body=self.sample_rss_content,
            status=200,
            content_type="application/rss+xml",
        )

        entries = self.rss_service.get_feed_entries(self.test_feed_url, max_entries=1)

        assert entries is not None
        assert len(entries) == 1
        assert entries[0].title == "First Test Article"

    @responses.activate
    def test_get_feed_entries_empty_feed(self):
        """Test getting entries from empty RSS feed."""
        empty_rss = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Empty Feed</title>
    <description>An RSS feed with no entries</description>
  </channel>
</rss>"""

        responses.add(
            responses.GET,
            self.test_feed_url,
            body=empty_rss,
            status=200,
            content_type="application/rss+xml",
        )

        entries = self.rss_service.get_feed_entries(self.test_feed_url)

        assert entries is not None
        assert len(entries) == 0

    @responses.activate
    def test_get_feed_entries_fetch_error(self):
        """Test get_feed_entries when feed fetch fails."""
        responses.add(responses.GET, self.test_feed_url, status=500)

        entries = self.rss_service.get_feed_entries(self.test_feed_url)

        assert entries is None

    def test_extract_entry_info(self):
        """Test extracting information from RSS entry."""
        # Parse our sample RSS content
        feed = feedparser.parse(self.sample_rss_content)
        entry = feed.entries[0]

        content_item = self.rss_service.extract_entry_info(entry, self.test_feed_url)

        assert isinstance(content_item, ContentItem)
        assert content_item.title == "First Test Article"
        assert content_item.source == f"RSS: {self.test_feed_url}"
        assert "Test Author" in content_item.author
        assert content_item.content == "This is the first test article description"
        assert content_item.metadata["link"] == "https://example.com/article1"
        assert content_item.metadata["id"] == "https://example.com/article1"

    def test_extract_entry_info_minimal_data(self):
        """Test extracting info from RSS entry with minimal data."""
        # Create a minimal entry
        minimal_entry = feedparser.FeedParserDict()
        minimal_entry.title = "Minimal Title"

        content_item = self.rss_service.extract_entry_info(minimal_entry, self.test_feed_url)

        assert isinstance(content_item, ContentItem)
        assert content_item.title == "Minimal Title"
        assert content_item.source == f"RSS: {self.test_feed_url}"
        assert content_item.author == "Unknown Author"
        assert content_item.content == ""
        assert content_item.metadata["link"] == ""

    @responses.activate
    def test_get_feed_info_success(self):
        """Test getting RSS feed information successfully."""
        responses.add(
            responses.GET,
            self.test_feed_url,
            body=self.sample_rss_content,
            status=200,
            content_type="application/rss+xml",
        )

        feed_info = self.rss_service.get_feed_info(self.test_feed_url)

        assert feed_info is not None
        assert feed_info["title"] == "Test RSS Feed"
        assert feed_info["description"] == "A sample RSS feed for testing"
        assert feed_info["link"] == "https://example.com"
        assert feed_info["language"] == "en-us"
        assert feed_info["total_entries"] == 2

    @responses.activate
    def test_get_feed_info_fetch_error(self):
        """Test get_feed_info when feed fetch fails."""
        responses.add(responses.GET, self.test_feed_url, status=404)

        feed_info = self.rss_service.get_feed_info(self.test_feed_url)

        assert feed_info is None

    @responses.activate
    def test_print_feed_summary_success(self, capsys):
        """Test printing RSS feed summary."""
        responses.add(
            responses.GET,
            self.test_feed_url,
            body=self.sample_rss_content,
            status=200,
            content_type="application/rss+xml",
        )

        self.rss_service.print_feed_summary(self.test_feed_url, max_entries=2)

        captured = capsys.readouterr()
        output = captured.out

        assert "RSS FEED SUMMARY" in output
        assert self.test_feed_url in output
        assert "Test RSS Feed" in output
        assert "First Test Article" in output
        assert "Second Test Article" in output

    @responses.activate
    def test_print_feed_summary_fetch_error(self, capsys):
        """Test printing feed summary when fetch fails."""
        responses.add(responses.GET, self.test_feed_url, status=500)

        self.rss_service.print_feed_summary(self.test_feed_url)

        captured = capsys.readouterr()
        output = captured.out

        assert "RSS FEED SUMMARY" in output
        # Should return early without showing entries

    def test_rss_service_initialization(self):
        """Test RSS service initialization."""
        custom_service = RSSService(user_agent="Custom Agent/2.0")

        assert custom_service.user_agent == "Custom Agent/2.0"
        assert custom_service.session.headers["User-Agent"] == "Custom Agent/2.0"

    def test_rss_service_default_initialization(self):
        """Test RSS service default initialization."""
        service = RSSService()

        assert service.user_agent == "InboxCast/1.0"
        assert service.session.headers["User-Agent"] == "InboxCast/1.0"

    @patch("feedparser.parse")
    def test_fetch_feed_parsing_exception(self, mock_parse):
        """Test fetch_feed when feedparser raises an exception."""
        mock_parse.side_effect = Exception("Parsing error")

        with patch.object(self.rss_service.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.content = self.sample_rss_content
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            feed = self.rss_service.fetch_feed(self.test_feed_url)

            assert feed is None

    def test_extract_entry_info_with_content_field(self):
        """Test extracting entry info when entry has content field."""
        # Create entry with content field
        entry = feedparser.FeedParserDict()
        entry.title = "Content Test"
        entry.author = "Content Author"
        entry.link = "https://example.com/content"
        entry.content = [feedparser.FeedParserDict({"value": "Rich content here"})]

        content_item = self.rss_service.extract_entry_info(entry, self.test_feed_url)

        assert content_item.content == "Rich content here"
        assert content_item.title == "Content Test"
        assert content_item.author == "Content Author"

    def test_extract_entry_info_with_published_parsed(self):
        """Test extracting entry info with published_parsed time."""
        entry = feedparser.FeedParserDict()
        entry.title = "Time Test"
        entry.published_parsed = (2024, 1, 1, 12, 30, 45, 0, 1, -1)

        content_item = self.rss_service.extract_entry_info(entry, self.test_feed_url)

        assert content_item.metadata["published"] == "2024-01-01 12:30:45"
