from __future__ import annotations

import argparse
from pathlib import Path

from analyze_data import analyze
from build_dashboard import build_html, build_report
from common import load_config, write_json


def main():
    parser=argparse.ArgumentParser(description="Run validation, executive analysis, report, and dashboard end to end.")
    parser.add_argument("--config",required=True); parser.add_argument("--input-dir",default="input"); parser.add_argument("--output-dir",default="outputs"); args=parser.parse_args()
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    results,validation=analyze(load_config(args.config),args.input_dir)
    write_json(out/"validation_report.json",validation); write_json(out/"analysis_results.json",results)
    report=build_report(results); (out/"executive_report.md").write_text(report); (out/"executive_dashboard.html").write_text(build_html(results,report))
    print(f"Complete. Outputs written to {out.resolve()}")


if __name__=="__main__": main()

