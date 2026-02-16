const BASE = "/api";

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  page_count: number | null;
  chunk_count: number;
  created_at: string;
}

export interface Citation {
  number: number;
  document_id: string;
  filename: string;
  content: string;
  page_number: number | null;
  section: string | null;
  chunk_id: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations: string | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail {
  id: string;
  title: string;
  messages: Message[];
}

// Documents
export async function uploadDocument(file: File): Promise<Document> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/documents`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function listDocuments(): Promise<Document[]> {
  const res = await fetch(`${BASE}/documents`);
  return res.json();
}

export async function deleteDocument(id: string): Promise<void> {
  await fetch(`${BASE}/documents/${id}`, { method: "DELETE" });
}

export async function createDocumentFromText(content: string, filename: string): Promise<Document> {
  const res = await fetch(`${BASE}/documents/from-text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, filename }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to create document" }));
    throw new Error(err.detail || "Failed to create document");
  }
  return res.json();
}

// Conversations
export async function createConversation(title?: string): Promise<Conversation> {
  const res = await fetch(`${BASE}/conversations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: title || "New Conversation" }),
  });
  return res.json();
}

export async function listConversations(): Promise<Conversation[]> {
  const res = await fetch(`${BASE}/conversations`);
  return res.json();
}

export async function getConversation(id: string): Promise<ConversationDetail> {
  const res = await fetch(`${BASE}/conversations/${id}`);
  return res.json();
}

export async function deleteConversation(id: string): Promise<void> {
  await fetch(`${BASE}/conversations/${id}`, { method: "DELETE" });
}

// Chat (SSE streaming)
export interface ChatStreamCallbacks {
  onToken: (token: string) => void;
  onCitations: (citations: Citation[]) => void;
  onDone: () => void;
  onError: (error: string) => void;
}

export function sendMessage(
  conversationId: string,
  message: string,
  callbacks: ChatStreamCallbacks,
  documentIds?: string[]
): AbortController {
  const controller = new AbortController();

  fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
      document_ids: documentIds,
    }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Chat request failed" }));
        callbacks.onError(err.detail || "Chat request failed");
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === "token") callbacks.onToken(data.content);
            else if (data.type === "citations") callbacks.onCitations(data.citations);
            else if (data.type === "done") callbacks.onDone();
          } catch {
            // Skip malformed lines
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        callbacks.onError(err.message);
      }
    });

  return controller;
}
