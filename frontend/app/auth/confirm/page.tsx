"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabaseClient";

// Both invite links and magic-link sign-ins land here. Supabase puts the
// session in the URL fragment (#access_token=...), which browsers never
// send to the server — so this has to run client-side to read it and
// explicitly establish the session before we can go anywhere protected.
export default function AuthConfirmPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const hash = window.location.hash;
    const params = new URLSearchParams(hash.startsWith("#") ? hash.slice(1) : hash);
    const access_token = params.get("access_token");
    const refresh_token = params.get("refresh_token");

    if (!access_token || !refresh_token) {
      setError("This link is invalid or has expired.");
      return;
    }

    const supabase = createClient();
    supabase.auth.setSession({ access_token, refresh_token }).then(({ error: sessionError }) => {
      if (sessionError) {
        setError("This link is invalid or has expired.");
        return;
      }
      router.replace("/workspace");
      router.refresh();
    });
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-neutral-50 px-4">
      <div className="w-full max-w-sm text-center">
        {error ? (
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
            {error} Ask a teammate to send a fresh sign-in link, then open it directly from the
            email without editing it.
          </div>
        ) : (
          <p className="text-sm text-neutral-500">Signing you in…</p>
        )}
      </div>
    </main>
  );
}
