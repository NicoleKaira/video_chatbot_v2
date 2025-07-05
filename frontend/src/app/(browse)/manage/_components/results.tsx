"use client"

import React, {useEffect, useState} from "react";

import { Skeleton } from "@/components/ui/skeleton";

import { ResultCardSkeleton } from "./video-info-card";
import {Button} from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import {Thumbnail} from "@/components/thumbnail";
import {useRouter} from "next/navigation";
import {useVideoContext} from "@/context/video-context";
import {SelectOptions} from "@/components/options-select";
import {Visibility} from "@/model/Visibility";
import {Course, Type, Video} from "@/model/Course";
import {getManageStreams} from "@/api/feed-service-manage";

export function Results() {
  const [data, setData] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string | null>("all");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const fetchedData = await getManageStreams();
        setData(fetchedData);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
    };

    fetchData();
  }, []);

  const handleButtonClick = (courseName: string) => {
    if (courseName === "all") {
      setSelectedCourse(null);
    }
    setSelectedCourse(courseName === selectedCourse ? null : courseName);
  };

  const filteredVideos = selectedCourse
    ? data.flatMap(course =>
      course.courseName === selectedCourse || selectedCourse === "all"
        ? course.courseVideos.map((video) => ({
          ...video,
          courseName: course.courseName,
        }))
        : []
    )
    : data.flatMap(course =>
      course.courseVideos.map((video) => ({
        ...video,
        courseName: course.courseName,
      }))
    );

  const router = useRouter();
  const { setVideoData } = useVideoContext();

  const handleClick = (data: Video) => {
    setVideoData(data.videoId, data.videoName, data.summary);

    router.push(`manage/${data.videoId}`);
  };

  return (
    <>
      {data && data.length > 0 && (
        <>
          <div className="mb-4">
            <div className="flex gap-4 mb-6">
              <Button
                key={"all"}
                variant={selectedCourse === "all" ? "default" : "unchecked"}
                onClick={() => handleButtonClick("all")}
              >
                All
              </Button>
              {data.map((course: Course) => (
                <Button
                  key={course.courseName}
                  variant={selectedCourse === course.courseName ? "default" : "unchecked"}
                  onClick={() => handleButtonClick(course.courseName)}
                >
                  {course.courseName}
                </Button>
              ))}
            </div>
          </div>
          <Table className={"table-fixed"}>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[200px]">Video</TableHead>
                <TableHead>Video Title</TableHead>
                <TableHead>Course Title</TableHead>
                <TableHead>Visibility</TableHead>
                <TableHead className="text-right">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredVideos.map((video) => (
                <TableRow key={video.videoId}>
                  <TableCell>
                    <Thumbnail
                      src={video.thumbnail}
                      fallback={""}
                      username={video.videoName}
                      hover={false}
                    />
                  </TableCell>
                  <TableCell>{video.videoName}</TableCell>
                  <TableCell>{video.courseName}</TableCell>
                  <TableCell>
                    <SelectOptions currentOption={Visibility[video.visibility as keyof typeof Visibility]} type={Type.VIDEO} id={video.videoId} disabled={video.status !== 'COMPLETED'}
                    />
                  </TableCell>
                  <TableCell className="text-right">{video.status}</TableCell>
                  <TableCell className="text-right">
                    <Button
                      onClick={() => {handleClick(video)}}
                      variant="outline"
                    >
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </>
      )}
    </>
  );
}

export function ResultsSkeleton() {
  return (
    <div>
      <Skeleton className="h-8 w-[290px] mb-4"/>
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
        {[...Array(4)].map((_, i) => (
          <ResultCardSkeleton key={i}/>
        ))}
      </div>
    </div>
  );
}
