import axios from "axios"; // Ensure axios is imported
const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

export const getManageStreams = async () => {
  try {
    const res = await axios.get(BASE_URL + `/videos/manage`, {
      headers: { 'Content-Type': 'application/json' },
    });

    return res.data.course_video_mapping;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw error;
    } else {
      throw new Error('different error than axios');
    }
  }
};