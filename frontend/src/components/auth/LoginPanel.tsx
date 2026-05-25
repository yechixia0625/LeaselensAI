"use client";

import { useState } from "react";
import { AuthService, isUnauthorizedError } from "@/services/authService";

interface LoginPanelProps {
  onSuccess: () => void;
}

export function LoginPanel({ onSuccess }: LoginPanelProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);

    try {
      const session = await AuthService.login(username.trim(), password);
      if (!session.authenticated) {
        setError("Login failed.");
        return;
      }
      onSuccess();
    } catch (err) {
      if (isUnauthorizedError(err)) {
        setError("Invalid username or password.");
      } else {
        setError("Login is temporarily unavailable.");
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="w-full max-w-md space-y-6 rounded-lg border border-zinc-800 bg-zinc-950/80 p-6 shadow-2xl">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-bold tracking-tight">
          Lease<span className="text-zinc-500">Lens</span>
        </h1>
        <p className="font-mono text-xs tracking-[0.18em] text-zinc-500">
          PUBLIC TEST ACCESS
        </p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <label className="block space-y-2">
          <span className="font-mono text-xs text-zinc-500">USERNAME</span>
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="w-full rounded border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm focus:border-zinc-600 focus:outline-none"
            autoComplete="username"
          />
        </label>
        <label className="block space-y-2">
          <span className="font-mono text-xs text-zinc-500">PASSWORD</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm focus:border-zinc-600 focus:outline-none"
            autoComplete="current-password"
          />
        </label>
        {error && <p className="font-mono text-xs text-red-400">{error}</p>}
        <button
          type="submit"
          disabled={pending || username.trim() === "" || password === ""}
          className="w-full rounded border border-zinc-700 py-2 font-mono text-xs tracking-[0.18em] text-zinc-100 hover:border-lime-300 disabled:opacity-50"
        >
          {pending ? "AUTHENTICATING..." : "ENTER"}
        </button>
      </form>
    </section>
  );
}
