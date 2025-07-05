import axios from "axios"; // Ensure axios is imported
import Cookies from "js-cookie";

const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

export const login = async (username: string, password: string) => {
  try {
    const res = await axios.post(BASE_URL + `/auth/login`, {
      "username": username, "password": password },
      {
        headers: { 'Content-Type': 'application/json' },
      });
    const { access_token, token_type, role, userId } = res.data;
    Cookies.set("token", access_token, { expires: 7 });
    Cookies.set("role", role, { expires: 7 });
    Cookies.set("user_id", userId, { expires: 7 })

    return { role, userId };
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