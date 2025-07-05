import axios from "axios"; // Ensure axios is imported
import Cookies from "js-cookie";

const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

export const addNewCourse = async (courseCode: string, courseName: string, courseDescription: string) => {
  try {
    const res = await axios.post(BASE_URL + `/course`, {
      "course_id": courseCode, "course_name": courseName, "course_description": courseDescription },
      {
        headers: { 'Content-Type': 'application/json' },
      });
    return res;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw error;
    } else {
      throw new Error('different error than axios');
    }
  }
};

export const logout = () => {
  Cookies.remove("token");
  Cookies.remove("user_id");
};