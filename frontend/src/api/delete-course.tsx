import axios from "axios";
const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

async function deleteCourse(course_code: string) {
  try {
    const res = await axios.delete(BASE_URL + `/course`, {
      params: { course_code: course_code },
      headers: { 'Content-Type': 'application/json' }
    });
    return res.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error("Delete course API error:", {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        url: BASE_URL + `/course?course_code=${course_code}`
      });
      throw error;
    } else {
      throw new Error('different error than axios');
    }
  }
}

export default {
  deleteCourse
};
