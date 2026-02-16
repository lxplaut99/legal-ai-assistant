"use client";

import { useState } from "react";
import type { Citation } from "@/lib/api";
import CitationCard from "./CitationCard";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  isStreaming?: boolean;
  onSaveAsDocument?: (content: string) => Promise<void>;
}

export default function MessageBubble({ role, content, citations, isStreaming, onSaveAsDocument }: MessageBubbleProps) {
  const isUser = role === "user";
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    if (!onSaveAsDocument || saving || saved) return;
    setSaving(true);
    try {
      await onSaveAsDocument(content);
      setSaved(true);
    } catch (err) {
      console.error("Failed to save document:", err);
    } finally {
      setSaving(false);
    }
  };

  // Render citation markers as styled spans
  const renderContent = (text: string) => {
    const parts = text.split(/(\[\d+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/^\[(\d+)\]$/);
      if (match) {
        return (
          <span
            key={i}
            className="inline-flex items-center justify-center bg-blue-600 text-white text-xs font-bold rounded-full w-4 h-4 mx-0.5 align-super cursor-help"
            title={`Citation ${match[1]}`}
          >
            {match[1]}
          </span>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  // Show save button for non-trivial assistant messages that aren't streaming
  const showSaveButton = !isUser && !isStreaming && content.length > 200;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] ${isUser ? "order-1" : ""}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-blue-600 text-white"
              : "bg-white border border-gray-200 text-gray-800"
          }`}
        >
          <div className={`whitespace-pre-wrap text-sm leading-relaxed ${isStreaming ? "streaming-cursor" : ""}`}>
            {isUser ? content : renderContent(content)}
          </div>
        </div>
        {/* Action buttons for assistant messages */}
        {showSaveButton && (
          <div className="mt-1.5 ml-1">
            <button
              onClick={handleSave}
              disabled={saving || saved}
              className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-md transition-colors ${
                saved
                  ? "text-green-600 bg-green-50"
                  : "text-gray-500 hover:text-blue-600 hover:bg-blue-50"
              }`}
            >
              {saved ? (
                <>
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Saved to Documents
                </>
              ) : saving ? (
                <>
                  <div className="animate-spin w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full" />
                  Saving...
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Save as Document
                </>
              )}
            </button>
          </div>
        )}
        {!isUser && citations && citations.length > 0 && (
          <div className="mt-2 space-y-1.5">
            <p className="text-xs text-gray-500 font-medium ml-1">Sources</p>
            {citations.map((c) => (
              <CitationCard key={c.chunk_id} citation={c} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
