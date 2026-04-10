/**
 * App-level security configuration
 * Applied to all pages in _app.tsx
 */

import axios from 'axios';

/**
 * Configure axios defaults with security headers
 */
export function configureSecurityHeaders() {
  // Set default headers for all requests
  axios.defaults.headers.common = {
    'X-Requested-With': 'XMLHttpRequest',
    'Cache-Control': 'no-store',
  };

  // Prevent CORS credentials from being sent automatically
  axios.defaults.withCredentials = false;

  // Set timeout to prevent hanging requests
  axios.defaults.timeout = 10000;
}

/**
 * Configure Content Security Policy (CSP) headers
 * These should ideally be set by your web server/Next.js config
 */
export function getCSPHeaders() {
  return {
    'Content-Security-Policy': [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'", // Needed for Next.js, consider stricter policy in production
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self' data:",
      "connect-src 'self' http://localhost:8000 http://localhost:3000 http://localhost:3001",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join('; '),
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy':
      'geolocation=(), microphone=(), camera=(), payment=()',
  };
}

/**
 * Prevent sensitive data leaks in console (production only)
 */
export function disableConsoleInProduction() {
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'production') {
    const noop = () => {};
    window.console = {
      ...window.console,
      log: noop,
      debug: noop,
      info: noop,
      warn: noop,
      // Keep error for debugging
      error: console.error,
    } as any;
  }
}

/**
 * Disable right-click and developer tools in production
 * Optional based on security requirements
 */
export function disableDevTools(enable: boolean = false) {
  if (!enable || process.env.NODE_ENV !== 'production') return;

  // Disable right-click
  document.addEventListener('contextmenu', e => {
    e.preventDefault();
    return false;
  });

  // Disable F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C
  document.addEventListener('keydown', e => {
    if (
      e.key === 'F12' ||
      (e.ctrlKey && e.shiftKey && e.key === 'I') ||
      (e.ctrlKey && e.shiftKey && e.key === 'J') ||
      (e.ctrlKey && e.shiftKey && e.key === 'C')
    ) {
      e.preventDefault();
      return false;
    }
  });
}
