"use client";

import { useCallback, useState } from "react";
import { uploadDocument, type Document } from "@/lib/api";

interface DocumentUploadProps {
  onUploaded: (doc: Document) => void;
}

export default function DocumentUpload({ onUploaded }: DocumentUploadProps) {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFiles = useCallback(
    async (files: FileList | null) => {
      if (!files || files.length === 0) return;
      setError(null);
      setUploading(true);
      try {
        for (const file of Array.from(files)) {
          const doc = await uploadDocument(file);
          onUploaded(doc);
        }
      } catch (err: any) {
        setError(err.message || "Upload failed");
      } finally {
        setUploading(false);
      }
    },
    [onUploaded]
  );

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
        dragOver ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        handleFiles(e.dataTransfer.files);
      }}
    >
      {uploading ? (
        <div className="text-sm text-gray-500">
          <div className="animate-spin inline-block w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full mb-1" />
          <p>Processing document...</p>
        </div>
      ) : (
        <>
          <svg className="w-8 h-8 mx-auto text-gray-400 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 16v-8m0 0l-3 3m3-3l3 3M9 20H5a2 2 0 01-2-2V6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v2" />
          </svg>
          <p className="text-xs text-gray-500">
            Drop PDF or DOCX here
          </p>
          <label className="mt-2 inline-block text-xs text-blue-600 hover:text-blue-700 cursor-pointer font-medium">
            or browse files
            <input
              type="file"
              className="hidden"
              accept=".pdf,.docx"
              multiple
              onChange={(e) => handleFiles(e.target.files)}
            />
          </label>
        </>
      )}
      {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
    </div>
  );
}
