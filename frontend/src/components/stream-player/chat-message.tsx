"use client";

import React from "react";
import {format} from "date-fns";

import {OngoingChatMessage, Role} from "@/components/stream-player/OngoingChatMessage";
import Image from "next/image";
import userIcon from "@/assets/images/user.svg"
import botIcon from "@/assets/images/bot.svg"


// Typing indicator component for loading state
const TypingIndicator = () => {
  return (
    <div className="flex items-center gap-1">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
      <span className="text-sm text-white/60 ml-2">AI is thinking...</span>
    </div>
  );
};

export function ChatMessage({ data }: { data: OngoingChatMessage }) {

  const formatMessage = (message: string) => {
    const formattedMessage = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    const parts = formattedMessage.split("\n");
    return parts.map((part, index) => (
      <span key={index}>
        <span dangerouslySetInnerHTML={{__html: part}}/>
        {index < parts.length - 1 && <br/>}
    </span>
    ));
  };

  return (
    <div className="flex p-2 gap-2 rounded-md hover:bg-white/5">
      <div className="flex-shrink-0">
        <Image
          className="h-[26px] w-[26px]"
          src={data.role === Role.User ? userIcon : botIcon}
          alt="user"
        />
      </div>
      <div className="flex flex-col justify-center gap-1 grow">
        <p className="text-sm text-white/40">{format(data.timestamp, "HH:MM")}</p>
        {data.role === Role.Loading ? (
          <TypingIndicator />
        ) : (
          <p className="text-sm whitespace-pre-wrap break-normal">{formatMessage(data.message)}</p>
        )}
      </div>
    </div>
  );

}