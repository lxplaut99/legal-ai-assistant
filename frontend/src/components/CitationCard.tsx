"use client";

import { useState } from "react";
import type { Citation } from "@/lib/api";

interface CitationCardProps {
  citation: Citation;
}

export default function CitationCard({ citation }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false);

  const location = [
    citation.filename,
    citation.section,
    citation.page_number ? `page ${citation.page_number}` : null,
  ]
    .filter(Boolean)
    .join(" | ");

  return (
    <div
      className="border border-gray-200 rounded-lg bg-gray-50 text-sm cursor-pointer hover:border-blue-300 transition-colors"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-center gap-2 px-3 py-2">
        <span className="bg-blue-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center shrink-0">
          {citation.number}
        </span>
        <span className="text-gray-600 truncate">{location}</span>
        <svg
          className={`w-4 h-4 text-gray-400 shrink-0 ml-auto transition-transform ${expanded ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
      {expanded && (
        <div className="px-3 pb-3 pt-1 border-t border-gray-200">
          <p className="text-gray-700 whitespace-pre-wrap text-xs leading-relaxed">
            {citation.content}
          </p>
        </div>
      )}
    </div>
  );
}
