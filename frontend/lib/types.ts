export type RunStatus =
  | "pending"
  | "awaiting_clarification"
  | "validating"
  | "mapping_columns"
  | "analyzing"
  | "generating_narrative"
  | "building_dashboard"
  | "complete"
  | "failed";

export interface RunSummary {
  id: string;
  status: RunStatus;
  step: string | null;
  run_date: string;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
}

export interface RunDetail extends RunSummary {
  dashboard_html_url: string | null;
  report_md_url: string | null;
  analysis_results_url: string | null;
  validation_report_url: string | null;
  config: Record<string, unknown> | null;
}

export type ChatRole = "user" | "assistant" | "system";

export interface ChatAttachment {
  id: string;
  original_filename: string;
  size_bytes: number | null;
}

export interface ChatMessage {
  id: string;
  author_id: string | null;
  author_email?: string | null;
  role: ChatRole;
  content: string;
  run_id: string | null;
  created_at: string;
  attachments: ChatAttachment[];
}
