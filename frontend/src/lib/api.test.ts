import { describe, it, expect, beforeEach, vi } from "vitest";
import * as api from "./api";

// Mock fetch globally
global.fetch = vi.fn();

describe("API Client", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset window.location
    delete (window as any).location;
    (window as any).location = { href: "" };
  });

  describe("fetchBoard", () => {
    it("fetches board data successfully", async () => {
      const mockBoard = {
        columns: [{ id: "col-1", title: "Backlog", cardIds: [] }],
        cards: {},
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBoard,
      });

      const result = await api.fetchBoard();
      expect(result).toEqual(mockBoard);
      expect(global.fetch).toHaveBeenCalledWith("/api/board", {
        credentials: "include",
      });
    });

    it("redirects to login on 401", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: "Unauthorized" }),
      });

      await expect(api.fetchBoard()).rejects.toThrow("Unauthorized");
      expect(window.location.href).toBe("/login");
    });

    it("throws error on other failures", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: "Server error" }),
      });

      await expect(api.fetchBoard()).rejects.toThrow("API Error: 500");
    });
  });

  describe("updateBoard", () => {
    it("updates board successfully", async () => {
      const mockBoard = {
        columns: [{ id: "col-1", title: "Updated", cardIds: [] }],
        cards: {},
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBoard,
      });

      const result = await api.updateBoard(mockBoard);
      expect(result).toEqual(mockBoard);
      expect(global.fetch).toHaveBeenCalledWith("/api/board", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(mockBoard),
      });
    });
  });

  describe("renameColumn", () => {
    it("renames column successfully", async () => {
      const mockResponse = { id: "col-1", title: "New Name" };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await api.renameColumn("col-1", "New Name");
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith("/api/board/columns/col-1", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ title: "New Name" }),
      });
    });
  });

  describe("addCard", () => {
    it("adds card successfully", async () => {
      const mockCard = {
        id: "card-1",
        title: "New Card",
        details: "Details",
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCard,
      });

      const result = await api.addCard("col-1", "New Card", "Details");
      expect(result).toEqual(mockCard);
      expect(global.fetch).toHaveBeenCalledWith(
        "/api/board/cards?column_id=col-1",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ title: "New Card", details: "Details" }),
        }
      );
    });

    it("adds card with empty details", async () => {
      const mockCard = {
        id: "card-1",
        title: "New Card",
        details: "",
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCard,
      });

      const result = await api.addCard("col-1", "New Card");
      expect(result).toEqual(mockCard);
    });
  });

  describe("deleteCard", () => {
    it("deletes card successfully", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: "Card deleted" }),
      });

      await api.deleteCard("card-1");
      expect(global.fetch).toHaveBeenCalledWith("/api/board/cards/card-1", {
        method: "DELETE",
        credentials: "include",
      });
    });

    it("throws error when card not found", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: "Card not found" }),
      });

      await expect(api.deleteCard("card-1")).rejects.toThrow("API Error: 404");
    });
  });

  describe("moveCard", () => {
    it("moves card successfully", async () => {
      const mockResponse = {
        id: "card-1",
        columnId: "col-2",
        position: 1,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await api.moveCard("card-1", "col-2", 1);
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith("/api/board/cards/card-1/move", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ columnId: "col-2", position: 1 }),
      });
    });
  });

  describe("Error handling", () => {
    it("handles network errors", async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error("Network error"));

      await expect(api.fetchBoard()).rejects.toThrow("Network error");
    });

    it("handles JSON parse errors in error responses", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error("Invalid JSON");
        },
      });

      await expect(api.fetchBoard()).rejects.toThrow("API Error: 500");
    });
  });
});

// Made with Bob
