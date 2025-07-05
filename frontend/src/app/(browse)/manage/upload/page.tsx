"use client";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl, FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { zodResolver } from "@hookform/resolvers/zod";
import {useFieldArray, useForm} from "react-hook-form";
import { z } from "zod";
import React, {useEffect, useState} from "react";
import {Plus, Trash2} from 'lucide-react';
import {uploadVideo} from "@/api/video-upload";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";
import {getManageStreams} from "@/api/feed-service-manage";
import {toast} from "sonner";
import {Textarea} from "@/components/ui/textarea";

const formSchema = z.object({
  courseCode: z.string().min(1, "Course Code is required"),
  videos: z.array(
    z.object({
      videoName: z.string().min(1, "Video Name is required"),
      file: z.instanceof(FileList || null).refine((val) => val.length === 1, { message: "Only one file is required" })
        .refine((file) => ["video/mp4"].includes(file[0].type), {message: "Invalid image file type"}),
      videoDescription: z.string().min(1, "Video Description is required"),
    })
  ).min(1, "At least one video must be added"),
});

export type FormDataUpload = z.infer<typeof formSchema>;

export default function UploadFile() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      courseCode: "",
      videos: [{ videoName: "", file: undefined, videoDescription: "" }]
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "videos",
  });

  const [courses, setCourses] = useState<{ courseCode: string; courseName: string }[]>([]);
  const [selectedCourseName, setSelectedCourseName] = useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const fetchedData = await getManageStreams();
        setCourses(fetchedData.map((course: { courseCode: string; courseName: string }) => ({
          courseCode: course.courseCode,
          courseName: course.courseName
        })));
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
    };

    fetchData();
  }, []);

  const handleCourseSelect = (courseCode: string) => {
    const selectedCourse = courses.find((course) => course.courseCode === courseCode);
    if (selectedCourse) {
      setSelectedCourseName(selectedCourse.courseName);
    }
  };

  // Manual handling of file input with useRef
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, index: number) => {
    const files = e.target.files;
    if (files) {
      // Update the files for the specific index in the form state
      if (files) {
        const file = files[0];

        // Ensure only .mp4 files are accepted
        if (file.type !== "video/mp4") {
          alert("Only MP4 files are allowed.");
          form.setValue(`videos.${index}.file`, new DataTransfer().files);
          e.target.value = "";
          return;
        } else {
          form.setValue(`videos.${index}.file`, files);
        }
      }
    }
  };

  const onSubmit = async (data: FormDataUpload) => {
    const status = await uploadVideo(data);
    if (status) {
      toast("Video successfully uploaded. Indexing might take a moment.")
    } else {
      toast("Video upload failed. Please contact an administrator.")
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="w-full p-10">
        {/* Course Code Field */}
        <FormField
          control={form.control}
          name="courseCode"
          render={({field}) => (
            <FormItem>
              <FormLabel>Course Code</FormLabel>
              <FormControl>
                <div className="flex flex-col space-y-2">  {/* Wrap Input and Select in a div */}
                  <Select value={field.value} onValueChange={(value) => {
                    field.onChange(value);
                    handleCourseSelect(value);
                  }}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder={field.value}/>
                    </SelectTrigger>
                    <SelectContent>
                      {courses.map((course) => (
                        <SelectItem key={course.courseCode} value={course.courseCode}>
                          {course.courseCode}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </FormControl>
              <FormDescription>
                This is the course identifier.
              </FormDescription>
              <FormMessage/>
            </FormItem>
          )}
        />

        {/* Display Selected Course Name */}
        <div className="mt-4">
          {selectedCourseName && (
            <p><strong>Selected Course: </strong>{selectedCourseName}</p>
          )}
        </div>

        {fields.map((item, index) => (
          <>
          <div key={item.id} className={"flex justify-between w-full border-t-2 py-2 align-center"}>
            <div className={"flex items-center"}>
              <Button
                type="button"
                onClick={() => remove(index)} // Remove the video entry
                className="text-red-500 hover:text-red-700 bg-transparent"
                disabled={fields.length === 1}
              >
                <Trash2 size={20}/>
              </Button>
            </div>

            <div className="w-3/4 px-2">
              <FormField
                control={form.control}
                name={`videos.${index}.videoName`}
                render={({field}) => (
                  <FormItem>
                    <FormLabel>Video Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Video Name" {...field} />
                    </FormControl>
                    <FormMessage/>
                  </FormItem>
                )}
              />
            </div>

            <div className="w-1/4 px-2">
              <FormField
                control={form.control}
                name={`videos.${index}.file`}
                render={() => (
                  <FormItem>
                    <FormLabel>File</FormLabel>
                    <FormControl>
                      <Input
                        type="file"
                        onChange={(e) => handleFileChange(e, index)}
                      />
                    </FormControl>
                    <FormMessage/>
                  </FormItem>
                )}
              />
            </div>

            {index === fields.length - 1 && (
              <div className={"flex items-center"}>
                <Button
                  type="button"
                  onClick={() => append({videoName: "", file: new DataTransfer().files, videoDescription: ""})}
                  className="text-white hover:text-red-700 bg-transparent"
                >
                  <Plus size={20}/>
                </Button>
              </div>
            )}

          </div>
          <div className="px-2 py-2">
            <FormField
            control={form.control}
              name={`videos.${index}.videoDescription`}
              render={({field}) => (
                <FormItem>
                  <FormLabel>Video Description</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Video Description" {...field} />
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />
          </div>
        </>
      )
    )}
  <div className={"flex py-4"}>
    <Button type="submit" variant={"primary"} className={"flex w-full"}>Submit</Button>
  </div>
</form>
</Form>
)
  ;
}