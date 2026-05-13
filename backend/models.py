from datetime import datetime
from sqlalchemy import Column as SQLColumn, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = SQLColumn(Integer, primary_key=True, autoincrement=True)
    username = SQLColumn(String, nullable=False, unique=True, index=True)
    password_hash = SQLColumn(String, nullable=False)
    created_at = SQLColumn(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    boards = relationship("Board", back_populates="user", cascade="all, delete-orphan")


class Board(Base):
    __tablename__ = "boards"

    id = SQLColumn(Integer, primary_key=True, autoincrement=True)
    user_id = SQLColumn(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = SQLColumn(String, nullable=False)
    created_at = SQLColumn(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = SQLColumn(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="boards")
    columns = relationship("Column", back_populates="board", cascade="all, delete-orphan", order_by="Column.position")


class Column(Base):
    __tablename__ = "columns"

    id = SQLColumn(String, primary_key=True)
    board_id = SQLColumn(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True)
    title = SQLColumn(String, nullable=False)
    position = SQLColumn(Integer, nullable=False)
    created_at = SQLColumn(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    board = relationship("Board", back_populates="columns")
    cards = relationship("Card", back_populates="column", cascade="all, delete-orphan", order_by="Card.position")

    # Constraints
    __table_args__ = (
        UniqueConstraint("board_id", "position", name="uq_board_position"),
        Index("idx_columns_board_position", "board_id", "position"),
    )


class Card(Base):
    __tablename__ = "cards"

    id = SQLColumn(String, primary_key=True)
    column_id = SQLColumn(String, ForeignKey("columns.id", ondelete="CASCADE"), nullable=False, index=True)
    title = SQLColumn(String, nullable=False)
    details = SQLColumn(Text, nullable=False, default="")
    position = SQLColumn(Integer, nullable=False)
    created_at = SQLColumn(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = SQLColumn(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    column = relationship("Column", back_populates="cards")

    # Constraints
    __table_args__ = (
        UniqueConstraint("column_id", "position", name="uq_column_position"),
        Index("idx_cards_column_position", "column_id", "position"),
    )

# Made with Bob
