from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.core.retry import retry_on_disconnect
from app.core.supabase_client import get_service_client

SIGNED_URL_EXPIRES_IN = 300  # seconds


@retry_on_disconnect
def upload_bytes(bucket: str, path: str, content: bytes, content_type: str = "application/octet-stream") -> None:
    client = get_service_client()
    client.storage.from_(bucket).upload(
        path, content, file_options={"content-type": content_type, "upsert": "true"}
    )


def upload_file(bucket: str, path: str, local_path: Path, content_type: str = "application/octet-stream") -> None:
    upload_bytes(bucket, path, local_path.read_bytes(), content_type)


@retry_on_disconnect
def download_bytes(bucket: str, path: str) -> bytes:
    client = get_service_client()
    return client.storage.from_(bucket).download(path)


@retry_on_disconnect
def remove_objects(bucket: str, paths: list[str]) -> None:
    if not paths:
        return
    client = get_service_client()
    client.storage.from_(bucket).remove(paths)


@retry_on_disconnect
def signed_url(bucket: str, path: str, expires_in: int = SIGNED_URL_EXPIRES_IN) -> str:
    client = get_service_client()
    result = client.storage.from_(bucket).create_signed_url(path, expires_in)
    return result["signedURL"] if "signedURL" in result else result["signed_url"]


def uploads_bucket() -> str:
    return get_settings().supabase_storage_uploads_bucket


def outputs_bucket() -> str:
    return get_settings().supabase_storage_outputs_bucket
