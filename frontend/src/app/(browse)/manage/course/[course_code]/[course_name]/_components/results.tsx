"use client"

import React, {useEffect, useState} from "react";

import {Skeleton} from "@/components/ui/skeleton";

import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table";
import {Thumbnail, ThumbnailSkeleton} from "@/components/thumbnail";
import {useParams, useRouter} from "next/navigation";
import {useVideoContext} from "@/context/video-context";
import {SelectOptions} from "@/components/options-select";
import CourseDetailForm from "@/app/(browse)/manage/course/[course_code]/[course_name]/_components/course-details-form";
import {Visibility} from "@/model/Visibility";
import {Type, Course, Video} from "@/model/Course";
import {Button} from "@/components/ui/button";
import {getManageStreams} from "@/api/feed-service-manage";

export function Results() {
  const { course_code, course_name } = useParams<{ course_code: string, course_name: string }>();
  const decodedCourseCode = decodeURIComponent(course_code);
  const decodedCourseName = decodeURIComponent(course_name);

  const [data, setData] = useState<Course[]>([]);

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

  const filteredVideos = (decodedCourseName && decodedCourseName)
    ? data.flatMap(course =>
      course.courseName === decodedCourseName && course.courseCode === decodedCourseCode
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

    router.push(`/manage/${data.videoId}`);
  };

  return (
    <>
      {data && data.length > 0 && (
        <>
          <CourseDetailForm
            courseCode={decodedCourseCode}
            courseName={decodedCourseName}
            courseDescription={""}
            // courseNotification={[]}
          />
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
                      disabled={video.status !== 'COMPLETED'}
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
