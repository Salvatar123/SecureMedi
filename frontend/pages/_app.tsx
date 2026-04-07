// Next.js App Wrapper

import React, { useEffect } from "react";
import type { AppProps } from "next/app";
import "@/styles/globals.css";
import { useAuthStore } from "@/lib/auth";

function MyApp({ Component, pageProps }: AppProps) {
  const initialize = useAuthStore((state) => state.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return <Component {...pageProps} />;
}

export default MyApp;
