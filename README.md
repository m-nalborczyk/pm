# Project Management MVP

Kanban board with AI chat integration.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Running the Application

**Windows:**
```powershell
.\scripts\start.ps1
```

**Mac/Linux:**
```bash
chmod +x scripts/start.sh scripts/stop.sh
./scripts/start.sh
```

Visit http://localhost:8000

### Stopping the Application

**Windows:**
```powershell
.\scripts\stop.ps1
```

**Mac/Linux:**
```bash
./scripts/stop.sh
```

## Development

### Backend Tests
```bash
cd backend
pytest --cov=. --cov-report=term-missing
```

### Frontend Tests
```bash
cd frontend
npm run test:all
```

## Tech Stack
- Frontend: Next.js 16, React 19, Tailwind CSS
- Backend: Python FastAPI with uv
- Database: SQLite
- AI: OpenRouter (openai/gpt-oss-120b:free)
- Container: Docker

## Project Structure
```
pm/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── scripts/          # Start/stop scripts
├── docs/             # Documentation
└── data/             # SQLite database (created on first run)