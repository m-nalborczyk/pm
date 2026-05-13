import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# Default test credentials
TEST_USERNAME = "user"
TEST_PASSWORD = "password"


@pytest.fixture
def authenticated_client():
    """Fixture that returns a client with authentication cookie"""
    response = client.post(
        "/api/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    session_token = response.cookies.get("session_token")
    
    class AuthenticatedClient:
        def __init__(self, token):
            self.token = token
            
        def get(self, url, **kwargs):
            kwargs.setdefault("cookies", {})["session_token"] = self.token
            return client.get(url, **kwargs)
        
        def post(self, url, **kwargs):
            kwargs.setdefault("cookies", {})["session_token"] = self.token
            return client.post(url, **kwargs)
        
        def put(self, url, **kwargs):
            kwargs.setdefault("cookies", {})["session_token"] = self.token
            return client.put(url, **kwargs)
        
        def patch(self, url, **kwargs):
            kwargs.setdefault("cookies", {})["session_token"] = self.token
            return client.patch(url, **kwargs)
        
        def delete(self, url, **kwargs):
            kwargs.setdefault("cookies", {})["session_token"] = self.token
            return client.delete(url, **kwargs)
    
    return AuthenticatedClient(session_token)


class TestHealthEndpoint:
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestBoardEndpoints:
    def test_get_board_authenticated(self, authenticated_client):
        """Test getting board when authenticated"""
        response = authenticated_client.get("/api/board")
        assert response.status_code == 200
        
        data = response.json()
        assert "columns" in data
        assert "cards" in data
        assert len(data["columns"]) == 5  # Default 5 columns
        assert isinstance(data["cards"], dict)

    def test_get_board_not_authenticated(self):
        """Test getting board without authentication"""
        response = client.get("/api/board")
        assert response.status_code == 401

    def test_board_structure(self, authenticated_client):
        """Test that board has correct structure"""
        response = authenticated_client.get("/api/board")
        data = response.json()
        
        # Check columns structure
        for column in data["columns"]:
            assert "id" in column
            assert "title" in column
            assert "cardIds" in column
            assert isinstance(column["cardIds"], list)
        
        # Check cards structure
        for card_id, card in data["cards"].items():
            assert "id" in card
            assert "title" in card
            assert "details" in card

    def test_update_board(self, authenticated_client):
        """Test updating board"""
        # Get current board
        response = authenticated_client.get("/api/board")
        board_data = response.json()
        
        # Modify board data
        board_data["columns"][0]["title"] = "Updated Backlog"
        
        # Update board
        response = authenticated_client.put("/api/board", json=board_data)
        assert response.status_code == 200
        
        # Verify update
        updated_data = response.json()
        assert updated_data["columns"][0]["title"] == "Updated Backlog"

    def test_update_board_not_authenticated(self):
        """Test updating board without authentication"""
        response = client.put("/api/board", json={"columns": [], "cards": {}})
        assert response.status_code == 401


class TestColumnEndpoints:
    def test_rename_column(self, authenticated_client):
        """Test renaming a column"""
        # Get board to find a column ID
        response = authenticated_client.get("/api/board")
        board_data = response.json()
        column_id = board_data["columns"][0]["id"]
        
        # Rename column
        response = authenticated_client.patch(
            f"/api/board/columns/{column_id}",
            json={"title": "New Column Name"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "New Column Name"

    def test_rename_nonexistent_column(self, authenticated_client):
        """Test renaming a non-existent column"""
        response = authenticated_client.patch(
            "/api/board/columns/nonexistent",
            json={"title": "New Name"}
        )
        assert response.status_code == 404


class TestCardEndpoints:
    def test_add_card(self, authenticated_client):
        """Test adding a new card"""
        # Get board to find a column ID
        response = authenticated_client.get("/api/board")
        board_data = response.json()
        column_id = board_data["columns"][0]["id"]
        
        # Add card
        response = authenticated_client.post(
            f"/api/board/cards?column_id={column_id}",
            json={"title": "New Card", "details": "Card details"}
        )
        assert response.status_code == 200
        
        card_data = response.json()
        assert card_data["title"] == "New Card"
        assert card_data["details"] == "Card details"
        assert "id" in card_data

    def test_add_card_without_details(self, authenticated_client):
        """Test adding a card without details"""
        response = authenticated_client.get("/api/board")
        board_data = response.json()
        column_id = board_data["columns"][0]["id"]
        
        response = authenticated_client.post(
            f"/api/board/cards?column_id={column_id}",
            json={"title": "Card Without Details"}
        )
        assert response.status_code == 200
        assert response.json()["details"] == ""

    def test_delete_card(self, authenticated_client):
        """Test deleting a card"""
        # Get board to find a card ID
        response = authenticated_client.get("/api/board")
        board_data = response.json()
        
        if board_data["cards"]:
            card_id = list(board_data["cards"].keys())[0]
            
            # Delete card
            response = authenticated_client.delete(f"/api/board/cards/{card_id}")
            assert response.status_code == 200
            assert response.json()["message"] == "Card deleted"
            
            # Verify card is deleted
            response = authenticated_client.get("/api/board")
            updated_data = response.json()
            assert card_id not in updated_data["cards"]

    def test_delete_nonexistent_card(self, authenticated_client):
        """Test deleting a non-existent card"""
        response = authenticated_client.delete("/api/board/cards/nonexistent")
        assert response.status_code == 404

    def test_move_card(self, authenticated_client):
        """Test moving a card"""
        # Get board
        response = authenticated_client.get("/api/board")
        board_data = response.json()
        
        if board_data["cards"] and len(board_data["columns"]) >= 2:
            card_id = list(board_data["cards"].keys())[0]
            target_column_id = board_data["columns"][1]["id"]
            
            # Move card
            response = authenticated_client.patch(
                f"/api/board/cards/{card_id}/move",
                json={"columnId": target_column_id, "position": 0}
            )
            assert response.status_code == 200
            
            move_data = response.json()
            assert move_data["columnId"] == target_column_id
            assert move_data["position"] == 0

    def test_move_nonexistent_card(self, authenticated_client):
        """Test moving a non-existent card"""
        response = authenticated_client.patch(
            "/api/board/cards/nonexistent/move",
            json={"columnId": "col-1", "position": 0}
        )
        assert response.status_code == 404


class TestCardOperations:
    def test_add_and_delete_card_flow(self, authenticated_client):
        """Test complete flow of adding and deleting a card"""
        # Get initial board state
        response = authenticated_client.get("/api/board")
        initial_data = response.json()
        column_id = initial_data["columns"][0]["id"]
        initial_card_count = len(initial_data["cards"])
        
        # Add card
        response = authenticated_client.post(
            f"/api/board/cards?column_id={column_id}",
            json={"title": "Test Card", "details": "Test Details"}
        )
        new_card = response.json()
        new_card_id = new_card["id"]
        
        # Verify card was added
        response = authenticated_client.get("/api/board")
        data = response.json()
        assert len(data["cards"]) == initial_card_count + 1
        assert new_card_id in data["cards"]
        
        # Delete card
        response = authenticated_client.delete(f"/api/board/cards/{new_card_id}")
        assert response.status_code == 200
        
        # Verify card was deleted
        response = authenticated_client.get("/api/board")
        final_data = response.json()
        assert len(final_data["cards"]) == initial_card_count
        assert new_card_id not in final_data["cards"]

    def test_move_card_between_columns(self, authenticated_client):
        """Test moving a card between columns"""
        # Get board
        response = authenticated_client.get("/api/board")
        board_data = response.json()
        
        # Add a new card to first column
        column1_id = board_data["columns"][0]["id"]
        column2_id = board_data["columns"][1]["id"]
        
        response = authenticated_client.post(
            f"/api/board/cards?column_id={column1_id}",
            json={"title": "Moving Card", "details": ""}
        )
        card_id = response.json()["id"]
        
        # Verify card is in column 1
        response = authenticated_client.get("/api/board")
        data = response.json()
        assert card_id in data["columns"][0]["cardIds"]
        
        # Move to column 2
        response = authenticated_client.patch(
            f"/api/board/cards/{card_id}/move",
            json={"columnId": column2_id, "position": 0}
        )
        assert response.status_code == 200
        
        # Verify card moved
        response = authenticated_client.get("/api/board")
        data = response.json()
        assert card_id not in data["columns"][0]["cardIds"]
        assert card_id in data["columns"][1]["cardIds"]


class TestBoardPersistence:
    def test_board_persists_across_requests(self, authenticated_client):
        """Test that board changes persist across requests"""
        # Get initial board
        response = authenticated_client.get("/api/board")
        initial_data = response.json()
        column_id = initial_data["columns"][0]["id"]
        
        # Add a card
        response = authenticated_client.post(
            f"/api/board/cards?column_id={column_id}",
            json={"title": "Persistent Card", "details": "Should persist"}
        )
        card_id = response.json()["id"]
        
        # Get board again
        response = authenticated_client.get("/api/board")
        data = response.json()
        
        # Verify card persists
        assert card_id in data["cards"]
        assert data["cards"][card_id]["title"] == "Persistent Card"


class TestErrorHandling:
    def test_invalid_json_in_update(self, authenticated_client):
        """Test error handling for invalid JSON"""
        response = authenticated_client.put(
            "/api/board",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_required_fields(self, authenticated_client):
        """Test error handling for missing required fields"""
        response = authenticated_client.get("/api/board")
        column_id = response.json()["columns"][0]["id"]
        
        # Try to add card without title
        response = authenticated_client.post(
            f"/api/board/cards?column_id={column_id}",
            json={"details": "No title"}
        )
        assert response.status_code == 422

# Made with Bob
