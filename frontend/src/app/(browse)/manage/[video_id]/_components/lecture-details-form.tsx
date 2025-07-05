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
import videoCourse from "@/api/video-update";
import {useVideoContext} from "@/context/video-context";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import deleteVideo from "@/api/delete-video";
import {router} from "next/client";
import {ShareDialog} from "@/app/(browse)/manage/[video_id]/_components/shareDialog";

const formSchema = z.object({
  videoName: z.string().min(1, "Course Code is required"),
  videoDescription: z.string().min(1, "Course Name is required"),
});

export type formLectureSchema = z.infer<typeof formSchema>;

export default function LectureDetailsForm() {
  const { videoId, videoName, summary } = useVideoContext();
  const [isDialogOpen, setDialogOpen] = useState(false);
  const [isDialogShareOpen, setDialogShareOpen] = useState(false);


  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      videoName: videoName,
      videoDescription: summary,
    },
  });

  const [isEditable, setIsEditable] = useState(false); // State to toggle edit mode

  const onSubmit = async (data: formLectureSchema) => {
    await videoCourse.triggerVideoUpdate(videoId, data);
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
    deleteVideo.deleteVideo(videoId)
    router.push(`manage/`);
  };

  const openDialog = () => {
    setDialogOpen(true)
  };

  const openDialogShare = () => {
    setDialogShareOpen(true)
  };

  return (
    <div className="relative">
      <Form {...form}>
        <div className="flex justify-end gap-4 px-10 mt-4">
          <Button
            onClick={openDialogShare} // Toggle edit mode
            variant={"secondary"}
          >
            Share
          </Button>
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
          <form onSubmit={form.handleSubmit(onSubmit)} className="w-full px-10">
            {/* Course Code Field */}
            <FormField
              control={form.control}
              name="videoName"
              render={({field}) => (
                <FormItem>
                  <FormLabel>Video Name</FormLabel>
                  <FormControl>
                    <Input placeholder={videoName} {...field} disabled={!isEditable}/>
                  </FormControl>
                  <FormDescription>
                    This is the video name.
                  </FormDescription>
                  <FormMessage/>
                </FormItem>
              )}
            />

            {/* Course Name Field */}
            <FormField
              control={form.control}
              name="videoDescription"
              render={({field}) => (
                <FormItem>
                  <FormLabel>Video Description</FormLabel>
                  <FormControl>
                    <Textarea placeholder={summary} {...field} disabled={!isEditable}/>
                  </FormControl>
                  <FormDescription>
                    This is the video description of the lecture video.
                  </FormDescription>
                  <FormMessage/>
                </FormItem>
              )}
            />
          </form>
      </Form>

      <Dialog open={isDialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Are you sure you want to delete the video?</DialogTitle>
          </DialogHeader>
          <DialogFooter>
            <Button onClick={handleDelete} type="submit" variant={"destructive"}>Yes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ShareDialog
        isDialogShareOpen={isDialogShareOpen}
        id={videoId}
        onOpenChange={setDialogShareOpen}
      />
    </div>
  );
}