// Document Configuration

import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta charSet="utf-8" />
        <meta name="description" content="SecureMedi - Secure Medical Data Platform" />
        <meta name="theme-color" content="#667eea" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='75' font-size='75' font-weight='bold' fill='%23667eea'>SM</text></svg>" />
      </Head>
      <body className="bg-background text-foreground">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
