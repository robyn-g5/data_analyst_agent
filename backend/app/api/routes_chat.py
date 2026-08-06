from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile

from app.db import repository as db
from app.models.schemas import ChatMessageOut, ChatMessagePostResponse, ChatMessagesResponse, RunSummaryOut
from app.services import pipeline_runner, run_manager

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _to_message_out(row: dict) -> ChatMessageOut:
    attachments = row.get("chat_attachments") or []
    return ChatMessageOut(
        id=row["id"],
        author_id=row["author_id"],
        role=row["role"],
        content=row["content"],
        run_id=row.get("run_id"),
        created_at=row["created_at"],
        attachments=[
            {"id": a["id"], "original_filename": a["original_filename"], "size_bytes": a.get("size_bytes")}
            for a in attachments
        ],
    )


@router.post("/messages", response_model=ChatMessagePostResponse)
async def post_message(
    background_tasks: BackgroundTasks,
    content: str = Form(""),
    files: list[UploadFile] = File(default=[]),
) -> ChatMessagePostResponse:
    file_payloads = [(f.filename, await f.read()) for f in files if f.filename]
    message_row, run_row = run_manager.handle_incoming_message(
        author_id=None, content=content, files=file_payloads
    )
    if run_row is not None:
        background_tasks.add_task(pipeline_runner.process_run, run_row["id"])
    return ChatMessagePostResponse(
        message=_to_message_out(message_row),
        run=RunSummaryOut.from_row(run_row) if run_row else None,
    )


@router.get("/messages", response_model=ChatMessagesResponse)
def list_messages(since: str | None = None, limit: int = 50) -> ChatMessagesResponse:
    rows = db.list_chat_messages(since_id=since, limit=limit)
    return ChatMessagesResponse(messages=[_to_message_out(r) for r in rows])


@router.delete("/messages", status_code=204)
def clear_messages() -> None:
    db.delete_all_chat_messages()
