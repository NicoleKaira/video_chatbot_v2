"use client";

import React, {useEffect, useMemo, useRef, useState} from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const generateId = (): string => {
  if (typeof window !== "undefined" && window.crypto) {
    const anyCrypto = window.crypto as unknown as { randomUUID?: () => string; getRandomValues?: (arr: Uint8Array) => Uint8Array };
    if (typeof anyCrypto.randomUUID === "function") return anyCrypto.randomUUID();
    if (typeof anyCrypto.getRandomValues === "function") {
      const bytes = new Uint8Array(16);
      anyCrypto.getRandomValues(bytes);
      bytes[6] = (bytes[6] & 0x0f) | 0x40; // version 4
      bytes[8] = (bytes[8] & 0x3f) | 0x80; // variant
      const toHex = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
      return `${toHex.slice(0, 8)}-${toHex.slice(8, 12)}-${toHex.slice(12, 16)}-${toHex.slice(16, 20)}-${toHex.slice(20)}`;
    }
  }
  return `id-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: generateId(),
      role: "assistant",
      content: "Hi! I'm your study assistant. Ask me anything about your videos lectures.",
    },
  ]);
  const [input, setInput] = useState("");
  const listRef = useRef<HTMLDivElement | null>(null);
  const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL || "";
  const VIDEO_ID = "zwb6lqhpzl"; // TODO: replace with the actual Azure Video Indexer video_id

  const canSend = useMemo(() => input.trim().length > 0, [input]);

  //automatically scroll when new message appear
  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages.length]);

  // Helper to convert local messages into API's previous_messages shape
  const buildPreviousMessages = (history: ChatMessage[]) => {
    const pairs: { user_input: string; assistant_response: string }[] = [];
    let lastUser: string | null = null;
    for (const m of history) {
      if (m.role === "user") {
        lastUser = m.content;
      } else if (m.role === "assistant" && lastUser) {
        pairs.push({ user_input: lastUser, assistant_response: m.content });
        lastUser = null;
      }
    }
    return pairs;
  };

  //sending the message 
  const sendMessage = async () => {
    if (!canSend) return; //no empty messages 

    const userMsg: ChatMessage = {
      id: generateId(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMsg]); // Add your previous message 
    setInput("");

    try {
      const previous_messages = buildPreviousMessages([...messages, userMsg]);
      const res = await fetch(`${BASE_URL}/chat/${VIDEO_ID}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ previous_messages, message: userMsg.content })
      });
      if (!res.ok) throw new Error("Chat API failed");
      const data = await res.json();
      const answer: string = data?.answer ?? "";
      const assistantMsg: ChatMessage = {
        id: generateId(),
        role: "assistant",
        content: answer || "(No answer returned)"
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      const errorMsg: ChatMessage = {
        id: generateId(),
        role: "assistant",
        content: "Sorry, I couldn't reach the chat service."
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] w-full flex-col gap-4 p-4 md:px-8">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Video Lecture Chatbot</h1>
      </div>

      <div className="grid h-full grid-rows-2 gap-4 md:grid-cols-2 md:grid-rows-1">
        {/* Left: YouTube player */}
        <Card className="p-4">
          <div className="relative h-full w-full">
            <div className="relative w-full pt-[56.25%]">{/* 16:9 ratio */}
              <iframe
                className="absolute left-0 top-0 h-full w-full rounded-md"
                src="https://www.youtube.com/live/gn-GUwOsLMo?si=NsxXqe-wRZLchH6k"
                title="YouTube video player"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
              />
            </div>
          </div>
        </Card>

        {/* Right: Chat UI */}
        <Card className="flex h-full flex-col p-0">
          <div ref={listRef} className="flex-1 space-y-4 overflow-y-auto p-4">
            {messages.map((m) => (
              <div key={m.id} className={`flex w-full ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] rounded-md px-3 py-2 text-sm leading-relaxed shadow-sm ${
                    m.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}
          </div>

          <div className="border-t p-3">
            <div className="flex items-center gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
              />
              <Button onClick={sendMessage} disabled={!canSend}>
                Send
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}


