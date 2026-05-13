import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import sessions

client = TestClient(app)

# Default test credentials (created in startup)
TEST_USERNAME = "user"
TEST_PASSWORD = "password"


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear sessions before each test"""
    sessions.clear()
    yield
    sessions.clear()


def test_login_success():
    """Test successful login with valid credentials"""
    response = client.post(
        "/api/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Login successful"}
    assert "session_token" in response.cookies


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        json={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_wrong_password():
    """Test login with correct username but wrong password"""
    response = client.post(
        "/api/auth/login",
        json={"username": TEST_USERNAME, "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_current_user_authenticated():
    """Test getting current user when authenticated"""
    # First login
    login_response = client.post(
        "/api/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    session_token = login_response.cookies.get("session_token")
    
    # Then get current user
    response = client.get(
        "/api/auth/me",
        cookies={"session_token": session_token}
    )
    assert response.status_code == 200
    assert response.json() == {"username": TEST_USERNAME}


def test_get_current_user_not_authenticated():
    """Test getting current user without authentication"""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_current_user_invalid_token():
    """Test getting current user with invalid token"""
    response = client.get(
        "/api/auth/me",
        cookies={"session_token": "invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired session"


def test_logout():
    """Test logout functionality"""
    # First login
    login_response = client.post(
        "/api/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    session_token = login_response.cookies.get("session_token")
    
    # Then logout
    logout_response = client.post(
        "/api/auth/logout",
        cookies={"session_token": session_token}
    )
    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "Logout successful"}
    
    # Verify session is invalid after logout
    response = client.get(
        "/api/auth/me",
        cookies={"session_token": session_token}
    )
    assert response.status_code == 401


def test_logout_without_token():
    """Test logout without session token"""
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}
