"use client";

import type { Conversation, Document as DocType } from "@/lib/api";
import DocumentUpload from "./DocumentUpload";
import DocumentList from "./DocumentList";

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
  documents: DocType[];
  selectedDocumentId: string | null;
  onSelectDocument: (doc: DocType) => void;
  onDocumentUploaded: (doc: DocType) => void;
  onDeleteDocument: (id: string) => void;
}

export default function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  documents,
  selectedDocumentId,
  onSelectDocument,
  onDocumentUploaded,
  onDeleteDocument,
}: SidebarProps) {
  return (
    <aside className="w-72 border-r border-gray-200 bg-white flex flex-col h-full shrink-0">
      {/* New conversation button */}
      <div className="p-3 border-b border-gray-200">
        <button
          onClick={onNewConversation}
          className="w-full py-2 px-3 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          + New Conversation
        </button>
      </div>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-3">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Conversations
          </h3>
          {conversations.length === 0 ? (
            <p className="text-xs text-gray-400 text-center py-2">No conversations yet</p>
          ) : (
            <div className="space-y-0.5">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`flex items-center gap-1 px-2 py-1.5 rounded-md cursor-pointer group text-sm ${
                    conv.id === activeConversationId
                      ? "bg-blue-50 text-blue-700"
                      : "hover:bg-gray-100 text-gray-700"
                  }`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <span className="truncate flex-1 text-xs">{conv.title}</span>
                  <span className="text-[10px] text-gray-400">{conv.message_count}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteConversation(conv.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500"
                  >
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Documents section */}
      <div className="border-t border-gray-200 p-3">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
          Documents
        </h3>
        <DocumentList documents={documents} selectedDocumentId={selectedDocumentId} onSelect={onSelectDocument} onDelete={onDeleteDocument} />
        <div className="mt-2">
          <DocumentUpload onUploaded={onDocumentUploaded} />
        </div>
      </div>
    </aside>
  );
}
