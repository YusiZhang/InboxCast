"""
Pydantic data model for content from different sources (Gmail, RSS, etc).
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class ContentItem(BaseModel):
    """
    Pydantic model for content items from different sources.
    
    All fields are optional to accommodate different source types and 
    varying data availability.
    """
    
    title: Optional[str] = None
    source: Optional[str] = None 
    author: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"  # Don't allow extra fields
        validate_assignment = True  # Validate on assignment