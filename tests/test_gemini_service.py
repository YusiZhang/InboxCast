"""
Tests for Gemini service.
"""

import os
from unittest.mock import Mock, patch

from models import ContentItem, GeminiConfig, GeminiResponse
from services import GeminiService


class TestGeminiService:
    """Test cases for GeminiService."""

    def test_gemini_service_initialization_no_api_key(self):
        """Test GeminiService initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            service = GeminiService()
            assert service.api_key is None
            assert service.client is None
            assert service._is_configured is False

    def test_gemini_service_initialization_with_api_key(self):
        """Test GeminiService initialization with API key parameter."""
        service = GeminiService(api_key="test-api-key")
        assert service.api_key == "test-api-key"
        assert service.client is None
        assert service._is_configured is False

    def test_gemini_service_initialization_with_env_api_key(self):
        """Test GeminiService initialization with environment variable API key."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env-api-key"}):
            service = GeminiService()
            assert service.api_key == "env-api-key"
            assert service.client is None
            assert service._is_configured is False

    def test_configure_no_api_key(self):
        """Test configure method fails without API key."""
        service = GeminiService()
        result = service.configure()
        assert result is False
        assert service._is_configured is False

    @patch("services.gemini_service.genai.configure")
    def test_configure_success(self, mock_configure):
        """Test successful configuration."""
        service = GeminiService(api_key="test-api-key")
        result = service.configure()

        assert result is True
        assert service._is_configured is True
        mock_configure.assert_called_once_with(api_key="test-api-key")

    @patch("services.gemini_service.genai.configure")
    def test_configure_exception(self, mock_configure):
        """Test configure method handles exceptions."""
        mock_configure.side_effect = Exception("Configuration error")

        service = GeminiService(api_key="test-api-key")
        result = service.configure()

        assert result is False
        assert service._is_configured is False

    @patch("services.gemini_service.genai.GenerativeModel")
    @patch("services.gemini_service.genai.configure")
    def test_generate_content_success(self, mock_configure, mock_model_class):
        """Test successful content generation."""
        # Setup mock response
        mock_usage = Mock()
        mock_usage.prompt_token_count = 10
        mock_usage.candidates_token_count = 20

        mock_candidate = Mock()
        mock_candidate.finish_reason.name = "STOP"
        mock_candidate.safety_ratings = []

        mock_response = Mock()
        mock_response.text = "Generated response text"
        mock_response.usage_metadata = mock_usage
        mock_response.candidates = [mock_candidate]

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        # Test
        service = GeminiService(api_key="test-api-key")
        config = GeminiConfig(user_prompt="Test prompt")

        result = service.generate_content(config)

        assert isinstance(result, GeminiResponse)
        assert result.text == "Generated response text"
        assert result.model_used == "gemini-1.5-flash"
        assert result.prompt_tokens == 10
        assert result.response_tokens == 20
        assert result.finish_reason == "STOP"

    @patch("services.gemini_service.genai.configure")
    def test_generate_content_not_configured(self, mock_configure):
        """Test generate_content when service is not configured."""
        mock_configure.side_effect = Exception("Config error")

        service = GeminiService(api_key="test-api-key")
        config = GeminiConfig(user_prompt="Test prompt")

        result = service.generate_content(config)

        assert result is None

    @patch("services.gemini_service.genai.GenerativeModel")
    @patch("services.gemini_service.genai.configure")
    def test_generate_content_no_text_response(self, mock_configure, mock_model_class):
        """Test generate_content when API returns no text."""
        mock_response = Mock()
        mock_response.text = None

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        service = GeminiService(api_key="test-api-key")
        config = GeminiConfig(user_prompt="Test prompt")

        result = service.generate_content(config)

        assert result is None

    @patch("services.gemini_service.genai.GenerativeModel")
    @patch("services.gemini_service.genai.configure")
    def test_generate_content_api_exception(self, mock_configure, mock_model_class):
        """Test generate_content handles API exceptions."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API error")
        mock_model_class.return_value = mock_model

        service = GeminiService(api_key="test-api-key")
        config = GeminiConfig(user_prompt="Test prompt")

        result = service.generate_content(config)

        assert result is None

    def test_summarize_content_success(self):
        """Test successful content summarization."""
        service = GeminiService(api_key="test-api-key")

        # Mock the generate_content method
        mock_response = GeminiResponse(
            text="This is a summary.",
            model_used="gemini-1.5-flash"
        )
        service.generate_content = Mock(return_value=mock_response)

        result = service.summarize_content("Long content to summarize", max_words=50)

        assert result == "This is a summary."
        service.generate_content.assert_called_once()

        # Check the config passed to generate_content
        call_args = service.generate_content.call_args[0][0]
        assert isinstance(call_args, GeminiConfig)
        assert "50 words" in call_args.system_prompt
        assert "Long content to summarize" in call_args.user_prompt

    def test_summarize_content_no_response(self):
        """Test summarize_content when generate_content returns None."""
        service = GeminiService(api_key="test-api-key")
        service.generate_content = Mock(return_value=None)

        result = service.summarize_content("Content to summarize")

        assert result is None

    def test_enhance_content_item_no_content(self):
        """Test enhance_content_item with ContentItem that has no content."""
        service = GeminiService(api_key="test-api-key")

        item = ContentItem(title="Test", source="test")
        result = service.enhance_content_item(item)

        assert result.title == "Test"
        assert result.source == "test"
        assert result.content is None

    def test_enhance_content_item_summary(self):
        """Test enhance_content_item with summary enhancement."""
        service = GeminiService(api_key="test-api-key")
        service.summarize_content = Mock(return_value="Summary text")

        item = ContentItem(
            title="Test Article",
            source="test",
            content="Long article content here..."
        )

        result = service.enhance_content_item(item, enhancement_type="summary")

        assert result.title == "Test Article"
        assert result.metadata["ai_summary"] == "Summary text"
        service.summarize_content.assert_called_once_with("Long article content here...")

    def test_enhance_content_item_tags(self):
        """Test enhance_content_item with tags enhancement."""
        service = GeminiService(api_key="test-api-key")

        mock_response = GeminiResponse(
            text="technology, AI, machine learning",
            model_used="gemini-1.5-flash"
        )
        service.generate_content = Mock(return_value=mock_response)

        item = ContentItem(
            title="AI Article",
            content="Content about artificial intelligence"
        )

        result = service.enhance_content_item(item, enhancement_type="tags")

        assert result.metadata["ai_tags"] == ["technology", "AI", "machine learning"]

    def test_enhance_content_item_analysis(self):
        """Test enhance_content_item with analysis enhancement."""
        service = GeminiService(api_key="test-api-key")

        mock_response = GeminiResponse(
            text="This content has a professional tone and targets developers.",
            model_used="gemini-1.5-flash"
        )
        service.generate_content = Mock(return_value=mock_response)

        item = ContentItem(
            title="Developer Guide",
            content="Technical content for developers"
        )

        result = service.enhance_content_item(item, enhancement_type="analysis")

        assert result.metadata["ai_analysis"] == "This content has a professional tone and targets developers."

    def test_enhance_content_item_exception_handling(self):
        """Test enhance_content_item handles exceptions gracefully."""
        service = GeminiService(api_key="test-api-key")
        service.generate_content = Mock(side_effect=Exception("API error"))

        item = ContentItem(
            title="Test",
            content="Content"
        )

        # Should not raise exception, just return original item
        result = service.enhance_content_item(item, enhancement_type="summary")

        assert result.title == "Test"
        assert result.content == "Content"
        # Should not have ai_summary in metadata due to exception
        assert "ai_summary" not in (result.metadata or {})

    def test_enhance_content_item_preserves_existing_metadata(self):
        """Test enhance_content_item preserves existing metadata."""
        service = GeminiService(api_key="test-api-key")
        service.summarize_content = Mock(return_value="Summary")

        item = ContentItem(
            title="Test",
            content="Content",
            metadata={"existing_key": "existing_value"}
        )

        result = service.enhance_content_item(item, enhancement_type="summary")

        assert result.metadata["existing_key"] == "existing_value"
        assert result.metadata["ai_summary"] == "Summary"

    @patch("services.gemini_service.genai.GenerativeModel")
    @patch("services.gemini_service.genai.configure")
    def test_print_generation_test_success(self, mock_configure, mock_model_class, capsys):
        """Test print_generation_test with successful generation."""
        # Setup mock response
        mock_response = Mock()
        mock_response.text = "AI is fascinating!"
        mock_response.usage_metadata.prompt_token_count = 5
        mock_response.usage_metadata.candidates_token_count = 3
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].finish_reason.name = "STOP"
        mock_response.candidates[0].safety_ratings = []

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        service = GeminiService(api_key="test-api-key")
        service.print_generation_test()

        captured = capsys.readouterr()
        assert "✅ Gemini API configured successfully" in captured.out
        assert "✅ Content generation successful!" in captured.out
        assert "AI is fascinating!" in captured.out

    def test_print_generation_test_configuration_failed(self, capsys):
        """Test print_generation_test when configuration fails."""
        service = GeminiService()  # No API key
        service.print_generation_test()

        captured = capsys.readouterr()
        assert "❌ Configuration failed" in captured.out

    @patch("services.gemini_service.genai.configure")
    def test_print_generation_test_generation_failed(self, mock_configure, capsys):
        """Test print_generation_test when content generation fails."""
        service = GeminiService(api_key="test-api-key")
        service.generate_content = Mock(return_value=None)

        service.print_generation_test()

        captured = capsys.readouterr()
        assert "❌ Content generation failed" in captured.out
