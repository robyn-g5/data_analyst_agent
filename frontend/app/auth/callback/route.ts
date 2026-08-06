import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabaseServer";

// Handles both the invite-email link and password-reset links. Supabase
// verifies the token server-side and redirects here with a `code` to
// exchange for a session; from there we always land on set-password so a
// freshly invited teammate can choose their own credentials.
export async function GET(request: NextRequest) {
  const { searchParams, origin } = request.nextUrl;
  const code = searchParams.get("code");

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      return NextResponse.redirect(`${origin}/auth/set-password`);
    }
  }

  return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`);
}
