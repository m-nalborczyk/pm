"""
Tests for AI chat integration with Kanban board.
"""
import pytest
from unittest.mock import Mock, patch
from backend.ai_service import build_kanban_prompt, get_ai_kanban_response, AIServiceError


def test_build_kanban_prompt_basic():
    """Test building a basic prompt with board state"""
    board_data = {
        "columns": [
            {"id": "col-1", "title": "Backlog", "cardIds": ["card-1"]},
            {"id": "col-2", "title": "In Progress", "cardIds": []}
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Test Card", "details": "Test details"}
        }
    }
    conversation_history = []
    user_message = "What cards are in Backlog?"
    
    prompt = build_kanban_prompt(board_data, conversation_history, user_message)
    
    assert "Backlog" in prompt
    assert "Test Card" in prompt
    assert "What cards are in Backlog?" in prompt
    assert "JSON" in prompt


def test_build_kanban_prompt_with_history():
    """Test building prompt with conversation history"""
    board_data = {
        "columns": [{"id": "col-1", "title": "Backlog", "cardIds": []}],
        "cards": {}
    }
    conversation_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    user_message = "Add a card"
    
    prompt = build_kanban_prompt(board_data, conversation_history, user_message)
    
    assert "Hello" in prompt
    assert "Hi there!" in prompt
    assert "Add a card" in prompt


def test_build_kanban_prompt_empty_column():
    """Test prompt with empty columns"""
    board_data = {
        "columns": [{"id": "col-1", "title": "Empty Column", "cardIds": []}],
        "cards": {}
    }
    conversation_history = []
    user_message = "Test"
    
    prompt = build_kanban_prompt(board_data, conversation_history, user_message)
    
    assert "Empty Column" in prompt
    assert "(empty)" in prompt


@patch('backend.ai_service.client')
def test_get_ai_kanban_response_success(mock_client):
    """Test successful AI response"""
    # Mock the OpenAI client response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"message": "I added a card", "board_updates": [{"operation": "add_card", "column_id": "col-1", "title": "New Card"}]}'
    mock_client.chat.completions.create.return_value = mock_response
    
    board_data = {
        "columns": [{"id": "col-1", "title": "Backlog", "cardIds": []}],
        "cards": {}
    }
    
    result = get_ai_kanban_response(board_data, [], "Add a card to Backlog")
    
    assert result["message"] == "I added a card"
    assert len(result["board_updates"]) == 1
    assert result["board_updates"][0]["operation"] == "add_card"


@patch('backend.ai_service.client')
def test_get_ai_kanban_response_with_markdown(mock_client):
    """Test AI response wrapped in markdown code blocks"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '```json\n{"message": "Done", "board_updates": []}\n```'
    mock_client.chat.completions.create.return_value = mock_response
    
    board_data = {"columns": [], "cards": {}}
    
    result = get_ai_kanban_response(board_data, [], "Test")
    
    assert result["message"] == "Done"
    assert result["board_updates"] == []


@patch('backend.ai_service.client')
def test_get_ai_kanban_response_invalid_json(mock_client):
    """Test handling of invalid JSON response"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = 'This is not JSON'
    mock_client.chat.completions.create.return_value = mock_response
    
    board_data = {"columns": [], "cards": {}}
    
    result = get_ai_kanban_response(board_data, [], "Test")
    
    # Should return the raw message with empty updates
    assert result["message"] == "This is not JSON"
    assert result["board_updates"] == []


@patch('backend.ai_service.client')
def test_get_ai_kanban_response_missing_message(mock_client):
    """Test handling of response missing message field"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"board_updates": []}'
    mock_client.chat.completions.create.return_value = mock_response
    
    board_data = {"columns": [], "cards": {}}
    
    # Should handle gracefully
    result = get_ai_kanban_response(board_data, [], "Test")
    assert "board_updates" in result or "message" in result


@patch('backend.ai_service.client')
def test_get_ai_kanban_response_api_error(mock_client):
    """Test handling of API errors"""
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    
    board_data = {"columns": [], "cards": {}}
    
    with pytest.raises(AIServiceError):
        get_ai_kanban_response(board_data, [], "Test")


def test_get_ai_kanban_response_no_client():
    """Test error when client is not initialized"""
    with patch('backend.ai_service.client', None):
        board_data = {"columns": [], "cards": {}}
        
        with pytest.raises(AIServiceError, match="not initialized"):
            get_ai_kanban_response(board_data, [], "Test")


@patch('backend.ai_service.client')
def test_get_ai_kanban_response_multiple_operations(mock_client):
    """Test AI response with multiple board operations"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '''{
        "message": "I performed multiple operations",
        "board_updates": [
            {"operation": "add_card", "column_id": "col-1", "title": "Card 1"},
            {"operation": "add_card", "column_id": "col-2", "title": "Card 2"},
            {"operation": "move_card", "card_id": "card-1", "column_id": "col-3", "position": 0}
        ]
    }'''
    mock_client.chat.completions.create.return_value = mock_response
    
    board_data = {"columns": [], "cards": {}}
    
    result = get_ai_kanban_response(board_data, [], "Do multiple things")
    
    assert len(result["board_updates"]) == 3
    assert result["board_updates"][0]["operation"] == "add_card"
    assert result["board_updates"][2]["operation"] == "move_card"


@patch('backend.ai_service.client')
def test_get_ai_kanban_response_conversation_context(mock_client):
    """Test that conversation history is included in prompt"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"message": "Based on our previous conversation...", "board_updates": []}'
    mock_client.chat.completions.create.return_value = mock_response
    
    board_data = {"columns": [], "cards": {}}
    conversation_history = [
        {"role": "user", "content": "Add a card called Test"},
        {"role": "assistant", "content": "I added the card"}
    ]
    
    result = get_ai_kanban_response(board_data, conversation_history, "Move that card")
    
    # Verify the prompt included history
    call_args = mock_client.chat.completions.create.call_args
    prompt = call_args[1]["messages"][1]["content"]
    assert "Add a card called Test" in prompt
    assert "I added the card" in prompt

# Made with Bob
