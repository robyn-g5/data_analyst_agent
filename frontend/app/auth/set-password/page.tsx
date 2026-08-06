"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabaseClient";

export default function SetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    const supabase = createClient();
    const { error: updateError } = await supabase.auth.updateUser({ password });
    setLoading(false);
    if (updateError) {
      setError(updateError.message);
      return;
    }
    router.replace("/workspace");
    router.refresh();
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-neutral-50 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-xl font-semibold text-neutral-900">Set your password</h1>
          <p className="mt-1 text-sm text-neutral-500">
            Choose a password to finish setting up your account.
          </p>
        </div>
        <form
          onSubmit={handleSubmit}
          className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm"
        >
          <div className="space-y-4">
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-neutral-700">
                New password
              </label>
              <input
                id="password"
                type="password"
                required
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 text-sm text-neutral-900 outline-none focus:border-neutral-500 focus:ring-1 focus:ring-neutral-500"
              />
            </div>
            <div>
              <label htmlFor="confirm" className="block text-sm font-medium text-neutral-700">
                Confirm password
              </label>
              <input
                id="confirm"
                type="password"
                required
                autoComplete="new-password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 text-sm text-neutral-900 outline-none focus:border-neutral-500 focus:ring-1 focus:ring-neutral-500"
              />
            </div>
          </div>
          {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="mt-6 w-full rounded-md bg-neutral-900 px-3 py-2 text-sm font-medium text-white transition hover:bg-neutral-700 disabled:opacity-50"
          >
            {loading ? "Saving…" : "Save password"}
          </button>
        </form>
      </div>
    </main>
  );
}
