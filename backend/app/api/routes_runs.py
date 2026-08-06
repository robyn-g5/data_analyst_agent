from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import RedirectResponse

from app.core.security import CurrentUser, verify_token
from app.db import repository as db
from app.models.schemas import ClarifyRequest, RunDetailOut, RunSummaryOut, RunsResponse
from app.services import pipeline_runner, storage

router = APIRouter(prefix="/api/runs", tags=["runs"])

FileKey = Literal["validation_report", "analysis_results", "report_md", "dashboard_html", "config"]

_FILE_KEY_TO_COLUMN = {
    "validation_report": "validation_report_path",
    "analysis_results": "analysis_results_path",
    "report_md": "report_md_path",
    "dashboard_html": "dashboard_html_path",
    "config": "config_path",
}


def _signed_or_none(path: str | None) -> str | None:
    if not path:
        return None
    return storage.signed_url(storage.outputs_bucket(), path)


def _to_run_detail(row: dict) -> RunDetailOut:
    return RunDetailOut(
        **RunSummaryOut.from_row(row).model_dump(),
        dashboard_html_url=_signed_or_none(row.get("dashboard_html_path")),
        report_md_url=_signed_or_none(row.get("report_md_path")),
        analysis_results_url=_signed_or_none(row.get("analysis_results_path")),
        validation_report_url=_signed_or_none(row.get("validation_report_path")),
        config=row.get("config"),
    )


@router.get("", response_model=RunsResponse)
def list_runs(user: CurrentUser = Depends(verify_token)) -> RunsResponse:
    return RunsResponse(runs=[RunSummaryOut.from_row(r) for r in db.list_runs()])


@router.get("/{run_id}", response_model=RunDetailOut)
def get_run(run_id: str, user: CurrentUser = Depends(verify_token)) -> RunDetailOut:
    row = db.get_run(run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    return _to_run_detail(row)


@router.get("/{run_id}/status", response_model=RunSummaryOut)
def get_run_status(run_id: str, user: CurrentUser = Depends(verify_token)) -> RunSummaryOut:
    row = db.get_run(run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunSummaryOut.from_row(row)


@router.get("/{run_id}/files/{file_key}")
def get_run_file(run_id: str, file_key: FileKey, user: CurrentUser = Depends(verify_token)) -> RedirectResponse:
    row = db.get_run(run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    column = _FILE_KEY_TO_COLUMN[file_key]
    path = row.get(column)
    if not path:
        raise HTTPException(status_code=404, detail="File not available for this run")
    return RedirectResponse(storage.signed_url(storage.outputs_bucket(), path))


@router.post("/{run_id}/clarify", response_model=RunSummaryOut)
def clarify_run(
    run_id: str,
    body: ClarifyRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(verify_token),
) -> RunSummaryOut:
    row = db.get_run(run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    if row["status"] != "awaiting_clarification":
        raise HTTPException(status_code=409, detail="This run isn't waiting on clarification")
    db.insert_chat_message(author_id=user.id, role="user", content=body.answer, run_id=run_id)
    db.update_run(run_id, status="pending", step=None)
    background_tasks.add_task(pipeline_runner.process_run, run_id)
    return RunSummaryOut.from_row(db.get_run(run_id))
