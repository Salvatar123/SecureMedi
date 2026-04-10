/**
 * Secure API client with cryptographic token handling
 * Includes CSRF protection, secure headers, and token encryption
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  getAccessToken,
  storeAccessToken,
  getRefreshToken,
  storeRefreshToken,
  clearAllTokens,
  hasAccessToken,
  getEncryptionKey,
} from './secureStorage';

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Create secure API client with interceptors
 */
export function createSecureApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
      // Security headers
      'X-Requested-With': 'XMLHttpRequest', // CSRF protection
    },
    // Prevent credentials from being sent automatically
    withCredentials: false,
  });

  /**
   * Request interceptor: Add encrypted token to Authorization header
   */
  client.interceptors.request.use(
    async config => {
      try {
        const encKey = getEncryptionKey();
        
        // Only add token if we have one and can decrypt it
        if (hasAccessToken() && encKey) {
          const token = await getAccessToken(encKey);
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }
        
        // Add security headers
        config.headers['X-Requested-With'] = 'XMLHttpRequest';
        config.headers['Cache-Control'] = 'no-store';
        
        return config;
      } catch (error) {
        console.error('Request interceptor error:', error);
        return config;
      }
    },
    error => Promise.reject(error)
  );

  /**
   * Response interceptor: Handle token refresh on 401
   */
  client.interceptors.response.use(
    response => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as any;

      // Check if 401 (Unauthorized) and not already retried
      if (
        error.response?.status === 401 &&
        !originalRequest._retry
      ) {
        originalRequest._retry = true;

        try {
          const encKey = getEncryptionKey();
          if (!encKey) {
            clearAllTokens();
            redirectToLogin();
            return Promise.reject(error);
          }

          const refreshToken = await getRefreshToken(encKey);
          if (!refreshToken) {
            clearAllTokens();
            redirectToLogin();
            return Promise.reject(error);
          }

          // Request new access token
          const response = await axios.post(
            `${API_BASE_URL}/api/auth/refresh`,
            { refresh_token: refreshToken },
            {
              headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
              },
            }
          );

          const newAccessToken = response.data.access_token;

          // Store new token
          if (encKey && newAccessToken) {
            await storeAccessToken(newAccessToken, encKey);

            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return client(originalRequest);
          }
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          clearAllTokens();
          redirectToLogin();
          return Promise.reject(refreshError);
        }
      }

      // Handle 403 (Forbidden)
      if (error.response?.status === 403) {
        console.warn('Access forbidden');
        // Could redirect to permission denied page
      }

      return Promise.reject(error);
    }
  );

  return client;
}

/**
 * Redirect to login page (external redirect for security)
 */
function redirectToLogin(): void {
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

/**
 * Singleton API client instance
 */
let apiClient: AxiosInstance | null = null;

export function getApiClient(): AxiosInstance {
  if (!apiClient) {
    apiClient = createSecureApiClient();
  }
  return apiClient;
}

/**
 * Reset API client (useful for logout)
 */
export function resetApiClient(): void {
  apiClient = null;
}

/**
 * Verify token with server
 */
export async function verifyToken(token: string): Promise<boolean> {
  try {
    const client = getApiClient();
    const response = await client.post('/api/auth/verify', { token });
    return response.status === 200;
  } catch (error) {
    console.error('Token verification failed:', error);
    return false;
  }
}

/**
 * Logout and clear all credentials
 */
export async function logout(): Promise<void> {
  try {
    const client = getApiClient();
    const encKey = getEncryptionKey();

    if (hasAccessToken() && encKey) {
      const token = await getAccessToken(encKey);
      if (token) {
        await client.post(
          '/api/auth/logout',
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
      }
    }
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    clearAllTokens();
    resetApiClient();
  }
}

/**
 * Request access key for emergency access
 */
export async function requestAccessKey(patientId: string): Promise<string> {
  try {
    const client = getApiClient();
    const response = await client.post('/api/auth/request-key', { patient_id: patientId });
    return response.data.key;
  } catch (error) {
    console.error('Failed to request access key:', error);
    throw error;
  }
}

/**
 * Login with credentials and store encrypted tokens
 */
export async function loginWithEncryption(
  loginData: any,
  encKey: CryptoKey
): Promise<{ token: string; refreshToken: string; role: string }> {
  try {
    // Use axios directly without interceptor to avoid infinite loops
    const response = await axios.post(
      `${API_BASE_URL}/api/auth/login/doctor`,
      loginData,
      {
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        },
      }
    );

    const { token, refresh_token, role } = response.data;

    // Store encrypted tokens
    await storeAccessToken(token, encKey);
    await storeRefreshToken(refresh_token, encKey);

    return {
      token,
      refreshToken: refresh_token,
      role,
    };
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
}
