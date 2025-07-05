"use client";

import React from "react";
import {format} from "date-fns";

import {OngoingChatMessage, Role} from "@/components/stream-player/OngoingChatMessage";
import Image from "next/image";
import userIcon from "@/assets/images/user.svg"
import botIcon from "@/assets/images/bot.svg"


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
        <p className="text-sm whitespace-pre-wrap break-normal">{formatMessage(data.message)}</p>
      </div>
    </div>
  );

}