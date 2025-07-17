"""
Pydantic data model for MiniMax voice-over requests.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VoiceOverRequest(BaseModel):
    """
    Pydantic model for MiniMax voice-over requests.

    Supports basic MiniMax AI text-to-speech parameters including
    tone, speed, and language settings.
    """

    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True,  # Validate on assignment
    )

    text: str = Field(..., description="Text content to be voiced over", min_length=1)
    voice_id: str = Field(..., description="Specific voice model ID")
    speed: float = Field(
        default=1.0,
        description="Speech speed multiplier",
        ge=0.5,  # minimum speed
        le=2.0,  # maximum speed
    )
    vol: float = Field(default=1.0, description="Volume of the speech", ge=0, le=10)
    pitch: int = Field(default=0, description="Pitch of the speech", ge=-12, le=12)


class VoiceOverResponse(BaseModel):
    """
    Pydantic model for MiniMax voice-over API responses.
    """

    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
    )

    success: bool = Field(..., description="Whether the request was successful")
    audio_data: bytes | None = Field(default=None, description="Binary audio data")
    audio_format: str | None = Field(default=None, description="Audio format (e.g., 'mp3')")
    error_message: str | None = Field(default=None, description="Error message if unsuccessful")
