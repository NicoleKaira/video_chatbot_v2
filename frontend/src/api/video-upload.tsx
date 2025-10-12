import axios from "axios";
import { FormDataUpload } from "@/app/(browse)/manage/upload/page";

const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

export interface Video {
  video_name: string;
  base64_encoded_video: string;
  video_description: string;
}

export interface VideoUploadParams {
  course_code: string;
  video: Video[];
}

// Convert file to base64 (raw base64 string without data URL prefix)
const readFileAsBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onloadend = () => {
      if (reader.result) {
        const dataUrl = reader.result as string;
        // Extract just the base64 part (remove "data:video/mp4;base64," prefix)
        const base64String = dataUrl.split(',')[1];
        console.log('Base64 conversion completed');
        resolve(base64String);
      } 
      else {
        reject("Failed to read file.");
      }
    };
    
    reader.readAsDataURL(file);
  });
};

export const uploadVideo = async (data: FormDataUpload) => {
  console.log("Uploading videos:", data);

  try {
    const videoUploadParams: VideoUploadParams = {
      course_code: data.courseCode,
      video: [],
    };

    console.log("Processing videos:", data.videos);

    // Convert all files to base64 asynchronously
    const videoPromises = data.videos.map(async (video) => {
      const file = video.file[0];
      console.log("Processing file:", file);

      const base64String = await readFileAsBase64(file);
      console.log("Base64 Encoded String:", base64String.substring(0, 100)); // Print first 100 chars

      return {
        video_name: video.videoName,
        base64_encoded_video: base64String,
        video_description: video.videoDescription,
      };
    });

    // Wait for all videos to be processed
    videoUploadParams.video = await Promise.all(videoPromises);

    console.log("Final payload:", videoUploadParams);

    // Submit the processed videos
    return await submitVideoUpload(videoUploadParams);
  } catch (error) {
    console.error("Error during video upload:", error);
    return false;
  }
};

const submitVideoUpload = async (videoUploadParams: VideoUploadParams) => {
  try {
    console.log("Submitting video upload:", videoUploadParams);

    const res = await axios.post(BASE_URL + `/upload`, videoUploadParams, {
      headers: { 'Content-Type': 'application/json' },
    });

    return res.status;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error("Axios error:", error.response?.data || error.message);
      throw error;
    } else {
      console.error("Unexpected error:", error);
      throw new Error("Error occurred during video upload submission");
    }
  }
};
