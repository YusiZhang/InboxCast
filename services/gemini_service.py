"""
Google Gemini API service for AI text generation.
"""

import os

import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

from models import ContentItem, GeminiConfig, GeminiResponse


class GeminiService:
    """Service class for Google Gemini API integration."""

    def __init__(self, api_key: str | None = None):
        """
        Initialize Gemini service.

        Args:
            api_key: Google AI Studio API key. If not provided, will try to get from
                    GEMINI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self._is_configured = False

    def configure(self) -> bool:
        """
        Configure the Gemini API client with the API key.

        Returns:
            bool: True if configuration successful, False otherwise
        """
        try:
            if not self.api_key:
                print("Error: No Gemini API key provided!")
                print("Please set GEMINI_API_KEY environment variable or pass api_key parameter.")
                print("Get your API key from: https://makersuite.google.com/app/apikey")
                return False

            # Configure the API client
            genai.configure(api_key=self.api_key)
            self._is_configured = True
            return True

        except Exception as e:
            print(f"Error configuring Gemini API: {str(e)}")
            return False

    def generate_content(self, config: GeminiConfig) -> GeminiResponse | None:
        """
        Generate content using Google Gemini API.

        Args:
            config: GeminiConfig object with model parameters and prompts

        Returns:
            GeminiResponse object with generated content, or None if error
        """
        if not self._is_configured:
            if not self.configure():
                return None

        try:
            # Initialize the model
            model = genai.GenerativeModel(
                model_name=config.model_name,
                system_instruction=config.system_prompt
            )

            # Configure generation parameters
            generation_config = genai.GenerationConfig(
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
                top_p=config.top_p,
                top_k=config.top_k,
            )

            # Generate content
            response: GenerateContentResponse = model.generate_content(
                config.user_prompt,
                generation_config=generation_config
            )

            # Extract response data
            if response.text:
                return GeminiResponse(
                    text=response.text,
                    model_used=config.model_name,
                    prompt_tokens=response.usage_metadata.prompt_token_count if response.usage_metadata else None,
                    response_tokens=response.usage_metadata.candidates_token_count if response.usage_metadata else None,
                    finish_reason=response.candidates[0].finish_reason.name if response.candidates else None,
                    metadata={
                        "safety_ratings": [
                            {
                                "category": rating.category.name,
                                "probability": rating.probability.name
                            }
                            for rating in response.candidates[0].safety_ratings
                        ] if response.candidates and response.candidates[0].safety_ratings else []
                    }
                )
            else:
                print("No text generated. Response may have been blocked by safety filters.")
                return None

        except Exception as e:
            print(f"Error generating content with Gemini: {str(e)}")
            return None

    def summarize_content(self, content: str, max_words: int = 100) -> str | None:
        """
        Summarize content using Gemini.

        Args:
            content: Text content to summarize
            max_words: Maximum words in summary

        Returns:
            Summary text or None if error
        """
        config = GeminiConfig(
            system_prompt=f"You are a helpful assistant that creates concise summaries. Summarize the following content in {max_words} words or less.",
            user_prompt=f"Please summarize this content:\n\n{content}"
        )

        response = self.generate_content(config)
        return response.text if response else None

    def enhance_content_item(self, item: ContentItem, enhancement_type: str = "summary") -> ContentItem:
        """
        Enhance a ContentItem with AI-generated content.

        Args:
            item: ContentItem to enhance
            enhancement_type: Type of enhancement ("summary", "tags", "analysis")

        Returns:
            Enhanced ContentItem with additional metadata
        """
        if not item.content:
            return item

        # Create enhanced copy
        enhanced_item = ContentItem(
            title=item.title,
            source=item.source,
            author=item.author,
            content=item.content,
            metadata=item.metadata.copy() if item.metadata else {}
        )

        try:
            if enhancement_type == "summary":
                summary = self.summarize_content(item.content)
                if summary:
                    if enhanced_item.metadata is None:
                        enhanced_item.metadata = {}
                    enhanced_item.metadata["ai_summary"] = summary

            elif enhancement_type == "tags":
                config = GeminiConfig(
                    system_prompt="You are a content tagger. Generate 3-5 relevant tags for content. Return only the tags separated by commas.",
                    user_prompt=f"Generate tags for this content:\n\nTitle: {item.title}\nContent: {item.content[:500]}..."
                )
                response = self.generate_content(config)
                if response:
                    if enhanced_item.metadata is None:
                        enhanced_item.metadata = {}
                    enhanced_item.metadata["ai_tags"] = [tag.strip() for tag in response.text.split(",")]

            elif enhancement_type == "analysis":
                config = GeminiConfig(
                    system_prompt="You are a content analyst. Provide a brief analysis of the content including tone, key themes, and target audience.",
                    user_prompt=f"Analyze this content:\n\nTitle: {item.title}\nContent: {item.content[:1000]}..."
                )
                response = self.generate_content(config)
                if response:
                    if enhanced_item.metadata is None:
                        enhanced_item.metadata = {}
                    enhanced_item.metadata["ai_analysis"] = response.text

        except Exception as e:
            print(f"Error enhancing content item: {str(e)}")

        return enhanced_item

    def print_generation_test(self, test_prompt: str = "Hello! Tell me a fun fact about artificial intelligence.") -> None:
        """
        Test Gemini API integration by generating content for a simple prompt.

        Args:
            test_prompt: Prompt to test with
        """
        print("=== Gemini API Generation Test ===")

        if not self._is_configured:
            if not self.configure():
                print("❌ Configuration failed")
                return

        print("✅ Gemini API configured successfully")

        # Test content generation
        config = GeminiConfig(
            system_prompt="You are a helpful and friendly AI assistant.",
            user_prompt=test_prompt,
            temperature=0.7,
            max_output_tokens=200
        )

        print(f"\nGenerating response for: '{test_prompt}'")
        response = self.generate_content(config)

        if response:
            print("\n✅ Content generation successful!")
            print(f"Model: {response.model_used}")
            print(f"Response: {response.text}")
            if response.prompt_tokens and response.response_tokens:
                print(f"Tokens - Input: {response.prompt_tokens}, Output: {response.response_tokens}")
            print(f"Finish reason: {response.finish_reason}")
        else:
            print("❌ Content generation failed")
