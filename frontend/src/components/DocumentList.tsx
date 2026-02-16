"use client";

import type { Document } from "@/lib/api";

interface DocumentListProps {
  documents: Document[];
  selectedDocumentId: string | null;
  onSelect: (doc: Document) => void;
  onDelete: (id: string) => void;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentList({ documents, selectedDocumentId, onSelect, onDelete }: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <p className="text-xs text-gray-400 text-center py-2">
        No documents uploaded yet
      </p>
    );
  }

  return (
    <div className="space-y-1">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className={`flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer group text-sm ${
            doc.id === selectedDocumentId
              ? "bg-blue-50 text-blue-700"
              : "hover:bg-gray-100"
          }`}
          onClick={() => onSelect(doc)}
        >
          <span className={`shrink-0 ${doc.id === selectedDocumentId ? "text-blue-500" : "text-gray-400"}`}>
            {doc.file_type === "pdf" ? (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M4 18h12V6h-4V2H4v16zm8-15.5L14.5 5H12V2.5zM2 0h10l4 4v16H2V0z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M4 18h12V6h-4V2H4v16zM6 8h8v1H6V8zm0 3h8v1H6v-1zm0 3h5v1H6v-1z" />
              </svg>
            )}
          </span>
          <div className="min-w-0 flex-1">
            <p className={`truncate text-xs font-medium ${doc.id === selectedDocumentId ? "text-blue-700" : "text-gray-700"}`}>
              {doc.filename}
            </p>
            <p className="text-gray-400 text-[10px]">
              {formatSize(doc.file_size)} &middot; {doc.chunk_count} chunks
            </p>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(doc.id);
            }}
            className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity"
            title="Delete document"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}
