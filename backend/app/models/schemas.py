from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

RunStatus = Literal[
    "pending",
    "awaiting_clarification",
    "validating",
    "mapping_columns",
    "analyzing",
    "generating_narrative",
    "building_dashboard",
    "complete",
    "failed",
]

ChatRole = Literal["user", "assistant", "system"]


class ChatAttachmentOut(BaseModel):
    id: str
    original_filename: str
    size_bytes: int | None = None


class ChatMessageOut(BaseModel):
    id: str
    author_id: str | None
    role: ChatRole
    content: str
    run_id: str | None
    created_at: datetime
    attachments: list[ChatAttachmentOut] = []


class ChatMessagesResponse(BaseModel):
    messages: list[ChatMessageOut]


class RunSummaryOut(BaseModel):
    id: str
    status: RunStatus
    step: str | None
    run_date: str
    created_at: datetime
    completed_at: datetime | None
    error_message: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "RunSummaryOut":
        return cls(
            id=row["id"],
            status=row["status"],
            step=row.get("step"),
            run_date=row["run_date"],
            created_at=row["created_at"],
            completed_at=row.get("completed_at"),
            error_message=row.get("error_message"),
        )


class RunsResponse(BaseModel):
    runs: list[RunSummaryOut]


class RunDetailOut(RunSummaryOut):
    dashboard_html_url: str | None = None
    report_md_url: str | None = None
    analysis_results_url: str | None = None
    validation_report_url: str | None = None
    config: dict[str, Any] | None = None


class ChatMessagePostResponse(BaseModel):
    message: ChatMessageOut
    run: RunSummaryOut | None = None


class ClarifyRequest(BaseModel):
    answer: str
