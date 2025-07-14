"""
Services package for InboxCast application.
Contains service classes for external API integrations.
"""

from .gmail_service import GmailService

__all__ = ['GmailService']