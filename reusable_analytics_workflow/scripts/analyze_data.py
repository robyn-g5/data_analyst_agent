from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from common import load_config, write_json
from validate_data import validate


def safe_div(n, d):
    return n / d if d not in (0, None) and not pd.isna(d) else None


def analyze(config: dict, input_dir: str | Path) -> tuple[dict, dict]:
    validation, frames = validate(config, input_dir)
    if validation["status"] == "review_required":
        raise ValueError("Validation requires review. Inspect validation_report.json before analysis.")
    c = config["columns"]
    funnel, usage, media = frames["growth_funnel"], frames["product_usage"], frames["paid_media"]
    for df in (funnel, usage, media):
        df["_month"] = df[c["date"]].dt.to_period("M").astype(str)

    months = sorted(funnel["_month"].dropna().unique())
    monthly = []
    for month in months:
        f, u, p = funnel[funnel._month == month], usage[usage._month == month], media[media._month == month]
        days = int(f[c["date"]].nunique())
        row = {
            "month": month, "days": days,
            "trials": float(f[c["trials"]].sum()), "subscriptions": float(f[c["subscriptions"]].sum()),
            "active_user_days": float(u[c["active_users"]].sum()), "sessions": float(u[c["sessions"]].sum()),
            "feature_adoptions": float(u[c["feature_adoptions"]].sum()),
            "impressions": float(p[c["impressions"]].sum()), "clicks": float(p[c["clicks"]].sum()),
            "spend": float(p[c["spend"]].sum())
        }
        row.update({
            "avg_daily_trials": safe_div(row["trials"], days),
            "avg_daily_subscriptions": safe_div(row["subscriptions"], days),
            "avg_dau": safe_div(row["active_user_days"], days),
            "avg_daily_feature_adoptions": safe_div(row["feature_adoptions"], days),
            "trial_conversion": safe_div(row["subscriptions"], row["trials"]),
            "feature_adoption_rate": safe_div(row["feature_adoptions"], row["active_user_days"]),
            "sessions_per_active": safe_div(row["sessions"], row["active_user_days"]),
            "ctr": safe_div(row["clicks"], row["impressions"]), "cpc": safe_div(row["spend"], row["clicks"])
        })
        monthly.append(row)

    paid_value = config["paid_channel_value"]
    keys = [c["date"], c["segment"], c["channel"], c["region"]]
    paid_funnel = funnel[funnel[c["channel"]] == paid_value]
    joined = media.merge(paid_funnel[keys + [c["trials"], c["subscriptions"]]], on=keys, validate="one_to_one")
    paid_segment = []
    for (segment, month), group in joined.groupby([c["segment"], "_month"]):
        spend, trials, subs = group[c["spend"]].sum(), group[c["trials"]].sum(), group[c["subscriptions"]].sum()
        paid_segment.append({"segment": segment, "month": month, "spend": float(spend), "trials": float(trials), "subscriptions": float(subs), "conversion_rate": safe_div(subs, trials), "cost_per_subscription": safe_div(spend, subs)})

    channels = []
    latest = months[-1]
    for channel, group in funnel[funnel._month == latest].groupby(c["channel"]):
        trials, subs = group[c["trials"]].sum(), group[c["subscriptions"]].sum()
        channels.append({"channel": channel, "month": latest, "trials": float(trials), "subscriptions": float(subs), "conversion_rate": safe_div(subs, trials)})

    results = {"project": config["project"], "definitions": config.get("definitions", {}), "months": months, "monthly": monthly, "paid_segment": paid_segment, "channel_conversion_latest": channels, "validation_summary": validation}
    if len(monthly) >= 2:
        prev, current = monthly[-2], monthly[-1]
        results["latest_mom"] = {k: safe_div(current[k], prev[k])-1 for k in ["avg_daily_trials", "avg_daily_subscriptions", "avg_dau", "avg_daily_feature_adoptions", "spend"]}
    return results, validation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--input-dir", default="input")
    parser.add_argument("--output", default="outputs/analysis_results.json")
    args = parser.parse_args()
    results, _ = analyze(load_config(args.config), args.input_dir)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, results)
    print(f"Analysis -> {args.output}")


if __name__ == "__main__":
    main()

