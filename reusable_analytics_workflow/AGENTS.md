# Analytics Agent Instructions

Read and follow `ANALYTICS_WORKFLOW.md` completely before working with new data.

- Preserve files in `input/` as raw sources.
- Update `config/analysis_config.json` for the supplied schemas and business definitions.
- Run `python scripts/run_pipeline.py --config config/analysis_config.json` end to end.
- Resolve validation failures before interpreting metrics.
- Keep evidence, insights, executive takeaways, and limitations distinct.
- Never describe acquisition efficiency as ROI without revenue, margin, retention, and LTV.
- Deliver `outputs/executive_report.md` and `outputs/executive_dashboard.html`.
- If a native dashboard-artifact tool is available, use it after the local outputs pass QA.

