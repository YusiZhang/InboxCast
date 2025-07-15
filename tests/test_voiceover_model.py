"""
Tests for the VoiceOverRequest and VoiceOverResponse models.
"""

import pytest
from pydantic import ValidationError

from models import VoiceOverRequest, VoiceOverResponse


class TestVoiceOverRequest:
    """Test cases for VoiceOverRequest model."""

    def test_voiceover_request_creation_with_minimal_fields(self):
        """Test creating VoiceOverRequest with only required fields."""
        request = VoiceOverRequest(text="Hello world")

        assert request.text == "Hello world"
        assert request.tone == "neutral"  # default
        assert request.speed == 1.0  # default
        assert request.language == "en-US"  # default
        assert request.voice_id is None  # default

    def test_voiceover_request_creation_with_all_fields(self):
        """Test creating VoiceOverRequest with all fields specified."""
        request = VoiceOverRequest(
            text="Welcome to InboxCast",
            tone="friendly",
            speed=1.2,
            language="zh-CN",
            voice_id="voice_001",
        )

        assert request.text == "Welcome to InboxCast"
        assert request.tone == "friendly"
        assert request.speed == 1.2
        assert request.language == "zh-CN"
        assert request.voice_id == "voice_001"

    def test_voiceover_request_empty_text_validation(self):
        """Test that empty text is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VoiceOverRequest(text="")

        assert "at least 1 character" in str(exc_info.value)

    def test_voiceover_request_missing_text_validation(self):
        """Test that missing text is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VoiceOverRequest()

        assert "Field required" in str(exc_info.value)

    def test_voiceover_request_invalid_tone_validation(self):
        """Test that invalid tone values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VoiceOverRequest(text="Hello", tone="invalid_tone")

        assert "Input should be" in str(exc_info.value)

    def test_voiceover_request_invalid_speed_validation(self):
        """Test that invalid speed values are rejected."""
        # Too slow
        with pytest.raises(ValidationError) as exc_info:
            VoiceOverRequest(text="Hello", speed=0.3)
        assert "greater than or equal to 0.5" in str(exc_info.value)

        # Too fast
        with pytest.raises(ValidationError) as exc_info:
            VoiceOverRequest(text="Hello", speed=2.5)
        assert "less than or equal to 2" in str(exc_info.value)

    def test_voiceover_request_invalid_language_validation(self):
        """Test that invalid language values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VoiceOverRequest(text="Hello", language="invalid_lang")

        assert "Input should be" in str(exc_info.value)

    def test_voiceover_request_extra_fields_forbidden(self):
        """Test that extra fields are not allowed."""
        with pytest.raises(ValidationError) as exc_info:
            VoiceOverRequest(text="Hello", extra_field="not_allowed")

        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_voiceover_request_valid_tones(self):
        """Test all valid tone values."""
        valid_tones = ["neutral", "friendly", "professional", "energetic", "calm"]

        for tone in valid_tones:
            request = VoiceOverRequest(text="Hello", tone=tone)
            assert request.tone == tone

    def test_voiceover_request_valid_languages(self):
        """Test all valid language values."""
        valid_languages = ["en-US", "zh-CN", "ja-JP", "ko-KR", "es-ES", "fr-FR", "de-DE"]

        for language in valid_languages:
            request = VoiceOverRequest(text="Hello", language=language)
            assert request.language == language

    def test_voiceover_request_dict_conversion(self):
        """Test converting VoiceOverRequest to dictionary."""
        request = VoiceOverRequest(
            text="Test content",
            tone="professional",
            speed=1.5,
            language="fr-FR",
            voice_id="voice_123",
        )

        request_dict = request.model_dump()
        expected = {
            "text": "Test content",
            "tone": "professional",
            "speed": 1.5,
            "language": "fr-FR",
            "voice_id": "voice_123",
        }

        assert request_dict == expected

    def test_voiceover_request_from_dict(self):
        """Test creating VoiceOverRequest from dictionary."""
        data = {"text": "Test content", "tone": "energetic", "speed": 0.8, "language": "de-DE"}

        request = VoiceOverRequest(**data)
        assert request.text == "Test content"
        assert request.tone == "energetic"
        assert request.speed == 0.8
        assert request.language == "de-DE"


class TestVoiceOverResponse:
    """Test cases for VoiceOverResponse model."""

    def test_voiceover_response_success_with_url(self):
        """Test creating successful VoiceOverResponse with audio URL."""
        response = VoiceOverResponse(
            success=True,
            audio_url="https://api.example.com/audio/123.mp3",
            duration=45.5,
            format="mp3",
        )

        assert response.success is True
        assert response.audio_url == "https://api.example.com/audio/123.mp3"
        assert response.audio_data is None
        assert response.duration == 45.5
        assert response.format == "mp3"
        assert response.error_message is None

    def test_voiceover_response_success_with_data(self):
        """Test creating successful VoiceOverResponse with audio data."""
        audio_bytes = b"fake_audio_data"
        response = VoiceOverResponse(
            success=True, audio_data=audio_bytes, duration=30.0, format="wav"
        )

        assert response.success is True
        assert response.audio_url is None
        assert response.audio_data == audio_bytes
        assert response.duration == 30.0
        assert response.format == "wav"
        assert response.error_message is None

    def test_voiceover_response_failure(self):
        """Test creating failed VoiceOverResponse."""
        response = VoiceOverResponse(success=False, error_message="API rate limit exceeded")

        assert response.success is False
        assert response.audio_url is None
        assert response.audio_data is None
        assert response.duration is None
        assert response.format is None
        assert response.error_message == "API rate limit exceeded"

    def test_voiceover_response_minimal_success(self):
        """Test creating minimal successful VoiceOverResponse."""
        response = VoiceOverResponse(success=True)

        assert response.success is True
        assert response.audio_url is None
        assert response.audio_data is None
        assert response.duration is None
        assert response.format is None
        assert response.error_message is None

    def test_voiceover_response_extra_fields_forbidden(self):
        """Test that extra fields are not allowed."""
        with pytest.raises(ValidationError) as exc_info:
            VoiceOverResponse(success=True, extra_field="not_allowed")

        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_voiceover_response_dict_conversion(self):
        """Test converting VoiceOverResponse to dictionary."""
        response = VoiceOverResponse(
            success=True, audio_url="https://example.com/audio.mp3", duration=25.3, format="mp3"
        )

        response_dict = response.model_dump()
        expected = {
            "success": True,
            "audio_url": "https://example.com/audio.mp3",
            "audio_data": None,
            "duration": 25.3,
            "format": "mp3",
            "error_message": None,
        }

        assert response_dict == expected

    def test_voiceover_response_exclude_none_values(self):
        """Test excluding None values from dictionary representation."""
        response = VoiceOverResponse(success=True, audio_url="https://example.com/audio.mp3")

        response_dict = response.model_dump(exclude_none=True)
        expected = {"success": True, "audio_url": "https://example.com/audio.mp3"}

        assert response_dict == expected
