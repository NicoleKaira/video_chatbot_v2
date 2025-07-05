import React from "react";
import Image from "next/image";

import { Skeleton } from "@/components/ui/skeleton";
import { UserAvatar } from "@/components/user-avatar";

export function Thumbnail({
  src,
  fallback,
  username,
  hover = true
}: {
  src: string | null;
  fallback: string;
  username: string;
  hover?: boolean;
}) {
  let content;

  if (!src) {
    content = (
      <div className={`bg-background flex flex-col items-center justify-center gap-y-4 h-full w-full ${hover ? "transition-transform group-hover:translate-x-2 group-hover:-translate-y-2" : ""} rounded-md`}>
        <UserAvatar
          size="lg"
          username={username}
          imageUrl={fallback}
        />
      </div>
    );
  } else {
    content = (
      <Image
        src={src}
        fill
        alt="Thumbnail"
        className={`object-cover ${hover ? "transition-transform group-hover:translate-x-2 group-hover:-translate-y-2" : ""} rounded-md`}
      />
    );
  }

  return (
    <div className="group aspect-video relative rounded-md cursor-pointer">
      <div className="rounded-md absolute inset-0 bg-blue-600 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center" />
      {content}
    </div>
  );
}

export function ThumbnailSkeleton() {
  return (
    <div className="group aspect-video relative rounded-xl cursor-pointer">
      <Skeleton className="h-full w-full" />
    </div>
  );
}
