import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import User, Board, Column, Card
from backend.crud import (
    create_user, get_user_by_username, verify_password,
    create_board, get_user_board, create_column, update_column_title,
    create_card, update_card, move_card, delete_card,
    get_board_data, update_board_positions, initialize_default_board
)


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestUserOperations:
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = create_user(db_session, "testuser", "testpass")
        assert user.id is not None
        assert user.username == "testuser"
        assert user.password_hash != "testpass"  # Should be hashed
        assert user.created_at is not None

    def test_get_user_by_username(self, db_session):
        """Test retrieving user by username"""
        create_user(db_session, "testuser", "testpass")
        user = get_user_by_username(db_session, "testuser")
        assert user is not None
        assert user.username == "testuser"

    def test_get_nonexistent_user(self, db_session):
        """Test retrieving non-existent user returns None"""
        user = get_user_by_username(db_session, "nonexistent")
        assert user is None

    def test_verify_password(self, db_session):
        """Test password verification"""
        user = create_user(db_session, "testuser", "testpass")
        assert verify_password("testpass", user.password_hash) is True
        assert verify_password("wrongpass", user.password_hash) is False

    def test_unique_username_constraint(self, db_session):
        """Test that duplicate usernames are not allowed"""
        create_user(db_session, "testuser", "pass1")
        with pytest.raises(Exception):
            create_user(db_session, "testuser", "pass2")


class TestBoardOperations:
    def test_create_board(self, db_session):
        """Test creating a board"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        assert board.id is not None
        assert board.user_id == user.id
        assert board.title == "Test Board"
        assert board.created_at is not None
        assert board.updated_at is not None

    def test_get_user_board(self, db_session):
        """Test retrieving user's board"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        retrieved_board = get_user_board(db_session, user.id)
        assert retrieved_board is not None
        assert retrieved_board.id == board.id

    def test_get_board_for_nonexistent_user(self, db_session):
        """Test retrieving board for non-existent user"""
        board = get_user_board(db_session, 999)
        assert board is None


class TestColumnOperations:
    def test_create_column(self, db_session):
        """Test creating a column"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        column = create_column(db_session, board.id, "col-1", "Backlog", 0)
        assert column.id == "col-1"
        assert column.board_id == board.id
        assert column.title == "Backlog"
        assert column.position == 0

    def test_update_column_title(self, db_session):
        """Test updating column title"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        column = create_column(db_session, board.id, "col-1", "Backlog", 0)
        updated = update_column_title(db_session, "col-1", "New Title")
        assert updated.title == "New Title"

    def test_unique_position_constraint(self, db_session):
        """Test that duplicate positions in same board are not allowed"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        create_column(db_session, board.id, "col-1", "Column 1", 0)
        with pytest.raises(Exception):
            create_column(db_session, board.id, "col-2", "Column 2", 0)


class TestCardOperations:
    def test_create_card(self, db_session):
        """Test creating a card"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        column = create_column(db_session, board.id, "col-1", "Backlog", 0)
        card = create_card(db_session, "card-1", "col-1", "Test Card", "Details", 0)
        assert card.id == "card-1"
        assert card.column_id == "col-1"
        assert card.title == "Test Card"
        assert card.details == "Details"
        assert card.position == 0

    def test_update_card(self, db_session):
        """Test updating card"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        column = create_column(db_session, board.id, "col-1", "Backlog", 0)
        card = create_card(db_session, "card-1", "col-1", "Test Card", "Details", 0)
        updated = update_card(db_session, "card-1", title="New Title", details="New Details")
        assert updated.title == "New Title"
        assert updated.details == "New Details"

    def test_move_card_same_column(self, db_session):
        """Test moving card within same column"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        column = create_column(db_session, board.id, "col-1", "Backlog", 0)
        card1 = create_card(db_session, "card-1", "col-1", "Card 1", "", 0)
        card2 = create_card(db_session, "card-2", "col-1", "Card 2", "", 1)
        
        moved = move_card(db_session, "card-1", "col-1", 1)
        assert moved.position == 1

    def test_move_card_different_column(self, db_session):
        """Test moving card to different column"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        col1 = create_column(db_session, board.id, "col-1", "Backlog", 0)
        col2 = create_column(db_session, board.id, "col-2", "In Progress", 1)
        card = create_card(db_session, "card-1", "col-1", "Card 1", "", 0)
        
        moved = move_card(db_session, "card-1", "col-2", 0)
        assert moved.column_id == "col-2"
        assert moved.position == 0

    def test_delete_card(self, db_session):
        """Test deleting a card"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        column = create_column(db_session, board.id, "col-1", "Backlog", 0)
        card = create_card(db_session, "card-1", "col-1", "Card 1", "", 0)
        
        success = delete_card(db_session, "card-1")
        assert success is True
        
        # Verify card is deleted
        deleted_card = db_session.query(Card).filter(Card.id == "card-1").first()
        assert deleted_card is None

    def test_delete_nonexistent_card(self, db_session):
        """Test deleting non-existent card returns False"""
        success = delete_card(db_session, "nonexistent")
        assert success is False


class TestBoardData:
    def test_get_board_data(self, db_session):
        """Test getting complete board data"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        col1 = create_column(db_session, board.id, "col-1", "Backlog", 0)
        col2 = create_column(db_session, board.id, "col-2", "In Progress", 1)
        card1 = create_card(db_session, "card-1", "col-1", "Card 1", "Details 1", 0)
        card2 = create_card(db_session, "card-2", "col-1", "Card 2", "Details 2", 1)
        card3 = create_card(db_session, "card-3", "col-2", "Card 3", "Details 3", 0)
        
        board_data = get_board_data(db_session, board.id)
        
        assert board_data is not None
        assert len(board_data["columns"]) == 2
        assert len(board_data["cards"]) == 3
        
        # Check column structure
        assert board_data["columns"][0]["id"] == "col-1"
        assert board_data["columns"][0]["title"] == "Backlog"
        assert board_data["columns"][0]["cardIds"] == ["card-1", "card-2"]
        
        # Check card structure
        assert board_data["cards"]["card-1"]["title"] == "Card 1"
        assert board_data["cards"]["card-1"]["details"] == "Details 1"

    def test_update_board_positions(self, db_session):
        """Test updating board positions"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        col1 = create_column(db_session, board.id, "col-1", "Backlog", 0)
        col2 = create_column(db_session, board.id, "col-2", "In Progress", 1)
        card1 = create_card(db_session, "card-1", "col-1", "Card 1", "Details 1", 0)
        card2 = create_card(db_session, "card-2", "col-1", "Card 2", "Details 2", 1)
        
        # Move card-2 to col-2
        new_columns = [
            {"id": "col-1", "title": "Backlog", "cardIds": ["card-1"]},
            {"id": "col-2", "title": "In Progress", "cardIds": ["card-2"]}
        ]
        new_cards = {
            "card-1": {"title": "Card 1", "details": "Details 1"},
            "card-2": {"title": "Card 2 Updated", "details": "Details 2"}
        }
        
        success = update_board_positions(db_session, board.id, new_columns, new_cards)
        assert success is True
        
        # Verify changes
        card2_updated = db_session.query(Card).filter(Card.id == "card-2").first()
        assert card2_updated.column_id == "col-2"
        assert card2_updated.title == "Card 2 Updated"


class TestInitialization:
    def test_initialize_default_board(self, db_session):
        """Test initializing default board with sample data"""
        user = create_user(db_session, "testuser", "testpass")
        board = initialize_default_board(db_session, user.id)
        
        assert board is not None
        assert board.title == "My Kanban Board"
        
        # Check columns created
        columns = db_session.query(Column).filter(Column.board_id == board.id).all()
        assert len(columns) == 5
        
        # Check cards created
        cards = db_session.query(Card).all()
        assert len(cards) == 8
        
        # Verify board data structure
        board_data = get_board_data(db_session, board.id)
        assert len(board_data["columns"]) == 5
        assert len(board_data["cards"]) == 8


class TestCascadeDeletes:
    def test_delete_user_cascades_to_boards(self, db_session):
        """Test that deleting user deletes their boards"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        
        db_session.delete(user)
        db_session.commit()
        
        # Verify board is deleted
        deleted_board = db_session.query(Board).filter(Board.id == board.id).first()
        assert deleted_board is None

    def test_delete_board_cascades_to_columns(self, db_session):
        """Test that deleting board deletes its columns"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        column = create_column(db_session, board.id, "col-1", "Backlog", 0)
        
        db_session.delete(board)
        db_session.commit()
        
        # Verify column is deleted
        deleted_column = db_session.query(Column).filter(Column.id == "col-1").first()
        assert deleted_column is None

    def test_delete_column_cascades_to_cards(self, db_session):
        """Test that deleting column deletes its cards"""
        user = create_user(db_session, "testuser", "testpass")
        board = create_board(db_session, user.id, "Test Board")
        column = create_column(db_session, board.id, "col-1", "Backlog", 0)
        card = create_card(db_session, "card-1", "col-1", "Card 1", "", 0)
        
        db_session.delete(column)
        db_session.commit()
        
        # Verify card is deleted
        deleted_card = db_session.query(Card).filter(Card.id == "card-1").first()
        assert deleted_card is None

# Made with Bob
