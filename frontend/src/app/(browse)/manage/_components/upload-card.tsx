"use client"

import React from "react";

import { Thumbnail, ThumbnailSkeleton } from "@/components/thumbnail";
import { Skeleton } from "@/components/ui/skeleton";
import upload from "@/assets/images/upload.svg"

export function UploadCard() {

  const handleClick = () => {
    console.log("clicked");
  };
  return (
    <div onClick={handleClick} className="h-full w-full space-y-4">
      <Thumbnail
        src={null}
        fallback={upload}
        username={"Upload"}
      />
      <div className="flex gap-x-3">
        <div className="flex flex-col text-sm overflow-hidden">
          <p className="truncate font-semibold hover:text-blue-500">
            Testing
          </p>
        </div>
      </div>
    </div>
  );
}

export function ResultCardSkeleton() {
  return (
    <div className="h-full w-full space-y-4">
      <ThumbnailSkeleton/>
      <div className="flex gap-x-3">
        <div className="flex flex-col gap-y-1">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-24" />
        </div>
      </div>
    </div>
  );
}
