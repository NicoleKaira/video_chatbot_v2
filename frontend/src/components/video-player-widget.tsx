"use client";

import React, {useEffect, useState} from "react";
import {VideoSkeleton} from "@/components/stream-player/video";
import video_api from "@/api/video-indexer-widget";
import {useParams} from "next/navigation";

export const VideoPlayerWidget = () => {
  const [videoPlayerWidgetUrl, setVideoPlayerWidgetUrl] = useState<string>("");
  const { video_id } = useParams<{ video_id: string }>();

  useEffect(() => {
    const fetchVideoPlayerWidget = async () => {
      try {
        const data = await video_api.fetchVideoPlayerWidget(video_id);
        setVideoPlayerWidgetUrl(data.video_widget_url);
      } catch (error) {
        console.error("Error fetching video player URL:", error);
      }
    };

    fetchVideoPlayerWidget();
  }, [video_id]);

  if (!videoPlayerWidgetUrl) {
    return <StreamPlayerSkeleton />;
  }

  return (
    <div className="aspect-video border-b group relative">
      <iframe
        className="w-full h-full"
        src={videoPlayerWidgetUrl}
        allowFullScreen
        title="Video Player"
      ></iframe>
    </div>
  );
}

export function StreamPlayerSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:gap-y-0 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-6 w-full h-full">
      <VideoSkeleton />
    </div>
  );
}



