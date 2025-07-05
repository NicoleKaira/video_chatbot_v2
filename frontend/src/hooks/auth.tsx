"use client";

import React, { createContext } from "react";
import useAuth, {User} from "./use-auth";

interface AuthContextType {
  user: User | null;
  loginUser: (username: string, password: string) => Promise<true | undefined>;
  logoutUser: () => void;
  loading: boolean;
  isAuthenticated: boolean;
}

const defaultAuthContextValue: AuthContextType = {
  user: null,
  loginUser: async () => true,  // Provide a no-op default function
  logoutUser: () => {},          // Provide a no-op default function
  loading: false,
  isAuthenticated: false
};

const AuthContext = createContext<AuthContextType>(defaultAuthContextValue);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const auth = useAuth();

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
};

export default AuthContext;
