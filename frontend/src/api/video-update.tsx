import axios from "axios";
import {formLectureSchema} from "@/app/(browse)/manage/[video_id]/_components/lecture-details-form";
const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

async function triggerVideoUpdate(video_id: string, data: formLectureSchema) {
  try {
    const res = await axios.put(BASE_URL + `/video`, {
        "video_detail": {
          "video_id": video_id,
          "video_name": data.videoName,
          "video_description": data.videoDescription,
        }
      },
      {
        headers: { 'Content-Type': 'application/json' },
      });
    return res.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw error;
    } else {
      throw new Error('different error than axios');
    }
  }
}

export default {
  triggerVideoUpdate
};
