// Auth Store using Zustand

import { create } from "zustand";
import Cookie from "js-cookie";

export type UserRole = "DOCTOR" | "PATIENT" | "ADMIN";

interface AuthState {
  token: string | null;
  userAddress: string | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  login: (token: string, address: string, role: UserRole) => void;
  logout: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>((set: any) => ({
  token: null,
  userAddress: null,
  role: null,
  isAuthenticated: false,

  login: (token: string, address: string, role: UserRole) => {
    Cookie.set("auth_token", token, { expires: 7 });
    Cookie.set("user_address", address, { expires: 7 });
    Cookie.set("user_role", role, { expires: 7 });
    set({
      token,
      userAddress: address,
      role,
      isAuthenticated: true,
    });
  },

  logout: () => {
    Cookie.remove("auth_token");
    Cookie.remove("user_address");
    Cookie.remove("user_role");
    set({
      token: null,
      userAddress: null,
      role: null,
      isAuthenticated: false,
    });
  },

  initialize: () => {
    const token = Cookie.get("auth_token");
    const userAddress = Cookie.get("user_address");
    const role = Cookie.get("user_role") as UserRole;

    if (token && userAddress && role) {
      set({
        token,
        userAddress,
        role,
        isAuthenticated: true,
      });
    }
  },
}));
