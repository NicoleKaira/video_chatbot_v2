"use client";

import React, {useEffect, useState} from "react";
import {Chat, ChatSkeleton} from "@/components/stream-player/chat";
import {cn} from "@/lib/utils";
import {useChatSidebar} from "@/store/use-chat-sidebar";
import {Header, HeaderSkeleton} from "@/components/stream-player/header";
import {Video, VideoSkeleton} from "@/components/stream-player/video";
import {AboutCard} from "@/components/stream-player/about-card";
import {ChatToggle} from "@/components/stream-player/chat-toggle";
import video_api from "@/api/video";
import {useParams} from "next/navigation";
import {useVideoContext} from "@/context/video-context";
import {toast} from "sonner";

export const StreamPlayer = () => {
  const { collapsed } = useChatSidebar((state) => state);
  const [videoWidgetUrl, setVideoWidgetUrl] = useState<string>("");
  const { video_id } = useParams<{ video_id: string }>();
  const { videoName, summary } = useVideoContext();


  useEffect(() => {
    const fetchVideoUrl = async () => {
      try {
        if (video_id) {
          const data = await video_api.fetchVideoWidget(video_id);
          setVideoWidgetUrl(data.video_widget_url);
        }
      } catch (error) {
        console.error("Error fetching video URL:", error);
        toast("Error fetching video URL:" + error)
      }
    };

    fetchVideoUrl().then();
  }, []);

  if (!videoWidgetUrl) {
    return <StreamPlayerSkeleton />;
  }

  return (
    <>
      {collapsed && (
        <div className="hidden lg:block fixed top-[100px] right-2 z-50">
          <ChatToggle />
        </div>
      )}
      <div
        className={cn(
          "grid grid-cols-1 lg:gap-y-0 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-6 w-full h-full",
          collapsed && "lg:grid-cols-2 xl:grid-cols-2 2xl:grid-cols-2"
        )}
      >
        <div
          className="space-y-4 col-span-1 lg:col-span-2 xl:col-span-2 2xl:col-span-5 lg:overflow-y-auto hidden-scrollbar pb-10">
          <Video videoWidgetUrl={videoWidgetUrl}/>
          <Header
            imageUrl=""
            hostName={videoName}
            name=""
          />
          <AboutCard
            hostName={videoName}
            bio={summary}
          />
        </div>
        <div className={cn("col-span-1", collapsed && "hidden")}>
          <Chat
            isChatEnabled={true} videoId={video_id}
          />
        </div>
      </div>
    </>
  );
}

export function StreamPlayerSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:gap-y-0 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-6 w-full h-full">
      <div className="space-y-4 col-span-1 lg:col-span-2 xl:col-span-2 2xl:col-span-5 lg:overflow-y-auto hidden-scrollbar pb-10">
        <VideoSkeleton />
        <HeaderSkeleton />
      </div>
      <div className="col-span-1 bg-background">
        <ChatSkeleton />
      </div>
    </div>
  );
}
