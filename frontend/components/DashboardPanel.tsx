"use client";

import { useState } from "react";
import type { RunSummary } from "@/lib/types";
import { STEP_LABELS, formatRunLabel, isTerminal } from "@/lib/status";

const PROGRESS_STEPS: RunSummary["status"][] = [
  "validating",
  "mapping_columns",
  "analyzing",
  "generating_narrative",
  "building_dashboard",
  "complete",
];

interface DashboardPanelProps {
  run: RunSummary | null;
  dashboardUrl?: string | null;
  downloads?: { label: string; url: string }[];
}

export function DashboardPanel({ run, dashboardUrl, downloads = [] }: DashboardPanelProps) {
  if (!run) {
    return (
      <section className="flex h-full flex-1 flex-col items-center justify-center bg-white px-8 text-center">
        <p className="text-sm text-neutral-400">
          Select a run from the left, or drop CSVs in the chat to generate a dashboard.
        </p>
      </section>
    );
  }

  return (
    <section className="flex h-full flex-1 flex-col bg-white">
      <div className="flex items-center justify-between border-b border-neutral-200 px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold text-neutral-900">
            {formatRunLabel(run.run_date)}
          </h2>
          <p className="mt-0.5 text-xs text-neutral-500">{STEP_LABELS[run.status]}</p>
        </div>
        <div className="flex gap-2">
          {dashboardUrl && <CopyLinkButton url={dashboardUrl} />}
          {downloads.map((d) => (
            <a
              key={d.url}
              href={d.url}
              className="rounded-md border border-neutral-300 px-2.5 py-1.5 text-xs font-medium text-neutral-700 transition hover:bg-neutral-50"
            >
              {d.label}
            </a>
          ))}
        </div>
      </div>

      {!isTerminal(run.status) && (
        <div className="border-b border-neutral-200 bg-neutral-50 px-5 py-3">
          <ProgressSteps status={run.status} />
        </div>
      )}

      {run.status === "failed" && (
        <div className="mx-5 mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {run.error_message ?? "This run failed. See the chat for details."}
        </div>
      )}

      <div className="flex-1 overflow-hidden">
        {dashboardUrl ? (
          <iframe
            title={`Dashboard for ${run.run_date}`}
            src={dashboardUrl}
            sandbox="allow-scripts"
            className="h-full w-full border-0"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-neutral-400">
            {isTerminal(run.status)
              ? "No dashboard available for this run."
              : "Building your dashboard…"}
          </div>
        )}
      </div>
    </section>
  );
}

function CopyLinkButton({ url }: { url: string }) {
  const [status, setStatus] = useState<"idle" | "copied" | "failed">("idle");

  async function handleClick() {
    try {
      await navigator.clipboard.writeText(url);
      setStatus("copied");
    } catch {
      setStatus("failed");
    }
    setTimeout(() => setStatus("idle"), 2000);
  }

  return (
    <button
      onClick={handleClick}
      className="rounded-md border border-neutral-300 px-2.5 py-1.5 text-xs font-medium text-neutral-700 transition hover:bg-neutral-50"
    >
      {status === "copied" ? "Link copied" : status === "failed" ? "Couldn't copy" : "Copy link"}
    </button>
  );
}

function ProgressSteps({ status }: { status: RunSummary["status"] }) {
  const currentIndex = PROGRESS_STEPS.indexOf(status);
  return (
    <ol className="flex items-center gap-2 text-xs text-neutral-500">
      {PROGRESS_STEPS.filter((s) => s !== "complete").map((step, index) => {
        const done = currentIndex > index;
        const active = currentIndex === index;
        return (
          <li key={step} className="flex items-center gap-2">
            <span
              className={`flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-medium ${
                done
                  ? "bg-neutral-900 text-white"
                  : active
                    ? "bg-blue-100 text-blue-700"
                    : "bg-neutral-200 text-neutral-400"
              }`}
            >
              {index + 1}
            </span>
            <span className={active ? "font-medium text-neutral-900" : ""}>
              {STEP_LABELS[step]}
            </span>
            {index < PROGRESS_STEPS.length - 2 && <span className="text-neutral-300">→</span>}
          </li>
        );
      })}
    </ol>
  );
}
