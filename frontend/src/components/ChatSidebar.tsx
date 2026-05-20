import type { FC } from "react";
import { useEffect, useRef, useState } from "react";
import { ChatMessage, type Message } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import * as api from "@/lib/api";

type ChatSidebarProps = {
  isOpen: boolean;
  onClose: () => void;
  onBoardUpdate: () => void;
};

export const ChatSidebar: FC<ChatSidebarProps> = ({
  isOpen,
  onClose,
  onBoardUpdate,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: `msg-${Date.now()}-user`,
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await api.sendChatMessage(content);

      const aiMessage: Message = {
        id: `msg-${Date.now()}-ai`,
        role: "assistant",
        content: response.message,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);

      if (response.board_updates && response.board_updates.length > 0) {
        onBoardUpdate();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className={`fixed inset-0 z-40 bg-black/10 transition-opacity ${
          isOpen ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onClose}
        data-testid="chat-backdrop"
      />

      {/* Sidebar */}
      <div
        className={`fixed right-0 top-0 z-50 flex h-full w-full max-w-md transform flex-col border-l border-[var(--stroke)] bg-white shadow-2xl transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
        data-testid="chat-sidebar"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[var(--stroke)] bg-gradient-to-r from-[var(--primary-blue)] to-[var(--secondary-purple)] px-6 py-4">
          <div>
            <h2 className="text-lg font-semibold text-white">AI Assistant</h2>
            <p className="text-xs text-white/80">
              Ask me to help manage your board
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-white/80 transition hover:bg-white/10 hover:text-white"
            data-testid="chat-close-button"
            aria-label="Close chat"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-[var(--surface)] p-6">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="mb-4 rounded-full bg-gradient-to-br from-[var(--primary-blue)] to-[var(--secondary-purple)] p-4">
                <svg
                  className="h-8 w-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
              </div>
              <p className="text-sm font-semibold text-[var(--navy-dark)]">
                Start a conversation
              </p>
              <p className="mt-2 max-w-xs text-xs text-[var(--gray-text)]">
                I can help you add, move, edit, or delete cards on your board.
                Just ask!
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="rounded-2xl border border-[var(--stroke)] bg-white/80 px-4 py-3 backdrop-blur">
                    <div className="flex gap-1">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--gray-text)]" />
                      <span
                        className="h-2 w-2 animate-bounce rounded-full bg-[var(--gray-text)]"
                        style={{ animationDelay: "0.1s" }}
                      />
                      <span
                        className="h-2 w-2 animate-bounce rounded-full bg-[var(--gray-text)]"
                        style={{ animationDelay: "0.2s" }}
                      />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="border-t border-red-200 bg-red-50 px-6 py-3">
            <p className="text-sm text-red-600">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-1 text-xs font-semibold text-red-700 underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Input */}
        <div className="border-t border-[var(--stroke)] bg-white p-6">
          <ChatInput onSend={handleSendMessage} disabled={loading} />
        </div>
      </div>
    </>
  );
};

// Made with Bob
