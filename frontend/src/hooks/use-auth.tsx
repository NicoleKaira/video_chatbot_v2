import { useState, useEffect } from "react";
import Cookies from "js-cookie";
import {login, logout} from "@/api/login";

export interface User {
  userId: string;
  role: string;
}

const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = Cookies.get("token");
    const userId = Cookies.get("user_id");
    const role = Cookies.get("role");
    if (token && userId && role) {
      setUser({ userId: userId, role: role });
    }
    setLoading(false);
  }, []);

  const loginUser = async (username: string, password: string) => {
    try {
      const { role, userId } = await login(username, password);
      setUser({ userId: userId, role: role });
      return true;
    } catch (error) {
      console.error("Error logging in:", error);
    }
  };

  const logoutUser = () => {
    logout();
    setUser(null);
  };

  const isAuthenticated = !!user;

  return {
    user,
    loginUser,
    logoutUser,
    loading,
    isAuthenticated,
  };
};

export default useAuth;
