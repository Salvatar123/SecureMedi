// Header Component

import React from "react";
import Link from "next/link";
import { useAuthStore } from "@/stores/authStore";
import { useRouter } from "next/router";
import { logout } from "@/lib/api";
import toast from "react-hot-toast";

export const Header: React.FC = () => {
  const { isAuthenticated, userRole, user } = useAuthStore();
  const logoutUser = useAuthStore((state) => state.logout);
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await logout();
      await logoutUser();
      toast.success("Logged out successfully");
      router.push("/login");
    } catch (error) {
      console.error("Logout error:", error);
      await logoutUser();
      router.push("/login");
    }
  };

  return (
    <header className="border-b border-border bg-card sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">SM</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              SecureMedi
            </span>
          </Link>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <div className="text-right">
                  <p className="text-sm font-semibold text-foreground">{user?.name || "User"}</p>
                  <p className="text-xs text-foreground/60">{userRole}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
