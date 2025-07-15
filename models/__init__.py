"""
Models package for InboxCast application.
Contains data models for content from different sources.
"""

from .content_model import ContentItem
from .gemini_model import GeminiConfig, GeminiResponse

__all__ = ["ContentItem", "GeminiConfig", "GeminiResponse"]
