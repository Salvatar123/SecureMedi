// Next.js App Wrapper with Security Configuration

import React, { useEffect } from "react";
import type { AppProps } from "next/app";
import "@/styles/globals.css";
import { useAuthStore } from "@/stores/authStore";
import { configureSecurityHeaders } from "@/lib/securityConfig";

// Configure security headers and defaults
if (typeof window !== 'undefined') {
  configureSecurityHeaders();
}

function MyApp({ Component, pageProps }: AppProps) {
  const initializeEncryption = useAuthStore((state) => state.initializeEncryption);

  useEffect(() => {
    initializeEncryption();
  }, [initializeEncryption]);

  return <Component {...pageProps} />;
}

export default MyApp;
