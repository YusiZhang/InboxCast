"""
Unit tests for the ContentItem model.
"""

import pytest
from pydantic import ValidationError

from models.content_model import ContentItem


class TestContentItem:
    """Test cases for ContentItem model."""

    def test_content_item_creation_with_all_fields(self):
        """Test creating ContentItem with all fields provided."""
        metadata = {"id": "test_id_123", "date": "2023-01-01", "tags": ["test", "example"]}

        content_item = ContentItem(
            title="Test Title",
            source="Test Source",
            author="Test Author",
            content="Test content body",
            metadata=metadata,
        )

        assert content_item.title == "Test Title"
        assert content_item.source == "Test Source"
        assert content_item.author == "Test Author"
        assert content_item.content == "Test content body"
        assert content_item.metadata == metadata

    def test_content_item_creation_with_minimal_fields(self):
        """Test creating ContentItem with minimal fields."""
        content_item = ContentItem()

        assert content_item.title is None
        assert content_item.source is None
        assert content_item.author is None
        assert content_item.content is None
        assert content_item.metadata is None

    def test_content_item_creation_with_partial_fields(self):
        """Test creating ContentItem with some fields."""
        content_item = ContentItem(title="Partial Title", author="Partial Author")

        assert content_item.title == "Partial Title"
        assert content_item.author == "Partial Author"
        assert content_item.source is None
        assert content_item.content is None
        assert content_item.metadata is None

    def test_content_item_validation_assignment(self):
        """Test that validation works on assignment."""
        content_item = ContentItem()

        # Valid assignment
        content_item.title = "New Title"
        assert content_item.title == "New Title"

        # Valid metadata assignment
        content_item.metadata = {"key": "value"}
        assert content_item.metadata == {"key": "value"}

    def test_content_item_extra_fields_forbidden(self):
        """Test that extra fields are not allowed."""
        with pytest.raises(ValidationError) as exc_info:
            ContentItem(title="Test", extra_field="should not be allowed")

        assert "extra_field" in str(exc_info.value)

    def test_content_item_dict_conversion(self):
        """Test converting ContentItem to dictionary."""
        metadata = {"id": "123", "type": "email"}
        content_item = ContentItem(title="Test Title", source="Gmail", metadata=metadata)

        content_dict = content_item.model_dump()

        assert content_dict["title"] == "Test Title"
        assert content_dict["source"] == "Gmail"
        assert content_dict["author"] is None
        assert content_dict["content"] is None
        assert content_dict["metadata"] == metadata

    def test_content_item_from_dict(self):
        """Test creating ContentItem from dictionary."""
        data = {
            "title": "From Dict Title",
            "source": "RSS",
            "author": "Dict Author",
            "content": "Dict content",
            "metadata": {"link": "https://example.com"},
        }

        content_item = ContentItem(**data)

        assert content_item.title == data["title"]
        assert content_item.source == data["source"]
        assert content_item.author == data["author"]
        assert content_item.content == data["content"]
        assert content_item.metadata == data["metadata"]

    def test_content_item_exclude_none_values(self):
        """Test excluding None values when converting to dict."""
        content_item = ContentItem(
            title="Test Title",
            source="Test Source",
            # author, content, metadata are None
        )

        content_dict = content_item.model_dump(exclude_none=True)

        assert content_dict == {"title": "Test Title", "source": "Test Source"}
        assert "author" not in content_dict
        assert "content" not in content_dict
        assert "metadata" not in content_dict
