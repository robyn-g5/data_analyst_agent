# Reusable Executive Analytics Workflow

This IDE-agnostic starter project reproduces the workflow used in this analysis:

1. inventory newly supplied data;
2. gather business context;
3. validate data quality and joinability;
4. analyze trajectory, conversion, engagement, and paid efficiency;
5. separate evidence, insights, takeaways, and limitations;
6. create a Markdown report and visual HTML dashboard;
7. render a native dashboard artifact when the active AI environment supports one.

## Quick start

1. Put new CSV files in `input/`.
2. Copy `config/analysis_config.example.json` to `config/analysis_config.json` and update filenames, columns, definitions, and business context.
3. Install the one runtime dependency:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Run the complete workflow:

   ```bash
   python scripts/run_pipeline.py --config config/analysis_config.json
   ```

The pipeline writes these files to `outputs/`:

- `validation_report.json`
- `analysis_results.json`
- `executive_report.md`
- `executive_dashboard.html`

To test the included example against the original workspace data:

```bash
python scripts/run_pipeline.py \
  --config config/analysis_config.example.json \
  --input-dir ../data \
  --output-dir outputs/example_run
```

## Using an AI coding assistant

Give the assistant [ANALYTICS_WORKFLOW.md](ANALYTICS_WORKFLOW.md) as the task instructions. `AGENTS.md` contains a compact repository-level version for assistants that automatically read that convention.

The assistant should inspect new schemas and update configuration rather than changing raw data. If the data does not support a requested metric, the report must say so instead of inventing a proxy.

## Portability

The scripts use Python, pandas, JSON, Markdown, and self-contained HTML. They do not depend on a particular IDE or AI vendor. Native artifact rendering is an optional final delivery step owned by whichever assistant environment is running the project.

