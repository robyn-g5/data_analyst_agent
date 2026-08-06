"use client";

import type { MouseEvent } from "react";
import type { RunSummary } from "@/lib/types";
import { STEP_LABELS, TONE_CLASSES, formatRunLabel, statusTone } from "@/lib/status";

interface RunHistoryPanelProps {
  runs: RunSummary[];
  selectedRunId: string | null;
  onSelect: (runId: string) => void;
  onDelete: (runId: string) => void;
}

export function RunHistoryPanel({ runs, selectedRunId, onSelect, onDelete }: RunHistoryPanelProps) {
  function handleDelete(event: MouseEvent, run: RunSummary) {
    event.stopPropagation();
    if (window.confirm(`Delete the ${formatRunLabel(run.run_date)} run? This can't be undone.`)) {
      onDelete(run.id);
    }
  }

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-neutral-200 bg-white">
      <div className="border-b border-neutral-200 px-4 py-4">
        <h2 className="text-sm font-semibold text-neutral-900">Run history</h2>
        <p className="mt-0.5 text-xs text-neutral-500">One tab per analysis run</p>
      </div>
      <div className="flex-1 overflow-y-auto">
        {runs.length === 0 && (
          <p className="px-4 py-6 text-sm text-neutral-400">
            No runs yet. Drop CSVs in the chat to get started.
          </p>
        )}
        <ul>
          {runs.map((run) => {
            const active = run.id === selectedRunId;
            const tone = statusTone(run.status);
            return (
              <li key={run.id} className="group relative">
                <button
                  onClick={() => onSelect(run.id)}
                  className={`flex w-full flex-col items-start gap-1 border-l-2 py-3 pl-4 pr-9 text-left transition ${
                    active
                      ? "border-neutral-900 bg-neutral-50"
                      : "border-transparent hover:bg-neutral-50"
                  }`}
                >
                  <span className="text-sm font-medium text-neutral-900">
                    {formatRunLabel(run.run_date)}
                  </span>
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ${TONE_CLASSES[tone]}`}
                  >
                    {STEP_LABELS[run.status]}
                  </span>
                </button>
                <button
                  onClick={(e) => handleDelete(e, run)}
                  aria-label={`Delete ${formatRunLabel(run.run_date)} run`}
                  className="absolute right-2 top-3 rounded p-1 text-neutral-300 opacity-0 transition hover:bg-neutral-200 hover:text-neutral-600 group-hover:opacity-100"
                >
                  ×
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </aside>
  );
}
