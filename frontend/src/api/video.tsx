import axios from "axios"; // Ensure axios is imported
const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

async function fetchVideoWidget(video_id: string) {
  try {
    const res = await axios.get(BASE_URL + `/video_indexer/${video_id}`, {
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
  fetchVideoWidget
};
