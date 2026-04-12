/**
 * Secure Authentication Store with Encryption
 * Combines auth state management with secure token handling
 */

import { create } from 'zustand';
import {
  generateEncryptionKey,
  isCryptoAvailable,
} from '../lib/crypto';
import {
  setEncryptionKey,
  clearEncryptionKey,
  clearAllTokens,
  hasAccessToken,
  getEncryptionKey,
  storeAccessToken,
  storeRefreshToken,
} from '../lib/secureStorage';
import { resetApiClient } from '../lib/api';
import { UserRole } from '../types';
import Cookie from 'js-cookie';

interface AuthState {
  // User info
  user: { address: string; name?: string } | null;
  userRole: UserRole | null;
  isAuthenticated: boolean;
  
  // Tokens
  token: string | null;
  refreshToken: string | null;

  // Encryption
  encryptionKey: CryptoKey | null;
  encryptionAvailable: boolean;

  // Loading states
  isLoading: boolean;
  error: string | null;

  // Actions
  initializeEncryption: () => Promise<void>;
  setUser: (user: any, role: UserRole) => void;
  setTokens: (token: string, refreshToken: string, role: UserRole, address: string, name?: string) => Promise<void>;
  setAuthenticated: (isAuth: boolean) => void;
  logout: () => Promise<void>;
  clearError: () => void;
  checkTokenValidity: () => boolean;
  refreshTokens: (newToken: string, newRefreshToken: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  // Initial state
  user: null,
  userRole: null,
  isAuthenticated: false,
  token: null,
  refreshToken: null,
  encryptionKey: null,
  encryptionAvailable: typeof window !== 'undefined' && isCryptoAvailable(),
  isLoading: false,
  error: null,

  // Initialize encryption on app load
  initializeEncryption: async () => {
    set({ isLoading: true });
    try {
      if (!isCryptoAvailable()) {
        throw new Error(
          'Encryption not available. Please use a modern browser.'
        );
      }

      const key = await generateEncryptionKey();
      setEncryptionKey(key);
      set({ encryptionKey: key, encryptionAvailable: true, error: null });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Encryption initialization failed';
      set({ error: message, encryptionAvailable: false });
      console.error('Encryption init error:', error);
    } finally {
      set({ isLoading: false });
    }
  },

  // Set user info and tokens after successful login
  setTokens: async (token: string, refreshToken: string, role: UserRole, address: string, name?: string) => {
    try {
      let encKey = get().encryptionKey;

      // Recover key from in-memory secure storage if Zustand state was reset.
      if (!encKey) {
        const recovered = getEncryptionKey();
        if (recovered) {
          encKey = recovered;
          set({ encryptionKey: recovered, encryptionAvailable: true });
        }
      }

      // Last-resort key generation to avoid login failure on initialization races.
      if (!encKey) {
        if (!isCryptoAvailable()) {
          throw new Error('Encryption key not available');
        }
        encKey = await generateEncryptionKey();
        setEncryptionKey(encKey);
        set({ encryptionKey: encKey, encryptionAvailable: true });
      }
      
      // Store tokens securely
      await storeAccessToken(token, encKey);
      await storeRefreshToken(refreshToken, encKey);
      
      // Also set in cookies for backwards compatibility
      Cookie.set('auth_token', token, { 
        expires: 7,
        secure: true,
        sameSite: 'Strict'
      });
      Cookie.set('refresh_token', refreshToken, {
        expires: 7,
        secure: true,
        sameSite: 'Strict'
      });

      set({
        token,
        refreshToken,
        user: { address, name },
        userRole: role,
        isAuthenticated: true,
        error: null,
      });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to store tokens';
      set({ error: errorMsg });
      throw error;
    }
  },

  // Set user info after login
  setUser: (user: any, role: UserRole) => {
    set({
      user: {
        address: user.address || user.user_address,
        name: user.name,
      },
      userRole: role,
      isAuthenticated: true,
      error: null,
    });
  },

  // Set authentication status
  setAuthenticated: (isAuth: boolean) => {
    if (!isAuth) {
      set({
        isAuthenticated: false,
        user: null,
        userRole: null,
      });
    } else {
      set({ isAuthenticated: true });
    }
  },

  // Update tokens on refresh
  refreshTokens: async (newToken: string, newRefreshToken: string) => {
    try {
      let encKey = get().encryptionKey;

      if (!encKey) {
        const recovered = getEncryptionKey();
        if (recovered) {
          encKey = recovered;
          set({ encryptionKey: recovered, encryptionAvailable: true });
        }
      }

      if (!encKey) {
        if (!isCryptoAvailable()) {
          throw new Error('Encryption key not available');
        }
        encKey = await generateEncryptionKey();
        setEncryptionKey(encKey);
        set({ encryptionKey: encKey, encryptionAvailable: true });
      }
      
      await storeAccessToken(newToken, encKey);
      await storeRefreshToken(newRefreshToken, encKey);
      Cookie.set('auth_token', newToken, {
        expires: 7,
        secure: true,
        sameSite: 'Strict'
      });
      Cookie.set('refresh_token', newRefreshToken, {
        expires: 7,
        secure: true,
        sameSite: 'Strict'
      });
      set({ token: newToken, refreshToken: newRefreshToken });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to refresh tokens';
      set({ error: errorMsg });
      throw error;
    }
  },

  // Logout: clear all auth data
  logout: async () => {
    set({ isLoading: true });
    try {
      // Clear tokens from storage
      clearAllTokens();
      // Clear encryption key from memory
      clearEncryptionKey();
      // Reset API client
      resetApiClient();
      
      // Clear cookies
      Cookie.remove('auth_token');
      Cookie.remove('refresh_token');
      Cookie.remove('user_address');
      Cookie.remove('user_role');

      set({
        isAuthenticated: false,
        user: null,
        userRole: null,
        token: null,
        refreshToken: null,
        encryptionKey: null,
        error: null,
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      set({ isLoading: false });
    }
  },

  // Clear error messages
  clearError: () => {
    set({ error: null });
  },

  // Check if token is still valid
  checkTokenValidity: (): boolean => {
    const encKey = getEncryptionKey();
    const hasToken = hasAccessToken();
    return !!(encKey && hasToken);
  },
}));

/**
 * Hook to initialize auth on app startup
 */
export function useInitializeAuth() {
  const { encryptionKey, initializeEncryption } = useAuthStore();

  // Initialize encryption on mount
  if (typeof window !== 'undefined' && !encryptionKey) {
    initializeEncryption();
  }
}
