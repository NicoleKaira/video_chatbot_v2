import axios from "axios";
const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

async function deleteCourse(course_code: string) {
  try {
    const res = await axios.delete(BASE_URL + `/video`,
      { headers: { 'Content-Type': 'application/json' }, data: {"course_code": course_code}});
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
  deleteCourse
};
