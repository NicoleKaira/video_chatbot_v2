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
import {useForm} from "react-hook-form";
import { z } from "zod";
import React, {useState} from "react";
import {Textarea} from "@/components/ui/textarea";
import {CourseDetails} from "@/model/Course";
import courseChange from "@/api/course-update"
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle} from "@/components/ui/dialog";
import {router} from "next/client";
import deleteCourse from "@/api/delete-course";

const formSchema = z.object({
  courseCode: z.string().min(1, "Course Code is required"),
  courseName: z.string().min(1, "Course Name is required"),
  courseDescription: z.string().nullable().optional(),
  // courseNotifications: z.array(z.string().min(1, "Notification is required")).optional(),
});

export type formCourseSchema = z.infer<typeof formSchema>;

export default function CourseDetailForm(course: CourseDetails) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      courseCode: course.courseCode,
      courseName: course.courseName,
      courseDescription: course.courseDescription,
      // courseNotifications: course.courseNotification || [],
    },
  });

  // const { fields, append, remove } = useFieldArray({
  //   control: form.control,
  //   // @ts-expect-error only accepts array of object for name field
  //   name: "courseNotifications"
  // });

  const [isEditable, setIsEditable] = useState(false); // State to toggle edit mode
  const [isDialogOpen, setDialogOpen] = useState(false);

  const onSubmit = async (data: formCourseSchema) => {
    await courseChange.triggerCourseUpdate(data);
  };

  const saveEdit = () => {
    if (isEditable) {
      form.handleSubmit(onSubmit)();
      setIsEditable(false);
    } else {
      setIsEditable(true);
    }
  };

  const handleDelete = () => {
    deleteCourse.deleteCourse(course.courseCode)
    router.push(`manage/`);
  };

  const openDialog = () => {
    setDialogOpen(true)
  };


  return (
    <div className="relative">
      <Form {...form}>
        <div className="flex justify-end gap-4 mt-4">
          <Button
            onClick={openDialog} // Toggle edit mode
            variant={"destructive"}
          >
            Delete
          </Button>
          <Button
            onClick={saveEdit} // Toggle edit mode
            variant={isEditable ? "primary" : "default"}
          >
            {isEditable ? "Save" : "Edit"}
          </Button>
        </div>
        <form onSubmit={form.handleSubmit(onSubmit)} className="w-full">
          {/* Course Code Field */}
          <FormField
            control={form.control}
            name="courseCode"
            render={({field}) => (
              <FormItem>
                <FormLabel>Course Code</FormLabel>
                <FormControl>
                  <Input placeholder={course.courseCode} {...field} disabled={true}/>
                </FormControl>
                <FormDescription>
                  This is the course identifier.
                </FormDescription>
                <FormMessage/>
              </FormItem>
            )}
          />

          {/* Course Name Field */}
          <FormField
            control={form.control}
            name="courseName"
            render={({field}) => (
              <FormItem>
                <FormLabel>Course Name</FormLabel>
                <FormControl>
                  <Input placeholder={course.courseName} {...field} disabled={!isEditable}/>
                </FormControl>
                <FormDescription>
                  This is the full name of the course.
                </FormDescription>
                <FormMessage/>
              </FormItem>
            )}
          />

          {/* Course Description */}
          <FormField
            control={form.control}
            name="courseDescription"
            render={({field}) => (
              <FormItem>
                <FormLabel>Course Description</FormLabel>
                <FormControl>
                  <Textarea placeholder={course.courseDescription || ""} {...field} value={field.value || ""}
                            disabled={!isEditable}/>
                </FormControl>
                <FormDescription>
                  This is the full name of the course.
                </FormDescription>
                <FormMessage/>
              </FormItem>
            )}
          />

          <Dialog open={isDialogOpen} onOpenChange={setDialogOpen}>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Are you sure you want to delete the course?</DialogTitle>
              </DialogHeader>
              <DialogFooter>
                <Button onClick={handleDelete} type="submit" variant={"destructive"}>Yes</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Course Notifications Field */}
          {/*<div className={"flex flex-col"}>*/}
          {/*<FormLabel>Course Notifications</FormLabel>*/}
          {/*{fields.map((item, index) => (*/}
          {/*  <div key={item.id} className="flex items-center space-x-4 py-2">*/}
          {/*    <div className="w-full">*/}
          {/*      <FormField*/}
          {/*        control={form.control}*/}
          {/*        name={`courseNotifications.${index}`}*/}
          {/*        render={({field}) => (*/}
          {/*          <FormItem>*/}
          {/*            <FormControl>*/}
          {/*              <Input placeholder="Enter notification" {...field} value={field.value || ""} disabled={!isEditable} />*/}
          {/*            </FormControl>*/}
          {/*            <FormMessage/>*/}
          {/*          </FormItem>*/}
          {/*        )}*/}
          {/*      />*/}
          {/*    </div>*/}
          {/*      <Button*/}
          {/*      type="button"*/}
          {/*      onClick={() => remove(index)} // Remove the notification field*/}
          {/*      className="text-red-500 hover:text-red-700"*/}
          {/*      disabled={!isEditable}*/}
          {/*    >*/}
          {/*      <Trash2 size={20}/>*/}
          {/*    </Button>*/}
          {/*  </div>*/}
          {/*))}*/}

          {/*/!* Add Notification Button *!/*/}
          {/*  <Button*/}
          {/*    type="button"*/}
          {/*    onClick={() => append("")} // Append an empty string to create a new notification input*/}
          {/*    className="text-white bg-blue-600 hover:bg-blue-700 w-full"*/}
          {/*    disabled={!isEditable}*/}
          {/*  >*/}
          {/*    <Plus size={20} className="mr-2"/>*/}
          {/*    Add Notification*/}
          {/*  </Button>*/}
          {/*</div>*/}
        </form>
      </Form>
    </div>
  );
}