from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache
def get_service_client() -> Client:
    """Service-role Supabase client. Bypasses RLS — backend-only, never exposed to the frontend."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not configured")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
