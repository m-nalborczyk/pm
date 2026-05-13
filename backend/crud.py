from typing import Optional
from sqlalchemy.orm import Session
import bcrypt
from backend.models import User, Board, Column, Card


def create_user(db: Session, username: str, password: str) -> User:
    """Create a new user with hashed password"""
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))


def create_board(db: Session, user_id: int, title: str) -> Board:
    """Create a new board for a user"""
    board = Board(user_id=user_id, title=title)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def get_user_board(db: Session, user_id: int) -> Optional[Board]:
    """Get the board for a user (MVP: one board per user)"""
    return db.query(Board).filter(Board.user_id == user_id).first()


def create_column(db: Session, board_id: int, column_id: str, title: str, position: int) -> Column:
    """Create a new column"""
    column = Column(id=column_id, board_id=board_id, title=title, position=position)
    db.add(column)
    db.commit()
    db.refresh(column)
    return column


def update_column_title(db: Session, column_id: str, title: str) -> Optional[Column]:
    """Update column title"""
    column = db.query(Column).filter(Column.id == column_id).first()
    if column:
        column.title = title
        db.commit()
        db.refresh(column)
    return column


def create_card(db: Session, card_id: str, column_id: str, title: str, details: str, position: int) -> Card:
    """Create a new card"""
    card = Card(id=card_id, column_id=column_id, title=title, details=details, position=position)
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def update_card(db: Session, card_id: str, title: Optional[str] = None, details: Optional[str] = None) -> Optional[Card]:
    """Update card title and/or details"""
    card = db.query(Card).filter(Card.id == card_id).first()
    if card:
        if title is not None:
            card.title = title
        if details is not None:
            card.details = details
        db.commit()
        db.refresh(card)
    return card


def move_card(db: Session, card_id: str, new_column_id: str, new_position: int) -> Optional[Card]:
    """Move card to a new column and position"""
    card = db.query(Card).filter(Card.id == card_id).first()
    if card:
        old_column_id = card.column_id
        old_position = card.position
        
        if old_column_id == new_column_id:
            # Moving within same column - need to handle position shifts carefully
            if old_position == new_position:
                return card  # No move needed
            
            # Temporarily set to a high position to avoid constraint violation
            card.position = 9999
            db.flush()
            
            if old_position < new_position:
                # Moving down: shift cards between old and new position up
                db.query(Card).filter(
                    Card.column_id == old_column_id,
                    Card.position > old_position,
                    Card.position <= new_position
                ).update({Card.position: Card.position - 1}, synchronize_session=False)
            else:
                # Moving up: shift cards between new and old position down
                db.query(Card).filter(
                    Card.column_id == old_column_id,
                    Card.position >= new_position,
                    Card.position < old_position
                ).update({Card.position: Card.position + 1}, synchronize_session=False)
            
            # Now set the final position
            card.position = new_position
        else:
            # Moving to different column
            # Remove from old column
            db.query(Card).filter(
                Card.column_id == old_column_id,
                Card.position > old_position
            ).update({Card.position: Card.position - 1}, synchronize_session=False)
            
            # Make space in new column
            db.query(Card).filter(
                Card.column_id == new_column_id,
                Card.position >= new_position
            ).update({Card.position: Card.position + 1}, synchronize_session=False)
            
            # Move the card
            card.column_id = new_column_id
            card.position = new_position
        
        db.commit()
        db.refresh(card)
    return card


def delete_card(db: Session, card_id: str) -> bool:
    """Delete a card"""
    card = db.query(Card).filter(Card.id == card_id).first()
    if card:
        column_id = card.column_id
        position = card.position
        
        # Delete the card
        db.delete(card)
        
        # Adjust positions of remaining cards in the column
        db.query(Card).filter(
            Card.column_id == column_id,
            Card.position > position
        ).update({Card.position: Card.position - 1})
        
        db.commit()
        return True
    return False


def get_board_data(db: Session, board_id: int) -> Optional[dict]:
    """Get complete board data with columns and cards in frontend format"""
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        return None
    
    # Get columns ordered by position
    columns = db.query(Column).filter(Column.board_id == board_id).order_by(Column.position).all()
    
    # Build the response in frontend format
    columns_data = []
    cards_data = {}
    
    for column in columns:
        # Get cards for this column ordered by position
        cards = db.query(Card).filter(Card.column_id == column.id).order_by(Card.position).all()
        
        card_ids = []
        for card in cards:
            card_ids.append(card.id)
            cards_data[card.id] = {
                "id": card.id,
                "title": card.title,
                "details": card.details
            }
        
        columns_data.append({
            "id": column.id,
            "title": column.title,
            "cardIds": card_ids
        })
    
    return {
        "columns": columns_data,
        "cards": cards_data
    }


def update_board_positions(db: Session, board_id: int, columns_data: list, cards_data: dict) -> bool:
    """Update all card positions based on frontend board state"""
    try:
        # Update column titles
        for col_data in columns_data:
            column = db.query(Column).filter(Column.id == col_data["id"]).first()
            if column:
                column.title = col_data["title"]
        
        # Update card positions and column assignments
        for col_data in columns_data:
            column_id = col_data["id"]
            for position, card_id in enumerate(col_data["cardIds"]):
                card = db.query(Card).filter(Card.id == card_id).first()
                if card:
                    card.column_id = column_id
                    card.position = position
                    # Update title and details if provided in cards_data
                    if card_id in cards_data:
                        card.title = cards_data[card_id]["title"]
                        card.details = cards_data[card_id]["details"]
        
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def initialize_default_board(db: Session, user_id: int) -> Board:
    """Create default board with 5 columns and sample cards"""
    # Create board
    board = create_board(db, user_id, "My Kanban Board")
    
    # Create 5 default columns
    columns_config = [
        ("col-backlog", "Backlog", 0),
        ("col-discovery", "Discovery", 1),
        ("col-progress", "In Progress", 2),
        ("col-review", "Review", 3),
        ("col-done", "Done", 4),
    ]
    
    for col_id, col_title, col_pos in columns_config:
        create_column(db, board.id, col_id, col_title, col_pos)
    
    # Create sample cards
    sample_cards = [
        ("card-1", "col-backlog", "Align roadmap themes", "Draft quarterly themes with impact statements and metrics.", 0),
        ("card-2", "col-backlog", "Gather customer signals", "Review support tags, sales notes, and churn feedback.", 1),
        ("card-3", "col-discovery", "Prototype analytics view", "Sketch initial dashboard layout and key drill-downs.", 0),
        ("card-4", "col-progress", "Refine status language", "Standardize column labels and tone across the board.", 0),
        ("card-5", "col-progress", "Design card layout", "Add hierarchy and spacing for scanning dense lists.", 1),
        ("card-6", "col-review", "QA micro-interactions", "Verify hover, focus, and loading states.", 0),
        ("card-7", "col-done", "Ship marketing page", "Final copy approved and asset pack delivered.", 0),
        ("card-8", "col-done", "Close onboarding sprint", "Document release notes and share internally.", 1),
    ]
    
    for card_id, col_id, card_title, card_details, card_pos in sample_cards:
        create_card(db, card_id, col_id, card_title, card_details, card_pos)
    
    return board

# Made with Bob
