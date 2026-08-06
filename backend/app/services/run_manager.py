from __future__ import annotations

from typing import Any

from app.db import repository as db
from app.services import storage


def handle_incoming_message(
    *, author_id: str | None, content: str, files: list[tuple[str, bytes]]
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Persists a chat message (+ any attachments), attaching it to an
    accumulating run if one exists, or creating a new one. Returns
    (message_row, run_row_or_None) — run is set only when this message
    touched a run (i.e. it had file attachments).
    """
    message = db.insert_chat_message(author_id=author_id, role="user", content=content, run_id=None)

    if not files:
        return message, None

    run = db.find_accumulating_run() or db.create_run(created_by=author_id)

    for filename, content_bytes in files:
        storage_path = f"{message['id']}/{filename}"
        storage.upload_bytes(storage.uploads_bucket(), storage_path, content_bytes, "text/csv")
        db.insert_chat_attachment(
            message_id=message["id"],
            run_id=run["id"],
            original_filename=filename,
            storage_path=storage_path,
            size_bytes=len(content_bytes),
        )

    db.update_chat_message(message["id"], run_id=run["id"])
    message["run_id"] = run["id"]

    return message, run
