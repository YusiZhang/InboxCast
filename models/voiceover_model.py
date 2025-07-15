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
    tone: Literal["neutral", "friendly", "professional", "energetic", "calm"] = Field(
        default="neutral", description="Voice tone style"
    )
    speed: float = Field(
        default=1.0,
        description="Speech speed multiplier",
        ge=0.5,  # minimum speed
        le=2.0,  # maximum speed
    )
    language: Literal["en-US", "zh-CN", "ja-JP", "ko-KR", "es-ES", "fr-FR", "de-DE"] = Field(
        default="en-US", description="Language for voice-over"
    )
    voice_id: str | None = Field(default=None, description="Specific voice model ID (optional)")


class VoiceOverResponse(BaseModel):
    """
    Pydantic model for MiniMax voice-over API responses.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    success: bool = Field(..., description="Whether the request was successful")
    audio_url: str | None = Field(default=None, description="URL to the generated audio file")
    audio_data: bytes | None = Field(default=None, description="Binary audio data")
    duration: float | None = Field(default=None, description="Audio duration in seconds")
    format: str | None = Field(default=None, description="Audio format (e.g., 'mp3', 'wav')")
    error_message: str | None = Field(default=None, description="Error message if unsuccessful")
