"use client";

import { useState, type FormEvent } from "react";
import type { ChatMessage } from "@/lib/types";
import { Dropzone } from "./Dropzone";

interface ChatPanelProps {
  messages: ChatMessage[];
  onSend: (content: string, files: File[]) => void | Promise<void>;
  onClear: () => void;
  sending?: boolean;
}

export function ChatPanel({ messages, onSend, onClear, sending }: ChatPanelProps) {
  const [content, setContent] = useState("");
  const [files, setFiles] = useState<File[]>([]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!content.trim() && files.length === 0) return;
    await onSend(content, files);
    setContent("");
    setFiles([]);
  }

  function handleClear() {
    if (window.confirm("Clear the whole chat history? This can't be undone.")) {
      onClear();
    }
  }

  return (
    <section className="flex h-full min-w-0 flex-1 flex-col border-r border-neutral-200 bg-neutral-50">
      <div className="flex items-center justify-between border-b border-neutral-200 bg-white px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold text-neutral-900">Team chat</h2>
          <p className="mt-0.5 text-xs text-neutral-500">
            One ongoing conversation — drop CSVs here to run a new analysis
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClear}
            className="shrink-0 rounded-md border border-neutral-300 px-2.5 py-1.5 text-xs font-medium text-neutral-700 transition hover:bg-neutral-50"
          >
            Clear chat
          </button>
        )}
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-5 py-4">
        {messages.map((message) => (
          <ChatBubble key={message.id} message={message} />
        ))}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-neutral-200 bg-white p-4">
        <Dropzone files={files} onFilesChange={setFiles} />
        <div className="mt-2 flex items-end gap-2">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Add notes or business context…"
            rows={2}
            className="min-w-0 flex-1 resize-none rounded-md border border-neutral-300 px-3 py-2 text-sm text-neutral-900 outline-none focus:border-neutral-500 focus:ring-1 focus:ring-neutral-500"
          />
          <button
            type="submit"
            disabled={sending}
            className="shrink-0 rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-neutral-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </section>
  );
}

function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-xl px-3.5 py-2.5 text-sm shadow-sm ${
          isUser
            ? "bg-neutral-900 text-white"
            : "border border-neutral-200 bg-white text-neutral-800"
        }`}
      >
        {message.content && <p className="whitespace-pre-wrap">{message.content}</p>}
        {message.attachments.length > 0 && (
          <ul className="mt-1.5 flex flex-wrap gap-1.5">
            {message.attachments.map((attachment) => (
              <li
                key={attachment.id}
                className={`rounded-full px-2 py-0.5 text-[11px] ${
                  isUser ? "bg-white/15 text-white" : "bg-neutral-100 text-neutral-600"
                }`}
              >
                {attachment.original_filename}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
