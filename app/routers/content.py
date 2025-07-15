"""
Content generation router using Gemini AI
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Literal

from services import GeminiService
from models import GeminiConfig, ContentItem

router = APIRouter()

class ContentRequest(BaseModel):
    content_items: List[Dict]  # From emails or RSS
    tone: Literal["neutral", "friendly", "professional", "energetic", "casual"] = "neutral"
    language: Literal["en-US", "zh-CN", "ja-JP", "ko-KR", "es-ES", "fr-FR", "de-DE"] = "en-US"
    max_words: Optional[int] = 500
    style: Literal["summary", "detailed", "headlines"] = "summary"

class ContentResponse(BaseModel):
    generated_content: str
    word_count: int
    source_count: int
    success: bool


@router.post("/generate")
async def generate_content(request: ContentRequest) -> ContentResponse:
    """Generate AI-powered content from emails and RSS feeds."""
    try:
        gemini_service = GeminiService()
        
        if not gemini_service.api_key:
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
            )
        
        # Configure Gemini service
        if not gemini_service.configure():
            raise HTTPException(status_code=500, detail="Failed to configure Gemini AI service")
        
        # Prepare content for processing
        source_texts = []
        for item in request.content_items:
            title = item.get("title", "")
            content = item.get("content", item.get("description", ""))
            source = item.get("source", "Unknown")
            
            # Combine title and content
            item_text = f"Source: {source}\nTitle: {title}\nContent: {content}"
            source_texts.append(item_text)
        
        combined_content = "\n\n".join(source_texts)
        
        # Create appropriate prompt based on style and preferences
        style_prompts = {
            "summary": "Create a concise summary of the following content items",
            "detailed": "Create a detailed analysis and overview of the following content items",
            "headlines": "Create engaging headlines and brief summaries for the following content items"
        }
        
        tone_instruction = {
            "neutral": "in a neutral, informative tone",
            "friendly": "in a friendly, conversational tone",
            "professional": "in a professional, business tone",
            "energetic": "in an energetic, enthusiastic tone",
            "casual": "in a casual, relaxed tone"
        }
        
        language_instruction = {
            "en-US": "in English",
            "zh-CN": "in Chinese (Simplified)",
            "ja-JP": "in Japanese",
            "ko-KR": "in Korean",
            "es-ES": "in Spanish",
            "fr-FR": "in French",
            "de-DE": "in German"
        }
        
        system_prompt = f"""You are an AI content creator for InboxCast, a service that converts emails and RSS feeds into podcast-style content. 
{style_prompts[request.style]} {tone_instruction[request.tone]} {language_instruction[request.language]}.
Keep the content under {request.max_words} words and make it suitable for audio narration."""
        
        user_prompt = f"""Please process the following content items and create engaging audio-ready content:

{combined_content}

Requirements:
- Style: {request.style}
- Tone: {request.tone}
- Language: {request.language}
- Maximum words: {request.max_words}
- Make it suitable for audio narration (clear, engaging, well-structured)"""
        
        # Create Gemini configuration
        config = GeminiConfig(
            model_name="gemini-1.5-flash",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_output_tokens=min(1000, request.max_words + 100)
        )
        
        # Generate content
        response = gemini_service.generate_content(config)
        
        if not response or not response.text:
            raise HTTPException(status_code=500, detail="Failed to generate content with Gemini AI")
        
        # Count words in generated content
        word_count = len(response.text.split())
        
        return ContentResponse(
            generated_content=response.text,
            word_count=word_count,
            source_count=len(request.content_items),
            success=True
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")


@router.post("/test")
async def test_content_generation():
    """Test content generation with sample data."""
    try:
        # Create sample content items
        sample_items = [
            {
                "title": "AI Technology Breakthrough",
                "content": "Researchers have made significant advances in artificial intelligence, improving natural language processing capabilities.",
                "source": "Tech News"
            },
            {
                "title": "Climate Change Update",
                "content": "New studies show the importance of renewable energy adoption for environmental sustainability.",
                "source": "Environmental Report"
            }
        ]
        
        # Create test request
        test_request = ContentRequest(
            content_items=sample_items,
            tone="friendly",
            language="en-US",
            max_words=200,
            style="summary"
        )
        
        # Generate content
        return await generate_content(test_request)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in content generation test: {str(e)}")