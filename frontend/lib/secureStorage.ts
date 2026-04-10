/**
 * Secure token storage with encryption
 * Stores tokens in sessionStorage with encryption for added security
 */

import { encryptToken, decryptToken } from './crypto';

const TOKEN_KEY = 'auth_token_encrypted';
const REFRESH_TOKEN_KEY = 'refresh_token_encrypted';
const ENCRYPTION_KEY_KEY = 'enc_key';

/**
 * Store encrypted access token
 */
export async function storeAccessToken(
  token: string,
  encryptionKey: CryptoKey
): Promise<void> {
  try {
    const encrypted = await encryptToken(token, encryptionKey);
    sessionStorage.setItem(TOKEN_KEY, encrypted);
  } catch (error) {
    console.error('Failed to store access token:', error);
    throw new Error('Failed to store access token securely');
  }
}

/**
 * Retrieve and decrypt access token
 */
export async function getAccessToken(
  encryptionKey: CryptoKey
): Promise<string | null> {
  try {
    const encrypted = sessionStorage.getItem(TOKEN_KEY);
    if (!encrypted) return null;
    
    return await decryptToken(encrypted, encryptionKey);
  } catch (error) {
    console.error('Failed to retrieve access token:', error);
    // Clear corrupted token
    clearAccessToken();
    return null;
  }
}

/**
 * Store encrypted refresh token (longer-lived, consider sessionStorage only)
 */
export async function storeRefreshToken(
  token: string,
  encryptionKey: CryptoKey
): Promise<void> {
  try {
    const encrypted = await encryptToken(token, encryptionKey);
    sessionStorage.setItem(REFRESH_TOKEN_KEY, encrypted);
  } catch (error) {
    console.error('Failed to store refresh token:', error);
    throw new Error('Failed to store refresh token securely');
  }
}

/**
 * Retrieve and decrypt refresh token
 */
export async function getRefreshToken(
  encryptionKey: CryptoKey
): Promise<string | null> {
  try {
    const encrypted = sessionStorage.getItem(REFRESH_TOKEN_KEY);
    if (!encrypted) return null;
    
    return await decryptToken(encrypted, encryptionKey);
  } catch (error) {
    console.error('Failed to retrieve refresh token:', error);
    clearRefreshToken();
    return null;
  }
}

/**
 * Clear access token
 */
export function clearAccessToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}

/**
 * Clear refresh token
 */
export function clearRefreshToken(): void {
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * Clear all authentication data
 */
export function clearAllTokens(): void {
  clearAccessToken();
  clearRefreshToken();
}

/**
 * Check if access token exists (without decrypting)
 */
export function hasAccessToken(): boolean {
  return !!sessionStorage.getItem(TOKEN_KEY);
}

/**
 * Check if refresh token exists (without decrypting)
 */
export function hasRefreshToken(): boolean {
  return !!sessionStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Store encryption key in memory (never persist to storage)
 * Returns a function to retrieve it
 */
let encryptionKeyStore: CryptoKey | null = null;

export function setEncryptionKey(key: CryptoKey): void {
  encryptionKeyStore = key;
}

export function getEncryptionKey(): CryptoKey | null {
  return encryptionKeyStore;
}

export function clearEncryptionKey(): void {
  encryptionKeyStore = null;
}
