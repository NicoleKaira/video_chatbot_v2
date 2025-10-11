"use client";

import React, {useEffect, useState} from "react";
import {Video, VideoSkeleton} from "@/components/stream-player/video";
import video_api from "@/api/video-indexer-widget";
import {useParams, usePathname} from "next/navigation";

export const VideoIndexerWidget = () => {
  const [videoIndexerWidgetUrl, setVideoIndexerWidgetUrl] = useState<string>("");
  const { video_id } = useParams<{ video_id: string }>();
  // const { videoName, summary } = useVideoContext();


  useEffect(() => {
    const fetchVideoIndexerWidget = async () => {
      try {
        const data = await video_api.fetchVideoIndexerWidget(video_id);
        console.log(data)
        setVideoIndexerWidgetUrl(data.video_insights_widget_url);
      } catch (error) {
        console.error("Error fetching video URL:", error);
      }
    };

    fetchVideoIndexerWidget().then();
  }, []);



  if (!videoIndexerWidgetUrl) {
    return <StreamPlayerSkeleton />;
  }

  return (
    <>
      <div className="aspect-video border-b group relative">
        <iframe
          className="w-full h-full"
          src={videoIndexerWidgetUrl}
          allowFullScreen
        ></iframe>
      </div>;
    </>
  );
}

export function StreamPlayerSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:gap-y-0 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-6 w-full h-full">
      <VideoSkeleton />
    </div>
  );
}
