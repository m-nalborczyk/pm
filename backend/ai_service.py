"""
AI Service for OpenRouter integration.

This module handles communication with OpenRouter API using the OpenAI-compatible interface.
"""
import os
import logging
from typing import Optional
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-4o-mini-2024-07-18"  # Using a reliable free model

# Initialize OpenAI client configured for OpenRouter
client = None
if OPENROUTER_API_KEY:
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )
else:
    logger.warning("OPENROUTER_API_KEY not found in environment variables")


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


def get_ai_response(prompt: str, timeout: int = 30) -> str:
    """
    Send a prompt to OpenRouter and get a response.
    
    Args:
        prompt: The prompt to send to the AI
        timeout: Request timeout in seconds (default: 30)
        
    Returns:
        The AI's response as a string
        
    Raises:
        AIServiceError: If the API call fails or times out
    """
    if not client:
        raise AIServiceError("OpenRouter client not initialized. Check OPENROUTER_API_KEY.")
    
    try:
        logger.info(f"Sending prompt to OpenRouter (model: {MODEL})")
        logger.debug(f"Prompt: {prompt[:100]}...")  # Log first 100 chars
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            timeout=timeout
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"Received response from OpenRouter ({len(ai_response)} chars)")
        logger.debug(f"Response: {ai_response[:100]}...")
        
        return ai_response
        
    except Exception as e:
        error_msg = f"OpenRouter API error: {str(e)}"
        logger.error(error_msg)
        raise AIServiceError(error_msg) from e


def test_ai_connection() -> dict:
    """
    Test the AI connection with a simple math question.
    
    Returns:
        Dictionary with status and response
    """
    try:
        response = get_ai_response("What is 2+2? Please answer with just the number.")
        return {
            "status": "success",
            "response": response,
            "model": MODEL
        }
    except AIServiceError as e:
        return {
            "status": "error",
            "error": str(e),
            "model": MODEL
        }

# Made with Bob
