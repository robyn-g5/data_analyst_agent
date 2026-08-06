"use client";

import { useState, type FormEvent } from "react";
import { createClient } from "@/lib/supabaseClient";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    const supabase = createClient();
    const { error: otpError } = await supabase.auth.signInWithOtp({
      email,
      options: {
        shouldCreateUser: false,
        emailRedirectTo: `${window.location.origin}/auth/confirm`,
      },
    });
    setLoading(false);
    if (otpError) {
      setError(otpError.message);
      return;
    }
    setSent(true);
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-neutral-50 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-xl font-semibold text-neutral-900">Executive Analytics</h1>
          <p className="mt-1 text-sm text-neutral-500">Sign in to your team workspace</p>
        </div>

        {sent ? (
          <div className="rounded-xl border border-neutral-200 bg-white p-6 text-center shadow-sm">
            <p className="text-sm text-neutral-700">
              Check <span className="font-medium">{email}</span> for a sign-in link.
            </p>
            <p className="mt-2 text-xs text-neutral-400">
              It'll open right into your workspace — no password needed.
            </p>
          </div>
        ) : (
          <form
            onSubmit={handleSubmit}
            className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm"
          >
            <label htmlFor="email" className="block text-sm font-medium text-neutral-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 text-sm text-neutral-900 outline-none focus:border-neutral-500 focus:ring-1 focus:ring-neutral-500"
            />
            {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="mt-6 w-full rounded-md bg-neutral-900 px-3 py-2 text-sm font-medium text-white transition hover:bg-neutral-700 disabled:opacity-50"
            >
              {loading ? "Sending…" : "Send sign-in link"}
            </button>
          </form>
        )}

        <p className="mt-6 text-center text-xs text-neutral-400">
          Access is invite-only. Ask a teammate to invite your email if you don&apos;t have an
          account yet.
        </p>
      </div>
    </main>
  );
}
