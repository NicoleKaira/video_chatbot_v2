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
import {addNewCourse} from "@/api/add-course";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card";
import {BookCheck} from "lucide-react";
import {Label} from "@/components/ui/label";
import {Input} from "@/components/ui/input";
import {Textarea} from "@/components/ui/textarea";
import {toast} from "sonner";

export function Results() {
  const [data, setData] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string | null>("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreatingCourse, setIsCreatingCourse] = useState(false);
  const [courseCode, setCourseCode] = useState("");
  const [courseName, setCourseName] = useState("");
  const [courseDescription, setCourseDescription] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const fetchedData = await getManageStreams();
        setData(fetchedData || []);
      } catch (error) {
        console.error("Failed to fetch data:", error);
        setData([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleCreateCourse = async () => {
    if (!courseCode.trim() || !courseName.trim() || !courseDescription.trim()) {
      toast.error("Please fill in all fields");
      return;
    }

    setIsCreatingCourse(true);
    try {
      await addNewCourse(courseCode.trim(), courseName.trim(), courseDescription.trim());
      toast.success("Course created successfully!");
      // Refresh the data
      const fetchedData = await getManageStreams();
      setData(fetchedData || []);
      // Reset form
      setCourseCode("");
      setCourseName("");
      setCourseDescription("");
    } catch (error: any) {
      console.error("Failed to create course:", error);
      const errorMessage = error?.response?.data?.message || "Failed to create course. Please try again.";
      toast.error(errorMessage);
    } finally {
      setIsCreatingCourse(false);
    }
  };

  const handleButtonClick = (courseName: string) => {
    if (courseName === "all") {
      setSelectedCourse(null);
    }
    setSelectedCourse(courseName === selectedCourse ? null : courseName);
  };

  const filteredVideos = selectedCourse
    ? (data || []).flatMap(course =>
        course.courseName === selectedCourse || selectedCourse === "all"
          ? (course.courseVideos || []).map((video) => ({
              ...video,
              courseName: course.courseName,
            }))
          : []
      )
    : (data || []).flatMap(course =>
        (course.courseVideos || []).map((video) => ({
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

  // Show loading skeleton
  if (isLoading) {
    return <ResultsSkeleton />;
  }

  // Show course creation form if no courses exist
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <BookCheck className="w-16 h-16 text-muted-foreground" />
            </div>
            <CardTitle className="text-2xl">No Courses Found</CardTitle>
            <CardDescription className="text-base mt-2">
              Create your first course to start uploading videos and managing content.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="course-code">Course Code *</Label>
              <Input
                id="course-code"
                placeholder="e.g., CS101"
                value={courseCode}
                onChange={(e) => setCourseCode(e.target.value)}
                disabled={isCreatingCourse}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="course-name">Course Name *</Label>
              <Input
                id="course-name"
                placeholder="e.g., Introduction to Computer Science"
                value={courseName}
                onChange={(e) => setCourseName(e.target.value)}
                disabled={isCreatingCourse}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="course-description">Course Description *</Label>
              <Textarea
                id="course-description"
                placeholder="Enter a description for your course"
                value={courseDescription}
                onChange={(e) => setCourseDescription(e.target.value)}
                disabled={isCreatingCourse}
                rows={4}
              />
            </div>
            <Button
              onClick={handleCreateCourse}
              disabled={isCreatingCourse || !courseCode.trim() || !courseName.trim() || !courseDescription.trim()}
              className="w-full"
              size="lg"
            >
              {isCreatingCourse ? "Creating Course..." : "Create Course"}
            </Button>
            <p className="text-xs text-muted-foreground text-center mt-2">
              Once created, you can upload videos and start using the chat feature.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
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
          {filteredVideos.length > 0 ? (
            filteredVideos.map((video) => (
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
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={5} className="text-center py-8">
                <p className="text-muted-foreground">No videos found.</p>
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
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
