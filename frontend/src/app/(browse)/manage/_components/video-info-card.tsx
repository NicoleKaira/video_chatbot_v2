"use client"

import React from "react";

import { Thumbnail, ThumbnailSkeleton } from "@/components/thumbnail";
import { Skeleton } from "@/components/ui/skeleton";
import {useRouter} from "next/navigation";
import {useVideoContext} from "@/context/video-context";

export function ResultCard({
                             data,
                           }: {
  data: {
    summary: string;
    videoId: string;
    videoName: string;
    thumbnail: string | null;
  };
}) {

  const router = useRouter();
  const { setVideoData } = useVideoContext();

  const handleClick = () => {
    // Store video data in the context
    setVideoData(data.videoId, data.videoName, data.summary);

    // Navigate to the video page
    router.push(`manage/${data.videoId}`);
  };
  return (
    <div onClick={handleClick} className="h-full w-full space-y-4">
      <Thumbnail
        src={data.thumbnail}
        fallback={""}
        username={data.videoName}
      />
      <div className="flex gap-x-3">
        <div className="flex flex-col text-sm overflow-hidden">
          <p className="truncate font-semibold hover:text-blue-500">
            {data.videoName}
          </p>
        </div>
      </div>
    </div>
  );
}

export function ResultCardSkeleton() {
  return (
    <div className="h-full w-full space-y-4">
      <ThumbnailSkeleton />
      <div className="flex gap-x-3">
        <div className="flex flex-col gap-y-1">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-24" />
        </div>
      </div>
    </div>
  );
}
