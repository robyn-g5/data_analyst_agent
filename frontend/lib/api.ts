import { createClient } from "./supabaseClient";
import type { ChatMessage, RunDetail, RunSummary } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL!;

async function authHeaders(): Promise<HeadersInit> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session ? { Authorization: `Bearer ${session.access_token}` } : {};
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { ...headers, ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchRuns(): Promise<RunSummary[]> {
  const data = await apiFetch<{ runs: RunSummary[] }>("/api/runs");
  return data.runs;
}

export async function fetchRunDetail(runId: string): Promise<RunDetail> {
  return apiFetch<RunDetail>(`/api/runs/${runId}`);
}

export async function fetchRunStatus(runId: string): Promise<RunSummary> {
  return apiFetch<RunSummary>(`/api/runs/${runId}/status`);
}

export async function fetchMessages(sinceId?: string): Promise<ChatMessage[]> {
  const query = sinceId ? `?since=${encodeURIComponent(sinceId)}` : "";
  const data = await apiFetch<{ messages: ChatMessage[] }>(`/api/chat/messages${query}`);
  return data.messages;
}

export async function sendMessage(
  content: string,
  files: File[]
): Promise<{ message: ChatMessage; run: RunSummary | null }> {
  const form = new FormData();
  form.set("content", content);
  files.forEach((file) => form.append("files", file));
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/api/chat/messages`, {
    method: "POST",
    headers,
    body: form,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

export async function submitClarification(runId: string, answer: string): Promise<RunSummary> {
  return apiFetch<RunSummary>(`/api/runs/${runId}/clarify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answer }),
  });
}

export function downloadUrl(runId: string, fileKey: string): string {
  return `${API_BASE}/api/runs/${runId}/files/${fileKey}`;
}
