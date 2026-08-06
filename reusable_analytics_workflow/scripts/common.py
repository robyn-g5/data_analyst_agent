from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_config(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def resolve_files(config: dict[str, Any], input_dir: str | Path) -> dict[str, Path]:
    root = Path(input_dir)
    resolved: dict[str, Path] = {}
    for role, pattern in config["files"].items():
        matches = sorted(root.glob(pattern))
        if len(matches) != 1:
            raise ValueError(f"Expected one file for role '{role}' using '{pattern}', found {len(matches)}")
        resolved[role] = matches[0]
    return resolved


def read_sources(config: dict[str, Any], input_dir: str | Path) -> tuple[dict[str, pd.DataFrame], dict[str, Path]]:
    files = resolve_files(config, input_dir)
    c = config["columns"]
    frames: dict[str, pd.DataFrame] = {}
    for role, path in files.items():
        df = pd.read_csv(path)
        for field in (c["date"], c.get("loaded_at")):
            if field and field in df.columns:
                df[field] = pd.to_datetime(df[field], errors="coerce")
        frames[role] = df
    return frames, files


def business_measure_columns(config: dict[str, Any], df: pd.DataFrame) -> list[str]:
    excluded = {
        config["columns"].get("record_id"), config["columns"].get("date"),
        config["columns"].get("loaded_at"), config["columns"].get("segment"),
        config["columns"].get("channel"), config["columns"].get("region")
    }
    return [col for col in df.columns if col not in excluded and pd.api.types.is_numeric_dtype(df[col])]


def deduplicate(config: dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
    c = config["columns"]
    key = config.get("deduplication", {}).get("key", c["record_id"])
    loaded = c.get("loaded_at")
    if key not in df.columns:
        return df.copy()
    if loaded and loaded in df.columns:
        return df.sort_values(loaded).drop_duplicates(key, keep="last").copy()
    return df.drop_duplicates(key, keep="last").copy()


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_ready(v) for v in value]
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def write_json(path: str | Path, payload: Any) -> None:
    Path(path).write_text(json.dumps(json_ready(payload), indent=2, allow_nan=False))

