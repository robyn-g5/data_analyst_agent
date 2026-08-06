from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import PIPELINE_CONFIG_EXAMPLE, PIPELINE_SCRIPTS_DIR, get_settings
from app.db import repository as db
from app.services import storage

if str(PIPELINE_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_SCRIPTS_DIR))

import analyze_data  # noqa: E402  (reused as-is from reusable_analytics_workflow/scripts)
import build_dashboard  # noqa: E402
import validate_data  # noqa: E402
from common import json_ready  # noqa: E402


def _run_dir(run_id: str) -> Path:
    return get_settings().pipeline_workspace_dir / run_id


def _stage_input_files(run_id: str, input_dir: Path) -> None:
    input_dir.mkdir(parents=True, exist_ok=True)
    attachments = db.list_attachments_for_run(run_id)
    for attachment in attachments:
        content = storage.download_bytes(storage.uploads_bucket(), attachment["storage_path"])
        (input_dir / attachment["original_filename"]).write_bytes(content)


def _stub_config() -> dict:
    """Phase B stand-in for Claude column mapping (Phase C): every run reuses
    the example config as-is. Sample data already matches its column names
    and file-role glob patterns, so this proves the rest of the pipeline
    end-to-end without the mapping intelligence yet.
    """
    return json.loads(PIPELINE_CONFIG_EXAMPLE.read_text())


def _missing_role_from_error(message: str) -> str | None:
    if "found 0" not in message:
        return None
    # message looks like: "Expected one file for role 'paid_media' using '*paid_media*.csv', found 0"
    marker = "role '"
    start = message.find(marker)
    if start == -1:
        return None
    start += len(marker)
    end = message.find("'", start)
    return message[start:end] if end != -1 else None


def process_run(run_id: str) -> None:
    run_dir = _run_dir(run_id)
    input_dir = run_dir / "input"
    outputs_dir = run_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    try:
        db.update_run(run_id, status="mapping_columns", step="Mapping columns")
        config = _stub_config()
        _stage_input_files(run_id, input_dir)

        db.update_run(run_id, status="validating", step="Validating data", config=config)
        try:
            validation_report, _cleaned = validate_data.validate(config, input_dir)
        except ValueError as exc:
            missing_role = _missing_role_from_error(str(exc))
            if missing_role:
                db.update_run(run_id, status="pending", step=None)
                db.insert_chat_message(
                    author_id=None,
                    role="assistant",
                    content=f"Got some files, but I still need the **{missing_role}** CSV before I can run the analysis.",
                    run_id=run_id,
                )
                return
            raise

        (outputs_dir / "validation_report.json").write_text(json.dumps(json_ready(validation_report), indent=2))

        if validation_report["status"] == "review_required":
            storage.upload_file(
                storage.outputs_bucket(),
                f"{run_id}/validation_report.json",
                outputs_dir / "validation_report.json",
                "application/json",
            )
            db.update_run(
                run_id,
                status="failed",
                step=None,
                error_message="Data validation found issues that need review before this can be analyzed.",
                validation_report_path=f"{run_id}/validation_report.json",
            )
            db.insert_chat_message(
                author_id=None,
                role="assistant",
                content="This run needs review before I can analyze it — see the validation report for details on the dashboard tab.",
                run_id=run_id,
            )
            return

        db.update_run(run_id, status="analyzing", step="Analyzing metrics")
        results, _validation = analyze_data.analyze(config, input_dir)

        db.update_run(run_id, status="building_dashboard", step="Building dashboard")
        report = build_dashboard.build_report(results)
        html = build_dashboard.build_html(results, report)

        (outputs_dir / "analysis_results.json").write_text(json.dumps(json_ready(results), indent=2))
        (outputs_dir / "executive_report.md").write_text(report)
        (outputs_dir / "executive_dashboard.html").write_text(html)
        (outputs_dir / "analysis_config.json").write_text(json.dumps(config, indent=2))

        for filename, content_type in [
            ("validation_report.json", "application/json"),
            ("analysis_results.json", "application/json"),
            ("executive_report.md", "text/markdown"),
            ("executive_dashboard.html", "text/html"),
            ("analysis_config.json", "application/json"),
        ]:
            storage.upload_file(storage.outputs_bucket(), f"{run_id}/{filename}", outputs_dir / filename, content_type)

        db.update_run(
            run_id,
            status="complete",
            step="Complete",
            completed_at=datetime.now(timezone.utc).isoformat(),
            validation_report_path=f"{run_id}/validation_report.json",
            analysis_results_path=f"{run_id}/analysis_results.json",
            report_md_path=f"{run_id}/executive_report.md",
            dashboard_html_path=f"{run_id}/executive_dashboard.html",
            config_path=f"{run_id}/analysis_config.json",
        )
        db.insert_chat_message(
            author_id=None,
            role="assistant",
            content="Your dashboard is ready — see the new tab on the left.",
            run_id=run_id,
        )
    except Exception as exc:  # noqa: BLE001 — surfaced to the user via chat + run status
        db.update_run(run_id, status="failed", step=None, error_message=str(exc))
        db.insert_chat_message(
            author_id=None,
            role="assistant",
            content=f"This run failed: {exc}",
            run_id=run_id,
        )
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)
