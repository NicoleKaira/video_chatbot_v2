"use client";

import React, {useEffect, useMemo, useRef, useState} from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Thumbnail } from "@/components/thumbnail";
import { getManageStreams } from "@/api/feed-service-manage";
import video_api from "@/api/video-indexer-widget";
import { Course, Video } from "@/model/Course";

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
  // Course and videos state
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourseCode, setSelectedCourseCode] = useState<string>("");
  const [selectedVideos, setSelectedVideos] = useState<string[]>([]); // up to 2 ids for display
  const [selectedChatVideos, setSelectedChatVideos] = useState<string[]>([]); // all videos for chat context
  const [selectionMode, setSelectionMode] = useState<'display' | 'chat'>('chat'); // current selection mode
  const [playerUrlsByVideoId, setPlayerUrlsByVideoId] = useState<Record<string, string>>({});

  const canSend = useMemo(() => input.trim().length > 0, [input]);

  //automatically scroll when new message appear
  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages.length]);

  // load courses and videos mapping
  useEffect(() => {
    const loadCourses = async () => {
      try {
        const data = await getManageStreams();
        setCourses(data);
        // default to first course if exists
        if (data && data.length > 0) {
          setSelectedCourseCode((prev) => prev || data[0].courseCode);
        }
      } catch (e) {
        console.error("Failed to load courses", e);
      }
    };
    loadCourses();
  }, []);

  // fetch player URLs when selected videos change
  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const toFetch = selectedVideos.filter((id) => !playerUrlsByVideoId[id]);
        if (toFetch.length === 0) return;
        const results = await Promise.all(
          toFetch.map(async (id) => {
            const res = await video_api.fetchVideoPlayerWidget(id);
            return { id, url: res.video_widget_url as string };
          })
        );
        setPlayerUrlsByVideoId((prev) => {
          const next = { ...prev } as Record<string, string>;
          for (const { id, url } of results) next[id] = url;
          return next;
        });
      } catch (e) {
        console.error("Failed to load player URLs", e);
      }
    };
    if (selectedVideos.length > 0) fetchPlayers();
  }, [selectedVideos]);

  const currentCourse = useMemo(() => {
    return courses.find((c) => c.courseCode === selectedCourseCode);
  }, [courses, selectedCourseCode]);

  const courseVideos: (Video & { courseName: string })[] = useMemo(() => {
    if (!currentCourse) return [] as any;
    return currentCourse.courseVideos.map((v) => ({ ...v, courseName: currentCourse.courseName }));
  }, [currentCourse]);

  const toggleVideoSelection = (videoId: string) => {
    setSelectedVideos((prev) => {
      if (prev.includes(videoId)) return prev.filter((id) => id !== videoId);
      if (prev.length >= 2) return [prev[1], videoId]; // keep last + new
      return [...prev, videoId];
    });
  };

  const toggleChatVideoSelection = (videoId: string) => {
    setSelectedChatVideos((prev) => {
      if (prev.includes(videoId)) return prev.filter((id) => id !== videoId);
      return [...prev, videoId];
    });
  };

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
    if (!canSend) return; // no empty messages

    const userMsg: ChatMessage = {
      id: generateId(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMsg]); // Add your previous message 
    setInput("");

    try {
      const previous_messages = buildPreviousMessages([...messages, userMsg]);
      
      // Use chat video selection, or all videos if none selected
      const videoIdsToSend = selectedChatVideos.length > 0 
        ? selectedChatVideos 
        : courseVideos.map(v => v.videoId);
      
      const res = await fetch(`${BASE_URL}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          previous_messages, 
          message: userMsg.content,
          video_ids: videoIdsToSend,
          course_code: selectedCourseCode
        })
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
        <div className="flex items-center gap-2">
          <label className="text-sm font-bold">Course</label>
          <select
            className="border rounded px-2 py-1"
            value={selectedCourseCode}
              onChange={(e) => {
                setSelectedCourseCode(e.target.value);
                setSelectedVideos([]);
                setSelectedChatVideos([]);
              }}
          >
            {courses.map((c) => (
              <option key={c.courseCode} value={c.courseCode}>{c.courseCode} — {c.courseName}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid h-full gap-4 md:grid-cols-5 md:grid-rows-1">
        {/* Panel 1: Course selector + scrollable videos list */}
        <Card className="p-4 flex flex-col md:col-span-1">
          <div className="mb-4">
            <h2 className="text-lg font-bold text-white mb-2">Video Sources</h2>
            <div className="border-b border-gray-300 mb-4"></div>
            <div className="mb-3 flex gap-2">
              <button 
                className={`px-3 py-1 text-xs rounded ${selectionMode === 'chat' ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => setSelectionMode('chat')}
              >
                Chat Context (All)
              </button>
              <button 
                className={`px-3 py-1 text-xs rounded ${selectionMode === 'display' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => setSelectionMode('display')}
              >
                Display (2 max)
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 overflow-y-auto flex-1 pr-1">
            {courseVideos.map((v) => {
              const isDisplaySelected = selectedVideos.includes(v.videoId);
              const isChatSelected = selectedChatVideos.includes(v.videoId);
              const isSelected = selectionMode === 'display' ? isDisplaySelected : isChatSelected;
              
              return (
                <button
                  key={v.videoId}
                  onClick={() => {
                    if (selectionMode === 'display') {
                      toggleVideoSelection(v.videoId);
                    } else {
                      toggleChatVideoSelection(v.videoId);
                    }
                  }}
                  className={`text-left rounded-lg p-4 hover:bg-muted transition-all duration-200 ${
                    isSelected 
                      ? (selectionMode === 'display' ? "ring-2 ring-blue-500 bg-blue-50 border-2 border-white" : "ring-2 ring-green-500 bg-green-50 border-2 border-white")
                      : ""
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className="w-24 shrink-0">
                      <Thumbnail
                        src={v.thumbnail}
                        fallback={""}
                        username={v.videoName}
                        hover={false}
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-sm line-clamp-2 mb-1 ${isSelected ? "text-black" : "text-white"}`}>{v.videoName}</div>
                      <div className="text-sm text-muted-foreground font-medium">{v.courseName}</div>
                      {isDisplaySelected && selectionMode === 'chat' && (
                        <div className="text-xs text-blue-600 mt-1">📺 Display</div>
                      )}
                      {isChatSelected && selectionMode === 'display' && (
                        <div className="text-xs text-green-600 mt-1">💬 Chat</div>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </Card>

        {/* Panel 2: Two selected videos stacked with titles */}
        <Card className="p-4 flex flex-col md:col-span-2">
          <div className="mb-4">
            <h2 className="text-lg font-bold text-white mb-2">Video</h2>
            <div className="border-b border-gray-300 mb-4"></div>
          </div>
          
          <div className="space-y-2">
            {selectedVideos.length === 0 && (
              <div className="text-sm text-muted-foreground">Under the Display tab, select up to two videos from the left list.</div>
            )}
          {selectedVideos.slice(0, 2).map((vid) => {
            const url = playerUrlsByVideoId[vid];
            const video = courseVideos.find((v) => v.videoId === vid);
            if (!url) return null;
            return (
              <div key={vid} className="space-y-1">
                <div className="text-sm font-bold">{video?.videoName || vid}</div>
                <div className="relative w-full pt-[40%]">
                  <iframe
                    className="absolute left-0 top-0 h-full w-full rounded-md"
                    src={url}
                    title={`Video ${vid}`}
                    allowFullScreen
                  />
                </div>
              </div>
            );
          })}
          </div>
        </Card>

        {/* Panel 3: Chat UI */}
        <Card className="flex h-full flex-col p-0 md:col-span-2">
          <div className="p-4 border-b border-gray-300">
            <h2 className="text-lg font-bold text-white mb-2">Chat</h2>
          </div>
          <div ref={listRef} className="flex-1 space-y-4 overflow-y-auto p-4">
            {messages.map((m) => (
              <div key={m.id} className={`flex w-full gap-2 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                {m.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-lg shrink-0">
                    🤖
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-md px-3 py-2 text-base leading-relaxed shadow-sm ${
                    m.role === "user" ? "bg-blue-500 text-white" : "bg-white text-black border"
                  }`}
                >
                  {m.content}
                </div>
                {m.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-blue-200 flex items-center justify-center text-lg shrink-0">
                    👤
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Context Section */}
          <div className="border-t p-3 bg-gray-100">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-black">Context</h3>
              <span className="text-xs text-black">
                {selectedChatVideos.length > 0 ? `${selectedChatVideos.length} video${selectedChatVideos.length > 1 ? 's' : ''}` : 'All videos'}
              </span>
            </div>
            
            {/* Video Selection Dropdown */}
            <div className="mb-3">
              <select
                className="w-full text-xs border border-gray-300 rounded px-2 py-1 bg-white text-black"
                value=""
                onChange={(e) => {
                  if (e.target.value) {
                    toggleChatVideoSelection(e.target.value);
                    e.target.value = ""; // Reset dropdown
                  }
                }}
              >
                <option value="">Select content context</option>
                {courseVideos
                  .filter(v => !selectedChatVideos.includes(v.videoId))
                  .map((video) => (
                    <option key={video.videoId} value={video.videoId}>
                      {video.videoName}
                    </option>
                  ))}
              </select>
            </div>
            
            <div className="flex flex-wrap gap-1">
              {selectedChatVideos.length > 0 ? (
                selectedChatVideos.map((videoId) => {
                  const video = courseVideos.find((v) => v.videoId === videoId);
                  return (
                    <div
                      key={videoId}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-md border border-green-200"
                    >
                      <span className="text-green-600">📹</span>
                      <span className="truncate max-w-[120px]">{video?.videoName || videoId}</span>
                      <button
                        onClick={() => toggleChatVideoSelection(videoId)}
                        className="ml-1 text-green-600 hover:text-green-800"
                      >
                        ×
                      </button>
                    </div>
                  );
                })
              ) : (
                <div className="text-xs text-black italic">
                  Using all {courseVideos.length} videos as context
                </div>
              )}
            </div>
          </div>

          <div className="border-t p-4 bg-gray-50">
            <div className="flex items-center gap-3">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about any video content..."
                className="text-base py-3 px-4 border-2 focus:border-gray-300 focus:ring-0"
              />
              <Button 
                onClick={sendMessage} 
                disabled={!canSend}
                className="px-6 py-3 text-base font-medium"
              >
                Send
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}


