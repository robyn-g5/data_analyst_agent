import type { RunStatus } from "./types";

export const STEP_LABELS: Record<RunStatus, string> = {
  pending: "Queued",
  awaiting_clarification: "Needs your input",
  validating: "Validating data",
  mapping_columns: "Mapping columns",
  analyzing: "Analyzing metrics",
  generating_narrative: "Writing narrative",
  building_dashboard: "Building dashboard",
  complete: "Complete",
  failed: "Failed",
};

export function isTerminal(status: RunStatus): boolean {
  return status === "complete" || status === "failed";
}

export function statusTone(status: RunStatus): "neutral" | "progress" | "attention" | "success" | "error" {
  if (status === "complete") return "success";
  if (status === "failed") return "error";
  if (status === "awaiting_clarification") return "attention";
  if (status === "pending") return "neutral";
  return "progress";
}

export const TONE_CLASSES: Record<ReturnType<typeof statusTone>, string> = {
  neutral: "bg-neutral-100 text-neutral-600",
  progress: "bg-blue-50 text-blue-700",
  attention: "bg-amber-50 text-amber-700",
  success: "bg-emerald-50 text-emerald-700",
  error: "bg-red-50 text-red-700",
};

export function formatRunLabel(runDate: string): string {
  const date = new Date(`${runDate}T00:00:00`);
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}
