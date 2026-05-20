"""
AI Service for OpenRouter integration.

This module handles communication with OpenRouter API using the OpenAI-compatible interface.
Supports structured outputs for Kanban board operations.
"""
import os
import json
import logging
from typing import Optional, List, Dict, Any
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


# JSON Schema for AI structured output
AI_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string",
            "description": "Response message to show the user"
        },
        "board_updates": {
            "type": "array",
            "description": "List of board operations to perform",
            "items": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add_card", "edit_card", "move_card", "delete_card", "rename_column", "add_column"],
                        "description": "Type of operation to perform"
                    },
                    "column_id": {
                        "type": "string",
                        "description": "Column ID (for add_card, move_card, rename_column)"
                    },
                    "card_id": {
                        "type": "string",
                        "description": "Card ID (for edit_card, move_card, delete_card)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Card/Column title (for add_card, edit_card, rename_column, add_column)"
                    },
                    "details": {
                        "type": "string",
                        "description": "Card details (for add_card, edit_card)"
                    },
                    "position": {
                        "type": "integer",
                        "description": "Card/Column position (for move_card, add_column)"
                    }
                },
                "required": ["operation"]
            }
        }
    },
    "required": ["message", "board_updates"]
}


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


def build_kanban_prompt(board_data: dict, conversation_history: List[Dict[str, str]], user_message: str) -> str:
    """
    Build a prompt for the AI that includes board state and conversation history.
    
    Args:
        board_data: Current board state with columns and cards
        conversation_history: List of previous messages (role, content)
        user_message: Current user message
        
    Returns:
        Formatted prompt string
    """
    prompt = """You are a helpful AI assistant for a Kanban board project management tool.

Current Board State:
"""
    
    # Add board structure
    for column in board_data.get("columns", []):
        prompt += f"\n{column['title']} (ID: {column['id']}):\n"
        card_ids = column.get("cardIds", [])
        if not card_ids:
            prompt += "  (empty)\n"
        else:
            for card_id in card_ids:
                card = board_data.get("cards", {}).get(card_id, {})
                prompt += f"  - {card.get('title', 'Untitled')} (ID: {card_id})\n"
                if card.get('details'):
                    prompt += f"    Details: {card['details']}\n"
    
    # Add conversation history
    if conversation_history:
        prompt += "\n\nConversation History:\n"
        for msg in conversation_history[-10:]:  # Last 10 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
    
    # Add current message and instructions
    prompt += f"\n\nUser: {user_message}\n\n"
    prompt += """Please respond with a JSON object containing:
1. "message": Your response to the user
2. "board_updates": An array of operations to perform (can be empty)

Each operation should have:
- "operation": one of "add_card", "edit_card", "move_card", "delete_card", "rename_column", "add_column"
- Additional fields based on operation type

Examples:
- Add card: {"operation": "add_card", "column_id": "col-backlog", "title": "New task", "details": "Description"}
- Edit card: {"operation": "edit_card", "card_id": "card-1", "title": "Updated title", "details": "Updated details"}
- Move card: {"operation": "move_card", "card_id": "card-1", "column_id": "col-progress", "position": 0}
- Delete card: {"operation": "delete_card", "card_id": "card-1"}
- Rename column: {"operation": "rename_column", "column_id": "col-backlog", "title": "New Column Name"}
- Add column: {"operation": "add_column", "title": "New Column", "position": 3}

Note: The board has fixed columns that can be renamed but not added/removed in the MVP. If user asks to add a column, explain this limitation and offer to rename an existing column instead.

Respond ONLY with valid JSON, no additional text."""
    
    return prompt


def get_ai_kanban_response(
    board_data: dict,
    conversation_history: List[Dict[str, str]],
    user_message: str,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Get AI response for Kanban board operations.
    
    Args:
        board_data: Current board state
        conversation_history: Previous conversation messages
        user_message: User's current message
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'message' and 'board_updates' keys
        
    Raises:
        AIServiceError: If the API call fails or response is invalid
    """
    if not client:
        raise AIServiceError("OpenRouter client not initialized. Check OPENROUTER_API_KEY.")
    
    try:
        prompt = build_kanban_prompt(board_data, conversation_history, user_message)
        
        logger.info(f"Sending Kanban prompt to OpenRouter (model: {MODEL})")
        logger.debug(f"Prompt length: {len(prompt)} chars")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for a Kanban board. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            timeout=timeout,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"Received response from OpenRouter ({len(ai_response)} chars)")
        logger.debug(f"Response: {ai_response[:200]}...")
        
        # Parse JSON response
        try:
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in ai_response:
                json_start = ai_response.find("```json") + 7
                json_end = ai_response.find("```", json_start)
                ai_response = ai_response[json_start:json_end].strip()
            elif "```" in ai_response:
                json_start = ai_response.find("```") + 3
                json_end = ai_response.find("```", json_start)
                ai_response = ai_response[json_start:json_end].strip()
            
            parsed_response = json.loads(ai_response)
            
            # Validate response structure
            if "message" not in parsed_response:
                raise ValueError("Response missing 'message' field")
            if "board_updates" not in parsed_response:
                parsed_response["board_updates"] = []
            
            # Validate board_updates is a list
            if not isinstance(parsed_response["board_updates"], list):
                raise ValueError("'board_updates' must be an array")
            
            return parsed_response
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Response was: {ai_response}")
            # Return a safe fallback
            return {
                "message": ai_response,
                "board_updates": []
            }
        except ValueError as e:
            logger.error(f"Invalid response structure: {e}")
            return {
                "message": ai_response if isinstance(ai_response, str) else "Invalid response format",
                "board_updates": []
            }
        
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
