"""
Tests for the MiniMaxService class.
"""

import os
from unittest.mock import mock_open, patch

import requests
import responses

from models import VoiceOverRequest, VoiceOverResponse
from services import MiniMaxService


class TestMiniMaxService:
    """Test cases for MiniMaxService."""

    def test_minimax_service_initialization_with_api_key(self):
        """Test MiniMaxService initialization with API key."""
        service = MiniMaxService(api_key="test_api_key")

        assert service.api_key == "test_api_key"
        assert service.base_url == "https://api.minimax.chat/v1/text_to_speech"
        assert "Authorization" in service.session.headers
        assert service.session.headers["Authorization"] == "Bearer test_api_key"
        assert service.session.headers["Content-Type"] == "application/json"

    def test_minimax_service_initialization_with_custom_base_url(self):
        """Test MiniMaxService initialization with custom base URL."""
        custom_url = "https://custom.api.example.com/tts"
        service = MiniMaxService(api_key="test_key", base_url=custom_url)

        assert service.base_url == custom_url

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "env_api_key"})
    def test_minimax_service_initialization_from_environment(self):
        """Test MiniMaxService initialization from environment variable."""
        service = MiniMaxService()

        assert service.api_key == "env_api_key"
        assert "Authorization" in service.session.headers

    def test_minimax_service_initialization_no_api_key(self):
        """Test MiniMaxService initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            service = MiniMaxService()

            assert service.api_key is None
            assert "Authorization" not in service.session.headers

    @responses.activate
    def test_generate_voice_over_success_with_url(self):
        """Test successful voice-over generation with audio URL response."""
        # Mock API response
        responses.add(
            responses.POST,
            "https://api.minimax.chat/v1/text_to_speech",
            json={
                "audio_url": "https://api.minimax.chat/audio/123.mp3",
                "duration": 45.5,
                "format": "mp3",
            },
            status=200,
        )

        service = MiniMaxService(api_key="test_key")
        request = VoiceOverRequest(text="Hello world", tone="friendly", speed=1.2, language="en-US")

        response = service.generate_voice_over(request)

        assert response.success is True
        assert response.audio_url == "https://api.minimax.chat/audio/123.mp3"
        assert response.duration == 45.5
        assert response.format == "mp3"
        assert response.error_message is None

    @responses.activate
    def test_generate_voice_over_success_with_audio_data(self):
        """Test successful voice-over generation with audio data response."""
        import base64

        fake_audio = b"fake_audio_data"
        encoded_audio = base64.b64encode(fake_audio).decode()

        # Mock API response
        responses.add(
            responses.POST,
            "https://api.minimax.chat/v1/text_to_speech",
            json={"audio_data": encoded_audio, "duration": 30.0, "format": "wav"},
            status=200,
        )

        service = MiniMaxService(api_key="test_key")
        request = VoiceOverRequest(text="Test content")

        response = service.generate_voice_over(request)

        assert response.success is True
        assert response.audio_data == fake_audio
        assert response.duration == 30.0
        assert response.format == "wav"
        assert response.error_message is None

    def test_generate_voice_over_no_api_key(self):
        """Test voice-over generation without API key."""
        service = MiniMaxService()  # No API key
        request = VoiceOverRequest(text="Hello world")

        response = service.generate_voice_over(request)

        assert response.success is False
        assert "API key not provided" in response.error_message

    @responses.activate
    def test_generate_voice_over_api_error(self):
        """Test voice-over generation with API error response."""
        # Mock API error response
        responses.add(
            responses.POST,
            "https://api.minimax.chat/v1/text_to_speech",
            json={"message": "Invalid request parameters"},
            status=400,
        )

        service = MiniMaxService(api_key="test_key")
        request = VoiceOverRequest(text="Hello world")

        response = service.generate_voice_over(request)

        assert response.success is False
        assert "Invalid request parameters" in response.error_message

    @responses.activate
    def test_generate_voice_over_api_error_no_message(self):
        """Test voice-over generation with API error without message."""
        # Mock API error response without error message
        responses.add(
            responses.POST, "https://api.minimax.chat/v1/text_to_speech", json={}, status=500
        )

        service = MiniMaxService(api_key="test_key")
        request = VoiceOverRequest(text="Hello world")

        response = service.generate_voice_over(request)

        assert response.success is False
        assert "status 500" in response.error_message

    @responses.activate
    def test_generate_voice_over_timeout(self):
        """Test voice-over generation with timeout."""
        # Mock timeout by not adding any response
        responses.add(
            responses.POST,
            "https://api.minimax.chat/v1/text_to_speech",
            body=requests.exceptions.Timeout(),
        )

        service = MiniMaxService(api_key="test_key")
        request = VoiceOverRequest(text="Hello world")

        response = service.generate_voice_over(request)

        assert response.success is False
        assert "timeout" in response.error_message.lower()

    @responses.activate
    def test_generate_voice_over_connection_error(self):
        """Test voice-over generation with connection error."""
        # Mock connection error
        responses.add(
            responses.POST,
            "https://api.minimax.chat/v1/text_to_speech",
            body=requests.exceptions.ConnectionError(),
        )

        service = MiniMaxService(api_key="test_key")
        request = VoiceOverRequest(text="Hello world")

        response = service.generate_voice_over(request)

        assert response.success is False
        assert "connection error" in response.error_message.lower()

    @responses.activate
    def test_generate_voice_over_invalid_response_format(self):
        """Test voice-over generation with invalid response format."""
        # Mock response without audio_url or audio_data
        responses.add(
            responses.POST,
            "https://api.minimax.chat/v1/text_to_speech",
            json={"status": "completed"},
            status=200,
        )

        service = MiniMaxService(api_key="test_key")
        request = VoiceOverRequest(text="Hello world")

        response = service.generate_voice_over(request)

        assert response.success is False
        assert "Invalid response format" in response.error_message

    @responses.activate
    def test_generate_voice_over_with_voice_id(self):
        """Test voice-over generation with specific voice ID."""
        # Mock API response
        responses.add(
            responses.POST,
            "https://api.minimax.chat/v1/text_to_speech",
            json={
                "audio_url": "https://api.minimax.chat/audio/123.mp3",
                "duration": 25.0,
                "format": "mp3",
            },
            status=200,
        )

        service = MiniMaxService(api_key="test_key")
        request = VoiceOverRequest(text="Hello world", voice_id="voice_001")

        response = service.generate_voice_over(request)

        assert response.success is True

        # Verify voice_id was included in the request
        sent_request = responses.calls[0].request
        import json

        sent_data = json.loads(sent_request.body)
        assert sent_data["voice_setting"]["voice_id"] == "voice_001"

    @responses.activate
    def test_save_audio_to_file_with_audio_data(self):
        """Test saving audio data to file."""
        audio_data = b"fake_audio_content"
        response = VoiceOverResponse(success=True, audio_data=audio_data, format="mp3")

        service = MiniMaxService(api_key="test_key")

        with patch("builtins.open", mock_open()) as mock_file:
            result = service.save_audio_to_file(response, "/tmp/test.mp3")

            assert result is True
            mock_file.assert_called_once_with("/tmp/test.mp3", "wb")
            mock_file().write.assert_called_once_with(audio_data)

    @responses.activate
    def test_save_audio_to_file_with_audio_url(self):
        """Test saving audio from URL to file."""
        audio_content = b"downloaded_audio_content"

        # Mock the audio download
        responses.add(
            responses.GET, "https://api.minimax.chat/audio/123.mp3", body=audio_content, status=200
        )

        response = VoiceOverResponse(
            success=True, audio_url="https://api.minimax.chat/audio/123.mp3", format="mp3"
        )

        service = MiniMaxService(api_key="test_key")

        with patch("builtins.open", mock_open()) as mock_file:
            result = service.save_audio_to_file(response, "/tmp/test.mp3")

            assert result is True
            mock_file.assert_called_once_with("/tmp/test.mp3", "wb")
            mock_file().write.assert_called_once_with(audio_content)

    def test_save_audio_to_file_failed_response(self):
        """Test saving audio with failed response."""
        response = VoiceOverResponse(success=False, error_message="API error")

        service = MiniMaxService(api_key="test_key")
        result = service.save_audio_to_file(response, "/tmp/test.mp3")

        assert result is False

    @responses.activate
    def test_save_audio_to_file_download_error(self):
        """Test saving audio with download error."""
        # Mock failed download
        responses.add(responses.GET, "https://api.minimax.chat/audio/123.mp3", status=404)

        response = VoiceOverResponse(
            success=True, audio_url="https://api.minimax.chat/audio/123.mp3"
        )

        service = MiniMaxService(api_key="test_key")
        result = service.save_audio_to_file(response, "/tmp/test.mp3")

        assert result is False

    @responses.activate
    def test_test_connection_success(self):
        """Test successful connection test."""
        # Mock successful API response
        responses.add(
            responses.POST,
            "https://api.minimax.chat/v1/text_to_speech",
            json={
                "audio_url": "https://api.minimax.chat/audio/test.mp3",
                "duration": 1.0,
                "format": "mp3",
            },
            status=200,
        )

        service = MiniMaxService(api_key="test_key")
        result = service.test_connection()

        assert result is True

    @responses.activate
    def test_test_connection_failure(self):
        """Test failed connection test."""
        # Mock API error response
        responses.add(
            responses.POST,
            "https://api.minimax.chat/v1/text_to_speech",
            json={"message": "Unauthorized"},
            status=401,
        )

        service = MiniMaxService(api_key="test_key")
        result = service.test_connection()

        assert result is False

    def test_test_connection_no_api_key(self):
        """Test connection test without API key."""
        service = MiniMaxService()  # No API key
        result = service.test_connection()

        assert result is False

    @responses.activate
    def test_test_connection_exception(self):
        """Test connection test with exception."""
        # Mock connection error
        responses.add(
            responses.POST,
            "https://api.minimax.chat/v1/text_to_speech",
            body=requests.exceptions.ConnectionError(),
        )

        service = MiniMaxService(api_key="test_key")
        result = service.test_connection()

        assert result is False
