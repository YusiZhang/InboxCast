"""
Tests for Gemini data models.
"""

import pytest
from pydantic import ValidationError

from models import GeminiConfig, GeminiResponse


class TestGeminiConfig:
    """Test cases for GeminiConfig model."""

    def test_gemini_config_creation_with_minimal_fields(self):
        """Test creating GeminiConfig with only required fields."""
        config = GeminiConfig(user_prompt="Hello, world!")

        assert config.user_prompt == "Hello, world!"
        assert config.model_name == "gemini-1.5-flash"  # default
        assert config.system_prompt is None  # default
        assert config.temperature == 0.7  # default
        assert config.max_output_tokens == 8192  # default
        assert config.top_p == 0.95  # default
        assert config.top_k == 40  # default

    def test_gemini_config_creation_with_all_fields(self):
        """Test creating GeminiConfig with all fields specified."""
        config = GeminiConfig(
            model_name="gemini-1.5-pro",
            system_prompt="You are a helpful assistant.",
            user_prompt="What is AI?",
            temperature=0.5,
            max_output_tokens=1000,
            top_p=0.8,
            top_k=20
        )

        assert config.model_name == "gemini-1.5-pro"
        assert config.system_prompt == "You are a helpful assistant."
        assert config.user_prompt == "What is AI?"
        assert config.temperature == 0.5
        assert config.max_output_tokens == 1000
        assert config.top_p == 0.8
        assert config.top_k == 20

    def test_gemini_config_missing_required_field(self):
        """Test GeminiConfig validation fails without required user_prompt."""
        with pytest.raises(ValidationError) as exc_info:
            GeminiConfig()

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing"
        assert "user_prompt" in error["loc"]

    def test_gemini_config_temperature_validation(self):
        """Test temperature field validation (must be 0.0 to 2.0)."""
        # Valid temperature
        config = GeminiConfig(user_prompt="test", temperature=1.0)
        assert config.temperature == 1.0

        # Invalid temperature - too low
        with pytest.raises(ValidationError) as exc_info:
            GeminiConfig(user_prompt="test", temperature=-0.1)
        assert "greater_than_equal" in str(exc_info.value)

        # Invalid temperature - too high
        with pytest.raises(ValidationError) as exc_info:
            GeminiConfig(user_prompt="test", temperature=2.1)
        assert "less_than_equal" in str(exc_info.value)

    def test_gemini_config_top_p_validation(self):
        """Test top_p field validation (must be 0.0 to 1.0)."""
        # Valid top_p
        config = GeminiConfig(user_prompt="test", top_p=0.5)
        assert config.top_p == 0.5

        # Invalid top_p - too low
        with pytest.raises(ValidationError) as exc_info:
            GeminiConfig(user_prompt="test", top_p=-0.1)
        assert "greater_than_equal" in str(exc_info.value)

        # Invalid top_p - too high
        with pytest.raises(ValidationError) as exc_info:
            GeminiConfig(user_prompt="test", top_p=1.1)
        assert "less_than_equal" in str(exc_info.value)

    def test_gemini_config_max_output_tokens_validation(self):
        """Test max_output_tokens field validation (must be > 0)."""
        # Valid max_output_tokens
        config = GeminiConfig(user_prompt="test", max_output_tokens=100)
        assert config.max_output_tokens == 100

        # Invalid max_output_tokens
        with pytest.raises(ValidationError) as exc_info:
            GeminiConfig(user_prompt="test", max_output_tokens=0)
        assert "greater_than" in str(exc_info.value)

    def test_gemini_config_top_k_validation(self):
        """Test top_k field validation (must be > 0)."""
        # Valid top_k
        config = GeminiConfig(user_prompt="test", top_k=10)
        assert config.top_k == 10

        # Invalid top_k
        with pytest.raises(ValidationError) as exc_info:
            GeminiConfig(user_prompt="test", top_k=0)
        assert "greater_than" in str(exc_info.value)

    def test_gemini_config_extra_fields_forbidden(self):
        """Test that extra fields are not allowed."""
        with pytest.raises(ValidationError) as exc_info:
            GeminiConfig(user_prompt="test", extra_field="not allowed")

        error = exc_info.value.errors()[0]
        assert error["type"] == "extra_forbidden"

    def test_gemini_config_dict_conversion(self):
        """Test converting GeminiConfig to dictionary."""
        config = GeminiConfig(
            user_prompt="test",
            system_prompt="system",
            temperature=0.8
        )

        config_dict = config.model_dump()
        assert config_dict["user_prompt"] == "test"
        assert config_dict["system_prompt"] == "system"
        assert config_dict["temperature"] == 0.8

    def test_gemini_config_from_dict(self):
        """Test creating GeminiConfig from dictionary."""
        config_dict = {
            "user_prompt": "Hello",
            "model_name": "gemini-1.5-pro",
            "temperature": 0.3
        }

        config = GeminiConfig(**config_dict)
        assert config.user_prompt == "Hello"
        assert config.model_name == "gemini-1.5-pro"
        assert config.temperature == 0.3


class TestGeminiResponse:
    """Test cases for GeminiResponse model."""

    def test_gemini_response_creation_with_minimal_fields(self):
        """Test creating GeminiResponse with only required fields."""
        response = GeminiResponse(
            text="Hello, how can I help you?",
            model_used="gemini-1.5-flash"
        )

        assert response.text == "Hello, how can I help you?"
        assert response.model_used == "gemini-1.5-flash"
        assert response.prompt_tokens is None
        assert response.response_tokens is None
        assert response.finish_reason is None
        assert response.metadata is None

    def test_gemini_response_creation_with_all_fields(self):
        """Test creating GeminiResponse with all fields specified."""
        metadata = {"safety_ratings": [{"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"}]}

        response = GeminiResponse(
            text="Generated response",
            model_used="gemini-1.5-pro",
            prompt_tokens=10,
            response_tokens=20,
            finish_reason="STOP",
            metadata=metadata
        )

        assert response.text == "Generated response"
        assert response.model_used == "gemini-1.5-pro"
        assert response.prompt_tokens == 10
        assert response.response_tokens == 20
        assert response.finish_reason == "STOP"
        assert response.metadata == metadata

    def test_gemini_response_missing_required_fields(self):
        """Test GeminiResponse validation fails without required fields."""
        # Missing text
        with pytest.raises(ValidationError) as exc_info:
            GeminiResponse(model_used="gemini-1.5-flash")

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing"
        assert "text" in error["loc"]

        # Missing model_used
        with pytest.raises(ValidationError) as exc_info:
            GeminiResponse(text="Hello")

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing"
        assert "model_used" in error["loc"]

    def test_gemini_response_extra_fields_forbidden(self):
        """Test that extra fields are not allowed."""
        with pytest.raises(ValidationError) as exc_info:
            GeminiResponse(
                text="Hello",
                model_used="gemini-1.5-flash",
                extra_field="not allowed"
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "extra_forbidden"

    def test_gemini_response_dict_conversion(self):
        """Test converting GeminiResponse to dictionary."""
        response = GeminiResponse(
            text="Hello",
            model_used="gemini-1.5-flash",
            prompt_tokens=5
        )

        response_dict = response.model_dump()
        assert response_dict["text"] == "Hello"
        assert response_dict["model_used"] == "gemini-1.5-flash"
        assert response_dict["prompt_tokens"] == 5

    def test_gemini_response_exclude_none_values(self):
        """Test excluding None values from response dictionary."""
        response = GeminiResponse(
            text="Hello",
            model_used="gemini-1.5-flash"
        )

        response_dict = response.model_dump(exclude_none=True)
        assert "prompt_tokens" not in response_dict
        assert "response_tokens" not in response_dict
        assert "finish_reason" not in response_dict
        assert "metadata" not in response_dict

    def test_gemini_response_validation_assignment(self):
        """Test validation on field assignment."""
        response = GeminiResponse(
            text="Hello",
            model_used="gemini-1.5-flash"
        )

        # Valid assignment
        response.text = "Updated text"
        assert response.text == "Updated text"

        # Invalid assignment (though Pydantic would handle this)
        # This test ensures validation is configured properly
        assert response.model_config["validate_assignment"] is True
