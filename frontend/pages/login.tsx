// Secure Login Page with Encryption

import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { Header } from "@/components/Header";
import { useAuthStore } from "@/stores/authStore";
import { getApiClient } from "@/lib/api";
import { generateEncryptionKey, isCryptoAvailable } from "@/lib/crypto";
import { sanitizeInput, isValidAddress, isValidPatientIdentifier } from "@/lib/sanitization";
import { setEncryptionKey as storeEncryptionKey } from "@/lib/secureStorage";
import toast from "react-hot-toast";

export default function LoginPage() {
  const router = useRouter();
  const { initializeEncryption } = useAuthStore();

  const [isDoctor, setIsDoctor] = useState(true);
  const [address, setAddress] = useState("");
  const [key, setKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cryptoSupported, setCryptoSupported] = useState(true);

  // Initialize encryption on component mount
  useEffect(() => {
    const initCrypto = async () => {
      if (!isCryptoAvailable()) {
        setCryptoSupported(false);
        setError(
          "Your browser does not support secure encryption. Please use a modern browser."
        );
        return;
      }

      try {
        await initializeEncryption();
        setCryptoSupported(true);
      } catch (err) {
        setCryptoSupported(false);
        setError(
          "Failed to initialize encryption. Please refresh the page."
        );
      }
    };

    initCrypto();
  }, [initializeEncryption]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate inputs
    if (!address || !key) {
      toast.error("Please fill all fields");
      return;
    }

    // Sanitize input
    const sanitizedAddress = sanitizeInput(address.trim());
    const sanitizedKey = sanitizeInput(key.trim());

    // Validate identifier format based on selected role
    if (isDoctor && !isValidAddress(sanitizedAddress)) {
      setError("Invalid wallet address format");
      toast.error("Invalid wallet address format");
      return;
    }

    if (!isDoctor && !isValidPatientIdentifier(sanitizedAddress)) {
      setError("Invalid patient ID format");
      toast.error("Invalid patient ID format");
      return;
    }

    if (!cryptoSupported) {
      setError("Encryption not available");
      toast.error("Encryption not supported in this browser");
      return;
    }

    setLoading(true);

    try {
      // Generate encryption key for this session
      const encryptionKey = await generateEncryptionKey();
      storeEncryptionKey(encryptionKey);

      // Get API client
      const apiClient = getApiClient();

      // Prepare login request
      const loginRequest = {
        address: sanitizedAddress,
        key: sanitizedKey,
      };

      // Attempt login based on role
      let response;
      if (isDoctor) {
        response = await apiClient.loginDoctor(loginRequest);
      } else {
        response = await apiClient.loginPatient(loginRequest);
      }

      // Check if login was successful
      if (response.success && response.token && response.refresh_token && response.role) {
        // Store tokens securely in auth store
        const { setTokens } = useAuthStore.getState();
        await setTokens(
          response.token,
          response.refresh_token,
          response.role,
          response.user_address || sanitizedAddress,
          response.user_name
        );

        toast.success(`Welcome, ${response.role}!`);

        // Redirect to dashboard or specified return URL
        const redirectUrl = (router.query.redirect as string) || "/dashboard";
        router.push(redirectUrl);
      } else {
        // Login returned success: false
        const errorMsg = response.message || "Login failed";
        setError(errorMsg);
        toast.error(errorMsg);
      }
    } catch (err: any) {
      let errorMessage = "Login failed. Please check your credentials.";

      if (err.message?.includes("Invalid request")) {
        errorMessage = "Invalid credentials - please verify your information";
      } else if (err.message?.includes("Unauthorized")) {
        errorMessage = "Invalid credentials";
      } else if (err.message?.includes("Access forbidden")) {
        errorMessage = "Your account is not authorized";
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      toast.error(errorMessage);
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Login - SecureMedi</title>
        <meta name="description" content="Secure login to SecureMedi" />
        {/* Security headers */}
        <meta httpEquiv="X-UA-Compatible" content="ie=edge" />
        <meta name="referrer" content="strict-origin-when-cross-origin" />
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

          {/* Encryption Status */}
          {!cryptoSupported && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              <p className="text-sm font-medium">
                ⚠️ Security Warning: Your browser doesn't support encryption.
                Please use a modern browser.
              </p>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-6 p-6 border border-border rounded-lg bg-card/50 backdrop-blur">
            {/* Role Toggle */}
            <div className="flex gap-2 bg-border/50 p-1 rounded-lg">
              <button
                type="button"
                onClick={() => {
                  setIsDoctor(true);
                  setError(null);
                }}
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
                onClick={() => {
                  setIsDoctor(false);
                  setError(null);
                }}
                className={`flex-1 py-2 rounded font-medium transition-colors ${
                  !isDoctor
                    ? "bg-primary text-white"
                    : "text-foreground/70 hover:text-foreground"
                }`}
              >
                Patient
              </button>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
                {error}
              </div>
            )}

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
                disabled={loading}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 text-foreground disabled:opacity-50 transition-colors"
                required
              />
            </div>

            {/* Key Field */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Private Key
              </label>
              <input
                type="password"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder={isDoctor ? "0x... doctor private key" : "0x... patient private key"}
                disabled={loading}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 text-foreground disabled:opacity-50 transition-colors"
                required
              />
              <p className="text-xs text-foreground/60 mt-1">
                Enter the private key linked to this account. Credentials are encrypted locally before transmission.
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !cryptoSupported}
              className="w-full py-2 bg-gradient-to-r from-primary to-secondary text-white rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="inline-block animate-spin">⌛</span>
                  Signing in...
                </span>
              ) : (
                "Login"
              )}
            </button>
          </form>

          {/* Security Info */}
          <div className="p-4 bg-border/20 rounded-lg border border-border/50">
            <p className="text-xs text-foreground/60 text-center leading-relaxed">
              🔐 All communications are encrypted using industry-standard AES-GCM encryption. Your credentials are never stored in plain text.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
