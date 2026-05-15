"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch("/api/auth/me", {
          credentials: "include",
        });

        if (response.ok) {
          // User is authenticated, go to board
          window.location.href = "/board";
        } else {
          // Not authenticated, go to login
          window.location.href = "/login";
        }
      } catch (error) {
        // Error checking auth, go to login
        window.location.href = "/login";
      } finally {
        setChecking(false);
      }
    };

    checkAuth();
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-[var(--gray-text)]">
        {checking ? "Loading..." : "Redirecting..."}
      </div>
    </div>
  );
}
