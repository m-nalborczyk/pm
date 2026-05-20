import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatMessage, type Message } from "./ChatMessage";

describe("ChatMessage", () => {
  it("renders user message correctly", () => {
    const message: Message = {
      id: "msg-1",
      role: "user",
      content: "Hello AI",
      timestamp: new Date("2024-01-01T12:00:00"),
    };

    render(<ChatMessage message={message} />);

    expect(screen.getByText("Hello AI")).toBeInTheDocument();
    expect(screen.getByTestId("chat-message-user")).toBeInTheDocument();
  });

  it("renders assistant message correctly", () => {
    const message: Message = {
      id: "msg-2",
      role: "assistant",
      content: "Hello! How can I help?",
      timestamp: new Date("2024-01-01T12:00:00"),
    };

    render(<ChatMessage message={message} />);

    expect(screen.getByText("Hello! How can I help?")).toBeInTheDocument();
    expect(screen.getByTestId("chat-message-assistant")).toBeInTheDocument();
  });

  it("displays timestamp", () => {
    const message: Message = {
      id: "msg-3",
      role: "user",
      content: "Test",
      timestamp: new Date("2024-01-01T12:30:00"),
    };

    render(<ChatMessage message={message} />);

    expect(screen.getByText(/12:30/)).toBeInTheDocument();
  });

  it("handles multiline content", () => {
    const message: Message = {
      id: "msg-4",
      role: "assistant",
      content: "Line 1\nLine 2\nLine 3",
      timestamp: new Date(),
    };

    render(<ChatMessage message={message} />);

    const element = screen.getByText((content, element) => {
      return element?.textContent === "Line 1\nLine 2\nLine 3";
    });
    expect(element).toBeInTheDocument();
  });
});

// Made with Bob
