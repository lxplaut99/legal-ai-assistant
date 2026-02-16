"use client";

import { useCallback, useEffect, useState } from "react";
import {
  type Conversation,
  type Document,
  createConversation,
  createDocumentFromText,
  deleteConversation,
  deleteDocument,
  listConversations,
  listDocuments,
} from "@/lib/api";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import ChatInterface from "@/components/ChatInterface";
import DocumentPreview from "@/components/DocumentPreview";

export default function Home() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [previewDocument, setPreviewDocument] = useState<Document | null>(null);

  // Load initial data
  useEffect(() => {
    listConversations().then(setConversations);
    listDocuments().then(setDocuments);
  }, []);

  const handleNewConversation = useCallback(async () => {
    const conv = await createConversation();
    setConversations((prev) => [conv, ...prev]);
    setActiveConversationId(conv.id);
  }, []);

  const handleDeleteConversation = useCallback(
    async (id: string) => {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        setActiveConversationId(null);
      }
    },
    [activeConversationId]
  );

  const handleDocumentUploaded = useCallback((doc: Document) => {
    setDocuments((prev) => [doc, ...prev]);
  }, []);

  const handleDeleteDocument = useCallback(
    async (id: string) => {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      if (previewDocument?.id === id) {
        setPreviewDocument(null);
      }
    },
    [previewDocument]
  );

  const handleSelectDocument = useCallback(
    (doc: Document) => {
      // Toggle: click again to close
      if (previewDocument?.id === doc.id) {
        setPreviewDocument(null);
      } else {
        setPreviewDocument(doc);
      }
    },
    [previewDocument]
  );

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={setActiveConversationId}
          onNewConversation={handleNewConversation}
          onDeleteConversation={handleDeleteConversation}
          documents={documents}
          selectedDocumentId={previewDocument?.id ?? null}
          onSelectDocument={handleSelectDocument}
          onDocumentUploaded={handleDocumentUploaded}
          onDeleteDocument={handleDeleteDocument}
        />
        <ChatInterface
          conversationId={activeConversationId}
          onSaveAsDocument={async (content) => {
            const timestamp = new Date().toISOString().slice(0, 10);
            const filename = `draft_${timestamp}.pdf`;
            const doc = await createDocumentFromText(content, filename);
            setDocuments((prev) => [doc, ...prev]);
            setPreviewDocument(doc);
          }}
        />
        {previewDocument && (
          <DocumentPreview
            document={previewDocument}
            onClose={() => setPreviewDocument(null)}
          />
        )}
      </div>
    </div>
  );
}
