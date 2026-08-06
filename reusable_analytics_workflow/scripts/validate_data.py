from __future__ import annotations

import argparse
from pathlib import Path

from common import business_measure_columns, deduplicate, load_config, read_sources, write_json


def validate(config: dict, input_dir: str | Path) -> tuple[dict, dict]:
    frames, files = read_sources(config, input_dir)
    c = config["columns"]
    report = {"status": "usable", "datasets": {}, "joinability": {}, "issues": []}
    cleaned = {}

    for role, raw in frames.items():
        clean = deduplicate(config, raw)
        cleaned[role] = clean
        key = config.get("deduplication", {}).get("key", c["record_id"])
        measures = business_measure_columns(config, raw)
        missing_by_column = {k: int(v) for k, v in raw.isna().sum().items() if v}
        negative_cells = int((raw[measures] < 0).sum().sum()) if measures else 0
        duplicate_keys = int(raw[key].duplicated().sum()) if key in raw.columns else None
        date_col = c["date"]
        profile = {
            "path": str(files[role]), "raw_rows": len(raw), "clean_rows": len(clean),
            "columns": raw.columns.tolist(), "missing_by_column": missing_by_column,
            "duplicate_business_keys": duplicate_keys, "negative_numeric_cells": negative_cells,
            "first_date": clean[date_col].min(), "last_date": clean[date_col].max(),
            "distinct_dates": int(clean[date_col].nunique())
        }
        report["datasets"][role] = profile
        if duplicate_keys:
            report["issues"].append({"severity": "medium", "dataset": role, "issue": f"{duplicate_keys} repeated business key(s)", "treatment": "Latest load retained."})
        for column, count in missing_by_column.items():
            report["issues"].append({"severity": "medium", "dataset": role, "issue": f"{count} missing value(s) in {column}", "treatment": "Left missing; no automatic imputation."})
        if negative_cells:
            report["status"] = "review_required"
            report["issues"].append({"severity": "high", "dataset": role, "issue": f"{negative_cells} negative numeric cell(s)", "treatment": "Review before interpretation."})

    keys = [c["date"], c["segment"], c["channel"], c["region"]]
    if "growth_funnel" in cleaned and "product_usage" in cleaned:
        left = set(map(tuple, cleaned["growth_funnel"][keys].values))
        right = set(map(tuple, cleaned["product_usage"][keys].values))
        report["joinability"]["growth_funnel_to_product_usage"] = {
            "keysets_equal": left == right, "left_only": len(left-right), "right_only": len(right-left)
        }
    if "paid_media" in cleaned and "growth_funnel" in cleaned:
        paid_value = config["paid_channel_value"]
        left = set(map(tuple, cleaned["paid_media"][keys].values))
        right_df = cleaned["growth_funnel"][cleaned["growth_funnel"][c["channel"]] == paid_value]
        right = set(map(tuple, right_df[keys].values))
        report["joinability"]["paid_media_to_paid_funnel"] = {
            "keysets_equal": left == right, "left_only": len(left-right), "right_only": len(right-left)
        }
    if any(not item["keysets_equal"] for item in report["joinability"].values()):
        report["status"] = "review_required"
    return report, cleaned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--input-dir", default="input")
    parser.add_argument("--output", default="outputs/validation_report.json")
    args = parser.parse_args()
    report, _ = validate(load_config(args.config), args.input_dir)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, report)
    print(f"Validation status: {report['status']} -> {args.output}")


if __name__ == "__main__":
    main()

