import React from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import Link from "next/link";

interface ErrorPageProps {
  statusCode?: number;
}

const ErrorPage: React.FC<ErrorPageProps> = ({ statusCode = 500 }) => {
  const router = useRouter();
  const { code, message } = router.query;

  const errorCode = (code as string) || statusCode?.toString() || "500";
  const errorMessage = (message as string) || getErrorMessage(errorCode);
  const errorDescription = getErrorDescription(errorCode);

  function getErrorMessage(code: string): string {
    const messages: { [key: string]: string } = {
      "400": "Bad Request",
      "401": "Unauthorized",
      "403": "Forbidden",
      "404": "Not Found",
      "500": "Internal Server Error",
      "503": "Service Unavailable",
    };
    return messages[code] || "Error";
  }

  function getErrorDescription(code: string): string {
    const descriptions: { [key: string]: string } = {
      "400": "The request could not be understood by the server.",
      "401": "You must be authenticated to access this resource.",
      "403": "You do not have permission to access this resource.",
      "404": "The requested resource could not be found.",
      "500": "An unexpected error occurred on the server.",
      "503": "The service is temporarily unavailable.",
    };
    return descriptions[code] || "An error occurred.";
  }

  return (
    <>
      <Head>
        <title>{errorCode} - {errorMessage}</title>
      </Head>
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          {/* Error Icon */}
          <div className="mb-6">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-100 mb-4">
              <svg
                className="w-12 h-12 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>

          {/* Error Code */}
          <h1 className="text-6xl font-bold text-gray-900 mb-2">{errorCode}</h1>

          {/* Error Message */}
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            {errorMessage}
          </h2>

          {/* Error Description */}
          <p className="text-gray-600 mb-8">{errorDescription}</p>

          {/* Custom Message */}
          {message && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8">
              <p className="text-yellow-800 text-sm">{message}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 justify-center">
            {errorCode === "401" ? (
              <Link
                href="/login"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
              >
                Go to Login
              </Link>
            ) : (
              <>
                <button
                  onClick={() => router.back()}
                  className="px-6 py-3 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 transition font-medium"
                >
                  Go Back
                </button>
                <Link
                  href="/"
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                >
                  Go Home
                </Link>
              </>
            )}
          </div>

          {/* Additional Help */}
          <div className="mt-8 pt-8 border-t border-gray-300">
            <p className="text-gray-600 text-sm mb-4">
              If this problem persists, please contact support.
            </p>
            <div className="flex gap-4 justify-center">
              <a
                href="mailto:support@securemedi.com"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Email Support
              </a>
              <span className="text-gray-400">•</span>
              <a
                href="https://securemedi.com/help"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Help Center
              </a>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ErrorPage;
