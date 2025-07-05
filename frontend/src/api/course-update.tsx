import axios from "axios";
import {
  formCourseSchema
} from "@/app/(browse)/manage/course/[course_code]/[course_name]/_components/course-details-form"; // Ensure axios is imported
const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

async function triggerCourseUpdate(data: formCourseSchema) {
  try {
    const res = await axios.put(BASE_URL + `/video`, {
      "course_detail": {
        "course_id": data.courseCode,
        "course_name": data.courseName,
        "course_description": data.courseDescription,
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
  triggerCourseUpdate
};
