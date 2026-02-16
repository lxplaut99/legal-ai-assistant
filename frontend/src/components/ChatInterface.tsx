"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  type Citation,
  type Message,
  getConversation,
  sendMessage,
} from "@/lib/api";
import MessageBubble from "./MessageBubble";

interface ChatInterfaceProps {
  conversationId: string | null;
  onSaveAsDocument?: (content: string) => Promise<void>;
}

interface DisplayMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  isStreaming?: boolean;
}

export default function ChatInterface({ conversationId, onSaveAsDocument }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Load conversation messages when ID changes
  useEffect(() => {
    if (!conversationId) {
      setMessages([]);
      return;
    }
    getConversation(conversationId).then((conv) => {
      setMessages(
        conv.messages.map((m) => ({
          id: m.id,
          role: m.role as "user" | "assistant",
          content: m.content,
          citations: m.citations ? JSON.parse(m.citations) : undefined,
        }))
      );
    });
  }, [conversationId]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(() => {
    if (!input.trim() || !conversationId || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setIsLoading(true);

    // Add user message
    const userMsg: DisplayMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: userMessage,
    };

    // Add placeholder for assistant
    const assistantMsg: DisplayMessage = {
      id: `assistant-${Date.now()}`,
      role: "assistant",
      content: "",
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);

    const assistantId = assistantMsg.id;

    abortRef.current = sendMessage(conversationId, userMessage, {
      onToken(token) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: m.content + token } : m
          )
        );
      },
      onCitations(citations) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, citations } : m
          )
        );
      },
      onDone() {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, isStreaming: false } : m
          )
        );
        setIsLoading(false);
      },
      onError(error) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: `Error: ${error}`, isStreaming: false }
              : m
          )
        );
        setIsLoading(false);
      },
    });
  }, [input, conversationId, isLoading]);

  if (!conversationId) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        <div className="text-center">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <p className="text-lg font-medium">No conversation selected</p>
          <p className="text-sm mt-1">Create a new conversation and upload documents to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-lg font-medium">Ask a question about your documents</p>
            <p className="text-sm mt-1">Upload documents in the sidebar, then ask questions here</p>
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            role={msg.role}
            content={msg.content}
            citations={msg.citations}
            isStreaming={msg.isStreaming}
            onSaveAsDocument={onSaveAsDocument}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 bg-white px-6 py-4">
        <div className="flex gap-3 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask a question or request a document..."
            rows={1}
            className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="bg-blue-600 text-white rounded-xl px-5 py-3 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
            ) : (
              "Send"
            )}
          </button>
        </div>
        <p className="text-[10px] text-gray-400 mt-2 text-center">
          AI assistant for licensed attorneys. Responses do not constitute legal advice.
        </p>
      </div>
    </div>
  );
}
