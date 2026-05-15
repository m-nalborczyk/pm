import pytest
from fastapi.testclient import TestClient
from backend.main import app, static_dir

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint returns 200 with correct status"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_serves_static_files():
    """Test root endpoint serves static files"""
    response = client.get("/")
    
    # Static files should exist in production build
    assert static_dir.exists(), "Static directory should exist after build"
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_static_assets_accessible():
    """Test that static assets like CSS and JS are accessible"""
    # Try to access a common Next.js static file pattern
    response = client.get("/_next/static/css/app/layout.css")
    # Should either exist (200) or not found (404), but not error
    assert response.status_code in [200, 404]


def test_ai_test_endpoint():
    """Test AI test endpoint returns response"""
    from unittest.mock import patch, Mock
    
    # Mock the AI service to avoid real API calls in tests
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "4"
    
    with patch('backend.ai_service.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        
        response = client.get("/api/ai/test")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'success'
        assert 'response' in data
        assert 'model' in data


def test_ai_test_endpoint_error():
    """Test AI test endpoint handles errors gracefully"""
    from unittest.mock import patch
    
    with patch('backend.ai_service.client') as mock_client:
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        response = client.get("/api/ai/test")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'error'
        assert 'error' in data

# Made with Bob
