"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useMediaQuery } from "usehooks-ts";
import {OngoingChatMessage, Role} from "./OngoingChatMessage"

import { ChatHeader, ChatHeaderSkeleton } from "./chat-header";
import { ChatForm, ChatFormSkeleton } from "./chat-form";
import { ChatList, ChatListSkeleton } from "./chat-list";
import {useChatSidebar} from "@/store/use-chat-sidebar";
import {getChatResponse} from "@/api/chat-response";

export function Chat({isChatEnabled, videoId}: {
  isChatEnabled: boolean;
  videoId: string
}) {
  const matches = useMediaQuery("(max-width: 1024px)");
  const { onExpand } = useChatSidebar((state) => state);
  const isHidden = !isChatEnabled;

  const [value, setValue] = useState("");
  const [messages, setMessages] = useState<OngoingChatMessage[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (matches) {
      onExpand();
    }
  }, [matches, onExpand]);

  const reversedMessages = useMemo(() => {
    return messages.sort((a, b) => b.timestamp - a.timestamp);
  }, [messages]);

  const onSubmit = async () => {
    const trimmedMessage = value.trim();
    if (!trimmedMessage) return;
    setIsSubmitting(true);

    // Add user message to the chat
    const newMessages = [
      ...messages,
      { role: Role.User, message: trimmedMessage, timestamp: Date.now() },
    ];
    setMessages(newMessages); // Update messages state with user message

    setValue(""); // Clear the input field

    try {
      // Call external API to get the chat response
      const messagesCopy = JSON.parse(JSON.stringify(messages));
      const response = await getChatResponse(videoId, messagesCopy, trimmedMessage);
      const updateMessages = [
        ...newMessages,
        { role: Role.Assistant, message: response, timestamp: Date.now() },
      ];
      setMessages(updateMessages); // Update messages state with user message

    } catch (error) {
      console.error("Error fetching chat response:", error);
    } finally {
      // Re-enable input field after the API call completes
      setIsSubmitting(false);
    }
  };

  const onChange = (value: string) => {
    setValue(value);
  };

  return (
    <div className="flex flex-col bg-background border-l border-b pt-0 h-[calc(100vh-80px)]">
      <ChatHeader />
        <ChatList messages={reversedMessages} isHidden={isHidden} />
        <ChatForm
          onSubmit={onSubmit}
          value={value}
          onChange={onChange}
          isHidden={isHidden}
          disabled={isSubmitting}
        />
    </div>
  );
}

export function ChatSkeleton() {
  return (
    <div className="flex flex-col border-l border-b pt-0 h-[calc(100vh-80px)] border-2">
      <ChatHeaderSkeleton />
      <ChatListSkeleton />
      <ChatFormSkeleton />
    </div>
  );
}