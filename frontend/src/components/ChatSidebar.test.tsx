import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ChatSidebar } from "./ChatSidebar";
import * as api from "@/lib/api";

vi.mock("@/lib/api");

describe("ChatSidebar", () => {
  const mockOnClose = vi.fn();
  const mockOnBoardUpdate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders when open", () => {
    render(
      <ChatSidebar
        isOpen={true}
        onClose={mockOnClose}
        onBoardUpdate={mockOnBoardUpdate}
      />
    );

    expect(screen.getByTestId("chat-sidebar")).toBeInTheDocument();
    expect(screen.getByText("AI Assistant")).toBeInTheDocument();
  });

  it("does not render when closed", () => {
    render(
      <ChatSidebar
        isOpen={false}
        onClose={mockOnClose}
        onBoardUpdate={mockOnBoardUpdate}
      />
    );

    const sidebar = screen.getByTestId("chat-sidebar");
    expect(sidebar).toHaveClass("translate-x-full");
  });

  it("shows empty state when no messages", () => {
    render(
      <ChatSidebar
        isOpen={true}
        onClose={mockOnClose}
        onBoardUpdate={mockOnBoardUpdate}
      />
    );

    expect(screen.getByText("Start a conversation")).toBeInTheDocument();
  });

  it("calls onClose when close button clicked", () => {
    render(
      <ChatSidebar
        isOpen={true}
        onClose={mockOnClose}
        onBoardUpdate={mockOnBoardUpdate}
      />
    );

    fireEvent.click(screen.getByTestId("chat-close-button"));
    expect(mockOnClose).toHaveBeenCalled();
  });

  it("calls onClose when backdrop clicked", () => {
    render(
      <ChatSidebar
        isOpen={true}
        onClose={mockOnClose}
        onBoardUpdate={mockOnBoardUpdate}
      />
    );

    fireEvent.click(screen.getByTestId("chat-backdrop"));
    expect(mockOnClose).toHaveBeenCalled();
  });

  it("sends message and displays response", async () => {
    const mockResponse = {
      message: "I can help you with that!",
      board_updates: [],
      board: { columns: [], cards: {} },
    };

    vi.mocked(api.sendChatMessage).mockResolvedValue(mockResponse);

    render(
      <ChatSidebar
        isOpen={true}
        onClose={mockOnClose}
        onBoardUpdate={mockOnBoardUpdate}
      />
    );

    const input = screen.getByTestId("chat-input");
    const sendButton = screen.getByTestId("chat-send-button");

    fireEvent.change(input, { target: { value: "Hello AI" } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText("Hello AI")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(
        screen.getByText("I can help you with that!")
      ).toBeInTheDocument();
    });

    expect(api.sendChatMessage).toHaveBeenCalledWith("Hello AI");
  });

  it("calls onBoardUpdate when board is updated", async () => {
    const mockResponse = {
      message: "Card added successfully!",
      board_updates: [{ operation: "add_card", card_id: "card-123" }],
      board: { columns: [], cards: {} },
    };

    vi.mocked(api.sendChatMessage).mockResolvedValue(mockResponse);

    render(
      <ChatSidebar
        isOpen={true}
        onClose={mockOnClose}
        onBoardUpdate={mockOnBoardUpdate}
      />
    );

    const input = screen.getByTestId("chat-input");
    const sendButton = screen.getByTestId("chat-send-button");

    fireEvent.change(input, { target: { value: "Add a card" } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockOnBoardUpdate).toHaveBeenCalled();
    });
  });

  it("displays error message on API failure", async () => {
    vi.mocked(api.sendChatMessage).mockRejectedValue(
      new Error("Network error")
    );

    render(
      <ChatSidebar
        isOpen={true}
        onClose={mockOnClose}
        onBoardUpdate={mockOnBoardUpdate}
      />
    );

    const input = screen.getByTestId("chat-input");
    const sendButton = screen.getByTestId("chat-send-button");

    fireEvent.change(input, { target: { value: "Test" } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Network error/)).toBeInTheDocument();
    });
  });

  it("shows loading state while sending message", async () => {
    vi.mocked(api.sendChatMessage).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(
      <ChatSidebar
        isOpen={true}
        onClose={mockOnClose}
        onBoardUpdate={mockOnBoardUpdate}
      />
    );

    const input = screen.getByTestId("chat-input");
    const sendButton = screen.getByTestId("chat-send-button");

    fireEvent.change(input, { target: { value: "Test" } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      const button = screen.getByTestId(
        "chat-send-button"
      ) as HTMLButtonElement;
      expect(button.disabled).toBe(true);
    });
  });

  it("dismisses error message", async () => {
    vi.mocked(api.sendChatMessage).mockRejectedValue(
      new Error("Test error")
    );

    render(
      <ChatSidebar
        isOpen={true}
        onClose={mockOnClose}
        onBoardUpdate={mockOnBoardUpdate}
      />
    );

    const input = screen.getByTestId("chat-input");
    const sendButton = screen.getByTestId("chat-send-button");

    fireEvent.change(input, { target: { value: "Test" } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Test error/)).toBeInTheDocument();
    });

    const dismissButton = screen.getByText("Dismiss");
    fireEvent.click(dismissButton);

    await waitFor(() => {
      expect(screen.queryByText(/Test error/)).not.toBeInTheDocument();
    });
  });
});

// Made with Bob
