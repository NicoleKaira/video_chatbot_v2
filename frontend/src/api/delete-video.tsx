import axios from "axios";
const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

async function deleteVideo(video_id: string) {
  try {
    const res = await axios.delete(BASE_URL + `/video`,
      { headers: { 'Content-Type': 'application/json' }, data: {"video_id": video_id}});
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
  deleteVideo
};
