"use client";

import React from "react";

import { Skeleton } from "@/components/ui/skeleton";

interface VideoProps {
  videoWidgetUrl: string;
}

export const Video: React.FC<VideoProps> = ({ videoWidgetUrl }) => {

  console.log(videoWidgetUrl);

  return <div className="aspect-video border-b group relative">
    <iframe
      className="w-full h-full"
      src={videoWidgetUrl}
      allowFullScreen
    ></iframe>
  </div>;
}

export function VideoSkeleton() {
  return (
    <div className="aspect-video border-x border-background">
      <Skeleton className="h-full w-full rounded-none"/>
    </div>
  );
}