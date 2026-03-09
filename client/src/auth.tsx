import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { api, TokenResponse, UserResponse } from "./api";

type AuthState = {
  token: string | null;
  username: string | null;
  isAdmin: boolean;
  tokenBalance: number;
  loading: boolean;
  user: UserResponse | null;
};

const defaultState: AuthState = {
  token: localStorage.getItem("token"),
  username: null,
  isAdmin: false,
  tokenBalance: 0,
  loading: true,
  user: null,
};

const AuthContext = createContext<{
  state: AuthState;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshBalance: () => Promise<void>;
} | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(defaultState);

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setState((s) => ({ ...s, loading: false, token: null }));
      return;
    }
    try {
      const user = await api<UserResponse>("/api/auth/me");
      setState((s) => ({
        ...s,
        token,
        username: user.username,
        isAdmin: user.is_admin,
        tokenBalance: user.token_balance,
        user,
        loading: false,
      }));
    } catch {
      localStorage.removeItem("token");
      setState((s) => ({ ...s, token: null, loading: false }));
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = useCallback(async (email: string, password: string) => {
    const data = await api<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem("token", data.access_token);
    setState((s) => ({
      ...s,
      token: data.access_token,
      username: data.username,
      isAdmin: data.is_admin,
      tokenBalance: data.token_balance,
    }));
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    const data = await api<TokenResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem("token", data.access_token);
    setState((s) => ({
      ...s,
      token: data.access_token,
      username: data.username,
      isAdmin: data.is_admin,
      tokenBalance: data.token_balance,
    }));
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setState((s) => ({ ...s, token: null, username: null, user: null }));
  }, []);

  const refreshBalance = useCallback(async () => {
    try {
      const user = await api<UserResponse>("/api/auth/me");
      setState((s) => ({ ...s, tokenBalance: user.token_balance, user }));
    } catch {}
  }, []);

  return (
    <AuthContext.Provider value={{ state, login, register, logout, refreshBalance }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
