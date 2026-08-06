# End-to-End Executive Analytics Workflow

## Purpose

Use this workflow when one or more structured data files are supplied and the user wants a decision-ready executive analysis and dashboard. It is IDE- and assistant-agnostic.

## Operating contract

Run the workflow end to end after collecting the minimum required business context. Do not pause for approval between inventory, validation, analysis, report creation, and dashboard creation unless a missing definition would materially change the result.

Never modify raw files. Treat `input/` as immutable source data. Put generated files in `outputs/`.

## Phase 1 — Describe before analyzing

Inventory the supplied files and describe only:

- filenames, formats, sizes, and row/column counts;
- date coverage;
- column names and apparent data types;
- categorical dimensions and high-level subject matter;
- likely grain, stated as an inference until validated.

Do not discuss performance, trends, causes, or recommendations during this phase.

## Phase 2 — Gather business context

Collect or infer cautiously:

- primary business question and decisions the analysis will support;
- audience and level of detail;
- metric definitions and attribution rules;
- comparison period, benchmark, target, or trajectory rule;
- important business events during the period;
- output expectations;
- financial inputs required for ROI or profitability claims.

If no target or external benchmark exists, assess direction, pace, consistency, and relative performance. Say explicitly that “good” is a trajectory judgment.

Update `config/analysis_config.json` with the confirmed context and source mappings.

## Phase 3 — Validate data before analysis

Run the validation script and check:

- required columns and types;
- row counts, date bounds, and date continuity;
- missing values, including the exact affected records for critical metrics;
- duplicate rows and duplicate business keys;
- negative or impossible numeric values;
- controlled category consistency;
- expected dimensional combinations;
- cross-file key coverage and join cardinality;
- source freshness and repeated load behavior.

For repeated business keys with identical business metrics and different load timestamps, retain the latest load and document the treatment. Do not impute missing business outcomes unless the user supplied an accepted rule.

Stop substantive interpretation when a critical quality issue could materially reverse the conclusion. Otherwise continue and disclose the limitation.

## Phase 4 — Analyze

Use complete periods. Normalize monthly totals by distinct calendar days when comparing daily concepts or months of unequal length.

Default analytical hierarchy:

1. company growth trajectory;
2. funnel volume and conversion quality;
3. product reach and engagement depth;
4. paid-media delivery and acquisition efficiency;
5. segment, channel, region, and time drivers;
6. decision implications.

Separate these concepts:

- total active-user days versus unique monthly users;
- subscriptions occurring on a date versus total paying customers;
- original acquisition source versus same-day causal attribution;
- cost per subscription versus ROI or profitability.

When available, calculate:

- month-over-month total and daily-normalized growth;
- trial-to-subscription conversion;
- feature adoption per active user;
- sessions per active user;
- CTR, CPC, click-to-trial, cost per trial, and cost per subscription;
- changes by customer segment, original acquisition channel, and region.

Do not calculate true ROI, payback, or profitability without revenue, margin, retention, and lifetime-value inputs.

## Phase 5 — Write the report

Create `outputs/executive_report.md` with these distinct sections:

1. Executive summary
2. KPI scorecard
3. Growth trajectory
4. Detailed insights
5. Executive takeaways and decisions
6. Data validation
7. Definitions and limitations
8. Sources

Lead with the answer. Quantify every material claim. Distinguish observed evidence from inference. Recommendations must follow from validated evidence and match the decision scope.

## Phase 6 — Build the dashboard

Create `outputs/executive_dashboard.html` as a self-contained visual dashboard. The default view should contain:

- decision-relevant KPI cards with prior-period movement;
- a normalized growth comparison;
- conversion-quality view;
- paid-efficiency view by segment;
- a compact decision table;
- the full report narrative below the visual layer;
- visible data-quality and ROI caveats.

Use charts for shape and comparison, and tables for exact lookup. Avoid comparing incompatible units on one raw scale; use an index or separate charts.

If the assistant environment provides a native dashboard-artifact capability, validate and render a source-backed artifact after the local Markdown and HTML outputs pass QA. Include the full report text in the artifact, not only the KPI cards and charts.

## Phase 7 — QA and handoff

Before delivery:

- reconcile dashboard values to `analysis_results.json`;
- scan for null-derived or divide-by-zero output;
- inspect the HTML at desktop and narrow widths;
- verify chart labels, units, percentage scales, and month ordering;
- verify the full report text is included;
- disclose unresolved source limitations.

Deliver the report, dashboard, validation report, and analysis results. Briefly state the controlling source period and material caveats.

