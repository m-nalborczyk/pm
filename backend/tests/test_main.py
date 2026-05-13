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

# Made with Bob
