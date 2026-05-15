"use client";

import { useEffect, useMemo, useState } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { KanbanColumn } from "@/components/KanbanColumn";
import { KanbanCardPreview } from "@/components/KanbanCardPreview";
import { moveCard as moveCardLocal, type BoardData } from "@/lib/kanban";
import * as api from "@/lib/api";

export const KanbanBoard = () => {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [activeCardId, setActiveCardId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    })
  );

  // Load board data on mount
  useEffect(() => {
    const loadBoard = async () => {
      try {
        setLoading(true);
        const data = await api.fetchBoard();
        setBoard(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load board");
      } finally {
        setLoading(false);
      }
    };

    loadBoard();
  }, []);

  const cardsById = useMemo(() => board?.cards || {}, [board?.cards]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveCardId(event.active.id as string);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCardId(null);

    if (!over || active.id === over.id || !board) {
      return;
    }

    const activeId = active.id as string;
    const overId = over.id as string;

    // Optimistic update
    const newColumns = moveCardLocal(board.columns, activeId, overId);
    const previousBoard = board;
    setBoard({ ...board, columns: newColumns });

    try {
      // Find the new column and position
      const newColumnId = newColumns.find((col) =>
        col.cardIds.includes(activeId)
      )?.id;
      const newPosition = newColumns
        .find((col) => col.id === newColumnId)
        ?.cardIds.indexOf(activeId);

      if (newColumnId && newPosition !== undefined) {
        await api.moveCard(activeId, newColumnId, newPosition);
      }
    } catch (err) {
      // Rollback on error
      setBoard(previousBoard);
      setError(err instanceof Error ? err.message : "Failed to move card");
    }
  };

  const handleRenameColumn = async (columnId: string, title: string) => {
    if (!board) return;

    // Optimistic update
    const previousBoard = board;
    setBoard({
      ...board,
      columns: board.columns.map((column) =>
        column.id === columnId ? { ...column, title } : column
      ),
    });

    try {
      await api.renameColumn(columnId, title);
    } catch (err) {
      // Rollback on error
      setBoard(previousBoard);
      setError(err instanceof Error ? err.message : "Failed to rename column");
    }
  };

  const handleAddCard = async (
    columnId: string,
    title: string,
    details: string
  ) => {
    if (!board) return;

    try {
      const newCard = await api.addCard(columnId, title, details);

      // Update board with new card
      setBoard({
        ...board,
        cards: {
          ...board.cards,
          [newCard.id]: newCard,
        },
        columns: board.columns.map((column) =>
          column.id === columnId
            ? { ...column, cardIds: [...column.cardIds, newCard.id] }
            : column
        ),
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add card");
    }
  };

  const handleDeleteCard = async (columnId: string, cardId: string) => {
    if (!board) return;

    // Optimistic update
    const previousBoard = board;
    setBoard({
      ...board,
      cards: Object.fromEntries(
        Object.entries(board.cards).filter(([id]) => id !== cardId)
      ),
      columns: board.columns.map((column) =>
        column.id === columnId
          ? {
              ...column,
              cardIds: column.cardIds.filter((id) => id !== cardId),
            }
          : column
      ),
    });

    try {
      await api.deleteCard(cardId);
    } catch (err) {
      // Rollback on error
      setBoard(previousBoard);
      setError(err instanceof Error ? err.message : "Failed to delete card");
    }
  };

  const activeCard = activeCardId ? cardsById[activeCardId] : null;

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-[var(--gray-text)]">Loading board...</div>
      </div>
    );
  }

  if (error && !board) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="rounded-xl border border-red-200 bg-red-50 px-6 py-4 text-red-600">
          {error}
        </div>
      </div>
    );
  }

  if (!board) {
    return null;
  }

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <main className="relative mx-auto flex min-h-screen max-w-[1500px] flex-col gap-10 px-6 pb-16 pt-12">
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-6 py-4 text-sm text-red-600">
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-4 font-semibold underline"
            >
              Dismiss
            </button>
          </div>
        )}
        <header className="flex flex-col gap-6 rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
                Single Board Kanban
              </p>
              <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
                Kanban Studio
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--gray-text)]">
                Keep momentum visible. Rename columns, drag cards between stages,
                and capture quick notes without getting buried in settings.
              </p>
            </div>
            <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-5 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
                Focus
              </p>
              <p className="mt-2 text-lg font-semibold text-[var(--primary-blue)]">
                One board. Five columns. Zero clutter.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            {board.columns.map((column) => (
              <div
                key={column.id}
                className="flex items-center gap-2 rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)]"
              >
                <span className="h-2 w-2 rounded-full bg-[var(--accent-yellow)]" />
                {column.title}
              </div>
            ))}
          </div>
        </header>

        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <section className="grid gap-6 lg:grid-cols-5">
            {board.columns.map((column) => (
              <KanbanColumn
                key={column.id}
                column={column}
                cards={column.cardIds.map((cardId) => board.cards[cardId])}
                onRename={handleRenameColumn}
                onAddCard={handleAddCard}
                onDeleteCard={handleDeleteCard}
              />
            ))}
          </section>
          <DragOverlay>
            {activeCard ? (
              <div className="w-[260px]">
                <KanbanCardPreview card={activeCard} />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </main>
    </div>
  );
};
