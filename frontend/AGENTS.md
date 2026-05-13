# Frontend Architecture Documentation

## Overview
NextJS 16.1.6 application with React 19.2.3, implementing a Kanban board with drag-and-drop functionality. Pure frontend demo with local state management.

## Tech Stack
- **Framework**: Next.js 16.1.6 (App Router)
- **UI Library**: React 19.2.3
- **Styling**: Tailwind CSS 4
- **Drag & Drop**: @dnd-kit/core 6.3.1
- **Testing**: Vitest 3.2.4 (unit), Playwright 1.58.0 (e2e)
- **Type Safety**: TypeScript 5

## Project Structure

### Core Components
- `KanbanBoard.tsx` - Main container managing board state and drag-and-drop context
- `KanbanColumn.tsx` - Column component with droppable area and card list
- `KanbanCard.tsx` - Draggable card with title, details, and delete action
- `KanbanCardPreview.tsx` - Drag overlay preview
- `NewCardForm.tsx` - Inline form for adding new cards

### Business Logic
- `lib/kanban.ts` - Core data types, initial data, and card movement logic

### Data Model
```typescript
Card: { id: string, title: string, details: string }
Column: { id: string, title: string, cardIds: string[] }
BoardData: { columns: Column[], cards: Record<string, Card> }
```

## State Management
Local React state in KanbanBoard component. No external state library. Board data structure separates cards (by ID) from columns (with card ID arrays) for efficient drag operations.

## Key Features
1. **Drag & Drop**: @dnd-kit with pointer sensor, 6px activation distance
2. **Column Renaming**: Inline editable column titles
3. **Card CRUD**: Add cards via inline form, delete with remove button
4. **Card Movement**: Drag cards within/between columns with visual feedback
5. **Responsive Layout**: 5-column grid on large screens

## Styling Approach
Tailwind CSS with custom CSS variables for color scheme:
- `--accent-yellow`: #ecad0a
- `--primary-blue`: #209dd7
- `--secondary-purple`: #753991
- `--navy-dark`: #032147
- `--gray-text`: #888888

Glassmorphism effects with backdrop-blur and gradient overlays.

## Testing Strategy
- **Unit Tests**: Vitest with @testing-library/react for component logic
- **E2E Tests**: Playwright for user workflows
- **Coverage**: Tests exist for KanbanBoard and kanban utility functions

## Build & Dev
- `npm run dev` - Development server
- `npm run build` - Production build (static export ready)
- `npm run test:unit` - Run Vitest tests
- `npm run test:e2e` - Run Playwright tests
- `npm run test:all` - Run all tests

## Current Limitations
- No backend integration (pure frontend demo)
- No persistence (state resets on refresh)
- No authentication
- Single board only
- No AI features

## Integration Points for Backend
When integrating with FastAPI backend:
1. Replace local state with API calls for board data
2. Add authentication context/hooks
3. Implement optimistic updates for drag operations
4. Add WebSocket or polling for real-time AI updates
5. Move card operations to API endpoints