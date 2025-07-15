"""
Pydantic data models for Google Gemini API configuration and responses.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GeminiConfig(BaseModel):
    """
    Configuration model for Google Gemini API integration.

    Used to configure model selection, prompts, and generation parameters.
    """

    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True,  # Validate on assignment
    )

    model_name: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model name (e.g., gemini-1.5-pro, gemini-1.5-flash)"
    )
    system_prompt: str | None = Field(
        default=None,
        description="System prompt to set context and behavior for the model"
    )
    user_prompt: str = Field(
        description="User prompt/question to send to the model"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Controls randomness in response generation (0.0 to 2.0)"
    )
    max_output_tokens: int = Field(
        default=8192,
        gt=0,
        description="Maximum number of tokens to generate in response"
    )
    top_p: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Controls diversity via nucleus sampling (0.0 to 1.0)"
    )
    top_k: int = Field(
        default=40,
        gt=0,
        description="Controls diversity by limiting vocabulary considered"
    )


class GeminiResponse(BaseModel):
    """
    Response model for Google Gemini API responses.

    Standardizes the response format from Gemini API calls.
    """

    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True,  # Validate on assignment
    )

    text: str = Field(description="Generated text response from Gemini")
    model_used: str = Field(description="Name of the Gemini model that generated the response")
    prompt_tokens: int | None = Field(
        default=None,
        description="Number of tokens in the input prompt"
    )
    response_tokens: int | None = Field(
        default=None,
        description="Number of tokens in the generated response"
    )
    finish_reason: str | None = Field(
        default=None,
        description="Reason why generation finished (e.g., 'STOP', 'MAX_TOKENS')"
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Additional metadata from the API response"
    )
