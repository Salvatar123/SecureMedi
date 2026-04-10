/**
 * Client-side encryption utilities for token protection
 * Uses Crypto Web API for AES-GCM encryption
 */

/**
 * Generate a random encryption key (in dev environment)
 * In production, this key should be derived from user password or secure key management
 */
export async function generateEncryptionKey(): Promise<CryptoKey> {
  return await window.crypto.subtle.generateKey(
    { name: 'AES-GCM', length: 256 },
    true, // extractable
    ['encrypt', 'decrypt']
  );
}

/**
 * Encrypt a token using AES-GCM
 */
export async function encryptToken(
  token: string,
  key: CryptoKey
): Promise<string> {
  const iv = window.crypto.getRandomValues(new Uint8Array(12));
  const encoder = new TextEncoder();
  
  const encryptedData = await window.crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    encoder.encode(token)
  );
  
  // Combine IV + encrypted data and encode as base64
  const combined = new Uint8Array(iv.length + encryptedData.byteLength);
  combined.set(iv, 0);
  combined.set(new Uint8Array(encryptedData), iv.length);
  
  return btoa(String.fromCharCode.apply(null, Array.from(combined)));
}

/**
 * Decrypt a token using AES-GCM
 */
export async function decryptToken(
  encryptedToken: string,
  key: CryptoKey
): Promise<string> {
  try {
    const combined = new Uint8Array(
      atob(encryptedToken)
        .split('')
        .map(c => c.charCodeAt(0))
    );
    
    const iv = combined.slice(0, 12);
    const encryptedData = combined.slice(12);
    
    const decryptedData = await window.crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      key,
      encryptedData
    );
    
    return new TextDecoder().decode(decryptedData);
  } catch (error) {
    console.error('Token decryption failed:', error);
    throw new Error('Failed to decrypt token');
  }
}

/**
 * Derive a key from a password (for alternative secure storage)
 * Uses PBKDF2
 */
export async function deriveKeyFromPassword(
  password: string,
  salt: Uint8Array
): Promise<CryptoKey> {
  const passwordKey = await window.crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(password),
    'PBKDF2',
    false,
    ['deriveBits', 'deriveKey']
  );
  
  return await window.crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt.buffer,
      iterations: 100000,
      hash: 'SHA-256',
    } as Pbkdf2Params,
    passwordKey,
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt', 'decrypt']
  );
}

/**
 * Generate a random salt for key derivation
 */
export function generateSalt(): Uint8Array {
  return window.crypto.getRandomValues(new Uint8Array(16));
}

/**
 * Check if crypto API is available
 */
export function isCryptoAvailable(): boolean {
  // Check if we're on the client side (browser environment)
  if (typeof window === 'undefined') {
    return false;
  }
  return !!(
    window.crypto &&
    window.crypto.subtle &&
    window.crypto.getRandomValues
  );
}
