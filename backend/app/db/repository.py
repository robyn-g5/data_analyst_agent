from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.supabase_client import get_service_client


def _client():
    return get_service_client()


# --- chat messages -----------------------------------------------------

def insert_chat_message(
    *, author_id: str | None, role: str, content: str, run_id: str | None = None
) -> dict[str, Any]:
    row = {"author_id": author_id, "role": role, "content": content, "run_id": run_id}
    resp = _client().table("chat_messages").insert(row).execute()
    return resp.data[0]


def list_chat_messages(since_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    query = (
        _client()
        .table("chat_messages")
        .select("*, chat_attachments(*)")
        .order("created_at", desc=False)
        .limit(limit)
    )
    if since_id:
        since_row = _client().table("chat_messages").select("created_at").eq("id", since_id).execute()
        if since_row.data:
            query = query.gt("created_at", since_row.data[0]["created_at"])
    resp = query.execute()
    return resp.data


def update_chat_message(message_id: str, **fields: Any) -> None:
    _client().table("chat_messages").update(fields).eq("id", message_id).execute()


# --- chat attachments ----------------------------------------------------

def insert_chat_attachment(
    *,
    message_id: str,
    run_id: str | None,
    original_filename: str,
    storage_path: str,
    size_bytes: int | None,
    role_guess: str | None = None,
) -> dict[str, Any]:
    row = {
        "message_id": message_id,
        "run_id": run_id,
        "original_filename": original_filename,
        "storage_path": storage_path,
        "size_bytes": size_bytes,
        "role_guess": role_guess,
    }
    resp = _client().table("chat_attachments").insert(row).execute()
    return resp.data[0]


def list_attachments_for_run(run_id: str) -> list[dict[str, Any]]:
    resp = _client().table("chat_attachments").select("*").eq("run_id", run_id).execute()
    return resp.data


# --- runs ------------------------------------------------------------

def create_run(*, created_by: str | None) -> dict[str, Any]:
    resp = _client().table("runs").insert({"created_by": created_by}).execute()
    return resp.data[0]


def get_run(run_id: str) -> dict[str, Any] | None:
    resp = _client().table("runs").select("*").eq("id", run_id).execute()
    return resp.data[0] if resp.data else None


def list_runs() -> list[dict[str, Any]]:
    resp = _client().table("runs").select("*").order("run_date", desc=True).order("created_at", desc=True).execute()
    return resp.data


def update_run(run_id: str, **fields: Any) -> None:
    fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    _client().table("runs").update(fields).eq("id", run_id).execute()


def find_accumulating_run(window_minutes: int = 30) -> dict[str, Any] | None:
    """A run still in 'pending' created recently enough that new attachments
    should join it instead of starting a new tab."""
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=window_minutes)).isoformat()
    resp = (
        _client()
        .table("runs")
        .select("*")
        .eq("status", "pending")
        .gte("created_at", cutoff)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None
