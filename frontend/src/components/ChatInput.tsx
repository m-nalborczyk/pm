import type { FC, FormEvent } from "react";
import { useState } from "react";

type ChatInputProps = {
  onSend: (message: string) => void;
  disabled?: boolean;
};

export const ChatInput: FC<ChatInputProps> = ({ onSend, disabled = false }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setInput("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={disabled}
        placeholder="Ask AI to help with your board..."
        className="flex-1 rounded-xl border border-[var(--stroke)] bg-white/80 px-4 py-3 text-sm text-[var(--navy-dark)] placeholder-[var(--gray-text)] backdrop-blur transition focus:border-[var(--primary-blue)] focus:outline-none disabled:opacity-50"
        data-testid="chat-input"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="rounded-xl bg-[var(--secondary-purple)] px-6 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
        data-testid="chat-send-button"
      >
        Send
      </button>
    </form>
  );
};

// Made with Bob
