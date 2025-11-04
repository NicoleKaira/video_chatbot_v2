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
import deleteCourse from "@/api/delete-course";
import {toast} from "sonner";
import {Trash2, BookCheck} from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card";

export function Results() {
  const [data, setData] = useState<Course[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [courseCode, setCourseCode] = useState("")
  const [courseName, setCourseName] = useState("")
  const [courseDescription, setCourseDescription] = useState("")
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [courseToDelete, setCourseToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreatingCourse, setIsCreatingCourse] = useState(false);

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

  const router = useRouter();

  const handleCourseClick = (courseCode: string, courseName: string) => {
    router.push(`course/${courseCode}/${courseName}`);
  };

  // Handle dialog open
  const handleAddCourse = () => {
    setIsDialogOpen(true);
  };

  const addCourse = async () => {
    if (!courseCode.trim() || !courseName.trim() || !courseDescription.trim()) {
      toast.error("Please fill in all fields");
      return;
    }

    setIsCreatingCourse(true);
    try {
      const data = await addNewCourse(courseCode.trim(), courseName.trim(), courseDescription.trim());
      console.log(data);
      if (data) {
        toast.success("Course created successfully!");
        setIsDialogOpen(false);
        setCourseCode("");
        setCourseName("");
        setCourseDescription("");
        // Refresh the data
        const fetchedData = await getManageStreams();
        setData(fetchedData || []);
      }
    } catch (error: any) {
      console.error("Failed to create course:", error);
      const errorMessage = error?.response?.data?.message || "Failed to create course. Please try again.";
      toast.error(errorMessage);
    } finally {
      setIsCreatingCourse(false);
    }
  };

  const handleDeleteClick = (courseCode: string) => {
    setCourseToDelete(courseCode);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!courseToDelete) return;
    
    setIsDeleting(true);
    try {
      await deleteCourse.deleteCourse(courseToDelete);
      toast.success("Course deleted successfully!");
      setDeleteDialogOpen(false);
      setCourseToDelete(null);
      // Refresh the data
      const fetchedData = await getManageStreams();
      setData(fetchedData);
    } catch (error: any) {
      console.error("Failed to delete course:", error);
      const errorMessage = error?.response?.data?.message || "Failed to delete course. Please try again.";
      toast.error(errorMessage);
    } finally {
      setIsDeleting(false);
    }
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
              onClick={addCourse}
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
                    <TableCell className="flex justify-end gap-2">
                      <Button
                        onClick={() => handleDeleteClick(course.courseCode)}
                        variant="destructive"
                        size="sm"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
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

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Course</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this course? This action cannot be undone and will delete all associated videos and data.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
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
