import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ChatInput } from "./ChatInput";

describe("ChatInput", () => {
  it("renders input field and send button", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    expect(screen.getByTestId("chat-input")).toBeInTheDocument();
    expect(screen.getByTestId("chat-send-button")).toBeInTheDocument();
  });

  it("calls onSend with trimmed message on submit", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByTestId("chat-input");
    const button = screen.getByTestId("chat-send-button");

    fireEvent.change(input, { target: { value: "  Hello AI  " } });
    fireEvent.click(button);

    expect(onSend).toHaveBeenCalledWith("Hello AI");
  });

  it("clears input after sending", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByTestId("chat-input") as HTMLInputElement;

    fireEvent.change(input, { target: { value: "Test message" } });
    fireEvent.click(screen.getByTestId("chat-send-button"));

    expect(input.value).toBe("");
  });

  it("does not send empty or whitespace-only messages", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByTestId("chat-input");
    const button = screen.getByTestId("chat-send-button");

    fireEvent.change(input, { target: { value: "   " } });
    fireEvent.click(button);

    expect(onSend).not.toHaveBeenCalled();
  });

  it("disables input and button when disabled prop is true", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} disabled={true} />);

    const input = screen.getByTestId("chat-input") as HTMLInputElement;
    const button = screen.getByTestId("chat-send-button") as HTMLButtonElement;

    expect(input.disabled).toBe(true);
    expect(button.disabled).toBe(true);
  });

  it("submits on Enter key press", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByTestId("chat-input");

    fireEvent.change(input, { target: { value: "Test" } });
    fireEvent.submit(input.closest("form")!);

    expect(onSend).toHaveBeenCalledWith("Test");
  });

  it("disables send button when input is empty", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const button = screen.getByTestId("chat-send-button") as HTMLButtonElement;

    expect(button.disabled).toBe(true);
  });

  it("enables send button when input has text", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByTestId("chat-input");
    const button = screen.getByTestId("chat-send-button") as HTMLButtonElement;

    fireEvent.change(input, { target: { value: "Test" } });

    expect(button.disabled).toBe(false);
  });
});

// Made with Bob
