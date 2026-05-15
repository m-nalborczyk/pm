"""
Tests for AI service module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.ai_service import get_ai_response, test_ai_connection, AIServiceError


class TestAIService:
    """Test AI service functionality"""
    
    def test_get_ai_response_success(self):
        """Test successful AI response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "4"
        
        with patch('backend.ai_service.client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_response
            
            result = get_ai_response("What is 2+2?")
            
            assert result == "4"
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['model'] == "openai/gpt-4o-mini-2024-07-18"
            assert call_args[1]['messages'][0]['content'] == "What is 2+2?"
    
    def test_get_ai_response_no_client(self):
        """Test error when client is not initialized"""
        with patch('backend.ai_service.client', None):
            with pytest.raises(AIServiceError) as exc_info:
                get_ai_response("test")
            
            assert "not initialized" in str(exc_info.value)
            assert "OPENROUTER_API_KEY" in str(exc_info.value)
    
    def test_get_ai_response_api_error(self):
        """Test handling of API errors"""
        with patch('backend.ai_service.client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            with pytest.raises(AIServiceError) as exc_info:
                get_ai_response("test")
            
            assert "OpenRouter API error" in str(exc_info.value)
            assert "API Error" in str(exc_info.value)
    
    def test_get_ai_response_timeout(self):
        """Test handling of timeout errors"""
        with patch('backend.ai_service.client') as mock_client:
            mock_client.chat.completions.create.side_effect = TimeoutError("Request timeout")
            
            with pytest.raises(AIServiceError) as exc_info:
                get_ai_response("test", timeout=1)
            
            assert "OpenRouter API error" in str(exc_info.value)
    
    def test_get_ai_response_custom_timeout(self):
        """Test that custom timeout is passed to API call"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "response"
        
        with patch('backend.ai_service.client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_response
            
            get_ai_response("test", timeout=60)
            
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['timeout'] == 60
    
    def test_test_ai_connection_success(self):
        """Test successful connection test"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "4"
        
        with patch('backend.ai_service.client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_response
            
            result = test_ai_connection()
            
            assert result['status'] == 'success'
            assert result['response'] == '4'
            assert 'model' in result
            assert result['model'] == "openai/gpt-4o-mini-2024-07-18"
    
    def test_test_ai_connection_failure(self):
        """Test connection test failure"""
        with patch('backend.ai_service.client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("Connection failed")
            
            result = test_ai_connection()
            
            assert result['status'] == 'error'
            assert 'error' in result
            assert 'Connection failed' in result['error']
            assert 'model' in result
    
    def test_test_ai_connection_no_client(self):
        """Test connection test when client not initialized"""
        with patch('backend.ai_service.client', None):
            result = test_ai_connection()
            
            assert result['status'] == 'error'
            assert 'not initialized' in result['error']


class TestAIServiceIntegration:
    """Integration tests for AI service (requires API key)"""
    
    @pytest.mark.skip(reason="Integration test - run manually to test real API")
    def test_real_api_call(self):
        """Test real API call to OpenRouter (run manually with pytest -k test_real_api_call)"""
        result = test_ai_connection()
        
        assert result['status'] == 'success'
        assert 'response' in result
        # The response should contain "4" somewhere
        assert '4' in result['response']

# Made with Bob
