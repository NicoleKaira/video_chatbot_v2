import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

export interface LogResponse {
  logs: string[];
  total_lines: number;
  returned_lines: number;
  error?: string;
}

export const fetchLogs = async (lines: number = 100, since?: string): Promise<LogResponse> => {
  try {
    const params: { lines?: number; since?: string } = { lines };
    if (since) {
      params.since = since;
    }
    
    const res = await axios.get<LogResponse>(BASE_URL + `/logs`, { params });
    return res.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error("Axios error fetching logs:", error.response?.data || error.message);
      throw error;
    } else {
      console.error("Unexpected error fetching logs:", error);
      throw new Error("Error occurred while fetching logs");
    }
  }
};

