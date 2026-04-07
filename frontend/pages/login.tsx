// Login Page

import React, { useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { Header } from "@/components/Header";
import { useAuthStore } from "@/lib/auth";
import { apiClient } from "@/lib/api";
import toast from "react-hot-toast";

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  const [isDoctor, setIsDoctor] = useState(true);
  const [address, setAddress] = useState("");
  const [key, setKey] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!address || !key) {
      toast.error("Please fill all fields");
      return;
    }

    setLoading(true);

    try {
      const response = isDoctor
        ? await apiClient.loginDoctor(address, key)
        : await apiClient.loginPatient(address, key);

      const data = response.data;

      if (data.success) {
        login(data.token, data.user_address, data.role);
        toast.success(`Welcome, ${data.role}!`);
        router.push("/dashboard");
      } else {
        toast.error(data.message || "Login failed");
      }
    } catch (error) {
      toast.error("Login failed. Please check your credentials.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Login - SecureMedi</title>
      </Head>

      <Header />

      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="max-w-md w-full space-y-8">
          {/* Logo */}
          <div className="text-center">
            <div className="inline-block p-3 bg-gradient-to-br from-primary to-secondary rounded-lg mb-4">
              <span className="text-white font-bold text-2xl">SM</span>
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              SecureMedi
            </h1>
            <p className="text-foreground/70 mt-2">Secure Medical Data Platform</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-6 p-6 border border-border rounded-lg bg-card/50">
            {/* Role Toggle */}
            <div className="flex gap-2 bg-border/50 p-1 rounded-lg">
              <button
                type="button"
                onClick={() => setIsDoctor(true)}
                className={`flex-1 py-2 rounded font-medium transition-colors ${
                  isDoctor
                    ? "bg-primary text-white"
                    : "text-foreground/70 hover:text-foreground"
                }`}
              >
                Doctor
              </button>
              <button
                type="button"
                onClick={() => setIsDoctor(false)}
                className={`flex-1 py-2 rounded font-medium transition-colors ${
                  !isDoctor
                    ? "bg-primary text-white"
                    : "text-foreground/70 hover:text-foreground"
                }`}
              >
                Patient
              </button>
            </div>

            {/* Address Field */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                {isDoctor ? "Wallet Address" : "Patient ID"}
              </label>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder={isDoctor ? "0x..." : "P001"}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:border-primary text-foreground"
              />
            </div>

            {/* Key Field */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                {isDoctor ? "Access Key" : "Private Key"}
              </label>
              <input
                type="password"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="Enter your key"
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:border-primary text-foreground"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-gradient-to-r from-primary to-secondary text-white rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 transition-all"
            >
              {loading ? "Logging in..." : "Login"}
            </button>
          </form>

          {/* Demo Info */}
          <div className="p-4 bg-border/20 rounded-lg border border-border/50">
            <p className="text-xs text-foreground/60 text-center">
              This is a secure healthcare platform. Use your registered credentials to access your account.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
