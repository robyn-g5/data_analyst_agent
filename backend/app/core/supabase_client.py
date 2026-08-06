from __future__ import annotations

from supabase import Client, create_client

from app.core.config import get_settings


def get_service_client() -> Client:
    """Service-role Supabase client. Bypasses RLS — backend-only, never exposed to the frontend.

    Deliberately not cached/reused across calls: supabase-py doesn't expose
    httpx connection-pool tuning (e.g. keepalive expiry), and a long-lived
    pooled connection that goes idle can be silently closed server-side,
    causing the next request to fail with httpx.RemoteProtocolError("Server
    disconnected"). Creating a fresh client per call avoids ever reusing a
    stale connection — at our traffic level the extra connection setup cost
    is negligible.
    """
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not configured")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
