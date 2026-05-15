from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Cookie, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.auth import authenticate, create_session, validate_session, delete_session
from backend.database import get_db, init_db
from backend.crud import (
    create_user, get_user_by_username, get_user_board,
    initialize_default_board, get_board_data, update_board_positions,
    update_column_title, create_card, delete_card, move_card
)

app = FastAPI(title="Project Management API")

# Path to static files
static_dir = Path(__file__).parent / "static"


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create default user if needed"""
    init_db()
    
    # Create default user if not exists
    db = next(get_db())
    try:
        user = get_user_by_username(db, "user")
        if not user:
            user = create_user(db, "user", "password")
            # Create default board with sample data
            initialize_default_board(db, user.id)
    finally:
        db.close()


# Dependency to get current user from session
def get_current_user(session_token: str = Cookie(None), db: Session = Depends(get_db)) -> dict:
    """Dependency to validate session and return user info"""
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_info = validate_session(session_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return user_info


# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str


class BoardUpdate(BaseModel):
    columns: list
    cards: dict


class ColumnRename(BaseModel):
    title: str


class CardCreate(BaseModel):
    title: str
    details: str = ""


class CardMove(BaseModel):
    columnId: str
    position: int


# Auth endpoints
@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/api/auth/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint - validates credentials and returns session token"""
    user_id = authenticate(db, credentials.username, credentials.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_session(credentials.username, user_id)
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=86400,  # 24 hours
        samesite="lax"
    )
    return response


@app.post("/api/auth/logout")
async def logout(session_token: str = Cookie(None)):
    """Logout endpoint - invalidates session"""
    if session_token:
        delete_session(session_token)
    
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie(key="session_token")
    return response


@app.get("/api/auth/me")
async def get_current_user_info(user_info: dict = Depends(get_current_user)):
    """Get current authenticated user"""
    return {"username": user_info["username"]}


# Board endpoints
@app.get("/api/board")
async def get_board(user_info: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's board data"""
    board = get_user_board(db, user_info["user_id"])
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    board_data = get_board_data(db, board.id)
    return board_data


@app.put("/api/board")
async def update_board(
    board_update: BoardUpdate,
    user_info: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update entire board (columns and cards)"""
    board = get_user_board(db, user_info["user_id"])
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    success = update_board_positions(db, board.id, board_update.columns, board_update.cards)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update board")
    
    board_data = get_board_data(db, board.id)
    return board_data


@app.patch("/api/board/columns/{column_id}")
async def rename_column(
    column_id: str,
    rename_data: ColumnRename,
    user_info: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rename a column"""
    column = update_column_title(db, column_id, rename_data.title)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    return {"id": column.id, "title": column.title}


@app.post("/api/board/cards")
async def add_card(
    card_data: CardCreate,
    column_id: str,
    user_info: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new card to a column"""
    from backend.crud import create_card
    from backend.models import Card
    
    # Generate card ID
    import secrets
    card_id = f"card-{secrets.token_hex(6)}"
    
    # Get current max position in column
    max_pos = db.query(Card).filter(Card.column_id == column_id).count()
    
    card = create_card(db, card_id, column_id, card_data.title, card_data.details, max_pos)
    return {
        "id": card.id,
        "title": card.title,
        "details": card.details
    }


@app.delete("/api/board/cards/{card_id}")
async def remove_card(
    card_id: str,
    user_info: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a card"""
    success = delete_card(db, card_id)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return {"message": "Card deleted"}


@app.patch("/api/board/cards/{card_id}/move")
async def move_card_endpoint(
    card_id: str,
    move_data: CardMove,
    user_info: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Move a card to a new column/position"""
    card = move_card(db, card_id, move_data.columnId, move_data.position)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return {
        "id": card.id,
        "columnId": card.column_id,
        "position": card.position
    }


# Mount static files for Next.js assets (CSS, JS, images, etc.)
app.mount("/_next", StaticFiles(directory=static_dir / "_next"), name="next-static")

# Catch-all route for SPA - serve appropriate HTML for each route
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve the Next.js SPA for all routes except API routes"""
    # If it's a file with extension (like .ico, .png, .svg, etc.), try to serve it
    if "." in full_path.split("/")[-1]:
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
    
    # Map routes to their HTML files
    route_map = {
        "": "index.html",  # Root
        "login": "login.html",
        "board": "board.html",
    }
    
    # Get the first part of the path (e.g., "login" from "login" or "login/something")
    route_part = full_path.split("/")[0] if full_path else ""
    
    # Find the appropriate HTML file
    html_file = route_map.get(route_part, "index.html")
    html_path = static_dir / html_file
    
    if html_path.exists():
        return FileResponse(html_path)
    
    # If no match, try 404.html
    not_found_path = static_dir / "404.html"
    if not_found_path.exists():
        return FileResponse(not_found_path, status_code=404)
    
    raise HTTPException(status_code=404, detail="Not found")
