"use client"

import React, {useEffect, useState} from "react";

import { Skeleton } from "@/components/ui/skeleton";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import {ThumbnailSkeleton} from "@/components/thumbnail";
import {useRouter} from "next/navigation";
import {SelectOptions} from "@/components/options-select";
import {Button} from "@/components/ui/button";
import {Visibility} from "@/model/Visibility";
import {Course, Type} from "@/model/Course";
import {getManageStreams} from "@/api/feed-service-manage";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import {Label} from "@/components/ui/label";
import {Input} from "@/components/ui/input";
import {Textarea} from "@/components/ui/textarea";
import {addNewCourse} from "@/api/add-course";

export function Results() {
  const [data, setData] = useState<Course[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [courseCode, setCourseCode] = useState("")
  const [courseName, setCourseName] = useState("")
  const [courseDescription, setCourseDescription] = useState("")


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

  const router = useRouter();

  const handleCourseClick = (courseCode: string, courseName: string) => {
    router.push(`course/${courseCode}/${courseName}`);
  };

  // Handle dialog open
  const handleAddCourse = () => {
    setIsDialogOpen(true);
  };

  const addCourse = async () => {
    const data = await addNewCourse(courseCode, courseName, courseDescription);
    console.log(data);
    if (data) {
      setIsDialogOpen(false);
      window.location.reload();
    }
  };

  return (
    <>
      {data && data.length > 0 && (
        <>
          <Table className={"table-fixed"}>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[200px]">Course Code</TableHead>
                <TableHead>Course Name</TableHead>
                <TableHead>Total Videos</TableHead>
                <TableHead>Visibility</TableHead>
                <TableHead className="flex justify-end">
                  <Button
                    onClick={handleAddCourse}
                    variant="primary"
                  >
                    Add Course
                  </Button>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((course) => (
                <React.Fragment key={course.courseCode + course.courseName}>
                  <TableRow>
                    <TableCell>{course.courseCode}</TableCell>
                    <TableCell>{course.courseName}</TableCell>
                    <TableCell>{course.courseVideos.length}</TableCell>
                    <TableCell>
                      <SelectOptions currentOption={Visibility[course.visibility as keyof typeof Visibility]} type={Type.COURSE} id={course.courseCode} disabled={false}
                      />
                    </TableCell>
                    <TableCell className="flex justify-end">
                      <Button
                        onClick={() => handleCourseClick(course.courseCode, course.courseName)}
                        variant="outline"
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        </>
      )}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Add Course</DialogTitle>
            <DialogDescription>
              Enter your course details.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="coursecode" className="text-right">
                Code
              </Label>
              <Input
                id="coursecode"
                placeholder="Coursecode"
                className="col-span-3"
                onChange={(e) => setCourseCode(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="coursename" className="text-right">
                Name
              </Label>
              <Input
                id="coursename"
                placeholder="Course Name"
                className="col-span-3"
                onChange={(e) => setCourseName(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="coursedescription" className="text-right">
                Description
              </Label>
              <Textarea
                id="coursedescription"
                placeholder="Course Description"
                className="col-span-3"
                onChange={(e) => setCourseDescription(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button onClick={addCourse} variant="primary" type="submit">Add Course</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
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
