"""
Audio generation router using MiniMax AI
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Literal, Optional
import os
import tempfile
import uuid

from services import MiniMaxService
from models import VoiceOverRequest

router = APIRouter()

class AudioRequest(BaseModel):
    text: str
    tone: Literal["neutral", "friendly", "professional", "energetic", "calm"] = "friendly"
    speed: float = 1.0
    language: Literal["en-US", "zh-CN", "ja-JP", "ko-KR", "es-ES", "fr-FR", "de-DE"] = "en-US"
    voice_id: Optional[str] = None

class AudioResponse(BaseModel):
    success: bool
    audio_file_path: Optional[str] = None
    duration: Optional[float] = None
    format: Optional[str] = None
    error_message: Optional[str] = None


@router.post("/generate")
async def generate_audio(request: AudioRequest) -> AudioResponse:
    """Generate audio from text using MiniMax AI."""
    try:
        minimax_service = MiniMaxService()
        
        if not minimax_service.api_key:
            raise HTTPException(
                status_code=500,
                detail="MiniMax API key not configured. Please set MINIMAX_API_KEY environment variable."
            )
        
        # Test connection first
        if not minimax_service.test_connection():
            raise HTTPException(status_code=500, detail="Cannot connect to MiniMax AI service")
        
        # Create voice-over request
        voiceover_request = VoiceOverRequest(
            text=request.text,
            tone=request.tone,
            speed=request.speed,
            language=request.language,
            voice_id=request.voice_id
        )
        
        # Generate voice-over
        response = minimax_service.generate_voice_over(voiceover_request)
        
        if not response.success:
            return AudioResponse(
                success=False,
                error_message=response.error_message or "Unknown error occurred"
            )
        
        # Save audio file to temporary location
        audio_filename = f"audio_{uuid.uuid4().hex}.mp3"
        audio_path = os.path.join("/tmp", audio_filename)
        
        if minimax_service.save_audio_to_file(response, audio_path):
            return AudioResponse(
                success=True,
                audio_file_path=audio_path,
                duration=response.duration,
                format=response.format or "mp3"
            )
        else:
            return AudioResponse(
                success=False,
                error_message="Failed to save audio file"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")


@router.get("/download/{file_path:path}")
async def download_audio(file_path: str):
    """Download generated audio file."""
    try:
        # Security check - only allow files from /tmp directory
        if not file_path.startswith("/tmp/audio_"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            path=file_path,
            media_type="audio/mpeg",
            filename=os.path.basename(file_path)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading audio: {str(e)}")


@router.post("/test")
async def test_audio_generation():
    """Test audio generation with sample text."""
    try:
        sample_text = """
        Welcome to InboxCast! This is a demonstration of our AI-powered text-to-speech functionality. 
        InboxCast converts your daily emails and RSS feeds into podcast-style audio content, 
        making it easy to stay informed while on the go.
        """
        
        test_request = AudioRequest(
            text=sample_text,
            tone="friendly",
            speed=1.0,
            language="en-US"
        )
        
        return await generate_audio(test_request)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in audio generation test: {str(e)}")


@router.get("/test-connection")
async def test_minimax_connection():
    """Test connection to MiniMax AI service."""
    try:
        minimax_service = MiniMaxService()
        
        if not minimax_service.api_key:
            return {
                "connected": False,
                "error": "MiniMax API key not configured",
                "message": "Please set MINIMAX_API_KEY environment variable"
            }
        
        connected = minimax_service.test_connection()
        
        return {
            "connected": connected,
            "service": "MiniMax AI",
            "api_key_configured": bool(minimax_service.api_key)
        }
    
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "service": "MiniMax AI"
        }