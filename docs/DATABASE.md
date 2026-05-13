# Database Schema Documentation

## Overview

SQLite database schema for the Project Management MVP. Designed to support the current single-user, single-board MVP while being extensible for future multi-user, multi-board functionality.

## Entity Relationship Diagram

```
┌─────────────────┐
│     users       │
│─────────────────│
│ id (PK)         │
│ username        │
│ password_hash   │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐
│     boards      │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │
│ title           │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐
│    columns      │
│─────────────────│
│ id (PK)         │
│ board_id (FK)   │
│ title           │
│ position        │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐
│     cards       │
│─────────────────│
│ id (PK)         │
│ column_id (FK)  │
│ title           │
│ details         │
│ position        │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## Table Definitions

### users

Stores user authentication and profile information.

| Column        | Type         | Constraints                    | Description                          |
|---------------|--------------|--------------------------------|--------------------------------------|
| id            | INTEGER      | PRIMARY KEY AUTOINCREMENT      | Unique user identifier               |
| username      | TEXT         | NOT NULL, UNIQUE               | Login username                       |
| password_hash | TEXT         | NOT NULL                       | Bcrypt hashed password               |
| created_at    | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIME | Account creation timestamp           |

**Indexes:**
- `idx_users_username` on `username` (for login lookups)

**Notes:**
- For MVP, only one user will exist (username: "user")
- Password stored as bcrypt hash, never plaintext
- Future: Add email, display_name, last_login, etc.

### boards

Stores Kanban board metadata. Each user can have multiple boards (future), but MVP limits to one board per user.

| Column     | Type         | Constraints                    | Description                          |
|------------|--------------|--------------------------------|--------------------------------------|
| id         | INTEGER      | PRIMARY KEY AUTOINCREMENT      | Unique board identifier              |
| user_id    | INTEGER      | NOT NULL, FOREIGN KEY(users)   | Owner of the board                   |
| title      | TEXT         | NOT NULL                       | Board name/title                     |
| created_at | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIME | Board creation timestamp             |
| updated_at | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIME | Last modification timestamp          |

**Indexes:**
- `idx_boards_user_id` on `user_id` (for fetching user's boards)

**Constraints:**
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`

**Notes:**
- MVP: One board per user, enforced at application level
- Future: Remove one-board limitation
- `updated_at` triggers on any column/card change

### columns

Stores Kanban columns (stages). Fixed at 5 columns for MVP, but schema supports dynamic columns.

| Column     | Type         | Constraints                    | Description                          |
|------------|--------------|--------------------------------|--------------------------------------|
| id         | TEXT         | PRIMARY KEY                    | Column identifier (e.g., "col-backlog") |
| board_id   | INTEGER      | NOT NULL, FOREIGN KEY(boards)  | Parent board                         |
| title      | TEXT         | NOT NULL                       | Column display name                  |
| position   | INTEGER      | NOT NULL                       | Display order (0-based)              |
| created_at | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIME | Column creation timestamp            |

**Indexes:**
- `idx_columns_board_id` on `board_id` (for fetching board columns)
- `idx_columns_board_position` on `(board_id, position)` (for ordered retrieval)

**Constraints:**
- `FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE`
- `UNIQUE (board_id, position)` (no duplicate positions per board)

**Notes:**
- MVP: 5 fixed columns created on board initialization
- `id` is TEXT to match frontend format ("col-backlog", etc.)
- `position` determines left-to-right display order
- Columns can be renamed but not added/removed in MVP

### cards

Stores individual Kanban cards with title and details.

| Column     | Type         | Constraints                    | Description                          |
|------------|--------------|--------------------------------|--------------------------------------|
| id         | TEXT         | PRIMARY KEY                    | Card identifier (e.g., "card-abc123") |
| column_id  | TEXT         | NOT NULL, FOREIGN KEY(columns) | Current column/stage                 |
| title      | TEXT         | NOT NULL                       | Card title/summary                   |
| details    | TEXT         | NOT NULL, DEFAULT ''           | Card description/notes               |
| position   | INTEGER      | NOT NULL                       | Position within column (0-based)     |
| created_at | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIME | Card creation timestamp              |
| updated_at | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIME | Last modification timestamp          |

**Indexes:**
- `idx_cards_column_id` on `column_id` (for fetching column cards)
- `idx_cards_column_position` on `(column_id, position)` (for ordered retrieval)

**Constraints:**
- `FOREIGN KEY (column_id) REFERENCES columns(id) ON DELETE CASCADE`
- `UNIQUE (column_id, position)` (no duplicate positions per column)

**Notes:**
- `id` is TEXT to match frontend format ("card-abc123xyz")
- `position` determines top-to-bottom display order within column
- Moving cards updates `column_id` and `position`
- `updated_at` triggers on any field change

## Relationships

1. **users → boards**: One-to-Many
   - One user can own multiple boards (future)
   - Cascade delete: Deleting user deletes all their boards

2. **boards → columns**: One-to-Many
   - One board has multiple columns (fixed at 5 for MVP)
   - Cascade delete: Deleting board deletes all its columns

3. **columns → cards**: One-to-Many
   - One column contains multiple cards
   - Cascade delete: Deleting column deletes all its cards

## JSON Serialization Format

The database schema maps to the frontend `BoardData` type:

### Frontend TypeScript Types

```typescript
type Card = {
  id: string;
  title: string;
  details: string;
};

type Column = {
  id: string;
  title: string;
  cardIds: string[];
};

type BoardData = {
  columns: Column[];
  cards: Record<string, Card>;
};
```

### Database to JSON Conversion

**Query Pattern:**
```sql
-- Get board with columns and cards
SELECT 
  c.id as column_id,
  c.title as column_title,
  c.position as column_position,
  card.id as card_id,
  card.title as card_title,
  card.details as card_details,
  card.position as card_position
FROM columns c
LEFT JOIN cards card ON card.column_id = c.id
WHERE c.board_id = ?
ORDER BY c.position, card.position;
```

**Conversion Logic:**
1. Group results by column
2. Build `cards` object: `{ [card.id]: { id, title, details } }`
3. Build `columns` array with `cardIds` ordered by `card.position`
4. Return `{ columns, cards }`

### JSON to Database Conversion

**On Board Update:**
1. Parse incoming `BoardData` JSON
2. Update `columns` table: Set `title` for each column
3. Update `cards` table:
   - For each column, iterate `cardIds` array
   - Update each card's `column_id` and `position` (index in array)
   - Update card `title` and `details` if changed
4. Handle card additions/deletions
5. Update board `updated_at` timestamp

## Migration Strategy

### Initial Database Creation

On first application startup:

1. Check if database file exists (`data/pm.db`)
2. If not, create database and run schema creation
3. Create default user (username: "user", password: "password")
4. Create default board for user with 5 columns
5. Optionally seed with sample cards

### Schema Creation SQL

```sql
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);

-- Boards table
CREATE TABLE boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_boards_user_id ON boards(user_id);

-- Columns table
CREATE TABLE columns (
    id TEXT PRIMARY KEY,
    board_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    position INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE,
    UNIQUE (board_id, position)
);

CREATE INDEX idx_columns_board_id ON columns(board_id);
CREATE INDEX idx_columns_board_position ON columns(board_id, position);

-- Cards table
CREATE TABLE cards (
    id TEXT PRIMARY KEY,
    column_id TEXT NOT NULL,
    title TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    position INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (column_id) REFERENCES columns(id) ON DELETE CASCADE,
    UNIQUE (column_id, position)
);

CREATE INDEX idx_cards_column_id ON cards(column_id);
CREATE INDEX idx_cards_column_position ON cards(column_id, position);

-- Trigger to update board.updated_at when cards change
CREATE TRIGGER update_board_timestamp_on_card_change
AFTER UPDATE ON cards
BEGIN
    UPDATE boards 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = (SELECT board_id FROM columns WHERE id = NEW.column_id);
END;

-- Trigger to update board.updated_at when columns change
CREATE TRIGGER update_board_timestamp_on_column_change
AFTER UPDATE ON columns
BEGIN
    UPDATE boards 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.board_id;
END;
```

### Default Data Seeding

```sql
-- Insert default user (password hash for "password")
INSERT INTO users (username, password_hash) 
VALUES ('user', '$2b$12$...');  -- bcrypt hash

-- Insert default board
INSERT INTO boards (user_id, title) 
VALUES (1, 'My Kanban Board');

-- Insert 5 default columns
INSERT INTO columns (id, board_id, title, position) VALUES
    ('col-backlog', 1, 'Backlog', 0),
    ('col-discovery', 1, 'Discovery', 1),
    ('col-progress', 1, 'In Progress', 2),
    ('col-review', 1, 'Review', 3),
    ('col-done', 1, 'Done', 4);

-- Optionally insert sample cards (matching frontend initialData)
INSERT INTO cards (id, column_id, title, details, position) VALUES
    ('card-1', 'col-backlog', 'Align roadmap themes', 'Draft quarterly themes with impact statements and metrics.', 0),
    ('card-2', 'col-backlog', 'Gather customer signals', 'Review support tags, sales notes, and churn feedback.', 1),
    -- ... etc
```

## Database File Location

- **Path**: `data/pm.db`
- **Docker Volume**: Mounted to persist data across container restarts
- **Backup**: Copy `data/pm.db` file (future: automated backups)

## Performance Considerations

### Indexes

All foreign keys and frequently queried columns are indexed:
- User lookups by username (login)
- Board lookups by user_id
- Column lookups by board_id
- Card lookups by column_id
- Ordered retrieval by position

### Query Optimization

- Use single query with JOIN to fetch entire board (avoid N+1)
- Batch updates for card position changes
- Use transactions for multi-table updates
- Prepared statements for all queries

### Scalability Notes

For MVP (single user, single board):
- Expected data: 1 user, 1 board, 5 columns, ~50 cards
- All queries will be fast with proper indexes
- No need for query optimization or caching

For future (multi-user, multi-board):
- Add pagination for large boards
- Consider caching board data in Redis
- Add database connection pooling
- Monitor query performance with EXPLAIN

## Data Integrity

### Constraints

- Foreign keys enforced with `PRAGMA foreign_keys = ON`
- Cascade deletes prevent orphaned records
- Unique constraints on positions prevent duplicates
- NOT NULL constraints on required fields

### Validation

Application-level validation:
- Username format and uniqueness
- Password strength requirements
- Card title length limits
- Position values are sequential (0, 1, 2, ...)

### Transactions

All multi-table operations wrapped in transactions:
- Board updates (columns + cards)
- Card moves (update position for multiple cards)
- User creation (user + board + columns)

## Future Enhancements

Schema is designed to support:

1. **Multiple boards per user**
   - Remove application-level one-board limit
   - Add board selection UI

2. **Board sharing/collaboration**
   - Add `board_members` table
   - Add permission levels (owner, editor, viewer)

3. **Card attachments**
   - Add `attachments` table
   - Store file metadata, link to cards

4. **Activity history**
   - Add `activity_log` table
   - Track all board changes for audit trail

5. **Custom fields**
   - Add `custom_fields` table
   - Allow users to add metadata to cards

6. **Tags/labels**
   - Add `tags` and `card_tags` tables
   - Support filtering and categorization

7. **Due dates and priorities**
   - Add columns to `cards` table
   - Support sorting and filtering

## Testing Strategy

### Unit Tests

- Test CRUD operations for each table
- Test foreign key constraints
- Test unique constraints
- Test cascade deletes
- Test triggers (updated_at)

### Integration Tests

- Test full board creation flow
- Test board JSON serialization/deserialization
- Test concurrent updates
- Test transaction rollbacks on error

### Data Validation Tests

- Test invalid foreign keys rejected
- Test duplicate positions rejected
- Test NULL values rejected where required
- Test data type constraints

## Conclusion

This schema provides a solid foundation for the MVP while remaining extensible for future features. The design prioritizes simplicity and data integrity, with clear relationships and proper constraints.