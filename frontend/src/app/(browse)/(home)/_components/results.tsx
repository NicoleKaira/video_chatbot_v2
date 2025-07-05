"use client"

import React, {useEffect, useState} from "react";

import { getStreams } from "@/api/feed-service";
import { Skeleton } from "@/components/ui/skeleton";

import { ResultCard, ResultCardSkeleton } from "./result-card";
import {Button} from "@/components/ui/button";

interface Video {
  summary: string;
  videoId: string;
  videoName: string;
  thumbnail: string | null;
}

interface Course {
  courseName: string;
  courseCode: string;
  courseVideos: Video[];
}

export function Results() {
  const [data, setData] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string | null>("all");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const fetchedData = await getStreams();
        console.log(fetchedData);
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

  const filteredCourses = selectedCourse
    ? selectedCourse === "all" ? data: data.filter((course) => course.courseName === selectedCourse)
    : data;

  return (
    <>
      {data && data.length > 0 && (
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
      )}
      {filteredCourses && filteredCourses.map((course: Course) => (
        <div key={course.courseName}>
          <h2 className="text-lg font-semibold mb-4">
            {course.courseName}
          </h2>
          <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
            {course.courseVideos.map((video: Video) => (
              <ResultCard key={video.videoId} data={video}/>
            ))}
          </div>
        </div>
      ))
      }
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
