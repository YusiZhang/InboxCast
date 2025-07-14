"""
Pydantic data model for content from different sources (Gmail, RSS, etc).
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class ContentItem(BaseModel):
    """
    Pydantic model for content items from different sources.

    All fields are optional to accommodate different source types and
    varying data availability.
    """

    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True,  # Validate on assignment
    )

    title: str | None = None
    source: str | None = None
    author: str | None = None
    content: str | None = None
    metadata: dict[str, Any] | None = None
