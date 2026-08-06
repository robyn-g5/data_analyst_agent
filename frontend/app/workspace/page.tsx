"use client";

import { useEffect, useMemo, useState } from "react";
import { RunHistoryPanel } from "@/components/RunHistoryPanel";
import { ChatPanel } from "@/components/ChatPanel";
import { DashboardPanel } from "@/components/DashboardPanel";
import { SignOutButton } from "@/components/SignOutButton";
import { useRuns } from "@/hooks/useRuns";
import { useChatMessages, useInvalidateChat } from "@/hooks/useChatMessages";
import { useRunStatus } from "@/hooks/useRunStatus";
import { useRunDetail } from "@/hooks/useRunDetail";
import { sendMessage, downloadUrl } from "@/lib/api";

export default function WorkspacePage() {
  const { data: runs = [] } = useRuns();
  const { data: messages = [] } = useChatMessages();
  const invalidateChat = useInvalidateChat();
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (!selectedRunId && runs.length > 0) {
      setSelectedRunId(runs[0].id);
    }
  }, [runs, selectedRunId]);

  const selectedRunSummary = useMemo(
    () => runs.find((r) => r.id === selectedRunId) ?? null,
    [runs, selectedRunId]
  );
  const { data: liveStatus } = useRunStatus(selectedRunId);
  const selectedRun = liveStatus ?? selectedRunSummary;

  const { data: runDetail } = useRunDetail(selectedRun);

  async function handleSend(content: string, files: File[]) {
    setSending(true);
    try {
      const { run } = await sendMessage(content, files);
      invalidateChat();
      if (run) setSelectedRunId(run.id);
    } finally {
      setSending(false);
    }
  }

  const downloads = runDetail
    ? [
        { label: "Dashboard", url: downloadUrl(runDetail.id, "dashboard_html") },
        { label: "Report", url: downloadUrl(runDetail.id, "report_md") },
        { label: "Data", url: downloadUrl(runDetail.id, "analysis_results") },
      ]
    : [];

  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b border-neutral-200 bg-white px-5 py-3">
        <h1 className="text-sm font-semibold text-neutral-900">Executive Analytics</h1>
        <SignOutButton />
      </header>
      <div className="flex min-h-0 flex-1">
        <RunHistoryPanel runs={runs} selectedRunId={selectedRunId} onSelect={setSelectedRunId} />
        <ChatPanel messages={messages} onSend={handleSend} sending={sending} />
        <DashboardPanel run={selectedRun} dashboardUrl={runDetail?.dashboard_html_url} downloads={downloads} />
      </div>
    </div>
  );
}
