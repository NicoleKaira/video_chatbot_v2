export interface Video {
  summary: string;
  videoId: string;
  videoName: string;
  thumbnail: string | null;
  visibility: string;
  status: string;
  videoDescription: string;
}

export interface Course {
  courseName: string;
  courseCode: string;
  courseVideos: Video[];
  visibility: string;
  courseDescription: string;
}

export interface CourseDetails {
  courseName: string;
  courseCode: string;
  courseDescription: string;
}

export enum Type {
  VIDEO = "VIDEO",
  COURSE = "COURSE",
}