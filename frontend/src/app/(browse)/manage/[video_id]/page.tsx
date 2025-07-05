"use client"

import { VideoIndexerWidget } from "@/components/video-indexer-widget";
import LectureDetailsForm from "@/app/(browse)/manage/[video_id]/_components/lecture-details-form";

export default function VideoIndexer() {
  return (
    <>
      <div>
        <LectureDetailsForm />
      </div>
      <div className={"p-10"}>
        <VideoIndexerWidget />
      </div>
    </>
  );
}
