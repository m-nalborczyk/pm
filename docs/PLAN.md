# Project Management MVP - Detailed Implementation Plan

## Docker Architecture Decision
**Approach**: Single multi-stage Dockerfile with both frontend and backend.
**Rationale**: Simpler for MVP, easier local development, Rancher-ready (can split into microservices later). Backend serves static frontend at /, reducing complexity.

## Success Criteria Format
Each part includes:
- **Functional Tests**: Specific user actions that must work
- **Technical Tests**: Unit/integration test requirements (80% coverage minimum)
- **Acceptance**: Clear pass/fail criteria

---

## Part 1: Planning ✓

### Objective
Create detailed implementation plan with substeps, tests, and success criteria for all 10 parts.

### Tasks
- [x] Review AGENTS.md and existing frontend code
- [x] Document frontend architecture in frontend/AGENTS.md
- [x] Decide on Docker architecture (single container)
- [x] Define success criteria format
- [x] Expand all 10 parts with detailed substeps

### Success Criteria
- [x] frontend/AGENTS.md created documenting current code
- [x] All 10 parts have detailed substeps with checkboxes
- [x] Each part has clear functional and technical tests
- [x] User approves plan before Part 2

---

## Part 2: Scaffolding

### Objective
Set up Docker infrastructure, FastAPI backend skeleton, and start/stop scripts. Verify with "hello world" example serving static HTML and making an API call.

### Tasks
- [ ] Create backend directory structure
  - [ ] `backend/main.py` - FastAPI app entry point
  - [ ] `backend/requirements.txt` - Python dependencies
  - [ ] `backend/pyproject.toml` - uv configuration
- [ ] Create Dockerfile (multi-stage)
  - [ ] Stage 1: Build frontend (Node.js)
  - [ ] Stage 2: Python runtime with uv
  - [ ] Copy built frontend to backend static directory
  - [ ] Expose port 8000
- [ ] Create docker-compose.yml
  - [ ] Mount .env file
  - [ ] Volume for SQLite database persistence
  - [ ] Port mapping 8000:8000
- [ ] Create start/stop scripts
  - [ ] `scripts/start.sh` (Mac/Linux)
  - [ ] `scripts/start.ps1` (Windows)
  - [ ] `scripts/stop.sh` (Mac/Linux)
  - [ ] `scripts/stop.ps1` (Windows)
- [ ] Implement FastAPI hello world
  - [ ] GET / - Serve static HTML "Hello World"
  - [ ] GET /api/health - Return {"status": "ok"}
- [ ] Write backend tests
  - [ ] Test health endpoint returns 200
  - [ ] Test root serves HTML

### Functional Tests
1. Run start script → container starts without errors
2. Visit http://localhost:8000 → see "Hello World" HTML
3. Visit http://localhost:8000/api/health → see {"status": "ok"}
4. Run stop script → container stops cleanly

### Technical Tests
- pytest test for /api/health endpoint
- pytest test for root HTML response
- Scripts work on Windows, Mac, Linux

### Success Criteria
- Docker container builds successfully
- FastAPI serves static HTML at /
- API endpoint /api/health responds with JSON
- Start/stop scripts work on all platforms
- All tests pass with 80%+ coverage

---

## Part 3: Add in Frontend

### Objective
Build and serve the NextJS frontend statically from FastAPI, displaying the Kanban board at /. Add comprehensive tests.

### Tasks
- [ ] Update Dockerfile
  - [ ] Add frontend build stage with npm install and build
  - [ ] Copy frontend/out to backend/static
- [ ] Update FastAPI to serve static files
  - [ ] Mount StaticFiles at /
  - [ ] Serve index.html for root and SPA routes
- [ ] Update frontend for static export
  - [ ] Add `output: 'export'` to next.config.ts
  - [ ] Verify no dynamic features that break static export
- [ ] Write integration tests
  - [ ] Test / serves Kanban board HTML
  - [ ] Test static assets load (CSS, JS)
  - [ ] Test Kanban board renders correctly
- [ ] Update frontend e2e tests
  - [ ] Test drag and drop works
  - [ ] Test add card works
  - [ ] Test delete card works
  - [ ] Test rename column works

### Functional Tests
1. Visit http://localhost:8000 → see full Kanban board
2. Drag card between columns → card moves
3. Add new card → card appears in column
4. Delete card → card removed
5. Rename column → column title updates

### Technical Tests
- Backend test: GET / returns 200 with HTML
- Backend test: Static assets accessible
- Frontend e2e: All Kanban operations work
- Unit tests: All existing frontend tests pass

### Success Criteria
- Frontend builds and exports successfully
- FastAPI serves complete Kanban app at /
- All drag-and-drop functionality works
- All frontend unit tests pass
- All e2e tests pass
- 80%+ test coverage maintained

---

## Part 4: Add Fake User Sign In

### Objective
Add authentication flow: login page at /, Kanban at /board after login with hardcoded credentials (user/password), logout functionality.

### Tasks
- [ ] Create login page component
  - [ ] `frontend/src/app/login/page.tsx`
  - [ ] Form with username and password fields
  - [ ] Submit button styled per color scheme
  - [ ] Error message display
- [ ] Add authentication state management
  - [ ] Create auth context or simple state
  - [ ] Store auth token in sessionStorage
- [ ] Update routing
  - [ ] / → login page (if not authenticated)
  - [ ] /board → Kanban board (if authenticated)
  - [ ] Redirect to login if accessing /board unauthenticated
- [ ] Add backend auth endpoints
  - [ ] POST /api/auth/login - Validate credentials, return token
  - [ ] POST /api/auth/logout - Clear session
  - [ ] GET /api/auth/me - Verify token
- [ ] Add logout button to Kanban header
- [ ] Write auth tests
  - [ ] Backend: Test login with correct credentials
  - [ ] Backend: Test login with wrong credentials
  - [ ] Backend: Test logout
  - [ ] Frontend: Test login flow
  - [ ] Frontend: Test logout flow
  - [ ] Frontend: Test protected route redirect

### Functional Tests
1. Visit / → see login page
2. Enter wrong credentials → see error message
3. Enter "user"/"password" → redirect to /board with Kanban
4. Refresh page → still authenticated, see Kanban
5. Click logout → redirect to login page
6. Try to access /board directly → redirect to login

### Technical Tests
- Backend: POST /api/auth/login returns token for valid credentials
- Backend: POST /api/auth/login returns 401 for invalid credentials
- Backend: GET /api/auth/me validates token
- Frontend: Login form validation works
- Frontend: Auth state persists across page refresh
- E2E: Complete login/logout flow

### Success Criteria
- Login page displays at /
- Hardcoded credentials (user/password) work
- Invalid credentials show error
- Successful login redirects to /board
- Logout returns to login page
- Protected routes redirect unauthenticated users
- All tests pass with 80%+ coverage

---

## Part 5: Database Modeling

### Objective
Design SQLite database schema for users, boards, columns, and cards. Document approach and get user approval.

### Tasks
- [ ] Design database schema
  - [ ] Users table (id, username, password_hash, created_at)
  - [ ] Boards table (id, user_id, title, created_at, updated_at)
  - [ ] Columns table (id, board_id, title, position, created_at)
  - [ ] Cards table (id, column_id, title, details, position, created_at, updated_at)
- [ ] Create schema documentation
  - [ ] `docs/DATABASE.md` with ERD and table definitions
  - [ ] Document relationships and constraints
  - [ ] Document indexes for performance
- [ ] Define JSON serialization format
  - [ ] Board JSON structure matching frontend BoardData type
  - [ ] Conversion functions between DB and JSON
- [ ] Create migration approach
  - [ ] SQLite schema creation script
  - [ ] Database initialization on first run

### Documentation Requirements
- ERD diagram (text-based or ASCII)
- Table definitions with column types and constraints
- Relationship descriptions
- JSON format examples
- Migration strategy

### Success Criteria
- Complete schema documented in docs/DATABASE.md
- Schema supports all MVP features
- Schema extensible for multi-user future
- JSON format matches frontend types
- User approves schema before implementation

---

## Part 6: Backend Database Integration

### Objective
Implement database layer with SQLAlchemy, create API routes for CRUD operations on Kanban boards, comprehensive backend tests.

### Tasks
- [ ] Set up SQLAlchemy
  - [ ] `backend/database.py` - Database connection and session
  - [ ] `backend/models.py` - SQLAlchemy models
  - [ ] Create database on startup if not exists
- [ ] Implement database operations
  - [ ] `backend/crud.py` - CRUD functions
  - [ ] Get board for user
  - [ ] Update board (columns and cards)
  - [ ] Create default board for new user
- [ ] Create API routes
  - [ ] GET /api/board - Get user's board as JSON
  - [ ] PUT /api/board - Update entire board
  - [ ] PATCH /api/board/columns/{id} - Rename column
  - [ ] POST /api/board/cards - Add card
  - [ ] DELETE /api/board/cards/{id} - Delete card
  - [ ] PATCH /api/board/cards/{id}/move - Move card
- [ ] Add authentication middleware
  - [ ] Verify token on protected routes
  - [ ] Extract user_id from token
- [ ] Write comprehensive backend tests
  - [ ] Test database initialization
  - [ ] Test CRUD operations
  - [ ] Test API endpoints with authentication
  - [ ] Test error cases (invalid data, unauthorized)
  - [ ] Test concurrent updates

### Functional Tests
1. Start fresh → database created automatically
2. Login → default board created for user
3. GET /api/board → returns board JSON
4. Update board via API → changes persisted
5. Restart server → board data still present

### Technical Tests
- Unit tests for all CRUD functions (80%+ coverage)
- Integration tests for all API endpoints
- Test authentication on protected routes
- Test database constraints and validations
- Test JSON serialization/deserialization
- Test error handling and edge cases

### Success Criteria
- SQLite database created on first run
- All API routes functional and tested
- Authentication required for board operations
- Board data persists across restarts
- All tests pass with 80%+ coverage
- No data loss or corruption

---

## Part 7: Frontend + Backend Integration

### Objective
Connect frontend to backend API, replace local state with API calls, implement optimistic updates, thorough integration testing.

### Tasks
- [ ] Create API client
  - [ ] `frontend/src/lib/api.ts` - API functions
  - [ ] fetchBoard(), updateBoard(), addCard(), deleteCard(), moveCard()
  - [ ] Include authentication token in requests
- [ ] Update KanbanBoard component
  - [ ] Load board from API on mount
  - [ ] Replace local state updates with API calls
  - [ ] Implement optimistic updates for drag operations
  - [ ] Handle loading and error states
- [ ] Update authentication flow
  - [ ] Store token from login response
  - [ ] Include token in API requests
  - [ ] Handle 401 responses (redirect to login)
- [ ] Add error handling
  - [ ] Display error messages to user
  - [ ] Retry logic for failed requests
  - [ ] Rollback optimistic updates on error
- [ ] Write integration tests
  - [ ] Test full user flow: login → view board → modify → persist
  - [ ] Test optimistic updates
  - [ ] Test error handling
  - [ ] Test concurrent user actions
- [ ] Update e2e tests
  - [ ] Test with real backend
  - [ ] Test persistence across page refresh
  - [ ] Test authentication flow

### Functional Tests
1. Login → see board loaded from database
2. Add card → card saved to database
3. Drag card → move persisted immediately
4. Refresh page → all changes still present
5. Delete card → card removed from database
6. Rename column → change persisted
7. Logout and login → see same board state

### Technical Tests
- Frontend: API client functions work correctly
- Frontend: Optimistic updates work
- Frontend: Error handling works
- Integration: Full CRUD operations persist
- Integration: Authentication flow works end-to-end
- E2E: All user workflows work with backend

### Success Criteria
- Frontend successfully communicates with backend
- All Kanban operations persist to database
- Optimistic updates provide instant feedback
- Errors handled gracefully with user feedback
- Page refresh maintains board state
- All tests pass with 80%+ coverage
- No race conditions or data inconsistencies

---

## Part 8: AI Connectivity

### Objective
Implement OpenRouter API integration in backend, test with simple "2+2" query to verify connectivity.

### Tasks
- [ ] Create AI service module
  - [ ] `backend/ai_service.py` - OpenRouter client
  - [ ] Load OPENROUTER_API_KEY from environment
  - [ ] Configure model: openai/gpt-oss-120b:free
- [ ] Implement basic AI call function
  - [ ] Function to send prompt and get response
  - [ ] Handle API errors and timeouts
  - [ ] Log requests and responses
- [ ] Create test endpoint
  - [ ] GET /api/ai/test - Send "What is 2+2?" to AI
  - [ ] Return AI response
- [ ] Write AI service tests
  - [ ] Test successful API call
  - [ ] Test error handling
  - [ ] Test timeout handling
  - [ ] Mock OpenRouter for unit tests

### Functional Tests
1. Call /api/ai/test → receive response about 2+2
2. Verify response is from AI (not hardcoded)
3. Check logs show API request/response

### Technical Tests
- Unit test: AI service sends correct request format
- Unit test: AI service handles errors gracefully
- Integration test: Real API call to OpenRouter works
- Test: API key loaded from environment

### Success Criteria
- OpenRouter API key loaded correctly
- AI service successfully calls OpenRouter
- Test endpoint returns AI response
- Error handling works for API failures
- All tests pass with 80%+ coverage
- API calls logged for debugging

---

## Part 9: AI Kanban Integration

### Objective
Extend AI to receive board JSON and user question, return structured output with response and optional board updates. Implement conversation history.

### Tasks
- [ ] Define structured output schema
  - [ ] Response message to user
  - [ ] Optional board updates (add/edit/move/delete cards)
  - [ ] JSON schema for OpenRouter structured outputs
- [ ] Implement conversation history
  - [ ] Store in database (conversations table)
  - [ ] Link to user and board
  - [ ] Include in AI context
- [ ] Update AI service
  - [ ] Build prompt with board JSON and history
  - [ ] Request structured output from AI
  - [ ] Parse and validate AI response
- [ ] Create AI chat endpoint
  - [ ] POST /api/ai/chat - Send message, get response
  - [ ] Include current board state
  - [ ] Include conversation history
  - [ ] Return AI response and board updates
- [ ] Implement board update logic
  - [ ] Apply AI-suggested changes to board
  - [ ] Validate changes before applying
  - [ ] Return updated board to frontend
- [ ] Write comprehensive tests
  - [ ] Test AI understands board structure
  - [ ] Test AI can create cards
  - [ ] Test AI can edit cards
  - [ ] Test AI can move cards
  - [ ] Test AI can delete cards
  - [ ] Test conversation history maintained
  - [ ] Test invalid AI responses handled

### Functional Tests
1. Ask AI "Add a card called 'Test' to Backlog" → card created
2. Ask AI "Move 'Test' to In Progress" → card moved
3. Ask AI "What cards are in Review?" → AI lists cards
4. Ask AI "Delete the 'Test' card" → card deleted
5. Ask follow-up question → AI remembers context

### Technical Tests
- Unit test: Structured output schema validation
- Unit test: Board update logic for each operation
- Integration test: AI creates cards correctly
- Integration test: AI moves cards correctly
- Integration test: AI edits cards correctly
- Integration test: AI deletes cards correctly
- Integration test: Conversation history works
- Test: Invalid AI responses rejected

### Success Criteria
- AI receives board JSON in every request
- AI returns structured output with response and updates
- AI can perform all CRUD operations on cards
- Conversation history maintained per user
- Invalid AI responses handled gracefully
- All tests pass with 80%+ coverage
- AI responses are contextually relevant

---

## Part 10: AI Chat UI

### Objective
Add beautiful sidebar chat widget to UI, support full conversation with AI, automatically refresh Kanban when AI updates board.

### Tasks
- [ ] Create chat UI components
  - [ ] `frontend/src/components/ChatSidebar.tsx` - Main sidebar
  - [ ] `frontend/src/components/ChatMessage.tsx` - Message bubble
  - [ ] `frontend/src/components/ChatInput.tsx` - Input field
- [ ] Implement chat state management
  - [ ] Store messages in component state
  - [ ] Handle loading states
  - [ ] Handle errors
- [ ] Add sidebar toggle
  - [ ] Button in Kanban header to open/close chat
  - [ ] Smooth slide-in animation
  - [ ] Responsive design
- [ ] Implement chat functionality
  - [ ] Send message to /api/ai/chat
  - [ ] Display AI response
  - [ ] Show loading indicator while waiting
  - [ ] Auto-scroll to latest message
- [ ] Implement board auto-refresh
  - [ ] Detect when AI returns board updates
  - [ ] Refresh board state automatically
  - [ ] Show notification of changes
  - [ ] Smooth transition for updates
- [ ] Style per color scheme
  - [ ] Use project colors
  - [ ] Match Kanban design language
  - [ ] Glassmorphism effects
- [ ] Write UI tests
  - [ ] Test chat opens/closes
  - [ ] Test message sending
  - [ ] Test message display
  - [ ] Test board refresh on AI update
  - [ ] Test error states
- [ ] Write e2e tests
  - [ ] Test full AI conversation flow
  - [ ] Test AI creating cards via chat
  - [ ] Test AI moving cards via chat
  - [ ] Test board updates automatically

### Functional Tests
1. Click chat button → sidebar slides in
2. Type message and send → message appears in chat
3. AI responds → response appears in chat
4. Ask AI to add card → card appears on board automatically
5. Ask AI to move card → card moves on board automatically
6. Close sidebar → sidebar slides out
7. Reopen sidebar → conversation history preserved

### Technical Tests
- Unit test: Chat components render correctly
- Unit test: Message sending works
- Unit test: Board refresh logic works
- Integration test: Chat API integration
- E2E test: Full conversation with board updates
- E2E test: Multiple AI operations in sequence
- Test: Error handling in chat

### Success Criteria
- Chat sidebar displays beautifully
- Sidebar matches project design language
- Messages send and display correctly
- AI responses appear in chat
- Board updates automatically when AI makes changes
- Visual feedback for board changes
- Conversation history maintained
- All tests pass with 80%+ coverage
- Smooth animations and transitions
- Responsive on different screen sizes

---

## Testing Standards (All Parts)

### Unit Test Requirements
- Minimum 80% code coverage
- Test all business logic functions
- Test error cases and edge cases
- Mock external dependencies
- Fast execution (< 1 second per test)

### Integration Test Requirements
- Test API endpoints end-to-end
- Test database operations
- Test authentication flow
- Test external service integration (OpenRouter)
- Use test database, not production

### E2E Test Requirements
- Test complete user workflows
- Test across different browsers (Playwright)
- Test responsive design
- Test error scenarios
- Run against Docker container

### Test Documentation
- Clear test descriptions
- Document test data setup
- Document expected outcomes
- Include failure debugging tips

---

## Deployment Checklist (Post-MVP)

- [ ] Environment variables documented
- [ ] Database backup strategy
- [ ] Logging configured
- [ ] Error monitoring setup
- [ ] Performance benchmarks established
- [ ] Security review completed
- [ ] Documentation complete
- [ ] User guide created