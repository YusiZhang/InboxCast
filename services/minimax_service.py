"""
MiniMax AI service for text-to-speech voice-over generation.
"""

import os

import requests

from models import VoiceOverRequest, VoiceOverResponse


class MiniMaxService:
    """Service class for MiniMax AI text-to-speech integration."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        """
        Initialize MiniMax service.

        Args:
            api_key: MiniMax API key. If not provided, will try to read from environment
            base_url: Base URL for MiniMax API. Defaults to official API endpoint
        """
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.base_url = base_url or "https://api.minimax.chat/v1/text_to_speech"
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update(
                {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            )

    def generate_voice_over(self, request: VoiceOverRequest) -> VoiceOverResponse:
        """
        Generate voice-over audio from text using MiniMax AI.

        Args:
            request: VoiceOverRequest containing text and voice parameters

        Returns:
            VoiceOverResponse with audio data or error information
        """
        if not self.api_key:
            return VoiceOverResponse(
                success=False,
                error_message="MiniMax API key not provided. Set MINIMAX_API_KEY environment variable.",
            )

        try:
            # Prepare request payload for MiniMax API
            payload = {
                "text": request.text,
                "voice_setting": {
                    "tone": request.tone,
                    "speed": request.speed,
                    "language": request.language,
                },
            }

            # Add voice_id if specified
            if request.voice_id:
                voice_setting = payload["voice_setting"]
                if isinstance(voice_setting, dict):
                    voice_setting["voice_id"] = request.voice_id

            # Make API request
            response = self.session.post(self.base_url, json=payload, timeout=30)

            if response.status_code == 200:
                response_data = response.json()

                # Handle different response formats
                if "audio_url" in response_data:
                    # URL-based response
                    return VoiceOverResponse(
                        success=True,
                        audio_url=response_data["audio_url"],
                        duration=response_data.get("duration"),
                        format=response_data.get("format", "mp3"),
                    )
                elif "audio_data" in response_data:
                    # Direct audio data response
                    import base64

                    audio_bytes = base64.b64decode(response_data["audio_data"])
                    return VoiceOverResponse(
                        success=True,
                        audio_data=audio_bytes,
                        duration=response_data.get("duration"),
                        format=response_data.get("format", "mp3"),
                    )
                else:
                    return VoiceOverResponse(
                        success=False, error_message="Invalid response format from MiniMax API"
                    )
            else:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        error_msg = error_data["message"]
                except Exception:
                    pass

                return VoiceOverResponse(success=False, error_message=error_msg)

        except requests.exceptions.Timeout:
            return VoiceOverResponse(
                success=False,
                error_message="Request timeout. MiniMax API did not respond within 30 seconds.",
            )
        except requests.exceptions.ConnectionError:
            return VoiceOverResponse(
                success=False, error_message="Connection error. Could not reach MiniMax API."
            )
        except Exception as e:
            return VoiceOverResponse(success=False, error_message=f"Unexpected error: {str(e)}")

    def save_audio_to_file(self, response: VoiceOverResponse, file_path: str) -> bool:
        """
        Save audio data from VoiceOverResponse to a file.

        Args:
            response: VoiceOverResponse containing audio data
            file_path: Path where to save the audio file

        Returns:
            bool: True if file was saved successfully, False otherwise
        """
        if not response.success:
            return False

        try:
            if response.audio_data:
                # Save direct audio data
                with open(file_path, "wb") as f:
                    f.write(response.audio_data)
                return True
            elif response.audio_url:
                # Download audio from URL
                audio_response = self.session.get(response.audio_url, timeout=30)
                if audio_response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(audio_response.content)
                    return True

            return False

        except Exception:
            return False

    def test_connection(self) -> bool:
        """
        Test connection to MiniMax API.

        Returns:
            bool: True if API is accessible, False otherwise
        """
        if not self.api_key:
            return False

        try:
            # Use a minimal test request
            test_request = VoiceOverRequest(
                text="Test", tone="neutral", speed=1.0, language="en-US"
            )

            response = self.generate_voice_over(test_request)
            return response.success

        except Exception:
            return False
