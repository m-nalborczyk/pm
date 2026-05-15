"use client";

import { useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";

export default function BoardPage() {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch("/api/auth/me", {
          credentials: "include",
        });

        if (response.ok) {
          setAuthenticated(true);
        } else {
          window.location.href = "/login";
        }
      } catch (error) {
        window.location.href = "/login";
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogout = async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
      window.location.href = "/login";
    } catch (error) {
      console.error("Logout failed:", error);
      window.location.href = "/login";
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-[var(--gray-text)]">Loading...</div>
      </div>
    );
  }

  if (!authenticated) {
    return null;
  }

  return (
    <div className="relative">
      <div className="absolute right-6 top-6 z-10">
        <button
          onClick={handleLogout}
          className="rounded-full border border-[var(--stroke)] bg-white/80 px-6 py-2 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] backdrop-blur transition hover:text-[var(--navy-dark)]"
        >
          Log Out
        </button>
      </div>
      <KanbanBoard />
    </div>
  );
}

// Made with Bob
