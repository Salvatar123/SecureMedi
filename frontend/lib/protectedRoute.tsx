/**
 * Protected Route Component
 * Ensures only authenticated users can access certain routes
 */

import { useEffect, ReactNode } from 'react';
import { useRouter } from 'next/router';
import { useAuthStore } from '../stores/authStore';
import { hasAccessToken, getEncryptionKey } from './secureStorage';
import { UserRole } from '../types';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredRole?: UserRole | UserRole[] | null;
  fallbackUrl?: string;
}

/**
 * Higher-order component for protected routes
 * Redirect to login if not authenticated
 * Redirect to unauthorized if insufficient permissions
 */
export function withProtectedRoute(
  Component: React.ComponentType<any>,
  options?: {
    requiredRole?: UserRole | UserRole[] | null;
    fallbackUrl?: string;
  }
) {
  return function ProtectedComponent(props: any) {
    const router = useRouter();
    const { isAuthenticated, userRole } = useAuthStore();

    const hasRequiredRole = () => {
      if (!options?.requiredRole) return true;
      if (!userRole) return false;
      if (Array.isArray(options.requiredRole)) {
        return options.requiredRole.includes(userRole);
      }
      return userRole === options.requiredRole;
    };

    useEffect(() => {
      // Check if user is authenticated
      const isAuth = isAuthenticated && hasAccessToken() && getEncryptionKey();

      if (!isAuth) {
        // Redirect to login with return URL
        router.push(`/login?redirect=${router.asPath}`);
        return;
      }

      // Check role if required
      if (!hasRequiredRole()) {
        // Redirect to unauthorized page
        router.push('/error?code=403&message=Insufficient%20permissions');
        return;
      }
    }, [isAuthenticated, userRole, router]);

    // Show loading state while checking authentication
    if (!isAuthenticated || !hasAccessToken()) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Authenticating...</p>
          </div>
        </div>
      );
    }

    // Check permissions
    if (!hasRequiredRole()) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600">Access Denied</h1>
            <p className="mt-2 text-gray-600">You don't have permission to access this page</p>
          </div>
        </div>
      );
    }

    return <Component {...props} />;
  };
}

/**
 * Protected Route Component (functional approach)
 */
export function ProtectedRoute({
  children,
  requiredRole,
  fallbackUrl = '/login',
}: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated, userRole } = useAuthStore();

  const hasRequiredRole = () => {
    if (!requiredRole) return true;
    if (!userRole) return false;
    if (Array.isArray(requiredRole)) {
      return requiredRole.includes(userRole);
    }
    return userRole === requiredRole;
  };

  useEffect(() => {
    const isAuth = isAuthenticated && hasAccessToken() && getEncryptionKey();

    if (!isAuth) {
      router.push(`${fallbackUrl}?redirect=${router.asPath}`);
      return;
    }

    if (!hasRequiredRole()) {
      router.push('/error?code=403');
      return;
    }
  }, [isAuthenticated, userRole, router, requiredRole, fallbackUrl]);

  const isAuth = isAuthenticated && hasAccessToken() && getEncryptionKey();

  if (!isAuth) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!hasRequiredRole()) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="bg-white p-8 rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold text-red-600">Access Denied</h1>
          <p className="mt-2 text-gray-600">
            You don't have permission to access this resource
          </p>
          <button
            onClick={() => router.push('/')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
