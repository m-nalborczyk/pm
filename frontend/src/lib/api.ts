import type { BoardData, Card } from "./kanban";

const API_BASE = "/api";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    if (response.status === 401) {
      // Use setTimeout to avoid blocking the current execution
      setTimeout(() => {
        window.location.href = "/login";
      }, 0);
      throw new ApiError("Unauthorized", 401);
    }

    let detail = "Request failed";
    try {
      const data = await response.json();
      detail = data.detail || data.message || detail;
    } catch {
      // Ignore JSON parse errors
    }

    throw new ApiError(
      `API Error: ${response.status}`,
      response.status,
      detail
    );
  }

  return response.json();
}

export async function fetchBoard(): Promise<BoardData> {
  const response = await fetch(`${API_BASE}/board`, {
    credentials: "include",
  });
  return handleResponse<BoardData>(response);
}

export async function updateBoard(board: BoardData): Promise<BoardData> {
  const response = await fetch(`${API_BASE}/board`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(board),
  });
  return handleResponse<BoardData>(response);
}

export async function renameColumn(
  columnId: string,
  title: string
): Promise<{ id: string; title: string }> {
  const response = await fetch(`${API_BASE}/board/columns/${columnId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ title }),
  });
  return handleResponse(response);
}

export async function addCard(
  columnId: string,
  title: string,
  details: string = ""
): Promise<Card> {
  const response = await fetch(
    `${API_BASE}/board/cards?column_id=${columnId}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ title, details }),
    }
  );
  return handleResponse<Card>(response);
}

export async function deleteCard(cardId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/board/cards/${cardId}`, {
    method: "DELETE",
    credentials: "include",
  });
  await handleResponse(response);
}

export async function moveCard(
  cardId: string,
  columnId: string,
  position: number
): Promise<Card> {
  const response = await fetch(`${API_BASE}/board/cards/${cardId}/move`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ columnId, position }),
  });
  return handleResponse<Card>(response);
}

export type AiChatResponse = {
  message: string;
  board_updates: Array<{
    operation: string;
    card_id?: string;
    column_id?: string;
  }>;
  board: BoardData;
};

export async function sendChatMessage(
  message: string
): Promise<AiChatResponse> {
  const response = await fetch(`${API_BASE}/ai/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ message }),
  });
  return handleResponse<AiChatResponse>(response);
}

// Made with Bob
