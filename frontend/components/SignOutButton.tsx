"use client";

import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabaseClient";

export function SignOutButton() {
  const router = useRouter();

  async function handleSignOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.replace("/login");
    router.refresh();
  }

  return (
    <button
      onClick={handleSignOut}
      className="rounded-md px-2.5 py-1.5 text-xs font-medium text-neutral-500 transition hover:bg-neutral-100 hover:text-neutral-900"
    >
      Sign out
    </button>
  );
}
