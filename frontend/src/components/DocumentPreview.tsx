"use client";

import { useEffect } from "react";
import type { Document } from "@/lib/api";

interface DocumentPreviewProps {
  document: Document;
  onClose: () => void;
}

export default function DocumentPreview({ document, onClose }: DocumentPreviewProps) {
  const fileUrl = `/api/documents/${document.id}/file`;
  const isPdf = document.file_type === "pdf";

  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white rounded-xl shadow-2xl flex flex-col w-[90vw] h-[90vh] max-w-5xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 shrink-0">
          <div className="min-w-0 flex-1">
            <h3 className="text-base font-semibold text-gray-800 truncate">{document.filename}</h3>
            <p className="text-xs text-gray-400 mt-0.5">
              {document.file_type.toUpperCase()}
              {document.page_count ? ` · ${document.page_count} pages` : ""}
              {` · ${document.chunk_count} chunks`}
            </p>
          </div>
          <div className="flex items-center gap-3 ml-4">
            <a
              href={fileUrl}
              download={document.filename}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium px-3 py-1.5 rounded-lg hover:bg-blue-50 transition-colors"
            >
              Download
            </a>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
              title="Close (Esc)"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden rounded-b-xl">
          {isPdf ? (
            <iframe
              src={`${fileUrl}#toolbar=1&navpanes=1&view=FitH`}
              className="w-full h-full border-0"
              title={`Preview of ${document.filename}`}
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 p-8">
              <svg className="w-20 h-20 mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-lg font-medium">DOCX Preview</p>
              <p className="text-sm mt-1 text-center">
                DOCX files cannot be previewed in-browser.
              </p>
              <a
                href={fileUrl}
                download={document.filename}
                className="mt-6 px-5 py-2.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
              >
                Download to View
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
